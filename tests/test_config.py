import logging
import unittest
from logging.config import dictConfig, fileConfig
from os.path import dirname, join

from mongolog import MongoHandler
from tests.support import clean_logger, mongo_client, mongo_options


class TestConfig(unittest.TestCase):
    def setUp(self):
        filename = join(dirname(__file__), 'logging-test.config')
        fileConfig(filename)

        self.db_name = '_mongolog_test'
        self.collection_name = 'log_test'

        self.conn = mongo_client()
        self.db = self.conn[self.db_name]
        self.collection = self.db[self.collection_name]

        self.conn.drop_database(self.db_name)

    def tearDown(self):
        self.conn.drop_database(self.db_name)
        self.conn.close()

    def test_logging_file_configuration(self):
        log = clean_logger('example')
        log.addHandler(
            MongoHandler(self.collection_name, self.db_name, **mongo_options())
        )

        log.debug('test')

        message = self.collection.find_one({'levelname': 'DEBUG', 'msg': 'test'})
        self.assertEqual(message['msg'], 'test')


class TestDictConfig(unittest.TestCase):
    def setUp(self):
        self.db_name = '_mongolog_test_dict'
        self.collection_name = 'log_test'

        options = mongo_options()
        self.config_dict = {
            'version': 1,
            'handlers': {
                'mongo': {
                    'class': 'mongolog.handlers.MongoHandler',
                    'db': self.db_name,
                    'collection': self.collection_name,
                    'host': options['host'],
                    'port': options['port'],
                    'level': 'INFO',
                }
            },
            'root': {
                'handlers': ['mongo'],
                'level': 'INFO',
            },
        }

        self.conn = mongo_client()
        self.db = self.conn[self.db_name]
        self.collection = self.db[self.collection_name]

        self.conn.drop_database(self.db_name)

    def tearDown(self):
        self.conn.drop_database(self.db_name)
        self.conn.close()

    def test_logging_dict_configuration(self):
        logging.getLogger().handlers[:] = []
        dictConfig(self.config_dict)

        log = logging.getLogger('dict_example')

        log.debug('testing dictionary config')

        message = self.collection.find_one(
            {'levelname': 'DEBUG', 'msg': 'dict_example'}
        )
        self.assertIsNone(message)

        log.info('dict_example')
        message = self.collection.find_one({'levelname': 'INFO', 'msg': 'dict_example'})
        self.assertIsNotNone(message)
        self.assertEqual(message['msg'], 'dict_example')
