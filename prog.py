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
import penv
import argparse
import sys

import log_config

import parsing.d2rp as d2rp
import dotalocal as dloc
import ui.gui as gui
import configulifier

from kivy.config import Config

if __name__ == '__main__':
    Config.set('kivy', 'log_level', 'debug')

    configulifier.load_config() # load app-level config

    gui.init()
    gui.GuiApp().run()
