import os

import pytest

from repository_sqlalchemy.base_repository import Base
from repository_sqlalchemy.database_config import DatabaseConfig
from repository_sqlalchemy.session_management import get_engine
from tests.test_model import TestRepository


@pytest.fixture(scope="session")
def sqlite_file_path(tmp_path_factory):
    file_path = tmp_path_factory.mktemp("data") / "repository_sqlalchemy.sqlite"
    yield str(file_path)


def remove_test_db(sqlite_file_path):
    """Remove test database file if it exists."""
    print(type(sqlite_file_path))
    try:
        if os.path.exists(sqlite_file_path):
            os.remove(sqlite_file_path)
    except Exception as e:
        print(f"Warning: Could not remove test database: {e}")


@pytest.fixture(scope="session")
def db_config(sqlite_file_path):
    # Ensure we start with a clean database file
    remove_test_db(sqlite_file_path)

    os.environ["DB_TYPE"] = "sqlite"
    os.environ["DB_NAME"] = sqlite_file_path
    return DatabaseConfig("sqlite")


"""
@pytest.fixture(scope="session")
def db_config():
    os.environ['DB_TYPE'] = 'postgresql'
    os.environ['DB_NAME'] = 'postgres'  # Default database name
    os.environ['DB_USER'] = 'postgres'  # Default username
    os.environ['DB_PASSWORD'] = 'mysecretpassword'  # Password set in Docker run command
    os.environ['DB_HOST'] = 'localhost'
    os.environ['DB_PORT'] = '5432'  # Default PostgreSQL port
    return DatabaseConfig('postgresql')
"""


@pytest.fixture(scope="session")
def engine(db_config):
    return get_engine()


@pytest.fixture(scope="session")
def tables(sqlite_file_path, engine):
    Base.metadata.create_all(engine)
    yield
    Base.metadata.drop_all(engine)
    # Clean up the database file after all tests
    remove_test_db(sqlite_file_path)


@pytest.fixture
def test_repository(tables):
    return TestRepository()
