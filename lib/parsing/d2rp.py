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

import argparse
import traceback
import os.path
import json

from kivy.logger import Logger

def _load_data(replay_dir, name):
    """
    Loads data from the given file of the parsed replay directory
    """
    try:
        with open(os.path.join(replay_dir, '{}.json'.format(name))) as infile:
            return json.load(infile).values()[0]
    except:
        Logger.debug('d2rp: {}'.format(traceback.format_exc()))
        return None


class D2RP(object):
    """
    Object with the contents of the parsed local replay
    """
    def __init__(self, replay_dir):
        self.match_id = os.path.split(replay_dir)[-1].strip('.dem')

        self.banpicks = _load_data(replay_dir, 'banpicks')
        self.buildings = _load_data(replay_dir, 'buildings')
        self.buybacks = _load_data(replay_dir, 'buybacks')
        self.chat = _load_data(replay_dir, 'chat')
        self.combatlog = _load_data(replay_dir, 'combatlog')
        self.cs = _load_data(replay_dir, 'cs')
        self.denies = _load_data(replay_dir, 'denies')
        self.glyphs = _load_data(replay_dir, 'glyphs')
        self.gold = _load_data(replay_dir, 'gold')
        self.herokills = _load_data(replay_dir, 'herokills')
        self.itemtimes = _load_data(replay_dir, 'itemtimes')
        self.levelups = _load_data(replay_dir, 'levelups')
        self.pauses = _load_data(replay_dir, 'pauses')
        self.players = _load_data(replay_dir, 'players')
        self.roshan = _load_data(replay_dir, 'roshan')
        self.runes = _load_data(replay_dir, 'runes')
