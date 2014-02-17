#!/usr/bin/env python

import argparse
import json
import logging
import struct
import sys

HEADERS = {
    'Content-Type': 'application/json',
    'Accept': 'application/json' }


class RequestsHandler:
    '''
    Small wrapper class to use 'requests' to execute HTTP requests.
    '''
    import requests

    def __init__(self, url, headers):
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

def get_args():
    fallback_url = 'http://localhost:8000/auth/'

    p = argparse.ArgumentParser(description='ejabberd authentication script')
    p.add_argument('--url', help='base URL')
    p.add_argument('--debug', action='store_const', const=True, help='toggle debug mode')
    p.add_argument('--log', help='log file')

    args = vars(p.parse_args())
    url = args['url'] if args['url'] else fallback_url
    logfile = args['log'] if args['log'] else '/var/log/ejabberd/extauth.log'

    return url, args['debug'], logfile

def from_ejabberd():
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

def to_ejabberd(success):
    '''
    Convert the input data into an ejabberd compatible input
    and send those to stdout.
    '''

    answer = 0
    if success: answer = 1

    token = struct.pack('>hh', 2, answer)

    sys.stdout.write(token)
    sys.stdout.flush()

def call_api(handler, data):
    '''
    Call the JSON compatible API handler with the specified data
    and parse the response for a success.
    '''

    body = json.dumps(data)
    result = handler.call(body)

    success = result['success']

    if not success:
        msg = result['message']
        logging.warn('Call to API returned without success: ' + msg)

    return success

def auth(h, username, server, password):
    data = {'user': username, 'pw': password, 'server': server}
    return call_api(h, data)

def isuser(h, username, server):
    # TODO
    return False

def setpass(h, username, server, password):
    # TODO
    return False

def loop(handler):
    while True:
        data = from_ejabberd()
        if data is None: break

        success = False
        cmd = data[0]

        if cmd == 'auth':
            logging.info('Processing "auth"')

            success = auth(handler, data[1], data[2], data[3])
        elif cmd == 'isuser':
            logging.info('Processing "isuser"')

            success = isuser(handler, data[1], data[2])
        elif cmd == 'setpass':
            logging.info('Processing "setpass"')

            success = setpass(handler, data[1], data[2], data[3])

        to_ejabberd(success)


if __name__ == '__main__':
    url, debug, log = get_args()

    level = logging.DEBUG if debug else logging.WARNING
    logging.basicConfig(level=level,
            format='%(asctime)s %(levelname)s %(message)s',
            filename=log)

    logging.info('Using %s as base URL', url)
    logging.info('Running in %s mode', 'debug' if debug else 'release')

    handler = ApiHandler(url, HEADERS)
    loop(handler)

    logging.warn('Terminating ejabberd auth script')


# vim: set et sw=4 sts=4 tw=80:
