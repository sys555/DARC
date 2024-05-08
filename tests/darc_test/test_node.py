import pytest
from unittest.mock import Mock, MagicMock, patch
from darc.darc.node import Node, message_handler
from darc.darc.message import Message

# Initialize the Node class and test its constructor
def test_node_initialization():
    node = Node()
    assert isinstance(node.handlers, dict)
    assert 'Init' in node.handlers
    assert 'Data_Process' in node.handlers

# Test the message handler registration decorator
def test_message_handler_decorator():
    @message_handler(['Test'])
    def test_func():
        return "Test Passed"
    
    assert hasattr(test_func, '_message_names')
    assert test_func._message_names == ['Test']

# Test the process method with registered handler
def test_process_with_registered_handler():
    node = Node()
    message = Mock(message_name='Init', content='Configuration')
    response = node.process(message)
    assert response == 'Initialized with Configuration'

# Test the process method with no registered handler
def test_process_with_no_handler():
    node = Node()
    message = Mock(message_name='NonExistent', content='None')
    response = node.process(message)
    assert response == 'No handler for NonExistent'

# # Test the gather function for partial and complete message collection
# def test_gather_function():
#     node = Node()
#     node._prefix = {'Test_Gather': ['Init']}
#     node.memory = []
    
#     # Message not yet complete
#     message_partial = Mock(task_id=1, message_name='Test_Gather', content='Part 1')
#     node.gather(message_partial)
#     assert len(node.memory) == 1
#     assert node.memory[0].content == 'Part 1'
    
#     # Completing the message
#     message_complete = Mock(task_id=1, message_name='Init', content='Part 2')
#     with patch.object(Node, 'handle_message', return_value='Handled') as mocked_method:
#         node.gather(message_complete)
#         mocked_method.assert_called_once_with(['Part 2', 'Part 1'], 'Test_Gather')

# Test pre_process function
def test_pre_process():
    node = Node()
    node.gather = Mock()
    message = Mock()
    node.pre_process(message)
    node.gather.assert_called_once_with(message)
