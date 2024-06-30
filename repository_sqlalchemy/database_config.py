import os
from urllib.parse import quote_plus

class DatabaseConfig:
    def __init__(self, db_type: str):
        self.db_type = db_type
        self.user = os.environ.get('DB_USER', '')
        self.password = os.environ.get('DB_PASSWORD', '')
        self.host = os.environ.get('DB_HOST', 'localhost')
        self.port = os.environ.get('DB_PORT', '5432')  # Default PostgreSQL port
        self.name = os.environ.get('DB_NAME', '')

    def get_connection_url(self) -> str:
        if self.db_type == 'postgresql':
            return f"postgresql://{self.user}:{quote_plus(str(self.password))}@{self.host}:{self.port}/{self.name}"
        elif self.db_type == 'mysql':
            return f"mysql+pymysql://{self.user}:{quote_plus(str(self.password))}@{self.host}:{self.port}/{self.name}"
        elif self.db_type == 'sqlite':
            return f"sqlite:///{self.name}"
        else:
            raise ValueError(f"Unsupported database type: {self.db_type}")

class DatabaseEngineFactory:
    @staticmethod
    def create_engine(config: DatabaseConfig, **kwargs):
        from sqlalchemy import create_engine
        url = config.get_connection_url()
        return create_engine(url, **kwargs)