from contextlib import suppress

import pytest

from repository_sqlalchemy.transaction_management import transaction
from tests.test_model import TestModel, TestRepository

name_test_obj = "Test Object"
name_outer_transaction = "Outer Transaction"
name_inner_transaction = "Inner Transaction"
name_before_savepoint = "Before Savepoint"
name_at_savepoint = "At Savepoint"
name_after_savepoint = "After Savepoint"


def test_singleton_behavior():
    # Create multiple instances
    repo1 = TestRepository()
    repo2 = TestRepository()
    repo3 = TestRepository()

    # Verify they are the same instance
    assert repo1 is repo2
    assert repo2 is repo3
    assert repo1 is repo3


def test_singleton_state_persistence(test_repository):
    # Test that state is preserved across instances
    with transaction():
        obj = test_repository.create(TestModel(name=name_test_obj))

        # Create new "instance" - should be same object
        another_repo = TestRepository()
        found_obj = another_repo.find_by_id(obj.id)

        assert found_obj is not None
        assert found_obj.id == obj.id
        assert found_obj.name == name_test_obj


def test_create(test_repository):
    with transaction():
        obj = test_repository.create(TestModel(name=name_test_obj))
        assert obj.id is not None
        assert obj.name == name_test_obj


def test_find_by_id(test_repository):
    with transaction():
        obj = test_repository.create(TestModel(name=name_test_obj))
        found_obj = test_repository.find_by_id(obj.id)
        assert found_obj is not None
        assert found_obj.id == obj.id
        assert found_obj.name == name_test_obj


def test_find_all(test_repository):
    with transaction():
        objs = test_repository.find_all()
        assert len(objs) == 3


def test_delete(test_repository):
    with transaction():
        obj = test_repository.create(TestModel(name=name_test_obj))
        test_repository.delete(obj)
        found_obj = test_repository.find_by_id(obj.id)
        assert found_obj is None


def test_get_count(test_repository):
    with transaction():
        test_repository.create(TestModel(name="Test Object 1"))
        test_repository.create(TestModel(name="Test Object 2"))
        count = test_repository.get_count()
        assert count == 5


def test_find_page(test_repository):
    with transaction():
        for i in range(20):
            test_repository.create(TestModel(name=f"Test Object {i+1}"))

        page = test_repository.find_page(offset=5, limit=5)
        assert len(page) == 5
        assert page[0].name == "Test Object 1"
        assert page[-1].name == "Test Object 5"


@pytest.mark.asyncio
async def test_transaction_decorator(test_repository):
    @transaction()
    def create_test_object():
        return test_repository.create(TestModel(name="Transactional Test"))

    obj = create_test_object()
    assert obj.id is not None
    assert obj.name == "Transactional Test"

    found_obj = test_repository.find_by_id(obj.id)
    assert found_obj is not None
    assert found_obj.name == "Transactional Test"


def test_nested_transaction_commit(test_repository):
    @transaction()
    def outer_transaction():
        obj1 = test_repository.create(TestModel(name=name_outer_transaction))

        @transaction()
        def inner_transaction():
            obj2 = test_repository.create(TestModel(name=name_inner_transaction))
            return obj2

        inner_obj = inner_transaction()
        return obj1, inner_obj

    outer_obj, inner_obj = outer_transaction()

    assert outer_obj.id is not None
    assert inner_obj.id is not None

    found_outer = test_repository.find_by_id(outer_obj.id)
    found_inner = test_repository.find_by_id(inner_obj.id)

    assert found_outer is not None
    assert found_outer.name == name_outer_transaction
    assert found_inner is not None
    assert found_inner.name == name_inner_transaction


def test_nested_transaction_rollback(test_repository):
    @transaction()
    def outer_transaction():
        obj1 = test_repository.create(TestModel(name=name_outer_transaction))

        @transaction()
        def inner_transaction():
            test_repository.create(TestModel(name=name_inner_transaction))
            raise ValueError("Simulating an error")

        with suppress(ValueError):
            inner_transaction()

        return obj1

    outer_obj = outer_transaction()
    assert outer_obj.id is not None
    found_outer = test_repository.find_by_id(outer_obj.id)
    assert found_outer is not None
    assert found_outer.name == name_outer_transaction


def test_savepoint(test_repository):
    @transaction()
    def complex_transaction():
        obj1 = test_repository.create(TestModel(name=name_before_savepoint))

        try:
            with transaction():  # This creates a savepoint
                test_repository.create(TestModel(name=name_at_savepoint))
                raise ValueError("Simulating an error")
        except ValueError:
            pass  # The savepoint will be rolled back

        obj3 = test_repository.create(TestModel(name=name_after_savepoint))
        return obj1, obj3

    before_obj, after_obj = complex_transaction()

    assert before_obj.id is not None
    assert after_obj.id is not None
    assert before_obj.name == name_before_savepoint
    assert after_obj.name == name_after_savepoint


def test_savepoint_commit(test_repository):
    @transaction()
    def complex_transaction():
        obj1 = test_repository.create(TestModel(name=name_before_savepoint))

        with transaction():  # This creates a savepoint
            obj2 = test_repository.create(TestModel(name=name_at_savepoint))

        obj3 = test_repository.create(TestModel(name=name_after_savepoint))
        return obj1, obj2, obj3

    before_obj, at_obj, after_obj = complex_transaction()

    assert before_obj.id is not None
    assert at_obj.id is not None
    assert after_obj.id is not None
    assert before_obj.name == name_before_savepoint
    assert at_obj.name == name_at_savepoint
    assert after_obj.name == name_after_savepoint
