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
import logging

log = logging.getLogger(__name__)

from kivy.app import App
from kivy.lang import Builder
from kivy.config import Config
from kivy.properties import ObjectProperty, ListProperty
from kivy.graphics.context_instructions import Color
from kivy.graphics.vertex_instructions import Rectangle
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.dropdown import DropDown
from kivy.uix.checkbox import CheckBox
from kivy.uix.modalview import ModalView
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.listview import ListItemLabel, ListItemButton
from kivy.uix.filechooser import FileChooserListView
from kivy.uix.screenmanager import ScreenManager, Screen, FadeTransition
from kivy.adapters.dictadapter import DictAdapter
from kivy.adapters.listadapter import ListAdapter

import dotalocal
import plotandscheme
import plotandscheme.aggregate as pas_agg
import squeeze
import util
import configulifier as config
from configulifier import CFG
from parsing.d2rp import D2RP

import matplotlib.pyplot as plt


#{ KV definition
Builder.load_string("""
#:import osp os.path


# GUIS
#{ ReplayChooser
<ReplayChooser>
    BoxLayout:
        BoxLayout:
            orientation: 'vertical'
            Label:
                text: 'Recent replays'
                size_hint: 1, None
                height: 32
                color: 0, 0, 0, 1
                font_size: 16
                canvas.before:
                    Color:
                        rgba: .8, .8, .8, 1
                    Rectangle:
                        pos: self.pos
                        size: self.size
            ListView:
                id: list_view
                adapter: root.recent_adpt

        BoxLayout:
            orientation: 'vertical'
            Label:
                text: 'Open Replay'
                size_hint: 1, None
                height: 32
                color: 0, 0, 0, 1
                font_size: 16
                canvas.before:
                    Color:
                        rgba: .8, .8, .8, 1
                    Rectangle:
                        pos: self.pos
                        size: self.size
            FileChooserListView:
                id: filechooser
                filters: ['*.dem']
                path: osp.expanduser('~')
            Button:
                text: 'Load'
                size_hint: 1, None
                height: 64
                on_release: root.load(filechooser.selection)

        BoxLayout:
            orientation: 'vertical'
            Label:
                text: 'Replay Details'
                size_hint: 1, None
                height: 32
                color: 0, 0, 0, 1
                font_size: 16
                canvas.before:
                    Color:
                        rgba: .8, .8, .8, 1
                    Rectangle:
                        pos: self.pos
                        size: self.size
            BoxLayout:
#}

#{ MatchPerformanceScreen
<MatchPerformanceScreen>:
    id: match_perf
    player_list: player_list_view

    early_toggle: early_toggle
    mid_toggle: mid_toggle
    late_toggle: late_toggle

    btn_annot_items: btn_annot_items
    btn_annot_deaths: btn_annot_deaths
    btn_annot_levels: btn_annot_levels

    GridLayout:
        rows: 2

        ###########
        # Title bar
        ###########
        BoxLayout:
            size_hint: (1,None)
            height: 32
            orientation: 'horizontal'
            canvas.before:
                Color:
                    rgba: .2, .2, .2, 1
                Rectangle:
                    pos: self.pos
                    size: self.size

            Label:
                text: root.replay
                size_hint: (None,1)

            Label: 
                text: 'Winner ' + root.winner
                size_hint: (None,1)

            Label:

        ###########
        # Main body
        ###########
        GridLayout:
            cols: 2

            Splitter:
                sizable_from: 'right'
                size_hint: (None,1)
                size: (400,self.height)

                BoxLayout:
                    orientation: 'vertical'

                    #############
                    # Player List
                    #############
                    PlayerListView:
                        id: player_list_view
                        match_perf: match_perf

                    ##########
                    # Controls
                    ##########
                    BoxLayout:
                        orientation: 'vertical'
                        ToggleButton:
                            id: early_toggle
                            text: 'Early'
                            group: 'game_phase'
                            state: 'down'
                            on_press: root.on_early()
                        ToggleButton:
                            id: mid_toggle
                            text: 'Mid'
                            group: 'game_phase'
                            on_press: root.on_mid()
                        ToggleButton:
                            id: late_toggle
                            text: 'Late'
                            group: 'game_phase'
                            on_press: root.on_late()

            BoxLayout:
                orientation: 'vertical'
                Image:
                    canvas:
                        Rectangle:
                            texture: root.top_graph
                            pos: self.pos
                            size: self.size
                Image:
                    id: bot_graph
                    canvas:
                        Rectangle:
                            texture: root.bot_graph
                            pos: self.pos
                            size: self.size

                FloatLayout:
                    size_hint: None, None
                    ToggleButton:
                        id: btn_annot_levels
                        text: 'Levels'
                        group: 'event_annot'
                        on_press: root.on_event_annot()
                        height: bot_graph.height*0.08
                        width: bot_graph.width*0.1
                        x: bot_graph.x+bot_graph.width*0.01
                        y: bot_graph.y+(bot_graph.height*0.495)
                    ToggleButton:
                        id: btn_annot_items
                        text: 'Items'
                        group: 'event_annot'
                        on_press: root.on_event_annot()
                        height: bot_graph.height*0.08
                        width: bot_graph.width*0.1
                        x: bot_graph.x+bot_graph.width*0.01
                        y: bot_graph.y+(bot_graph.height*0.35)
                    ToggleButton:
                        id: btn_annot_deaths
                        text: 'Deaths'
                        group: 'event_annot'
                        on_press: root.on_event_annot()
                        height: bot_graph.height*0.08
                        width: bot_graph.width*0.1
                        x: bot_graph.x+bot_graph.width*0.01
                        y: bot_graph.y+(bot_graph.height*0.2)

#}

#{ ReplayBrowserScreen
<ReplayBrowserScreen>
    details_panel: details_panel
    browser: r_browser

    BoxLayout:
        BoxLayout:
            orientation: 'vertical'

            ReplayBrowser:
                id: r_browser
                select_callback: details_panel.load_replay

            BoxLayout:
                size_hint: 1, None
                height: 32
                Button:
                    text: 'Match Performance'
                    on_press: root.on_match_perf()
                Button:
                    text: 'Player Performance'
                    on_press: root.on_player_perf()

        ReplayDetails:
            id: details_panel
#}

#{ PlayerPerformanceScreen
<PlayerPerformanceScreen>
    top_graph: top_graph
    item_drop_btn: item_drop_btn
    BoxLayout:
        orientation: 'vertical'
        GraphPanel:
            id: top_graph
            title: 'Last Hits'
        BoxLayout:
            orientation: 'vertical'
            Label:
                text: 'Item Times'
                size_hint: 1, None
                height: 32
                color: 0, 0, 0, 1
                font_size: 14
                canvas.before:
                    Color:
                        rgba: .8, .8, .8, 1
                    Rectangle:
                        pos: self.pos
                        size: self.size
            Button:
                id: item_drop_btn
                size_hint: 1,None
                height: 32
                text: 'Select Item'
            Image:
                canvas:
                    Rectangle:
                        texture: root.item_texture
                        pos: self.pos
                        size: self.size
#}

#{ PreferencesScreen
<PreferencesScreen>
    pref_pane: pref_pane
#    in_replay_path: replay_path
    api_key: api_key_ti
    steam_id: steam_id_ti

    BoxLayout:
        id: pref_pane
        Label:
            text: ''
        BoxLayout:
            orientation: 'vertical'
            TitleLabel:
                text: 'Preferences'
            BoxLayout:
                orientation: 'vertical'
#                BoxLayout:
#                    size_hint: 1, None
#                    height: 32
#                    Label:
#                        text: 'Replay Path'
#                    TextInput:
#                        id: replay_path
#                        on_focus: root.focus_replay_path(self, self.focus)
                BoxLayout:
                    size_hint: 1, None
                    height: 32
                    Label:
                        text: 'API Key'
                    TextInput:
                        id: api_key_ti
                BoxLayout:
                    size_hint: 1, None
                    height: 32
                    Label:
                        text: 'Steam ID'
                    TextInput:
                        id: steam_id_ti
                Label:
            Button:
                size_hint: 1,None
                height: 48
                text: 'Continue'
                on_press: root.on_continue
        Label:
            text: ''
#}


# PANELS
#{ PlayerListView
[CustomListItem@SelectableView+BoxLayout]:
    size_hint_y: None
    height: ctx.height
    ListItemButton:
        font_name: 'data/fonts/DroidSansMono.ttf'
        font_size: 13
        text: ctx.player_label
        halign: 'left'
        valign: 'middle'
        text_size: self.size
        texture_size: self.size
        size_hint: (1,1)

<PlayerListView>:
    ListView:
        adapter: root.player_adapter
#}

#{ ReplayBrowser
<ReplayBrowser>
    fltr_cb_carry: cb_carry
    fltr_cb_jungler: cb_jungler
    fltr_cb_nuker: cb_nuker
    fltr_cb_support: cb_support

    ListView:
        canvas.before:
            Color:
                rgba: .1, .8, .1, 1
        adapter: root.replay_adpt

    BoxLayout:
        Label:
            text: 'Hero Type'
            size_hint: None,None
            height: 32
            width: self.width
            color: 0, 0, 0, 1
            font_size: 14
            canvas.before:
                Color:
                    rgba: .6, .6, .6, 1
                Rectangle:
                    pos: self.pos
                    size: self.size

        LabeledCheckBox:
            id: cb_carry
            padding: 3
            text: 'Carry'
            change_callback: root.on_hero_filter_change
        LabeledCheckBox:
            id: cb_jungler
            padding: 3
            text: 'Jungler'
            change_callback: root.on_hero_filter_change
        LabeledCheckBox:
            id: cb_nuker
            padding: 3
            text: 'Nuker'
            change_callback: root.on_hero_filter_change
        LabeledCheckBox:
            id: cb_support
            padding: 3
            text: 'Support'
            change_callback: root.on_hero_filter_change

#}

#{ ReplayDetails
<ReplayDetails>
    radiant_list: radiant_list
    dire_list: dire_list
    winner_lbl: winner_lbl
    youwon_lbl: youwon_lbl

    orientation: 'vertical'
    Label:
        text: 'Match'
        size_hint: 1,None
        height: 32
        color: 0, 0, 0, 1
        font_size: 14
        canvas.before:
            Color:
                rgba: .6, .6, .6, 1
            Rectangle:
                pos: self.pos
                size: self.size
    BoxLayout:
        size_hint: 1, None
        height: 32
        Label:
            text: 'Winner'
        Label:
            id: winner_lbl
    BoxLayout:
        size_hint: 1, None
        height: 32
        Label:
            id: youwon_lbl
    Label:
        text: 'Players'
        size_hint: 1,None
        height: 32
        color: 0, 0, 0, 1
        font_size: 14
        canvas.before:
            Color:
                rgba: .6, .6, .6, 1
            Rectangle:
                pos: self.pos
                size: self.size
    Label:
        text: 'Radiant'
        font_size: 12
        size_hint: 1,None
        height: 24
    ListView:
        id: radiant_list
    Label:
        text: 'Dire'
        font_size: 12
        size_hint: 1,None
        height: 24
    ListView:
        id: dire_list
#}

#{ GraphPanel
<GraphPanel>
    orientation: 'vertical'
    title: 'Not set'
    Label:
        text: root.title
        size_hint: 1, None
        height: 32
        color: 0, 0, 0, 1
        font_size: 14
        canvas.before:
            Color:
                rgba: .8, .8, .8, 1
            Rectangle:
                pos: self.pos
                size: self.size
    Image:
        canvas:
            Rectangle:
                texture: root.texture
                pos: self.pos
                size: self.size
#}

#}

# UTIL
#{ LabeledTextInput
<LabeledTextInput>
    size_hint: 1, None
    height: root.height
    input_box: textinput
    Label:
        text: root.text
    TextInput:
        id: textinput
        on_focus: root.on_focus
#}

#{ LabeledCheckBox
<LabeledCheckBox>
    size_hint: 1, None
    height: root.height
    padding: root.border_width
    checkbox: checkbox
    active: False
    canvas.before:
        Color:
            rgba: root.border_color
        Rectangle:
            pos: self.pos
            size: self.size
    Label:
        canvas.before:
            Color:
                rgba: root.background_color
            Rectangle:
                pos: self.pos
                size: self.size
        text: root.text
    CheckBox:
        id: checkbox
        on_active: root.on_change(self)
        active: root.active
        canvas.before:
            Color:
                rgba: root.background_color
            Rectangle:
                pos: self.pos
                size: self.size
#}

#{ ReplayListItem
[ReplayListItem@SelectableView+BoxLayout]:
    size_hint_y: None
    height: 32
    ReadOnlyCheckBox:
        size_hint: None,None
        size: 32,32
        active: ctx.is_local
    ListItemButton:
        text: ctx.id
    ListItemLabel:
        text: ctx.played
    ListItemLabel:
        text: ctx.team
    ListItemLabel:
        text: ctx.hero
#}

#{ PlayerListItem
[PlayerListItem@SelectableView+BoxLayout]:
    size_hint_y: None
    height: ctx.height
    ListItemLabel:
        font_size: 13
        text: ctx.hero
        halign: 'right'
        valign: 'middle'
        text_size: self.size
        texture_size: self.size
        size_hint: (1,1)
    ListItemLabel:
        text: ' '
    ListItemLabel:
        font_size: 13
        text: ctx.player
        halign: 'left'
        valign: 'middle'
        text_size: self.size
        texture_size: self.size
        size_hint: (1,1)
#}

#{ TitleLabel
<TitleLabel>
    size_hint: 1,None
    height: 32
    color: 0, 0, 0, 1
    font_size: 14
    canvas.before:
        Color:
            rgba: .6, .6, .6, 1
        Rectangle:
            pos: self.pos
            size: self.size
""")
#}


##################################
# Screen Classes
##################################
#{ class MatchPerformanceScreen
class MatchPerformanceScreen(Screen):
    winner = ObjectProperty('')
    replay = ObjectProperty('')
    top_graph = ObjectProperty(None)
    bot_graph = ObjectProperty(None)
    player_list = ObjectProperty(None)

    def __init__(self, *args, **kwargs):
        super(MatchPerformanceScreen,self).__init__(*args, **kwargs)
        self.match = None
        self.match_details = None
        self.d2rp = None

    def load_match(self, match_id):
        # dump local demo file 
        squeeze.dump_demo(match_id)

        self.d2rp = D2RP(squeeze.fs_replay_path(match_id))
        self.match, self.match_details = squeeze.replay_details(match_id)
        self.winner = self.match_details.winner
        self.replay = str(self.match.match_id)

        self.player_list.d2rp = self.d2rp
        self.player_list.reload()
        self.redraw()
    
    def redraw(self):
        if self.early_toggle.state == 'down':
            self.on_early()
        elif self.mid_toggle.state == 'down':
            self.on_mid()
        elif self.late_toggle.state == 'down':
            self.on_late()

    def on_early(self):
        selected = self.player_list.get_selected()
        annotated = self.get_annotated()
        plotandscheme.d2rp = self.d2rp
        self.top_graph = plotandscheme.create_gold_graph(selected, 0, 600)
        self.bot_graph = plotandscheme.create_event_graph(selected, 0, 600, annotated)

    def on_mid(self):
        selected = self.player_list.get_selected()
        annotated = self.get_annotated()
        plotandscheme.d2rp = self.d2rp
        self.top_graph = plotandscheme.create_gold_graph(selected, 600, 1200)
        self.bot_graph = plotandscheme.create_event_graph(selected, 600, 1200, annotated)

    def on_late(self):
        selected = self.player_list.get_selected()
        annotated = self.get_annotated()
        plotandscheme.d2rp = self.d2rp
        self.top_graph = plotandscheme.create_gold_graph(selected, 1200, sys.maxint)
        self.bot_graph = plotandscheme.create_event_graph(selected, 1200, sys.maxint, annotated)

    def on_event_annot(self):
        self.redraw()

    def get_annotated(self):
        a = []
        if self.btn_annot_items.state == 'down':
            a.append('items')
        if self.btn_annot_deaths.state == 'down':
            a.append('kills')
        if self.btn_annot_levels.state == 'down':
            a.append('levels')
        return a
