# -*- coding: utf-8 *-*
import logging
import unittest

from mongolog import MongoHandler

try:
    from pymongo import MongoClient as Connection
except ImportError:
    from pymongo import Connection


class TestRootLoggerHandler(unittest.TestCase):
    """
    Test Handler attached to RootLogger
    """
    def setUp(self):
        """ Create an empty database that could be used for logging """
        self.db_name = '_mongolog_test'
        self.collection_name = 'log'

        self.conn = Connection()
        self.db = self.conn[self.db_name]
        self.collection = self.db[self.collection_name]

        self.conn.drop_database(self.db_name)

    def tearDown(self):
        """ Drop used database """
        self.conn.drop_database(self.db_name)

    def testLogging(self):
        """ Simple logging example """
        log = logging.getLogger('log')
        log.setLevel(logging.DEBUG)
        log.addHandler(MongoHandler(self.collection_name, self.db_name))

        log.debug('test')

        r = self.collection.find_one({'levelname': 'DEBUG', 'msg': 'test'})
        self.assertEqual(r['msg'], 'test')

    def testLoggingException(self):
        """ Logging example with exception """
        log = logging.getLogger('exception')
        log.setLevel(logging.DEBUG)
        log.addHandler(MongoHandler(self.collection_name, self.db_name))

        try:
            1 / 0
        except ZeroDivisionError:
            log.error('test zero division', exc_info=True)

        r = self.collection.find_one({'levelname': 'ERROR',
            'msg': 'test zero division'})
        self.assertTrue(r['exc_info'].startswith('Traceback'))

    def testQueryableMessages(self):
        """ Logging example with dictionary """
        log = logging.getLogger('query')
        log.setLevel(logging.DEBUG)
        log.addHandler(MongoHandler(self.collection_name, self.db_name))

        log.info({'address': '340 N 12th St', 'state': 'PA', 'country': 'US'})
        log.info({'address': '340 S 12th St', 'state': 'PA', 'country': 'US'})
        log.info({'address': '1234 Market St', 'state': 'PA', 'country': 'US'})

        query = {
            'levelname': 'INFO',
            'msg.address': '340 N 12th St',
        }
        docs_count = self.collection.count_documents(query)
        self.assertEqual(
            docs_count,
            1,
            "Expected query to return 1 "
            "message; it returned %d" % docs_count
        )
        cursor = self.collection.find(query)
        self.assertEqual(cursor[0]['msg']['address'], '340 N 12th St')

        query = {
            'levelname': 'INFO',
            'msg.state': 'PA',
        }
        docs_count = self.collection.count_documents(query)
        self.assertEqual(
            docs_count,
            3,
            "Didn't find all three documents"
        )
