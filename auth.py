#!/usr/bin/env python

# Copyright 2014 Gregor Uhlenheuer
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


import argparse
import json
import logging
import os
import struct
import sys
import urllib2


#
# DEFAULTS AND CONSTANTS
#

DEFAULT_LOG = '/var/log/ejabberd/extauth.log'
FALLBACK_URL = 'http://localhost:8000/auth/'
HEADERS = {
    'Content-Type': 'application/json',
    'Accept': 'application/json' }


#
# CLASS DEFINITIONS
#

class ApiHandler:
    '''
    Class to execute the HTTP requests to process
    the authentication orders from ejabberd.
    '''

    def __init__(self, url, headers):
        '''Initialize a ApiHandler instance.'''

        self.url = url
        self.headers = headers

    def call(self, data):
        '''
        Call the specified authentication API using the
        urllib2 library functions.
        '''

        req = urllib2.Request(self.url, data, self.headers)
        res = urllib2.urlopen(req)
        return json.load(res)

class EjabberdAuth:
    '''
    Class that encapsulates the ejabberd authentication logic.
    '''

    def __init__(self, url, headers, handler=None):
        '''
        Initialize a new EjabberdAuth instance.
        '''
        self.url = url
        self.headers = headers

        if handler is None:
            self.handler = ApiHandler(url, headers)
        else:
            self.handler = handler

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

        answer = 1 if success else 0
        token = struct.pack('>hh', 2, answer)

        sys.stdout.write(token)
        sys.stdout.flush()

        logging.debug('Returned %s success', 'with' if success else 'without')

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
        '''Try to authenticate the user with the specified password'''

        logging.debug('Processing "auth"')
        data = {'user': username, 'pw': password, 'server': server}

        return self.__call_api(data)

    def __isuser(self, username, server):
        '''Try to find the specified user'''

        logging.debug('Processing "isuser"')

        # TODO
        return False

    def __setpass(self, username, server, password):
        '''Try to set the user's password'''

        logging.debug('Processing "setpass"')

        # TODO
        return False

    def loop(self):
        '''
        Start the endless loop that reads on stdin and passes
        the authentication results to stdout towards the
        connected ejabberd instance.
        '''

        while True:
            data = self.__from_ejabberd()
            if data is None:
                break

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

    desc = 'ejabberd authentication script'
    parser = argparse.ArgumentParser(description=desc)

    parser.add_argument('--url',
            help='base URL')
    parser.add_argument('--debug', action='store_const', const=True,
            help='toggle debug mode')
    parser.add_argument('--log',
            help='log file')

    args = vars(parser.parse_args())
    url = args['url'] if args['url'] else FALLBACK_URL
    logfile = args['log'] if args['log'] else DEFAULT_LOG

    return url, args['debug'], logfile


if __name__ == '__main__':
    URL, DEBUG, LOG = get_args()

    LEVEL = logging.DEBUG if DEBUG else logging.INFO
    PID = str(os.getpid())
    FMT = '[%(asctime)s] ['+PID+'] [%(levelname)s] %(message)s'
    logging.basicConfig(level=LEVEL, format=FMT, filename=LOG)

    logging.info('Starting ejabberd auth script')
    logging.info('Using %s as base URL', URL)
    logging.info('Running in %s mode', 'debug' if DEBUG else 'release')

    EJABBERD = EjabberdAuth(URL, HEADERS)
    EJABBERD.loop()

    logging.warn('Terminating ejabberd auth script')

# vim: set et sw=4 sts=4 tw=80:
