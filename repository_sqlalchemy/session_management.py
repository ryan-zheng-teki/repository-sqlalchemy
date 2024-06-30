import os
from sqlalchemy.orm import sessionmaker
from contextlib import contextmanager
from contextvars import ContextVar
from repository_sqlalchemy.database_config import DatabaseConfig, DatabaseEngineFactory

session_context_var: ContextVar[any] = ContextVar("db_session", default=None)

_engine = None
_Session = None

def get_engine():
    global _engine
    if _engine is None:
        db_type = os.environ.get('DB_TYPE', 'postgresql')
        db_config = DatabaseConfig(db_type)
        _engine = DatabaseEngineFactory.create_engine(
            db_config)
    return _engine

def get_session():
    global _Session
    if _Session is None:
        _Session = sessionmaker(bind=get_engine(), expire_on_commit=False)
    return _Session()
