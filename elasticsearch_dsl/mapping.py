try:
    import collections.abc as collections_abc  # only works on python 3.3+
except ImportError:
    import collections as collections_abc

from six import iteritems, itervalues
from itertools import chain

from .utils import DslBase
from .field import Text, construct_field, Nested
from .connections import connections

META_FIELDS = frozenset((
    'dynamic', 'transform', 'dynamic_date_formats', 'date_detection',
    'numeric_detection', 'dynamic_templates', 'enabled'
))

class Properties(DslBase):
    _param_defs = {'properties': {'type': 'field', 'hash': True}}
    def __init__(self, name):
        self._name = name
        super(Properties, self).__init__()

    def __repr__(self):
        return 'Properties(%r)' % self._name

    def __getitem__(self, name):
        return self.properties[name]

    def __contains__(self, name):
        return name in self.properties

    @property
    def name(self):
        return self._name

    def field(self, name, *args, **kwargs):
        self.properties[name] = construct_field(*args, **kwargs)
        return self

    def _collect_fields(self):
        """ Iterate over all Field objects within, including multi fields. """
        for f in itervalues(self.properties.to_dict()):
            yield f
            # multi fields
            if hasattr(f, 'fields'):
                for inner_f in itervalues(f.fields.to_dict()):
                    yield inner_f
            # nested and inner objects
            if hasattr(f, '_collect_fields'):
                for inner_f in f._collect_fields():
                    yield inner_f

    def update(self, other_object):
        if not hasattr(other_object, 'properties'):
            # not an inner/nested object, no merge possible
            return

        our, other = self.properties, other_object.properties
        for name in other:
            if name in our:
                if hasattr(our[name], 'update'):
                    our[name].update(other[name])
                continue
            our[name] = other[name]


class Mapping(object):
    def __init__(self, name):
        self.properties = Properties(name)
        self._meta = {}

    def __repr__(self):
        return 'Mapping(%r)' % self.doc_type

    def _clone(self):
        m = Mapping(self.properties.name)
        m.properties._params = self.properties._params.copy()
        return m

    @classmethod
    def from_es(cls, index, doc_type, using='default'):
        m = cls(doc_type)
        m.update_from_es(index, using)
        return m

    def resolve_nested(self, field_path):
        field = self
        nested = []
        parts = field_path.split('.')
        for i, step in enumerate(parts):
            try:
                field = field[step]
            except KeyError:
                return (), None
            if isinstance(field, Nested):
                nested.append('.'.join(parts[:i+1]))
        return nested, field

    def resolve_field(self, field_path):
        field = self
        for step in field_path.split('.'):
            try:
                field = field[step]
            except KeyError:
                return
        return field

    def _collect_analysis(self):
        analysis = {}
        fields = []
        if '_all' in self._meta:
            fields.append(Text(**self._meta['_all']))

        for f in chain(fields, self.properties._collect_fields()):
            for analyzer_name in ('analyzer', 'normalizer', 'search_analyzer', 'search_quote_analyzer'):
                if not hasattr(f, analyzer_name):
                    continue
                analyzer = getattr(f, analyzer_name)
                d = analyzer.get_analysis_definition()
                # empty custom analyzer, probably already defined out of our control
                if not d:
                    continue

                # merge the definition
                # TODO: conflict detection/resolution
                for key in d:
                    analysis.setdefault(key, {}).update(d[key])

        return analysis

    def save(self, index, using='default'):
        from .index import Index
        index = Index(index, doc_type=self.doc_type, using=using)
        index.mapping(self)
        return index.save()

    def update_from_es(self, index, using='default'):
        es = connections.get_connection(using)
        raw = es.indices.get_mapping(index=index, doc_type=self.doc_type)
        _, raw = raw.popitem()
        self._update_from_dict(raw['mappings'])

    def _update_from_dict(self, raw):
        raw = raw[self.doc_type]
        for name, definition in iteritems(raw.get('properties', {})):
            self.field(name, definition)

        # metadata like _all etc
        for name, value in iteritems(raw):
            if name != 'properties':
                if isinstance(value, collections_abc.Mapping):
                    self.meta(name, **value)
                else:
                    self.meta(name, value)

    def update(self, mapping, update_only=False):
        for name in mapping:
            if update_only and name in self:
                # nested and inner objects, merge recursively
                if hasattr(self[name], 'update'):
                    # FIXME only merge subfields, not the settings
                    self[name].update(mapping[name], update_only)
                continue
            self.field(name, mapping[name])

        if update_only:
            for name in mapping._meta:
                if name not in self._meta:
                    self._meta[name] = mapping._meta[name]
        else:
            self._meta.update(mapping._meta)

    def __contains__(self, name):
        return name in self.properties.properties

    def __getitem__(self, name):
        return self.properties.properties[name]

    def __iter__(self):
        return iter(self.properties.properties)

    @property
    def doc_type(self):
        return self.properties.name

    def field(self, *args, **kwargs):
        self.properties.field(*args, **kwargs)
        return self

    def meta(self, name, params=None, **kwargs):
        if not name.startswith('_') and name not in META_FIELDS:
            name = '_' + name

        if params and kwargs:
            raise ValueError('Meta configs cannot have both value and a dictionary.')

        self._meta[name] = kwargs if params is None else params
        return self

    def to_dict(self):
        d = self.properties.to_dict()
        meta = self._meta

        # hard coded serialization of analyzers in _all
        if '_all' in meta:
            meta = meta.copy()
            _all = meta['_all'] = meta['_all'].copy()
            for f in ('analyzer', 'search_analyzer', 'search_quote_analyzer'):
                if hasattr(_all.get(f, None), 'to_dict'):
                    _all[f] = _all[f].to_dict()
        d[self.doc_type].update(meta)
        return d
