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

import json
import os.path
import logging
import collections

import penv
import err

log = logging.getLogger(__name__)

CFG = collections.defaultdict(lambda: None)
_cfg_path = os.path.join(penv.LIBDIR, '..', 'config.json')


def load_config():
    """
    Loads config into the CFG dictionary providing default values where appropriate
    """
    global CFG
    global _cfg_path

    if os.path.exists(_cfg_path):
        log.info('Loading config from {}'.format(_cfg_path))
        with open(_cfg_path) as cfg_file:
            CFG = json.load(cfg_file)
            log.debug('CFG={}'.format(CFG))
    else:
        log.info('Config file not found: {}'.format(_cfg_path))


def save_config():
    """
    Updates the on-disk save file from the current values in CFG
    """
    if len(CFG) > 0:
        log.info('Saving config to {}'.format(_cfg_path))
        with open(_cfg_path, 'w') as cfg_file:
            json.dump(CFG, cfg_file, indent=1)
    else:
        log.info('Skipping config save')


###########################################################
# on module load
###########################################################
load_config()
