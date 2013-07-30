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

import os.path
import unicodedata
import json
import types

import penv

_done_init = False

hero = None
hero_by_id = None
heroes_by_type = None


item = None


class MatchType(penv.Enum):
    _map = { 0: 'Public matchmaking',
             1: 'Practice',
             2: 'Tournament',
             3: 'Tutorial',
             4: 'Co-op with bots',
             5: 'Team match',
             6: 'Solo matchmaking'}

class HeroType(penv.Enum):
    _map = { 0: 'carry',
             1: 'jungler',
             2: 'nuker',
             3: 'support' }

class GameMode(penv.Enum):
    _map = {  1: 'All Pick',
              2: 'Captains Mode',
              3: 'Random Draft',
              4: 'Single Draft',
              5: 'All Random',
              6: 'INTRO/DEATH',
              7: 'The Diretide',
              8: 'Reverse Captains Mode',
              9: 'Greeviling',
             10: 'Tutorial',
             11: 'Mid Only',
             12: 'Least Played',
             13: 'New Player Pool' }

class LeaverStatus(penv.Enum):
    _map = { None: 'Bot',
                0: 'Stayed',
                1: 'Safe Leave',
                2: 'Abandonded',
                3: 'Unknown' }


def player(name):
    """
    Returns a str-friendly version of the player's name
    """
    if isinstance(name, types.UnicodeType):
        return unicodedata.normalize('NFKC', name).encode('ascii','ignore')
    else:
        return name


def hero_is_type(hero, hero_type):
    """
    Returns whether a hero is of a certain type (Carry, Support, etc)
    """
    return hero in heroes_by_type[hero_type.name]


def decode_hero(hero_id):
    """
    Returns human name for Hero ID
    """
    return hero_by_id[hero_id]


def init_dotalocal():
    """
    Loads human strings and initializes lookup tables
    """
    if _done_init:
        return 
    
    fname = os.path.join(penv.LIBDIR, 'translate.json')
    with open(fname) as tfile:
        data = json.load(tfile)

    # heroes
    global hero
    global hero_by_id
    hero = {}
    hero_by_id = {}

    for entry in data['heroes']:
        hero[entry['name']] = entry['localized_name']
        hero_by_id[entry['id']] = entry['name']

    # items
    global item
    item = data['items']

    # heroes by type
    global heroes_by_type
    heroes_by_type = data['heroes_by_type']


###########################################################
# run at module import
###########################################################
init_dotalocal()
