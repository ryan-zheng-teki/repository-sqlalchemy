import logging
from contextlib import contextmanager
from functools import wraps

from repository_sqlalchemy.session_management import get_session, session_context_var

logger = logging.getLogger(__name__)

@contextmanager
def transaction():
    session = session_context_var.get()
    if session is None:
        session = get_session()
        session_context_var.set(session)

    # Check if there's already an active transaction
    is_nested = session.in_transaction()

    try:
        if is_nested:
            savepoint = session.begin_nested()
            logger.debug("Starting nested transaction")
            yield savepoint
        else:
            # Start a new transaction
            session.begin()
            logger.debug("Starting new transaction")
            yield session

        if is_nested:
            savepoint.commit()
            logger.debug("Savepoint committed")
        else:
            session.commit()
            session.close()
            logger.debug("Transaction committed")
    except Exception as e:
        logger.exception(
            "Exception occurred during transaction, rolling back", exc_info=e
        )
        if is_nested:
            savepoint.rollback() 
            logger.debug("Savepoint rolled back")
        else:
            session.rollback()
            session.close()
            logger.debug("Transaction rolled back")
        raise
    finally:
        if not is_nested:
            session_context_var.set(None)

def transactional(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        with transaction():
            return func(*args, **kwargs)

    return wrapper