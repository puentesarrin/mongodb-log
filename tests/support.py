import logging
import os
import unittest

from pymongo import MongoClient
from pymongo.errors import ServerSelectionTimeoutError


def mongo_client_options():
    port = os.environ.get('MONGO_PORT')
    return {
        'host': os.environ.get('MONGO_HOST', 'localhost'),
        'port': int(port) if port else None,
        'serverSelectionTimeoutMS': 1000,
    }


def mongo_handler_options():
    options = mongo_client_options()
    return {
        'host': options['host'],
        'port': options['port'],
    }


def mongo_client(**options):
    client = MongoClient(**mongo_client_options(), **options)
    try:
        client.admin.command('ping')
    except ServerSelectionTimeoutError as exc:
        client.close()
        raise unittest.SkipTest(f'MongoDB is not available: {exc}') from exc
    return client


def clean_logger(name, level=logging.DEBUG):
    logger = logging.getLogger(name)
    logger.handlers[:] = []
    logger.propagate = False
    logger.setLevel(level)
    return logger
