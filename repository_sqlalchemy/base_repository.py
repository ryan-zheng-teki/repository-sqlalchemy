import logging
from typing import Any, Dict, Generic, List, TypeVar, Optional
from sqlalchemy.orm import Session, declarative_base

from repository_sqlalchemy.metaclasses import SingletonRepositoryMetaclass
from repository_sqlalchemy.session_management import session_context_var

logger = logging.getLogger(__name__)

Base = declarative_base()

# Define a type variable for the model
ModelType = TypeVar("ModelType")

class BaseRepository(Generic[ModelType], metaclass=SingletonRepositoryMetaclass):
    # Subclasses should set this to the concrete model class
    model = None

    @property
    def session(self) -> Session:
        return session_context_var.get()

    def create(self, obj: ModelType) -> ModelType:
        """Insert a new row and return the persisted object."""
        self.session.add(obj)
        self.session.flush()
        self.session.refresh(obj)
        return obj

    def update(self, instance: ModelType, data: Optional[Dict[str, Any]] = None) -> ModelType:
        """
        Update an existing object and persist.
        If the instance is detached, merge it into the current session first.
        If 'data' is provided, it performs a partial update on the instance's fields.
        If 'data' is None, it assumes the instance is already updated and merges its state.
        """
        # Re-attach detached instances to ensure they are managed by the current session
        instance = self.session.merge(instance)

        if data:
            for key, value in data.items():
                if hasattr(instance, key):
                    setattr(instance, key, value)
                else:
                    raise AttributeError(f"{type(instance).__name__} has no attribute '{key}'")

        self.session.flush()
        return instance

    def bulk_create(self, objects: List[ModelType]) -> List[ModelType]:
        """Insert multiple new rows in bulk."""
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
        return (
            self.session.query(self.model)
            .order_by(self.model.id)
            .offset(offset)
            .limit(limit)
            .all()
        )

    def delete(self, obj: ModelType) -> None:
        """Delete a row from the database."""
        # Merge to reattach if detached
        obj = self.session.merge(obj)
        self.session.delete(obj)
        self.session.flush()
