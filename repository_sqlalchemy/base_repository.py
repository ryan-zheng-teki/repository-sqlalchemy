import logging
from typing import (
    Any,
    Dict,
    Generic,
    List,
    TypeVar,
)
from sqlalchemy.orm import (
    Session,
)
from sqlalchemy.ext.declarative import declarative_base

from repository_sqlalchemy.transaction_metaclass import TransactionalMetaclass
from repository_sqlalchemy.session_management import session_context_var

logger = logging.getLogger(__name__)

Base = declarative_base()

# Define a type variable for the model
ModelType = TypeVar("ModelType")


class BaseRepository(Generic[ModelType], metaclass=TransactionalMetaclass):
    # Subclasses should set this to the concrete model class
    model = None

    @property
    def session(self) -> Session:
        return session_context_var.get()

    def create(self, obj: ModelType) -> ModelType:
        self.session.add(obj)
        self.session.flush()
        self.session.refresh(obj)
        return obj
    
    def update(self, instance: ModelType, data: Dict[str, Any]) -> ModelType:
            """
            Update an existing model instance with the provided data.

            :param instance: The model instance to update.
            :param data: A dictionary of fields to update and their new values.
            :return: The updated model instance.
            """
            for key, value in data.items():
                if hasattr(instance, key):
                    setattr(instance, key, value)
                else:
                    raise AttributeError(f"{type(instance).__name__} has no attribute '{key}'")

            self.session.flush()
            return instance

    def bulk_create(self, objects: List[ModelType]) -> List[ModelType]:
        self.session.bulk_save_objects(objects)
        self.session.flush()
        return objects

    def expunge_all(self):
        """Explicitly remove all objects from the current session."""
        try:
            self.session.expunge_all()
            logger.info(f"All objects expunged from session {id(self.session)}")
        except Exception as e:
            logger.error(f"Error during expunge_all: {str(e)}")
            raise

    def find_by_id(self, id: int) -> ModelType:
        return self.session.query(self.model).filter_by(id=id).first()

    def find_all(self) -> List[ModelType]:
        return self.session.query(self.model).all()

    def get_count(self) -> int:
        return self.session.query(self.model).count()

    def find_page(self, offset: int = 0, limit: int = 10) -> List[ModelType]:
        """Generic pagination method applicable to any model. offset-limit
        based.

        :param offset: The number of records to skip.
        :param limit: The maximum number of items to return.
        :return: A list of model instances.
        """
        return (
            self.session.query(self.model)
            .order_by(self.model.id)
            .offset(offset)
            .limit(limit)
            .all()
        )

    def delete(self, obj: ModelType) -> None:
        self.session.delete(obj)
        self.session.flush()