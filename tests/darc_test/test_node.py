import pytest
from unittest.mock import Mock, MagicMock
from darc.darc.node import Node, message_handler
from darc.darc.message import Message

# Define a sample Message class if it's not already defined
class Message:
    def __init__(self, message_name, content, task_id=None):
        self.message_name = message_name
        self.content = content
        self.task_id = task_id

# Test Node initialization
def test_node_initialization():
    node = Node()
    assert 'Init' in node.handlers
    assert 'Data_Process' in node.handlers
    assert callable(node.handlers['Init'])
    assert callable(node.handlers['Data_Process'])

# Test processing messages with registered handlers
def test_process_message_with_handler():
    node = Node()
    message = Message(message_name='Init', content='Test')
    response = node.process_message(message)
    assert response == "Initialized with Test"

# Test processing messages without a registered handler
def test_process_message_without_handler():
    node = Node()
    message = Message(message_name='Unknown', content='Test')
    response = node.process_message(message)
    assert response == "No handler for Unknown"

# Test the gather method functionality
@pytest.mark.parametrize("messages, expected_response", [
    # Case with all required messages received
    ([('Init', 'init data', 'task1'), ('Data_Process', 'data1', 'task1')], "Handled Data_Process with contents: data1"),
    # Case with incomplete message set
    ([('Data_Process', 'data1', 'task1')], "Waiting for more messages")
])
def test_gather(messages, expected_response):
    node = Node()
    # Define what messages are needed before processing can happen
    node._prefix = {'Data_Process': ['Init']}
    node.handle_message = MagicMock(return_value="Handled Data_Process with contents: data1")
    
    for msg in messages:
        message = Message(message_name=msg[0], content=msg[1], task_id=msg[2])
        response = node.gather(message)
    
    if expected_response.startswith("Handled"):
        # Try processing after all required messages are supposedly gathered
        final_message = Message(message_name=messages[-1][0], content=messages[-1][1], task_id=messages[-1][2])
        response = node.recv(final_message)
        assert response == expected_response
    else:
        # Check if the last message is still waiting in memory
        assert node.memory[-1].content == messages[-1][1]
        assert response == expected_response
