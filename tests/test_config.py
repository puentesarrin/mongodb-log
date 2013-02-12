# -*- coding: utf-8 *-*
import logging
import unittest

from mongolog import MongoHandler
from os.path import dirname, join

try:
    from logging.config import fileConfig, dictConfig
except ImportError:
    from logging.config import fileConfig
    dictConfig = None #py<2.7

try:
    from pymongo import MongoClient as Connection
except ImportError:
    from pymongo import Connection


class TestConfig(unittest.TestCase):

    def setUp(self):
        """ Create an empty database that could be used for logging """
        filename = join(dirname(__file__), 'logging-test.config')
        fileConfig(filename)

        self.db_name = '_mongolog_test'
        self.collection_name = 'log_test'

        self.conn = Connection()
        self.db = self.conn[self.db_name]
        self.collection = self.db[self.collection_name]

        self.conn.drop_database(self.db_name)

    def tearDown(self):
        """ Drop used database """
        self.conn.drop_database(self.db_name)

    def testLoggingFileConfiguration(self):
        log = logging.getLogger('example')
        log.addHandler(MongoHandler(self.collection_name, self.db_name))

        log.debug('test')

        message = self.collection.find_one({'levelname': 'DEBUG',
                                            'msg': 'test'})
        self.assertEquals(message['msg'], 'test')


class TestDictConfig(unittest.TestCase):

    def setUp(self):
        """ Create an empty database that could be used for logging """
        self.db_name = '_mongolog_test_dict'
        self.collection_name = 'log_test'

        self.configDict = {
            'version': 1,
            'handlers': {
                'mongo': {
                    'class': 'mongolog.handlers.MongoHandler',
                    'db': self.db_name,
                    'collection': self.collection_name,
                    'level': 'INFO'
                }
            },
            'root': {
                'handlers': ['mongo'],
                'level': 'INFO'
            }
        }

        self.conn = Connection()
        self.db = self.conn[self.db_name]
        self.collection = self.db[self.collection_name]

        self.conn.drop_database(self.db_name)

    def testLoggingDictConfiguration(self):
        if dictConfig:
            dictConfig(self.configDict)
        else:
            self.assertEquals('Python<2.7', 'Python<2.7')
            return
        
        log = logging.getLogger('dict_example')
        log.addHandler(MongoHandler(self.collection_name, self.db_name))

        log.debug('testing dictionary config')

        message = self.collection.find_one({'levelname': 'DEBUG',
                                            'msg': 'dict_example'})
        self.assertEquals(message, None,
            "Logger put debug message in when info level handler requested")

        log.info('dict_example')
        message = self.collection.find_one({'levelname': 'INFO',
                                            'msg': 'dict_example'})
        self.assertNotEquals(message, None,
            "Logger didn't insert message into database")
        self.assertEquals(message['msg'], 'dict_example',
            "Logger didn't insert correct message into database")

    def tearDown(self):
        """ Drop used database """
        self.conn.drop_database(self.db_name)
