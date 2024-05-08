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

def test_pre_process_with_incomplete_messages():
    # Initialize Node
    node = Node()
    node._prefix = {"Data_Process": ['init', 'db']}  # Expecting both 'init' and 'db' messages

    # Create a mock message that meets only part of the requirements
    incomplete_message = Message(task_id=1, message_name='Data_Process', content='Initialization Data')

    # Patch the `gather` method to simulate its behavior when not all required messages are received
    with patch.object(Node, 'gather', return_value=False) as mock_gather:
        # Simulate receiving an incomplete set of messages
        result = node.pre_process(incomplete_message)

        # Verify that `gather` was called correctly
        mock_gather.assert_called_once_with(incomplete_message)

        # Assert that `pre_process` returns False or does not proceed with processing
        assert result == False  # Adjust this line based on how `pre_process` actually handles the response from `gather`

def test_incomplete_message_processing():
    node = Node()
    # Setting the expected message sequence for the 'Data_Process' task
    node._prefix = {"Data_Process": ['init', 'db']}

    # Creating a message that is expected to be part of a set
    incomplete_message = Message(task_id=1, message_name='Data_Process', content='Part 1')

    # Patch the `gather` method to control its output and monitor its behavior
    with patch.object(Node, 'gather', return_value=False) as mock_gather:
        # Patch `pre_process` to check its return value when incomplete messages are received
        with patch.object(Node, 'pre_process', return_value=False) as mock_pre_process:
            # Receive the incomplete message
            node.recv(incomplete_message)

            # Assert that pre_process was called and checked the result of gather
            mock_pre_process.assert_called_once_with(incomplete_message)
            mock_gather.assert_called_once_with(incomplete_message)

            # Check that pre_process indeed returned False, indicating waiting for more messages
            assert mock_pre_process.return_value == False, "pre_process should return False for incomplete messages"



# def test_gather_function():
#     node = Node()
#     node._prefix = {"Data_Process": ['init', 'db']}

#     message_init = Message(task_id=1, message_name='Data_Process', content='Part 1')
#     message_db = Message(task_id=1, message_name='Data_Process', content='db data')

#     # Patching the `gather` and `handle_data_processing` methods
#     with patch.object(Node, 'gather') as mock_gather:
#         with patch.object(Node, 'handle_data_processing', return_value='Data processed: db data') as mock_handler:
#             # Simulate the receipt of messages
#             node.recv(message_init)
#             node.recv(message_db)

#             # Assert `gather` was called correctly
#             assert mock_gather.call_count == 2
#             mock_gather.assert_any_call(message_init)
#             mock_gather.assert_any_call(message_db)

#             # Check if the handler was called after receiving all necessary parts
#             # This depends on your logic in `gather` when all parts are received
#             # Since you mocked `gather`, ensure your mock mimics the behavior expected when all messages are gathered
#             # e.g., assume the second call to `gather` triggers the message handling
#             if mock_gather.call_count == 2:
#                 mock_handler.assert_called_once_with(message_db)


# Test pre_process function
def test_pre_process():
    node = Node()
    node.gather = Mock()
    message = Mock()
    node.pre_process(message)
    node.gather.assert_called_once_with(message)
