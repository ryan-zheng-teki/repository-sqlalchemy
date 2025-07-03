from sqlalchemy import Column, String

from repository_sqlalchemy.base_repository import BaseModel, BaseRepository


class TestModel(BaseModel):
    __tablename__ = "test_model"

    name = Column(String)


class TestRepository(BaseRepository[TestModel]): ...