#}

#{ class ReplayChooser
class ReplayChooser(Screen):
    recent_adpt = ObjectProperty(None)

    def __init__(self, *args, **kwargs):
        self.recent_adpt = ListAdapter(data=squeeze.local_replay_ids(), 
                                       cls=ListItemButton, 
                                       selection_mode='single')
        self.recent_adpt.bind(on_selection_change=self.on_select)
        super(ReplayChooser, self).__init__(*args, **kwargs)

    def load(self, filename):
        filename = filename[0]
        squeeze.dump_demo(filename)
        demo_num = os.path.split(filename)[-1].strip('.dem')

        d2rp.init_d2rp(os.path.join(squeeze.PARSER_PATH, 'json', demo_num))

        s_mgr.current = 's_match_perf'

    def on_select(self, selected):
        print selected.selection[0].text 

#}

#{ class ReplayBrowserScreen
class ReplayBrowserScreen(Screen):
    browser = ObjectProperty(None)

    def on_match_perf(self):
        if len(self.browser.replay_adpt.selection) > 0:
            # view match details for selected match
            match_id = self.browser.replay_adpt.selection[0].text
            #squeeze.download_replay(match_id) # not supported
            global s_mgr
            screen = s_mgr.get_screen('s_match_perf')
            screen.load_match(match_id)
            s_mgr.current = 's_match_perf'


    def on_player_perf(self):
        global s_mgr
        screen = s_mgr.get_screen('s_player_perf')
        if len(self.browser.replay_adpt.selection) > 0:
            screen.load_replays([s.text for s in self.browser.replay_adpt.selection])
        else: # default to all replays
            screen.load_replays(squeeze.local_replay_ids())
        s_mgr.current = 's_player_perf'
