from sqlalchemy import Column, Integer, String
from repository_sqlalchemy.base_repository import Base, BaseRepository


class TestModel(Base):
    __tablename__ = "test_model"
    __test__ = False
    id = Column(Integer, primary_key=True)
    name = Column(String)

class TestRepository(BaseRepository[TestModel]):
    pass
