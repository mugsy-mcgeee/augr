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

from collections import defaultdict

import numpy
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import matplotlib.mlab as ml
import matplotlib.font_manager as font_manager

import plotandscheme as pas
import squeeze

d2rp_list = []


def agg_cs(steam_id):
    """
    Aggregates the CS over time from the list of matches in d2rp_list
    """
    global d2rp_list

    all_cs = []
    all_ts = []
    all_matches = []
    for match_idx,data in enumerate(sorted(d2rp_list, key=lambda x:int(x.match_id))):
        player = squeeze.player_from_replay(steam_id, data.match_id)
        all_matches.append( pas.ts_cs(data, player['hero']) )

    return all_matches


def agg_item(steam_id, item):
    """
    Creates lists of timings for each item obtained for the matches is d2rp_list
    """
    global d2rp_list

    times = []
    for match_idx,data in enumerate(sorted(d2rp_list, key=lambda x:int(x.match_id))):
        player = squeeze.player_from_replay(steam_id, data.match_id)
        when = None
        for entry in (x for x in data.itemtimes if x['hero'] == player['hero']):
            print '{} : ENTRY={}'.format(item,entry)
            if entry['item'] == item:
                # time in seconds, normalize negative buy times
                when = max(0, (entry['time'] / 30))
                break # only first time item is bought

        # None if item wasn't bought that match
        times.append(when) 
    return times
        

#################################################

def create_cs_graph(steam_id):
    """
    Creates a CS-over-time graph for matches in d2rp_list and returns
    an image of the graph.
    """
    all_matches = agg_cs(steam_id)

    pas.new_graph()
    max_hit = 50
    max_time = 1200
    base_height = defaultdict(int)
    plots = []
    for match_idx,tscs in enumerate(all_matches):
        ts,cs = tscs
        for when,hit in zip(ts,cs):
            if hit > max_hit or when > max_time:
                break
            elif hit % 5 == 0:
                left = match_idx
                height = when
                bottom = base_height[match_idx]
                color = cm.jet( 1 - (float(hit)/max_hit) )

                plots.append( plt.bar(left, height, width=1, bottom=bottom, color=color) )
                base_height[match_idx] += height

    plt.xticks([x+0.5 for x in range(len(all_matches))], range(len(all_matches)))
    plt.xlim(0, len(all_matches))
    plt.ylim(0, max_time)
    plots.reverse()
    lprop = font_manager.FontProperties(size=10)
    plt.legend( [p[0] for p in plots], [x for x in range(50,0,-5)], bbox_to_anchor=(1, 1), loc=2, borderaxespad=0., prop=lprop)

    # regression lines
    for hit_set in [0, 3]: # 5 and 20 hits
        x = []
        y = []
        for match_idx,tscs in enumerate(all_matches):
            ts,cs = tscs
            x.append(match_idx)
            if len(ts) > hit_set:
                y.append(ts[hit_set])
            else:
                y.append(1200*hit_set) # weight at 10 mins * hit_set
        if len(x) > 0 and len(y) > 0:
            coeffs = numpy.polyfit(x,y, 1)
            fit_x = numpy.arange(min(x)-1, max(x)+1, .01)
            plt.plot(fit_x, numpy.polyval(coeffs, fit_x), '--', color='w')
    return pas.plt_to_image()


def create_item_graph(steam_id, item):
    """
    Creates a item-over-time graph for matches in d2rp_list and returns
    an image of the graph.
    """
    buy_times = agg_item(steam_id, item)

    x = []
    y = []
    for match_idx,when in enumerate(buy_times):
        if when:
            x.append(match_idx)
            y.append(when)

    pas.new_graph()
    if len(x) > 0 and len(y) > 0:
        plt.scatter(x, y, color='r')
        plt.xlim(min(x)-1, max(x)+1)
        plt.ylim(0, max(y))
        # regression line
        coeffs = numpy.polyfit(x,y, 1)
        fit_x = numpy.arange(min(x)-1, max(x)+1, .01)
        plt.plot(fit_x, numpy.polyval(coeffs, fit_x), '--', color='w')
    return pas.plt_to_image()
