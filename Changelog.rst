.. _changelog:

Changelog
=========

6.4.0 (2019-04-26)
------------------

* ``Index.document`` now correctly sets the ``Document``'s ``_index`` only when
  using default index (``#1091``)
* ``Document`` inheritance allows overriding ``Object`` and ``Nested`` field metadata like ``dynamic``
* adding ``auto_date_histogram`` aggregation
* Do not change data in place when (de)serializing



6.3.1 (2018-12-05)
------------------

* ``Analyzer.simulate`` now supports built-in analyzers
* proper (de)serialization of the ``Range`` wrapper
* Added ``search_analyzer`` to ``Completion`` field

6.3.0 (2018-11-21)
------------------

* Fixed logic around defining a different ``doc_type`` name.
* Added ``retry_on_conflict`` parameter to ``Document.update``.
* fields defined on an index are now used to (de)serialize the data even when
  not defined on a ``Document``
* Allow ``Index.analyzer`` to construct the analyzer
* Detect conflict in analyzer definitions when calling ``Index.analyzer``
* Detect conflicting mappings when creating an index
* Add ``simulate`` method to ``analyzer`` object to test the analyzer using the
  ``_analyze`` API.
* Add ``script`` and ``script_id`` options to ``Document.update``
* ``Facet`` can now use other metric than ``doc_count``
* ``Range`` objects to help with storing and working with ``_range`` fields
* Improved behavior of ``Index.save`` where it does a better job when index
  already exists
* Composite aggregations now correctly support multiple ``sources`` aggs
* ``UpdateByQuery`` implementated by @emarcey

6.2.1 (2018-07-03)
------------------

* allow users to redefine ``doc_type`` in ``Index`` (``#929``)
* include ``DocType`` in ``elasticsearch_dsl`` module directly (``#930``)

6.2.0 (2018-07-03)
------------------

**Backwards incompatible change** - ``DocType`` refactoring.

In ``6.2.0`` we refactored the ``DocType`` class and renamed it to
``Document``. The primary motivation for this was the support for types being
dropped from elasticsearch itself in ``7.x`` - we needed to somehow link the
``Index`` and ``Document`` classes. To do this we split the options that were
previously defined in the ``class Meta`` between it and newly introduced
``class Index``. The split is that all options that were tied to mappings (like
setting ``dynamic = MetaField('strict')``) remain in ``class Meta`` and all
options for index definition (like ``settings``, ``name``, or ``aliases``) got
moved to the new ``class Index``.

You can see some examples of the new functionality in the ``examples``
directory. Documentation has been updated to reflect the new API.

``DocType`` is now just an alias for ``Document`` which will be removed in
``7.x``. It does, however, work in the new way which is not fully backwards
compatible.

* ``Percolator`` field now expects ``Query`` objects as values
* you can no longer access meta fields on a ``Document`` instance by specifying
  ``._id`` or similar. Instead all access needs to happen via the ``.meta``
  attribute.
* Implemented ``NestedFacet`` for ``FacetedSearch``. This brought a need to
  slightly change the semantics of ``Facet.get_values`` which now expects the
  whole data dict for the aggregation, not just the ``buckets``. This is
  a backwards incompatible change for custom aggregations that redefine that
  method.
* ``Document.update`` now supports ``refresh`` kwarg
* ``DslBase._clone`` now produces a shallow copy, this means that modifying an
  existing query can have effects on existing ``Search`` objects.
* Empty ``Search`` no longer defaults to ``match_all`` query and instead leaves
  the ``query`` key empty. This is backwards incompatible when using
  ``suggest``.

6.1.0 (2018-01-09)
------------------

* Removed ``String`` field.
* Fixed issue with ``Object``/``Nested`` deserialization

6.0.1 (2018-01-02)
------------------

Fixing wheel package for Python 2.7 (#803)

6.0.0 (2018-01-01)
------------------

Backwards incompatible release compatible with elasticsearch 6.0, changes
include:

 * use ``doc`` as default ``DocType`` name, this change includes:
   * ``DocType._doc_type.matches`` method is now used to determine which
   ``DocType`` should be used for a hit instead of just checking ``_type``
 * ``Nested`` and ``Object`` field refactoring using newly introduced
   ``InnerDoc`` class. To define a ``Nested``/``Object`` field just define the
   ``InnerDoc`` subclass and then use it when defining the field::

      class Comment(InnerDoc):
          body = Text()
          created_at = Date()

      class Blog(DocType):
          comments = Nested(Comment)

 * methods on ``connections`` singleton are now exposed on the ``connections``
   module directly.
 * field values are now only deserialized when coming from elasticsearch (via
   ``from_es`` method) and not when assigning values in python (either by
   direct assignment or in ``__init__``).

5.4.0 (2017-12-06)
------------------
 * fix ``ip_range`` aggregation and rename the class to ``IPRange``.
   ``Iprange`` is kept for bw compatibility
 * fix bug in loading an aggregation with meta data from dict
 * add support for ``normalizer`` parameter of ``Keyword`` fields
 * ``IndexTemplate`` can now be specified using the same API as ``Index``
 * ``Boolean`` field now accepts ``"false"`` as ``False``

5.3.0 (2017-05-18)
------------------
 * fix constant score query definition
 * ``DateHistogramFacet`` now works with ``datetime`` objects
 * respect ``__`` in field names when creating queries from dict

5.2.0 (2017-03-26)
------------------
 * make sure all response structers are pickleable (for caching)
 * adding ``exclude`` to ``Search``
 * fix metric aggregation deserialization
 * expose all index-level APIs on ``Index`` class
 * adding ``delete`` to ``Search`` which calls ``delete_by_query`` API

5.1.0 (2017-01-08)
------------------
 * Renamed ``Result`` and ``ResultMeta`` to ``Hit`` and ``HitMeta`` respectively
 * ``Response`` now stores ``Search`` which it gets as first arg to ``__init__``
 * aggregation results are now wrapped in classes and properly deserialized
 * ``Date`` fields now allow for numerical timestamps in the java format (in millis)
 * Added API documentation
 * replaced generated classes with manually created

5.0.0 (2016-11-04)
------------------
Version compatible with elasticsearch 5.0.

Breaking changes:

 * ``String`` field type has been deprecated in favor of ``Text`` and ``Keyword``
 * ``fields`` method has been removed in favor of ``source`` filtering

2.2.0 (2016-11-04)
------------------
 * accessing missing string fields no longer returnd ``''`` but returns
   ``None`` instead.
 * fix issues with bool's ``|`` and ``&`` operators and ``minimum_should_match``

2.1.0 (2016-06-29)
------------------
 * ``inner_hits`` are now also wrapped in ``Response``
 * ``+`` operator is deprecated, ``.query()`` now uses ``&`` to combine queries
 * added ``mget`` method to ``DocType``
 * fixed validation for "empty" values like ``''`` and ``[]``

2.0.0 (2016-02-18)
------------------
Compatibility with Elasticsearch 2.x:

 * Filters have been removed and additional queries have been added. Instead of
   ``F`` objects you can now use ``Q``.
 * ``Search.filter`` is now just a shortcut to add queries in filter context
 * support for pipeline aggregations added

Backwards incompatible changes:

 * list of analysis objects and classes was removed, any string used as
   tokenizer, char or token filter or analyzer will be treated as a builtin
 * internal method ``Field.to_python`` has been renamed to ``deserialize`` and
   an optional serialization mechanic for fields has been added.
 * Custom response class is now set by ``response_class`` method instead of a
   kwarg to ``Search.execute``

Other changes:

 * ``FacetedSearch`` now supports pagination via slicing

0.0.10 (2016-01-24)
-------------------
 * ``Search`` can now be iterated over to get back hits
 * ``Search`` now caches responses from Elasticsearch
 * ``DateHistogramFacet`` now defaults to returning empty intervals
 * ``Search`` no longer accepts positional parameters
 * Experimental ``MultiSearch`` API
 * added option to talk to ``_suggest`` endpoint (``execute_suggest``)

0.0.9 (2015-10-26)
------------------
 * ``FacetedSearch`` now uses its own ``Facet`` class instead of built in
   aggregations

0.0.8 (2015-08-28)
------------------
 * ``0.0.5`` and ``0.0.6`` was released with broken .tar.gz on pypi, just a build fix

0.0.5 (2015-08-27)
------------------
 * added support for (index/search)_analyzer via #143, thanks @wkiser!
 * even keys accessed via ``['field']`` on ``AttrDict`` will be wrapped in
   ``Attr[Dict|List]`` for consistency
 * Added a convenient option to specify a custom ``doc_class`` to wrap
   inner/Nested documents
 * ``blank`` option has been removed
 * ``AttributeError`` is no longer raised when accessing an empty field.
 * added ``required`` flag to fields and validation hooks to fields and
   (sub)documents
 * removed ``get`` method from ``AttrDict``. Use ``getattr(d, key, default)``
   instead.
 * added ``FacetedSearch`` for easy declarative faceted navigation

0.0.4 (2015-04-24)
------------------

 * Metadata fields (such as id, parent, index, version etc) must be stored (and
   retrieved) using the ``meta`` attribute (#58) on both ``Result`` and
   ``DocType`` objects or using their underscored variants (``_id``,
   ``_parent`` etc)
 * query on Search can now be directly assigned
 * ``suggest`` method added to ``Search``
 * ``Search.doc_type`` now accepts ``DocType`` subclasses directly
 * ``Properties.property`` method renamed to ``field`` for consistency
 * Date field now raises ``ValidationException`` on incorrect data

0.0.3 (2015-01-23)
------------------

Added persistence layer (``Mapping`` and ``DocType``), various fixes and
improvements.

0.0.2 (2014-08-27)
------------------

Fix for python 2

0.0.1 (2014-08-27)
------------------

Initial release.
