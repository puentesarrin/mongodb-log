import logging

from mongolog import MongoHandler


if __name__ == '__main__':
    log = logging.getLogger('example')
    log.setLevel(logging.DEBUG)

    log.addHandler(MongoHandler.to('log', db='mongolog'))

    log.debug('1 - debug message')
    log.info('2 - info message')
    log.warning('3 - warning message')
    log.error('4 - error message')
    log.critical('5 - critical message')
