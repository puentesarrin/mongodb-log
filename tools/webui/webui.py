import web

from pymongo import DESCENDING, MongoClient

import settings

urls = (
    '/(.*)', 'index',
)


def get_mongo_collection(db, collection, host, port):
    return MongoClient(host=host, port=port)[db][collection]


app = web.application(urls, globals())
render = web.template.render('templates/', base='base')
db = get_mongo_collection(**settings.MONGO)


class index:
    def GET(self, level):
        args = {}
        if level and level in ['info', 'debug', 'warning', 'error', 'critical']:
            args = {'levelname': level.upper()}

        def fill_missing(record):
            if 'host' not in record:
                record['host'] = '(unknown)'
            return record

        logs = map(
            fill_missing,
            db.find(args, limit=100).sort('$natural', DESCENDING),
        )

        return render.index(logs)


if __name__ == '__main__':
    app.run()
