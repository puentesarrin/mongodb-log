import unittest

from mongolog import MongoHandler
from tests.support import clean_logger, mongo_client, mongo_handler_options


class TestRootLoggerHandler(unittest.TestCase):
    def setUp(self):
        self.db_name = '_mongolog_test'
        self.collection_name = 'log'

        self.conn = mongo_client()
        self.db = self.conn[self.db_name]
        self.collection = self.db[self.collection_name]

        self.conn.drop_database(self.db_name)

    def tearDown(self):
        self.conn.drop_database(self.db_name)
        self.conn.close()

    def test_logging(self):
        log = clean_logger('log')
        log.addHandler(
            MongoHandler(self.collection_name, self.db_name, **mongo_handler_options())
        )

        log.debug('test')

        record = self.collection.find_one({'levelname': 'DEBUG', 'msg': 'test'})
        self.assertEqual(record['msg'], 'test')
        self.assertEqual(record['message'], 'test')

    def test_logging_exception(self):
        log = clean_logger('exception')
        log.addHandler(
            MongoHandler(self.collection_name, self.db_name, **mongo_handler_options())
        )

        try:
            1 / 0
        except ZeroDivisionError:
            log.error('test zero division', exc_info=True)

        record = self.collection.find_one(
            {'levelname': 'ERROR', 'msg': 'test zero division'}
        )
        self.assertTrue(record['exc_info'].startswith('Traceback'))

    def test_queryable_messages(self):
        log = clean_logger('query')
        log.addHandler(
            MongoHandler(self.collection_name, self.db_name, **mongo_handler_options())
        )

        log.info({'address': '340 N 12th St', 'state': 'PA', 'country': 'US'})
        log.info({'address': '340 S 12th St', 'state': 'PA', 'country': 'US'})
        log.info({'address': '1234 Market St', 'state': 'PA', 'country': 'US'})

        query = {
            'levelname': 'INFO',
            'msg.address': '340 N 12th St',
        }
        docs_count = self.collection.count_documents(query)
        self.assertEqual(docs_count, 1)
        cursor = self.collection.find(query)
        self.assertEqual(cursor[0]['msg']['address'], '340 N 12th St')

        query = {
            'levelname': 'INFO',
            'msg.state': 'PA',
        }
        docs_count = self.collection.count_documents(query)
        self.assertEqual(docs_count, 3)
