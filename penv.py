#   Copyright 2013 Matthew Shanker
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

import sys
import os.path
import types

# add lib to pythonpath
LIBDIR=os.path.join(os.path.dirname(os.path.realpath(__name__)),'lib')
sys.path.append(LIBDIR)


class EnumUnmappedValue(Exception):
    pass

# attempt at Enum like class
class Enum(object):
    _map = {}

    def __init__(self, val):
        if isinstance(val, types.IntType):
            self.val = val
            self.name = self._map[val]
        elif issubclass(val.__class__, self.__class__):
            self.val = val.val
            self.name = val.name
        else:
            try:
                self.name = val
                self.val = [k for k,v in self._map.iteritems() if v == val][0]
            except:
                raise EnumUnmappedValue(val)

    @classmethod
    def all(cls):
        """Return a list of all mapped enumeration types"""
        print cls
        return [cls(k) for k in cls._map.iterkeys()]

    def __eq__(self, other):
        if isinstance(other, types.IntType):
            result =  self.val == other
        elif isinstance(other, types.StringType):
            result = self.name == other
        elif issubclass(other.__class__, self.__class__):
            result = self.val == other.val and self.name == other.name
        else:
            raise Exception('Cannot compare Enum and {}'.format(other.__class__))

        return result
    
    def __str__(self):
        return self.name

    def __repr__(self):
        return '{}:{}'.format(self.val, self.name)

