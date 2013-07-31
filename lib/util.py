#   Copyright 2013 Mugsy Mcgeee
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.

import os.path
from configulifier import CFG
import threading
import pickle
import time
import logging
import urllib2

log = logging.getLogger(__name__)


def dict_to_url(args):
    """
    Convenience function to construct URL parameters from a dict
    """
    return '&'.join( ('{}={}'.format(k,v) for k,v in args.iteritems()) )


class with_network_retry(object):
    """
    decorator: @with_network_retry
    Tries to catch HTTP 503 errors and retries with backoff
    """
    def __init__(self, f):
        self.func = f

    def __call__(self, *args):
        retry = 0
        max_tries = 5

        while retry < max_tries:
            try:
                return self.func(*args)
            except urllib2.HTTPError as e:
                if 'HTTP Error 503' in str(e):
                    retry += 1
                    if retry < max_tries:
                        log.warn('HTTP 503, retrying in {} secs'.format(retry*2))
                        time.sleep(retry*2)
                    else:
                        raise


class NoneValueFound(Exception):
    pass

class NonNullableDict(object):
    """
    Dictionary-like object that throws an exception if any of the values are None.
    This is mainly used to enforce that we never pass None values to our GUI widgets 
    """
    def __init__(self, other_dict):
        for k,v in other_dict.iteritems():
            if v is None:
                raise NoneValueFound('Key: {} has value {}'.format(k,v))
        self.data = other_dict

    def keys(self):
        return self.data.keys()
    def values(self):
        return self.data.values()
    def items(self):
        return self.data.items()
    def iterkeys(self):
        return self.data.iterkeys()
    def itervalues(self):
        return self.data.itervalues()
    def iteritems(self):
        return self.data.iteritems()
    def get(self, key, default):
        return self.data.get(key, default)
    def __getitem__(self, key):
        return self.data.__getitem__(key)
    def __setitem__(self, key, value):
        if value is None:
            raise NoneValueFound('Key: {} has value {}'.format(key,value))
        self.data.__setitem__(key,value)
    def __contains__(self, k):
        return self.data.__contains__(k)
    def __len__(self):
        return self.data.__len__()


class CaseClass(object):
    """
    Creates a class with attributes based on key/values pass into the init.
    """
    def __init__(self, **kwds):
        self.__dict__.update(kwds)

    def __eq__(self, other):
        return self.__dict__ == other.__dict__
