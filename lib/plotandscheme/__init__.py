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

from StringIO import StringIO
import logging

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.cm as cm

from kivy.core.image.img_pil import ImageLoaderPIL
from kivy.core.image import ImageData
from kivy.graphics.texture import Texture

import dotalocal
import blingy

log = logging.getLogger(__name__)

g_xdata = None
g_ydata = None

d2rp = None

colors = [cm.Accent(x/10.) for x in range(10)]


matplotlib.rcParams['lines.color'] = 'cccccc'
matplotlib.rcParams['patch.edgecolor'] = 'cccccc'
matplotlib.rcParams['text.color'] = 'cccccc'
matplotlib.rcParams['axes.facecolor'] = 'black'
matplotlib.rcParams['axes.edgecolor'] = 'cccccc'
matplotlib.rcParams['axes.labelcolor'] = 'cccccc'
matplotlib.rcParams['xtick.color'] = 'cccccc'
matplotlib.rcParams['ytick.color'] = 'cccccc'
matplotlib.rcParams['grid.color'] = 'cccccc'
matplotlib.rcParams['figure.facecolor'] = 'black'
matplotlib.rcParams['figure.edgecolor'] = 'black'
matplotlib.rcParams['savefig.facecolor'] = 'black'
matplotlib.rcParams['savefig.edgecolor'] = 'black'



def new_graph():
    # clear previous state
    plt.clf() 
    plt.cla()

    plt.figure(figsize=(8,3))


def plt_to_image():
    buf = StringIO()
    plt.savefig(buf, format='png', dpi=400)
    buf.seek(0)
    imgdata = ImageLoaderPIL(buf)._data[0]
    t = Texture.create_from_data(imgdata)
    # for some reason image is loaded upside-down
    t.flip_vertical() 
    return t


def ts_gold(d2rp, hero):
    last_gold = 0
    gold = []
    ts = []
    for entry in d2rp.gold:
        if entry['hero'] == hero:
            last_gold += entry['gold']
            gold.append(last_gold)
            ts.append( entry['time'] / 30.0 ) # in seconds
    return (ts, gold)


def ts_cs(d2rp, hero):
    cs = []
    ts = []
    hit = 0
    for entry in d2rp.cs:
        if entry['hero'] == hero:
            hit += 1
            cs.append( hit )
            ts.append( entry['time'] / 30.0 ) # in seconds
    return (ts, cs)


def ts_kills(d2rp, hero=None):
    killed = []
    ts = []
    for entry in d2rp.herokills:
        if hero is None or entry['killer'] == hero:
            killed.append(entry['dead'])
            ts.append( entry['time'] / 30.0 ) # in seconds
    return (ts, killed)


def ts_items(d2rp, hero=None):
    items = []
    ts = []
    for entry in d2rp.itemtimes:
        if hero is None or entry['hero'] == hero:
            items.append(entry['item'])
            ts.append( entry['time'] / 30.0 ) # in seconds
    return (ts, items)


def ts_levels(d2rp, hero=None):
    levels = []
    ts = []
    for entry in d2rp.levelups:
        if hero is None or entry['hero'] == hero:
            levels.append('{} : {}'.format(entry['level'], dotalocal.hero[entry['hero']]))
            ts.append( entry['time'] / 30.0 ) # in seconds
    return (ts, levels)

####################################

def create_gold_graph(players, start_time, end_time):
    global d2rp
    new_graph()

    for player in players:
        x,y = ts_gold(d2rp, player['hero'])
        early_x = [0.0]
        early_y = [0.0]
        for i,ts in enumerate(x):
            if ts > start_time and ts < end_time:
                early_x.append(ts)
                early_y.append(y[i])

        try:
            line = plt.plot(early_x, early_y, linewidth=2.0, color=colors[player['index']])
        except IndexError:
            print '{} not valid player index'.format(player['index'])
            raise
        line[0].set_label( dotalocal.player(player['profile'].name) )

    plt.xlim(start_time, end_time)

    blingy.decorate_gold()
    return plt_to_image()


def _graph_kills(players, start_time, end_time, annotate):
    global d2rp
    kills_by_player = []
    for p in players:
        ts, killed = ts_kills(d2rp, p['hero'])
        kills_by_player.append( (ts,killed) )

    plt.xlim(start_time, end_time)

    for player,tskills in zip(players, kills_by_player):
        x = []
        y = []
        i = 0
        for when,dead in zip(*tskills):
            dead = dotalocal.hero[dead]
            if when > start_time and when < end_time:
                x.append(when)
                y.append(1)
                if annotate:
                    plt.annotate(dead, xy=(when, 1), 
                            xytext=(when, 1.5+(i*0.5)%5),
                            size='x-small',
                            arrowprops=dict(arrowstyle='->', 
                                            connectionstyle='arc3,rad=.2'))
            i += 1
        plt.plot(x,y, 'o', color=colors[ player['index'] ])


def _graph_items(players, start_time, end_time, annotate):
    global d2rp
    items_by_player = []
    for p in players:
        ts, items = ts_items(d2rp, p['hero'])
        items_by_player.append( (ts,items) )

    plt.xlim(start_time, end_time)

    for player,tsitems in zip(players, items_by_player):
        x = []
        y = []
        i = 0
        for when,item in zip(*tsitems):
            item = dotalocal.item[item]
            if when > start_time and when < end_time:
                x.append(when)
                y.append(2)
                if annotate:
                    plt.annotate(item, xy=(when, 2), 
                            xytext=(when, 2.5+(i*0.5)%3),
                            size='x-small',
                            arrowprops=dict(arrowstyle='->', 
                                            connectionstyle='arc3,rad=.2'))
            i += 1
        plt.plot(x,y, 'o', color=colors[ player['index'] ])

def _graph_levels(players, start_time, end_time, annotate):
    global d2rp
    levels_by_player = []
    for p in players:
        ts, levels = ts_levels(d2rp, p['hero'])
        levels_by_player.append( (ts,levels) )

    plt.xlim(start_time, end_time)

    for player,tslevels in zip(players, levels_by_player):
        x = []
        y = []
        i = 0
        for when,level in zip(*tslevels):
            if when > start_time and when < end_time:
                x.append(when)
                y.append(3)
                if annotate:
                    plt.annotate(level, xy=(when, 3), 
                            xytext=(when, 3.5+(i*0.5)%2),
                            size='x-small',
                            arrowprops=dict(arrowstyle='->', 
                                            connectionstyle='arc3,rad=.2'))

            i += 1
        plt.plot(x,y, 'o', color=colors[ player['index'] ])


def create_event_graph(players, start_time, end_time, annotate=[]):
    new_graph()

    _graph_kills(players, start_time, end_time, 'kills' in annotate)
    _graph_items(players, start_time, end_time, 'items' in annotate)
    _graph_levels(players, start_time, end_time, 'levels' in annotate)

    blingy.decorate_event()
    return plt_to_image()
