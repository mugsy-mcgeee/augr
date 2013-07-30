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
import json
import urllib2
from subprocess import Popen
from datetime import datetime, timedelta
from glob import glob
import time
import logging
import socket
import unicodedata
import pickle

import penv
import err
import dotalocal
from configulifier import CFG
from dotalocal import MatchType, HeroType, GameMode
import util
import vault
log = logging.getLogger(__name__)

PARSER_PATH=os.path.join(penv.LIBDIR, '..', 'Dota2_ReplayParser_v102')
PARSER_BIN=os.path.join(PARSER_PATH, 'DotaParser.exe')

my_id = CFG['steam_id']
STEAM_BASE = 'https://api.steampowered.com'
STEAM_NS = {'match': 'IDOTA2Match_570'}
STEAM_REQ = {'GetMatchHistory': '{}/{}'.format(STEAM_NS['match'], 'GetMatchHistory/v001'),
             'GetMatchDetails': '{}/{}'.format(STEAM_NS['match'], 'GetMatchDetails/V001')}


def dump_demo(match_id):
    """
    Check if a dump already exists and exit if so. Otherwise verify that
    the demo file exists and call out to the replay parser.
    """
    # return if dump directory already exists
    if os.path.exists(fs_replay_path(match_id)):
        return

    demo_path = os.path.join(CFG['replay_path'], '{}.dem'.format(match_id))
    if os.path.exists(demo_path):
        Popen([PARSER_BIN, demo_path]).communicate()
    else:
        log.error('Demo not found: {}'.format(demo_path))


def fs_replay_path(match_id):
    """
    Returns the path to the parsed dump for a given match_id.
    Does not guarantee that the path will exist.
    """
    return os.path.join(PARSER_PATH, 'json', match_id)


def local_replay_ids():
    """
    Returns a list of match_ids for replays that are found
    locally on disk.
    """
    return [int(os.path.split(x)[-1].strip('.dem')) for x in 
            glob(os.path.join(CFG['replay_path'], '*.dem'))]


def player_from_json(raw):
    """
    Parses JSON received from Steam API about a match player and returns a dict
    """
    try:
        if raw['account_id'] == 4294967295:
            steam_id = 'Hidden'
        else:
            steam_id = str(raw['account_id'] + 76561197960265728)
            
        profile = profile_by_id(steam_id)

        if (raw['player_slot'] & 128) == 0:
            team = 'Radiant'
        else:
            team = 'Dire'

        slot = raw['player_slot'] & 7
    except KeyError:
        import traceback
        traceback.print_exc()
        raise err.MalformedPlayer(raw)

    # player index, 0-7
    if team == 'Radiant':
        index = 0
    else:
        index = 5
    index += slot

    # items
    for i in range(6):
        items = []
        try:
            items.append(raw['item_{}'.format(i)])
        except KeyError:
            pass

    # leaver status
    try:
        leaver = dotalocal.LeaverStatus(raw['leaver_status'])
    except KeyError:
        leaver = dotalocal.LeaverStatus('Unknown')

    return {'steam_id': steam_id,
            'profile': profile.snapshot() if profile else None,
            'slot': slot,
            'team': team,
            'index': index,
            'kills': raw.get('kills', None),
            'deaths': raw.get('deaths', None),
            'assists': raw.get('assists', None),
            'leaver': leaver,
            'gold': raw.get('gold', None),
            'last_hits': raw.get('last_hits', None),
            'denies': raw.get('denies', None),
            'gold_per_min': raw.get('gold_per_min', None),
            'xp_per_min': raw.get('xp_per_min', None),
            'gold_spent': raw.get('gold_spent', None),
            'hero_damage': raw.get('hero_damage', None),
            'tower_damage': raw.get('tower_damage', None),
            'hero_healing': raw.get('hero_healing', None),
            'level': raw.get('level', None),
            'abilities': raw.get('ability_upgrades', None),
            'hero': dotalocal.decode_hero(raw['hero_id'])}


