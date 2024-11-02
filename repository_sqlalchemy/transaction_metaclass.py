from functools import wraps
from typing import Any, Callable, Type, Dict, Tuple

from repository_sqlalchemy.transaction_management import transactional

class TransactionalMetaclass(type):
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
            "update",  # Added "update" to the list of transactional prefixes
            "delete",
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
        # Check if this is a subclass of BaseRepository
        if bases and any(base.__name__ == 'BaseRepository' for base in bases):
            # Get the type parameter passed to the child class
            if hasattr(new_class, '__orig_bases__'):
                model_type = new_class.__orig_bases__[0].__args__[0]

                # Set the model attribute if it's not already defined
                if not hasattr(new_class, 'model') or new_class.model is None:
                    new_class.model = model_type