#}

#{ class PlayerPerformanceScreen
class PlayerPerformanceScreen(Screen):
    top_graph = ObjectProperty(None)
    item_texture = ObjectProperty(None)

    item_drop_btn = ObjectProperty(None)
    _item_dropdown = None


    def _item_selected(self, local_item_name):
        # convert local to key name
        try:
            item = [k for k,v in dotalocal.item.iteritems() if v == local_item_name][0]
        except IndexError:
            log.error('_item_selected: Invalid item name {}'.format(local_item_name))
            return
        self.item_drop_btn.text = local_item_name
        self.item_texture = pas_agg.create_item_graph(squeeze.my_id, item)

    def _init_item_dropdown(self):
        self._item_dropdown = DropDown()
        for item_name in sorted(dotalocal.item.itervalues()):
            btn = Button(text=item_name, size_hint_y=None, height=32)
            btn.bind(on_release=lambda btn: self._item_dropdown.select(btn.text))
            self._item_dropdown.add_widget(btn)

        self.item_drop_btn.bind(on_release=self._item_dropdown.open)
        self._item_dropdown.bind(on_select=lambda inst, x: self._item_selected(x))

    def load_replays(self, replay_list):
        if not self._item_dropdown:
            self._init_item_dropdown()

        pas_agg.d2rp_list = []

        for replay_id in replay_list:
            # skip replays the player did not play in
            player = squeeze.player_from_replay(squeeze.my_id, replay_id)
            if player is None:
                continue

            squeeze.dump_demo(replay_id)
            match = squeeze.replay(replay_id)
            d2rp = D2RP(squeeze.fs_replay_path(replay_id))
            pas_agg.d2rp_list.append(d2rp)

        self.top_graph.texture = pas_agg.create_cs_graph(squeeze.my_id)
