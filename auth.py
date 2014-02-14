#!/usr/bin/python

import json
import logging
import os
import struct
import sys
import urllib2

# may be we need this one later
# import hashlib

URL = 'http://localhost:8000/auth/'
HEADERS = { 'Content-Type': 'application/json' }


def from_ejabberd():
    try:
        input_length = sys.stdin.read(2)

        if len(input_length) is not 2:
            logging.debug('wrong input')
            return None

        (size,) = struct.unpack('>h', input_length)
        result = sys.stdin.read(size)

        logging.info('Read %d bytes: %s', size, result)

        return result.split(':')
    except:
        return None

def to_ejabberd(bool):
    answer = 0
    if bool:
        answer = 1
    token = struct.pack('>hh', 2, answer)
    sys.stdout.write(token)
    sys.stdout.flush()

def call_api(data):
    body = json.dumps(data)
    request = urllib2.Request(URL, body, HEADERS)

    try:
        res = urllib2.urlopen(request)
        return json.load(res)
    except:
        pass
    finally:
        f.close()

    return None

def auth(username, server, password):
    # clear = "barfoo"
    # salt = "foobar"
    # hash = hashlib.md5( salt + clear ).hexdigest()

    api = call_api({'user': username, 'pw': password, 'server': server})

    if api['success']:
        return True
    else:
        return False

def isuser(username, server):
    return True

def setpass(username, server, password):
    return True

while True:
    data = from_ejabberd()
    if data is None: continue

    success = False

    if data[0] == "auth":
        logging.info('Processing "auth"')

        success = auth(data[1], data[2], data[3])
    elif data[0] == "isuser":
        logging.info('Processing "isuser"')

        success = isuser(data[1], data[2])
    elif data[0] == "setpass":
        logging.info('Processing "setpass"')

        success = setpass(data[1], data[2], data[3])

    to_ejabberd(success)
