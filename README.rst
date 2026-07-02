MongoLog: centralized logging with MongoDB
==========================================

.. image:: https://github.com/puentesarrin/mongodb-log/actions/workflows/ci.yml/badge.svg
   :target: https://github.com/puentesarrin/mongodb-log/actions/workflows/ci.yml
   :alt: CI status

.. image:: https://coveralls.io/repos/github/puentesarrin/mongodb-log/badge.svg?branch=master
   :target: https://coveralls.io/github/puentesarrin/mongodb-log?branch=master
   :alt: Coverage status

.. image:: https://img.shields.io/pypi/v/mongolog.svg
   :target: https://pypi.org/project/mongolog/
   :alt: PyPI version

MongoLog is a Python logging handler that stores standard ``logging`` records
in a MongoDB collection. It keeps the normal log record fields and adds useful
context such as host, current user, UTC time, rendered message text, and
formatted exception tracebacks.

MongoLog supports Python 3.9 and newer. CI tests against MongoDB 5, 6, 7, and 8.

Installation
------------

Install from PyPI::

   $ python -m pip install mongolog

Or install the latest source checkout::

   $ python -m pip install git+https://github.com/puentesarrin/mongodb-log.git

MongoDB setup
-------------

Create a collection for log records. A capped collection is useful for log data
because older records automatically roll out when the collection reaches its
configured size::

   > use mongolog
   > db.createCollection('log', {capped: true, size: 100000})

Usage
-----

Add ``MongoHandler`` to any standard Python logger::

   import logging

   from mongolog import MongoHandler


   log = logging.getLogger('demo')
   log.setLevel(logging.DEBUG)
   log.addHandler(MongoHandler.to('log', db='mongolog'))

   log.debug('Some message')

Structured messages remain queryable in MongoDB because MongoLog stores the
original ``record.msg`` value::

   log.info({'address': '340 N 12th St', 'state': 'PA', 'country': 'US'})

Development
-----------

Install development tools and run the test suite with tox::

   $ python -m pip install -e ".[dev]"
   $ tox

The tests use a real MongoDB server. By default they connect to
``localhost:27017``. Override that with ``MONGO_HOST`` and ``MONGO_PORT``::

   $ MONGO_HOST=localhost MONGO_PORT=27017 tox

Run the same tests directly with unittest::

   $ python -m unittest discover -s tests -p 'test_*.py'

To test against specific Python interpreters installed on your machine::

   $ tox -e py39,py310,py311,py312,py313,py314

Releases
--------

CI builds the source distribution and wheel on every push. Tag pushes publish
to PyPI through GitHub Actions Trusted Publishing using the ``pypi`` environment.

License
-------

MongoLog is available under the BSD 2-Clause License.

Authors
-------

Original author: `Andrei Savu`_

Maintainer: `Jorge Puente Sarrín`_

.. _Andrei Savu: https://github.com/andreisavu
.. _Jorge Puente Sarrín: https://github.com/puentesarrin