#}

#{ class PreferencesScreen
class PreferencesScreen(Screen):
    def __init__(self, *args, **kwargs):
        super(PreferencesScreen, self).__init__(*args, **kwargs)
        self.chooser = None

    def _show_filechooser(self):
        self.clear_widgets()

        self.chooser = FileChooserListView(path=self.in_replay_path.text, dirselect=True)
        select_btn = Button(text='Select', size_hint=(1,None), height=48)
        select_btn.bind(on_press=self._set_replay_path_from_chooser)

        layout = BoxLayout()
        mid = BoxLayout(orientation='vertical')
        mid.add_widget(self.chooser)
        mid.add_widget(select_btn)

        layout.add_widget(Label())
        layout.add_widget(mid)
        layout.add_widget(Label())
        self.add_widget(layout)

    def focus_replay_path(self, instance, value):
        self._show_filechooser()

    def _set_replay_path_from_chooser(self, btn):
        if len(self.chooser.selection) > 0:
            self.in_replay_path.text = self.chooser.selection[0]

        self.in_replay_path.focus = False
        self.clear_widgets()
        self.add_widget(self.pref_pane)

    def on_continue(self, btn):
        CFG['api_key'] = self.api_key.text.strip()
        CFG['steam_id'] = self.steam_id.text.strip()
        config.save_config()

        global s_mgr
        s_mgr.current = 's_replay_browser'
#}

