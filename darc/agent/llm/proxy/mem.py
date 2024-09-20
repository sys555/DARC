import os
from mem0 import Memory

m = Memory()
# 1. Add: Store a memory from any unstructured text
result = m.add("I like badminton.", user_id="alice", metadata={"category": "hobbi"})

# Created memory --> 'Improving her tennis skills.' and 'Looking for online suggestions.'
# 3. Search: search related memories
related_memories = m.search(query="What are Alice's hobbies?", user_id="alice")
print(related_memories)

# Retrieved memory --> 'Likes to play tennis on weekends'
# 4. Get all memories
all_memories = m.get_all()
# memory_id = all_memories["memories"][0] ["id"] # get a memory_id
print(all_memories)

# All memory items --> 'Likes to play tennis on weekends.' and 'Looking for online suggestions.'
# 5. Get memory history for a particular memory_id
# history = m.history(memory_id=<memory_id_1>)

# Logs corresponding to memory_id_1 --> {'prev_value': 'Working on improving tennis skills and interested in online courses for tennis.', 'new_value': 'Likes to play tennis on weekends' }