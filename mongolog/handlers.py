import getpass
import logging
from datetime import datetime, timezone
from socket import gethostname

from bson.errors import InvalidDocument
from pymongo import MongoClient
from pymongo.collection import Collection


class MongoFormatter(logging.Formatter):
    def format(self, record):
        """Return a MongoDB document for a logging record."""
        data = record.__dict__.copy()

        data.update(
            username=getpass.getuser(),
            time=datetime.now(timezone.utc),
            host=gethostname(),
            message=record.getMessage(),
            args=tuple(str(arg) for arg in record.args),
        )
        if data.get('exc_info'):
            data['exc_info'] = self.formatException(data['exc_info'])
        return data


class MongoHandler(logging.Handler):
    """Logging handler that stores records in a MongoDB collection."""

    @classmethod
    def to(
        cls,
        collection,
        db='mongolog',
        host='localhost',
        port=None,
        username=None,
        password=None,
        auth_source=None,
        level=logging.NOTSET,
    ):
        return cls(
            collection,
            db=db,
            host=host,
            port=port,
            username=username,
            password=password,
            auth_source=auth_source,
            level=level,
        )

    def __init__(
        self,
        collection,
        db='mongolog',
        host='localhost',
        port=None,
        username=None,
        password=None,
        auth_source=None,
        level=logging.NOTSET,
    ):
        super().__init__(level)
        if isinstance(collection, str):
            client_options = {}
            if username is not None:
                client_options['username'] = username
            if password is not None:
                client_options['password'] = password
            if auth_source is not None:
                client_options['authSource'] = auth_source
            elif username is not None or password is not None:
                client_options['authSource'] = db

            client = MongoClient(host=host, port=port, **client_options)
            self.collection = client[db][collection]
        elif isinstance(collection, Collection):
            self.collection = collection
        else:
            raise TypeError('collection must be a string or pymongo Collection')
        self.formatter = MongoFormatter()

    def emit(self, record):
        try:
            self.collection.insert_one(self.format(record))
        except InvalidDocument:
            self.handleError(record)
