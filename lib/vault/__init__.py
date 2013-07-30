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
import pickle
import sqlalchemy as sa
from sqlalchemy.sql import select
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql.expression import Insert as insert
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.hybrid import hybrid_property

import util
from configulifier import CFG


class InvalidArgument(Exception):
    pass
class PlayerNotFound(Exception):
    pass
class ReplayNotFound(Exception):
    pass


_engine = sa.create_engine('sqlite+pysqlite:///{}'.format(CFG['db_path']))
_metadata = sa.MetaData(bind=_engine)
_base = declarative_base(bind=_engine, metadata=_metadata)
_session = sessionmaker(bind=_engine)


#############################
# TABLES
#############################
class Queryable(object):
    @classmethod
    def query(cls, *args):
        if len(args) == 0:
            args = [cls]
        return _session().query(*args)

    @classmethod
    def all(cls):
        return cls.query().all()


class SteamProfile(Queryable, _base):
    __tablename__ = 'profiles'
    id       = sa.Column(sa.Integer, primary_key=True)
    steam_id = sa.Column(sa.String)
    name     = sa.Column(sa.String)

    def __repr__(self):
        return "<SteamProfile('{}','{}')>".format(self.steam_id, self.name)

    def snapshot(self):
        return util.CaseClass(id=self.id, steam_id=self.steam_id, name=self.name)

    @classmethod
    def get(cls, session, **kwargs):
        """
        byid: steam_id
        """
        if 'byid' in kwargs:
            s = session.query(SteamProfile).filter_by(steam_id=kwargs['byid']).first()
            if s is not None:
                return s
            else:
                raise PlayerNotFound()
        else:
            raise InvalidArgument()


class ReplayHeader(Queryable, _base):
    __tablename__ = 'replay_headers'
    id         = sa.Column('id', sa.Integer, primary_key=True)
    match_id   = sa.Column('match_id', sa.Integer)
    lobby_type = sa.Column('lobby_type', sa.Integer)
    players    = sa.Column('players', sa.Binary)
    when       = sa.Column('when', sa.DateTime)

    def __repr__(self):
        return "<ReplayHeader('{}','{}')>".format(self.match_id, self.when)

    def all_players(self):
        return pickle.loads(self.players)

    def snapshot(self):
        return util.CaseClass(id=self.id,
                              match_id=self.match_id,
                              lobby_type=self.lobby_type,
                              players=self.players,
                              when=self.when)

    @classmethod
    def latest(cls, session):
        return session.query(ReplayHeader).order_by(ReplayHeader.when).first()

    @classmethod
    def get(cls, session, **kwargs):
        """
        byid: match_id
        older_than: datetime
        newer_than: datetime
        """
        if 'byid' in kwargs:
            s = session.query(ReplayHeader).filter(ReplayHeader.match_id==kwargs['byid']).first()
            if s is not None:
                return s
            else:
                raise ReplayNotFound()
        elif 'older_than' in kwargs:
            return session.query(ReplayHeader).filter(ReplayHeader.when < kwargs['older_than']).all()
        else:
            raise InvalidArgument()


class ReplayDetail(Queryable, _base):
    __tablename__ = 'replay_details'
    id        = sa.Column('id', sa.Integer, primary_key=True)
    match_id  = sa.Column('match_id', sa.Integer)
    game_type = sa.Column('game_type', sa.Integer)
    winner    = sa.Column('winner', sa.String)
    duration  = sa.Column('duration', sa.Integer)
    players   = sa.Column('players', sa.Binary)
    when      = sa.Column('when', sa.DateTime)
    url       = sa.Column('url', sa.String)

    def __repr__(self):
        return "<ReplayDetail('{}','{}')>".format(self.match_id, self.when)

    def all_players(self):
        return pickle.loads(self.players)

    def snapshot(self):
        return util.CaseClass(id=self.id,
                              match_id=self.match_id,
                              game_type=self.game_type,
                              winner=self.winner,
                              duration=self.duration,
                              players=self.players,
                              when=self.when,
                              url=self.url)

    @classmethod
    def get(cls, session, **kwargs):
        """
        byid: match_id
        """
        if 'byid' in kwargs:
            s = session.query(ReplayDetail).filter(ReplayDetail.match_id==kwargs['byid']).first()
            if s is not None:
                return s
            else:
                raise ReplayNotFound()
        else:
            raise InvalidArgument()


#######################################
# auto-create tables on load
#######################################
_metadata.create_all()