def replay_from_json(raw):
    """
    Parses JSON received from Steam API about a Replay header and returns a dict
    """
    players = []
    for p in raw['players']:
        try:
            players.append( player_from_json(p) )
        except err.MalformedPlayer, e:
            log.error('MalformedPlayer: {}'.format(e))

    return vault.ReplayHeader(match_id=raw['match_id'],
                              lobby_type=raw['lobby_type'],
                              players=pickle.dumps(players),
                              when=datetime.fromtimestamp(raw['start_time']))


def details_from_json(raw):
    """
    Parses JSON received from Steam API about Replay details and returns a dict
    """
    return vault.ReplayDetail(match_id=raw['match_id'],
                              game_type=raw['game_mode'],
                              winner='Radiant' if raw['radiant_win'] else 'Dire',
                              duration=raw['duration'],
                              players=pickle.dumps( map(player_from_json, raw['players']) ),
                              when=datetime.fromtimestamp(raw['start_time']),
                              url='http://replay{}.valve.net/570/{}.dem.bz2'.format(raw['cluster'],
                                                                                    raw['match_id']))



def steam_api_call(req_path, opts, retries=5):
    """
    Performs a call to the Steam API
    """
    opts['key'] = CFG['api_key']
    opts['format'] = 'json'
    opts['language'] = 'EN'
    url = '{}/{}?{}'.format(STEAM_BASE, req_path, util.dict_to_url(opts))
    log.info('steam_api_call=[{}]'.format(url))
    try:
        r = json.load(urllib2.urlopen(url))['result']

        if 'statusDetail' in r and r['statusDetail'].endswith("user that hasn't allowed it"):
            raise err.ReplaysNotPublic

        return r
    except urllib2.HTTPError:
        sys.tracebacklimit = 0
        raise
    except socket.error, e:
        if retries > 0:
            wait = (5-retries)*2+1
            log.info('Socket error, retrying request in {} seconds'.format(wait))
            time.sleep(wait)
            return steam_api_call(req_path, opts, retries-1)
        else:
            raise err.SteamAPIFailure(e)


@util.with_network_retry
def profile_by_id(steam_id):
    """
    Retrieves or creates a SteamProfile object. This object contains the user's
    Steam ID and profile name. The profile name is scraped from their steamcommunity page.
    If steam_id is 'Hidden' then we don't know their real steam id and we return a
    placeholder SteamProfile.
    """
    session = vault._session()
    steam_id = str(steam_id)

    profile = None

    try:
        if steam_id == 'Hidden':
            profile = vault.SteamProfile(steam_id=steam_id, name=steam_id)
        else:
            profile = vault.SteamProfile.get(session, byid=steam_id)
    except vault.PlayerNotFound:
        # if player not in cache then generate new SteamProfile 
        url = 'http://steamcommunity.com/profiles/{}/'.format(steam_id)
        print 'Query profile: {}'.format(steam_id)
        player_name = 'Unknown'
        for line in urllib2.urlopen(url).readlines():
            if 'Steam Community :: ID ::' in line:
                try:
                    player_name = unicode(line.split('::')[2].split('</title>')[0].strip(), 'utf-8')
                except KeyError:
                    raise Exception('Unexpected HTML ({})'.format(line))
            elif 'Steam Community :: ' in line:
                try:
                    player_name = unicode(line.split('::')[1].split('</title>')[0].strip(), 'utf-8')
                except KeyError:
                    raise Exception('Unexpected HTML ({})'.format(line))
        # If SteamProfile creation successful then save to the cache
        if player_name:
            profile = vault.SteamProfile(steam_id=steam_id, name=player_name)
            session.add(profile)
            session.commit()

    return profile


def player_from_replay(steam_id, match_id):
    """
    Given a steam_id, returns the Player from the match. If that player
    is not found in the match then return None
    """
    match = replay(match_id)
    try:
        return [p for p in match.all_players() if steam_id == p['steam_id']][0]
    except (IndexError, KeyError):
        return None


