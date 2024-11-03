import pytest
from sqlalchemy.exc import IntegrityError
from repository_sqlalchemy.transaction_management import transaction
from tests.test_model import TestModel, TestRepository



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
        obj = test_repository.create(TestModel(name="Test Object"))
        
        # Create new "instance" - should be same object
        another_repo = TestRepository()
        found_obj = another_repo.find_by_id(obj.id)
        
        assert found_obj is not None
        assert found_obj.id == obj.id
        assert found_obj.name == "Test Object"

def test_create(test_repository):
    with transaction():
        obj = test_repository.create(TestModel(name="Test Object"))
        assert obj.id is not None
        assert obj.name == "Test Object"

def test_find_by_id(test_repository):
    with transaction():
        obj = test_repository.create(TestModel(name="Test Object"))
        found_obj = test_repository.find_by_id(obj.id)
        assert found_obj is not None
        assert found_obj.id == obj.id
        assert found_obj.name == "Test Object"

def test_find_all(test_repository):
    with transaction():
        test_repository.create(TestModel(name="Test Object 1"))
        test_repository.create(TestModel(name="Test Object 2"))
        all_objects = test_repository.find_all()
        assert len(all_objects) == 2
        assert all_objects[0].name == "Test Object 1"
        assert all_objects[1].name == "Test Object 2"

def test_delete(test_repository):
    with transaction():
        obj = test_repository.create(TestModel(name="Test Object"))
        test_repository.delete(obj)
        found_obj = test_repository.find_by_id(obj.id)
        assert found_obj is None

def test_get_count(test_repository):
    with transaction():
        test_repository.create(TestModel(name="Test Object 1"))
        test_repository.create(TestModel(name="Test Object 2"))
        count = test_repository.get_count()
        assert count == 2

def test_find_page(test_repository):
    with transaction():
        for i in range(20):
            test_repository.create(TestModel(name=f"Test Object {i+1}"))
        
        page = test_repository.find_page(offset=5, limit=5)
        assert len(page) == 5
        assert page[0].name == "Test Object 6"
        assert page[-1].name == "Test Object 10"

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
        obj1 = test_repository.create(TestModel(name="Outer Transaction"))
        
        @transaction()
        def inner_transaction():
            obj2 = test_repository.create(TestModel(name="Inner Transaction"))
            return obj2
        
        inner_obj = inner_transaction()
        return obj1, inner_obj

    outer_obj, inner_obj = outer_transaction()
    
    assert outer_obj.id is not None
    assert inner_obj.id is not None
    
    found_outer = test_repository.find_by_id(outer_obj.id)
    found_inner = test_repository.find_by_id(inner_obj.id)
    
    assert found_outer is not None
    assert found_outer.name == "Outer Transaction"
    assert found_inner is not None
    assert found_inner.name == "Inner Transaction"

def test_nested_transaction_rollback(test_repository):
    @transaction()
    def outer_transaction():
        obj1 = test_repository.create(TestModel(name="Outer Transaction"))
        
        @transaction()
        def inner_transaction():
            obj2 = test_repository.create(TestModel(name="Inner Transaction"))
            raise ValueError("Simulating an error")
        
        try:
            inner_transaction()
        except ValueError:
            pass
        
        return obj1

    outer_obj = outer_transaction()
    
    assert outer_obj.id is not None
    
    found_outer = test_repository.find_by_id(outer_obj.id)
    assert found_outer is not None
    assert found_outer.name == "Outer Transaction"
    
    all_objects = test_repository.find_all()
    assert len(all_objects) == 1
    assert all_objects[0].name == "Outer Transaction"

def test_savepoint(test_repository):
    @transaction()
    def complex_transaction():
        obj1 = test_repository.create(TestModel(name="Before Savepoint"))
        
        try:
            with transaction():  # This creates a savepoint
                test_repository.create(TestModel(name="At Savepoint"))
                raise ValueError("Simulating an error")
        except ValueError:
            pass  # The savepoint will be rolled back
        
        obj3 = test_repository.create(TestModel(name="After Savepoint"))
        return obj1, obj3

    before_obj, after_obj = complex_transaction()
    
    assert before_obj.id is not None
    assert after_obj.id is not None
    
    all_objects = test_repository.find_all()
    assert len(all_objects) == 2
    assert all_objects[0].name == "Before Savepoint"
    assert all_objects[1].name == "After Savepoint"

def test_savepoint_commit(test_repository):
    @transaction()
    def complex_transaction():
        obj1 = test_repository.create(TestModel(name="Before Savepoint"))
        
        with transaction():  # This creates a savepoint
            obj2 = test_repository.create(TestModel(name="At Savepoint"))
        
        obj3 = test_repository.create(TestModel(name="After Savepoint"))
        return obj1, obj2, obj3

    before_obj, at_obj, after_obj = complex_transaction()
    
    assert before_obj.id is not None
    assert at_obj.id is not None
    assert after_obj.id is not None
    
    all_objects = test_repository.find_all()
    assert len(all_objects) == 3
    assert all_objects[0].name == "Before Savepoint"
    assert all_objects[1].name == "At Savepoint"
    assert all_objects[2].name == "After Savepoint"