from functools import wraps
from typing import Any, Callable, Type, Dict, Tuple
import threading

from repository_sqlalchemy.transaction_management import transactional

class SingletonMeta(type):
    """
    Thread-safe implementation of the Singleton pattern using metaclass.
    """
    _instances = {}
    _lock = threading.Lock()

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            with cls._lock:
                # Double-checked locking
                if cls not in cls._instances:
                    cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]

class TransactionalMetaclass(type):
    """
    Metaclass that automatically applies transactional decorator to repository methods.
    """
    def __new__(cls, name: str, bases: tuple, attrs: Dict[str, Any]) -> Type:
        # Existing transactional logic
        cls.apply_transactional_wrapper(attrs)

        # Create the new class
        new_class = super().__new__(cls, name, bases, attrs)

        # Set the model attribute
        cls.set_model_attribute(new_class, bases)

        return new_class

    @classmethod
    def apply_transactional_wrapper(cls, attrs: Dict[str, Any]) -> None:
        transactional_prefixes = (
            "find",
            "get",
            "create",
            "update",
            "delete",
            "upsert",
        )

        for attr_name, attr_value in attrs.items():
            if callable(attr_value) and any(
                attr_name.startswith(prefix) for prefix in transactional_prefixes
            ):
                attrs[attr_name] = cls.add_transactional(attr_value)

    @staticmethod
    def add_transactional(method: Callable) -> Callable:
        if hasattr(method, "_transactional"):
            return method

        @wraps(method)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            return transactional(method)(*args, **kwargs)

        wrapper._transactional = True
        return wrapper

    @staticmethod
    def set_model_attribute(new_class: Type, bases: Tuple[Type, ...]) -> None:
        if bases and any(base.__name__ == 'BaseRepository' for base in bases):
            if hasattr(new_class, '__orig_bases__'):
                model_type = new_class.__orig_bases__[0].__args__[0]
                if not hasattr(new_class, 'model') or new_class.model is None:
                    new_class.model = model_type

class SingletonRepositoryMetaclass(TransactionalMetaclass, SingletonMeta):
    """
    Combined metaclass that applies both repository functionality and singleton pattern.
    This ensures that the repository is a singleton and retains repository behaviors.
    """
    pass
