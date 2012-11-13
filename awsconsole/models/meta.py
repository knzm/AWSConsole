# -*- coding: utf-8 -*-

from sqlalchemy import engine_from_config
from sqlalchemy.orm import  scoped_session, sessionmaker, ColumnProperty
from sqlalchemy.ext.declarative import declarative_base
from zope.sqlalchemy import ZopeTransactionExtension

DBSession = scoped_session(sessionmaker(extension=ZopeTransactionExtension()))

__all__ = ['DBSession', 'BaseModel', 'init_model']


class BaseModel(declarative_base()):
    __abstract__ = True

    # Code snippet from Elixir's source
    def to_dict(self, deep={}, exclude=[]):
        """Generate a JSON-style nested dict/list structure from an object."""
        col_prop_names = [p.key for p in self.__mapper__.iterate_properties \
                                      if isinstance(p, ColumnProperty)]
        data = dict([(name, getattr(self, name))
                     for name in col_prop_names if name not in exclude])
        for rname, rdeep in deep.iteritems():
            dbdata = getattr(self, rname)
            #FIXME: use attribute names (ie coltoprop) instead of column names
            fks = self.__mapper__.get_property(rname).remote_side
            exclude = [c.name for c in fks]
            if dbdata is None:
                data[rname] = None
            elif isinstance(dbdata, list):
                data[rname] = [o.to_dict(rdeep, exclude) for o in dbdata]
            else:
                data[rname] = dbdata.to_dict(rdeep, exclude)
        return data


def init_model(settings):
    engine = engine_from_config(settings, 'sqlalchemy.')
    DBSession.configure(bind=engine)
    BaseModel.metadata.bind = engine
    BaseModel.metadata.create_all(engine)
