import pytest
import os
from sqlalchemy.orm import sessionmaker
from repository_sqlalchemy.database_config import DatabaseConfig
from repository_sqlalchemy.session_management import get_engine
from tests.test_model import TestModel, Base, TestRepository

# Constants
TEST_DB_PATH = os.path.join(os.path.dirname(__file__), 'data', 'test.db')


def remove_test_db():
    """Remove test database file if it exists"""
    try:
        if os.path.exists(TEST_DB_PATH):
            os.remove(TEST_DB_PATH)
    except Exception as e:
        print(f"Warning: Could not remove test database: {e}")

@pytest.fixture(scope="session")
def db_config():
    # Ensure we start with a clean database file
    remove_test_db()
    os.makedirs(os.path.dirname(TEST_DB_PATH), exist_ok=True)
    
    os.environ['DB_TYPE'] = 'sqlite'
    os.environ['DB_NAME'] = TEST_DB_PATH
    return DatabaseConfig('sqlite')

'''
@pytest.fixture(scope="session")
def db_config():
    os.environ['DB_TYPE'] = 'postgresql'
    os.environ['DB_NAME'] = 'postgres'  # Default database name
    os.environ['DB_USER'] = 'postgres'  # Default username
    os.environ['DB_PASSWORD'] = 'mysecretpassword'  # Password set in Docker run command
    os.environ['DB_HOST'] = 'localhost'
    os.environ['DB_PORT'] = '5432'  # Default PostgreSQL port
    return DatabaseConfig('postgresql')
'''

@pytest.fixture(scope="session")
def engine(db_config):
    return get_engine()

@pytest.fixture(scope="session")
def tables(engine):
    Base.metadata.create_all(engine)
    yield
    Base.metadata.drop_all(engine)
    # Clean up the database file after all tests
    remove_test_db()

@pytest.fixture
def test_repository(tables):
    return TestRepository()

@pytest.fixture(autouse=True)
def clean_db(engine, tables):
    Session = sessionmaker(bind=engine, expire_on_commit=False)
    session = Session()
    try:
        session.query(TestModel).delete()
        session.commit()
    finally:
        session.close()
