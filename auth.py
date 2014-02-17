#!/usr/bin/env python

import argparse
import json
import logging
import struct
import sys

FALLBACK_URL = 'http://localhost:8000/auth/'
HEADERS = {
    'Content-Type': 'application/json',
    'Accept': 'application/json' }


class RequestsHandler:
    '''
    Small wrapper class to use 'requests' to execute HTTP requests.
    '''
    def __init__(self, url, headers):
        import requests
        logging.info('Using requests library for HTTP requests')

        self.url = url
        self.headers = headers

    def call(self, data):
        res = requests.post(self.url, data, self.headers)
        return res.json()

class UrlLibHandler:
    '''
    Small wrapper class to use 'urllib2' to execute HTTP requests.
    '''

    def __init__(self, url, headers):
        import urllib2
        logging.info('Using urllib2 library for HTTP requests')

        self.url = url
        self.headers = headers

    def call(self, data):
        req = urllib2.Request(self.url, data, self.headers)
        res = urllib2.urlopen(req)
        return json.load(res)

class ApiHandler:
    '''
    Class to execute the HTTP requests to process
    the authentication orders from ejabberd.
    '''

    def __init__(self, url, headers):
        self.handler = None

        # first we try the 'requests' library
        # afterwards the 'urllib2' is tried to load
        try:
            self.handler = RequestsHandler(url, headers)
        except ImportError:
            self.handler = UrlLibHandler(url, headers)

    def call(self, data):
        return self.handler.call(data)

class EjabberdAuth:

    def __init__(self, url, headers):
        self.url = url
        self.headers = headers
        self.handler = ApiHandler(url, headers)

    def __from_ejabberd(self):
        '''
        Listen on stdin and read input data sent from to
        connected ejabberd instance.
        '''

        try:
            input_length = sys.stdin.read(2)

            if len(input_length) is not 2:
                logging.warn('ejabberd called with invalid input')
                return None

            (size,) = struct.unpack('>h', input_length)
            result = sys.stdin.read(size)

            logging.debug('Read %d bytes: %s', size, result)

            return result.split(':')
        except:
            return None

    def __to_ejabberd(self, success):
        '''
        Convert the input data into an ejabberd compatible input
        and send those to stdout.
        '''

        answer = 0
        if success: answer = 1

        token = struct.pack('>hh', 2, answer)

        sys.stdout.write(token)
        sys.stdout.flush()

    def __call_api(self, data):
        '''
        Call the JSON compatible API handler with the specified data
        and parse the response for a success.
        '''

        body = json.dumps(data)
        result = self.handler.call(body)

        success = result['success']

        if not success:
            msg = result['message']
            logging.warn('Call to API returned without success: ' + msg)

        return success

    def __auth(self, username, server, password):
        logging.info('Processing "auth"')
        data = {'user': username, 'pw': password, 'server': server}

        return self.__call_api(data)

    def __isuser(self, username, server):
        logging.info('Processing "isuser"')

        # TODO
        return False

    def __setpass(self, username, server, password):
        logging.info('Processing "setpass"')

        # TODO
        return False

    def loop(self):
        while True:
            data = self.__from_ejabberd()
            if data is None: break

            success = False
            cmd = data[0]

            if cmd == 'auth':
                success = self.__auth(data[1], data[2], data[3])
            elif cmd == 'isuser':
                success = self.__isuser(data[1], data[2])
            elif cmd == 'setpass':
                success = self.__setpass(data[1], data[2], data[3])
            else:
                logging.warn('Unhandled ejabberd cmd "%s"', cmd)

            self.__to_ejabberd(success)


def get_args():
    '''
    Parse some basic configuration from command line arguments
    '''

    p = argparse.ArgumentParser(description='ejabberd authentication script')
    p.add_argument('--url', help='base URL')
    p.add_argument('--debug', action='store_const', const=True, help='toggle debug mode')
    p.add_argument('--log', help='log file')

    args = vars(p.parse_args())
    url = args['url'] if args['url'] else FALLBACK_URL
    logfile = args['log'] if args['log'] else '/var/log/ejabberd/extauth.log'

    return url, args['debug'], logfile


if __name__ == '__main__':
    url, debug, log = get_args()

    level = logging.DEBUG if debug else logging.INFO
    logging.basicConfig(level=level,
            format='%(asctime)s %(levelname)s %(message)s',
            filename=log)

    logging.info('Starting ejabberd auth script')
    logging.info('Using %s as base URL', url)
    logging.info('Running in %s mode', 'debug' if debug else 'release')

    ejabberd = EjabberdAuth(url, HEADERS)
    ejabberd.loop()

    logging.warn('Terminating ejabberd auth script')

# vim: set et sw=4 sts=4 tw=80:
