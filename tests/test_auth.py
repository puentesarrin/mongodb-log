import unittest

from mongolog import MongoHandler
from tests.support import clean_logger, mongo_client, mongo_options


class TestAuth(unittest.TestCase):
    def setUp(self):
        self.db_name = '_mongolog_auth'
        self.collection_name = 'log'
        self.user_name = 'MyUsername'
        self.password = 'MySeCrEtPaSsWoRd'

        self.conn = mongo_client()
        self.db = self.conn[self.db_name]
        self.collection = self.db[self.collection_name]

        self.conn.drop_database(self.db_name)
        self.db.command(
            'createUser',
            self.user_name,
            pwd=self.password,
            roles=['readWrite'],
        )

    def tearDown(self):
        self.conn.drop_database(self.db_name)
        self.conn.close()

    def test_authentication(self):
        log = clean_logger('authentication')
        log.addHandler(
            MongoHandler(
                self.collection_name,
                self.db_name,
                username=self.user_name,
                password=self.password,
                **mongo_options(),
            )
        )

        log.error('test')

        message = self.collection.find_one({'levelname': 'ERROR', 'msg': 'test'})
        self.assertEqual(message['msg'], 'test')
