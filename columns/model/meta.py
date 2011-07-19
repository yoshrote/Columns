"""SQLAlchemy Metadata and Session object"""
from sqlalchemy.orm import scoped_session, sessionmaker

from sqlalchemy import MetaData, orm

__all__ = ['Base', 'Session']

# SQLAlchemy session manager. Updated by model.init_model()
Session = None

# Global metadata. If you have multiple databases with overlapping table
# names, you'll need a metadata for each database
metadata = MetaData()

# SQLAlchemy database engine.  Updated by model.init_model()
engine = None