def all_replays(steam_id, 
                match_types=[MatchType(5),MatchType(2),MatchType(0),MatchType(6)], 
                hero_types=[HeroType(0),HeroType(1),HeroType(2),HeroType(3)],
                max_results=1000):
    """
    Generator that yields all of the matches in a player's history, up to max_results.
    First we get the latest replay that we have in our local cache and then request
    all of the matches that are newer than this and yield them starting with the
    newest. After that we yield the matches that are in the cache.
    """

    count = 0
    session = vault._session()

    try:
        args = {'account_id': steam_id, 'matches_requested': 25}

        # New games that aren't in the cache yet
        ########################################
        latest = vault.ReplayHeader.latest(session)
        newest_cache = latest.when if latest else None
        log.debug('NEWEST_CACHE={}'.format(newest_cache))
        if newest_cache:
            args['date_min'] = (newest_cache-datetime.fromtimestamp(0)).total_seconds()+1
        r = steam_api_call(STEAM_REQ['GetMatchHistory'], args)
        log.debug('Matches={}'.format(len(r['matches'])))

        while True:
            matches = r['matches']
            for match in matches:
                replay = replay_from_json(match)
                if newest_cache and replay.when == newest_cache:
                    matches.remove(match)
                    continue # skip if it's actually the newest in the cache

                # persist replay
                session.add(replay)
                args['start_at_match_id'] = int(replay.match_id)-1
                #log.debug('ID={}'.format(args['start_at_match_id']))

                # TODO: re-implement this logic
                valid_hero = True

                if replay.lobby_type in match_types and valid_hero:
                    count += 1
                    log.debug('CacheMiss: {}'.format(replay.match_id))
                    yield replay.snapshot()

            if len(matches) < args['matches_requested'] or max_results is None or count >= max_results:
                break

            r = steam_api_call(STEAM_REQ['GetMatchHistory'], args)
            log.debug('Matches={}'.format(len(r['matches'])))

        # Rest of the games in the cache
        ########################################
        for replay in vault.ReplayHeader.get(session, older_than=replay.when):
            # TODO: re-implement this logic
            valid_hero = True

            if replay.lobby_type in match_types and valid_hero:
                count += 1
                log.debug('CacheHit: {}'.format(replay.match_id))
                yield replay.snapshot()

            if max_results is None or count >= max_results:
                break

    except StopIteration:
        pass
    session.commit()


def replay(match_id):
    """
    Returns a ReplayHeader for the given match_id from a GetMatchHistory Steam API call
    """
    session = vault._session()

    try:
        replay = vault.ReplayHeader.get(session, byid=match_id)
    except vault.ReplayNotFound:
        r = steam_api_call(STEAM_REQ['GetMatchHistory'], {'match_id': match_id})
        try:
            replay = replay_from_json(r['matches'][0])
            session.add(replay)
            session.commit()
        except Exception, e:
            raise err.MalformedReplay(e)
    return replay


def replay_details(match_id):
    """
    Returns a ReplayDetail for the given match_id from a GetMatchDetails Steam API call
    """
    session = vault._session()

    try:
        details = vault.ReplayDetail.get(session, byid=match_id)
    except vault.ReplayNotFound:
        r = steam_api_call(STEAM_REQ['GetMatchDetails'], {'match_id': match_id})
        try:
            details = details_from_json(r)
            session.add(details)
            session.commit()
        except Exception, e:
            raise err.MalformedReplay(e)

    return (replay(match_id), details)


def download_replay(match_id):
    """
    Does nothing right now but retrieve the download URL from the
    Steam API. This URL is currently invalid because it lacks the
    salt value necessary to complete it. Valve has decided to
    disable providing this to the public for now.
    """
    replay, details = replay_details(match_id)
    print 'URL={}'.format(details['url'])