##################################
# Panel Classes
##################################
#{ class ReplayDetails
class ReplayDetails(BoxLayout):
    radiant_list = ObjectProperty(None)
    dire_list = ObjectProperty(None)
    winner_lbl = ObjectProperty(None)
    youwon_lbl = ObjectProperty(None)

    def __init__(self, *args, **kwargs):
        super(ReplayDetails, self).__init__(*args, **kwargs)

    def _player_to_list_item(self, row, rec):
        rec = util.NonNullableDict(rec)
        return {'hero': dotalocal.hero[rec['hero']], 'player': rec['profile'].name, 'height': 32}

    def load_replay(self, match_id):
        match, details = squeeze.replay_details(match_id)

        self.winner_lbl.text = details.winner
        owner = squeeze.player_from_replay(squeeze.my_id, match_id)
        if owner is not None:
            if owner['team'] == details.winner:
                self.youwon_lbl.text = 'Your team Won'
                with self.youwon_lbl.canvas.before:
                    Color(.2, .5, .2, 1)
                    Rectangle(size=self.youwon_lbl.size, pos=self.youwon_lbl.pos)
            else:
                self.youwon_lbl.text = 'Your team Lost'
                with self.youwon_lbl.canvas.before:
                    Color(.5, .2, .2, 1)
                    Rectangle(size=self.youwon_lbl.size, pos=self.youwon_lbl.pos)
        else:
            owner_won = None


        players = details.all_players()
        hero_len = max( [len(dotalocal.hero[p['hero']]) for p in players] )
        radiant = [util.NonNullableDict(x) for x in players if x['team'] == 'Radiant']
        dire = [util.NonNullableDict(x) for x in players if x['team'] == 'Dire']

        self.radiant_list.adapter = ListAdapter(data=sorted(radiant, key=lambda x:x['slot']), 
                args_converter=self._player_to_list_item, template='PlayerListItem')
        self.dire_list.adapter = ListAdapter(data=sorted(dire, key=lambda x:x['slot']), 
                args_converter=self._player_to_list_item, template='PlayerListItem')
#}

#{ class ReplayBrowser
class ReplayBrowser(ModalView):
    replay_adpt = ObjectProperty(None)
    select_callback = ObjectProperty(None)

    fltr_cb_carry = ObjectProperty(None)
    fltr_cb_jungler = ObjectProperty(None)
    fltr_cb_nuker = ObjectProperty(None)
    fltr_cb_support = ObjectProperty(None)

    def __init__(self, *args, **kwargs):
        super(ReplayBrowser, self).__init__(*args, **kwargs)
        self._refresh_replays()

    def _refresh_replays(self, hero_types=None):
        if not hero_types:
            hero_types = dotalocal.HeroType.all()
        list_data = [r for r in squeeze.all_replays(squeeze.my_id, 
                                                    hero_types=hero_types,
                                                    max_results=40)]
        self.replay_adpt = ListAdapter(data=list_data,
                                       args_converter=self._replay_adpt_converter,
                                       selection_mode='multiple',
                                       template='ReplayListItem')
        self.replay_adpt.bind(on_selection_change=self._on_replay_select)

    def _replay_adpt_converter(self, row_idx, record):
        owner = squeeze.player_from_replay(squeeze.my_id, record.match_id)
        if owner is not None:
            hero = dotalocal.hero[owner['hero']]
            team = owner['team']
        else:
            hero = 'Unknown'
            team = 'Unknown'

        is_downloaded = record.match_id in squeeze.local_replay_ids()

        return {'id': str(record.match_id),
                'played': str(record.when),
                'hero': hero,
                'team': team,
                'is_local': is_downloaded}

    def on_hero_filter_change(self, checkbox):
        htypes = []
        if self.fltr_cb_carry.checkbox.active:
            htypes.append(dotalocal.HeroType('carry'))
        if self.fltr_cb_jungler.checkbox.active:
            htypes.append(dotalocal.HeroType('jungler'))
        if self.fltr_cb_nuker.checkbox.active:
            htypes.append(dotalocal.HeroType('nuker'))
        if self.fltr_cb_support.checkbox.active:
            htypes.append(dotalocal.HeroType('support'))
        self._refresh_replays(htypes)

    def _on_replay_select(self, adpt):
        if len(adpt.selection) > 0:
            self.select_callback(adpt.selection[0].text)

#}

#{ class GraphPanel
class GraphPanel(BoxLayout):
    graph = ObjectProperty(None)
    texture = ObjectProperty(None)
#}

