import pytest
from darc.ain.python.memory import Mem
import logging

@pytest.fixture
def mem():
    return Mem()

def test_add_memory(mem):
    result = mem.add("I like rice.", user_id="alice", metadata={"category": "hobby"})
    assert result is not None
    assert result["message"] is "ok"

@pytest.mark.skip("dont know memory_id")
def test_update_memory(mem):
    result = mem.add("I like rice.", user_id="alice", metadata={"category": "hobby"})
    # dont know memory_id
    memory_id = result["id"]
    updated_result = mem.update(memory_id=memory_id, new_value="I love rice.")
    assert updated_result is not None
    assert "id" in updated_result
    assert updated_result["id"] == memory_id

def test_search_memory(mem):
    # mem.add("I like rice.", user_id="alice", metadata={"category": "hobby"})
    related_memories = mem.search(query="What are Alice's hobbies?", user_id="alice")
    assert isinstance(related_memories, list)
    assert len(related_memories) > 0

def test_get_all_memories(mem):
    # mem.add("I like rice.", user_id="alice", metadata={"category": "hobby"})
    all_memories = mem.get_all()
    # [
    #     {
    #         'created_at': '2024-09-13T02:36:12.528605-07:00',
    #         'hash': 'ab6c60a349de6ffbe05dc35169c5e6f2',
    #         'id': '077ab88d-16be-46ee-bd41-87b6c7210d25',
    #         'memory': 'Likes rice',
    #         ...
    #     }
    # ]
    
    assert isinstance(all_memories, list)
    assert len(all_memories) > 0
