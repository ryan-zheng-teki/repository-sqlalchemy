import pytest
from repository_sqlalchemy.transaction_management import transaction
from tests.test_model import TestModel, TestRepository

def test_inherited_update_runs_transaction(test_repository):
    # Create an object outside explicit transaction
    repo = TestRepository()
    obj = repo.create(TestModel(name="Outside Transaction"))
    assert obj.id is not None

    # Now update outside explicit transaction; should still commit
    updated = repo.update(obj, {"name": "Updated Name"})
    assert updated.name == "Updated Name"

    # Reload from database in a new transaction
    with transaction():
        found = repo.find_by_id(obj.id)
        assert found.name == "Updated Name"

def test_inherited_delete_runs_transaction(test_repository):
    repo = TestRepository()
    obj = repo.create(TestModel(name="ToDelete"))
    assert obj.id is not None

    # Delete outside explicit transaction
    repo.delete(obj)

    # Attempt to find inside a transaction
    with transaction():
        found = repo.find_by_id(obj.id)
        assert found is None