##################################
# Util Classes
##################################
#{ class PlayerListView
class PlayerListView(ModalView):
    player_adapter = ObjectProperty(None)
    match_perf = ObjectProperty(None)

    def __init__(self, **kwargs):
        super(PlayerListView, self).__init__(**kwargs)

        # filled in later with call to reload()
        self.player_adapter = DictAdapter(sorted_keys=[],
                                          data={},
                                          args_converter=self._player_converter,
                                          selection_mode='multiple',
                                          propagate_selection_to_data=True,
                                          template='CustomListItem')

        self.d2rp = None # set by parent

    def _player_converter(self, idx, rec):
        return {'player_label': rec['player_label'],
                'is_selected': rec['is_selected'],
                'size_hint_y': None,
                'height': 25}

    def reload(self):
        if not self.d2rp:
            return

        hero_len = max([len(dotalocal.hero[h['hero']]) for h in self.d2rp.players])

        p_str = {}
        for i,hero in enumerate(self.d2rp.players):
            hero_s = dotalocal.hero[hero['hero']]
            player = dotalocal.player(hero['player'])
            p_str[str(i)] = { 
                'player_label': ' {} | {}'.format(hero_s.ljust(hero_len), player),
                'is_selected': False }

        self.player_adapter = DictAdapter(sorted_keys=[i for i in range(len(p_str))],
                                          data=p_str,
                                          args_converter=self._player_converter,
                                          selection_mode='multiple',
                                          propagate_selection_to_data=True,
                                          template='CustomListItem')

        self.player_adapter.bind(on_selection_change=self.selection_changed)

    def selection_changed(self, *args):
        self.match_perf.redraw()

    def get_selected(self):
        selected = []
        for btn in self.player_adapter.selection:
            hero_s = btn.text.split('|')[0].strip()
            #for pl in self.d2rp.players:
            for pl in self.match_perf.match.all_players():
                if dotalocal.hero[pl['hero']] == hero_s:
                    selected.append(pl)
                    break
        return selected
#}

#{ class LabeledTextInput
class LabeledTextInput(BoxLayout):
    height = ObjectProperty(32)
    text = ObjectProperty('Not set')
    input_box = ObjectProperty(None)
    focus_callback = ObjectProperty(None)

    def __init__(self, *args, **kwargs):
        super(LabeledTextInput, self).__init__(*args, **kwargs)

    def on_focus(self, item):
        print 'LabeledTextInput.on_focus'
        if self.focus_callback:
            self.focus_callback(item)
#}

#{ class LabeledCheckBox
class LabeledCheckBox(BoxLayout):
    height = ObjectProperty(32)
    border_width = ObjectProperty(2)
    border_color = ListProperty([.2, .2, .2, 1])
    background_color = ListProperty([.1, .1, .1, 1])
    text = ObjectProperty('Not set')
    checkbox = ObjectProperty(None)
    change_callback = ObjectProperty(None)

    def __init__(self, *args, **kwargs):
        super(LabeledCheckBox, self).__init__(*args, **kwargs)

    def on_change(self, checkbox):
        if self.change_callback:
            self.change_callback(checkbox)
#}

#{ class TitleLabel
class TitleLabel(Label):
    pass
#}

#{ class ReadOnlyCheckBox
class ReadOnlyCheckBox(CheckBox):
    def on_touch_down(self, touch):
        if not self.collide_point(*touch.pos):
            return
        return True
#}

##################################
#{ init

s_mgr = None

def init():
    global s_mgr

    if s_mgr:
        return
    
    Config.set('kivy', 'desktop', 1)
    Config.set('graphics', 'width', '1200')
    Config.set('graphics', 'height', '600')

    fader = FadeTransition()
    fader.duration = 0.25
    
    s_mgr = ScreenManager(transition=fader)
    s_mgr.add_widget(ReplayBrowserScreen(name='s_replay_browser'))
    s_mgr.add_widget(MatchPerformanceScreen(name='s_match_perf'))
    s_mgr.add_widget(PlayerPerformanceScreen(name='s_player_perf'))
    s_mgr.add_widget(PreferencesScreen(name='s_preferences'))

    if CFG['api_key'] is None:
        s_mgr.current = 's_preferences'
    else:
        s_mgr.current =  's_replay_browser'
#}

class GuiApp(App):
    def build(self):
        return s_mgr
