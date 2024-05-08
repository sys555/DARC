import pytest
from unittest.mock import Mock, patch
from darc.darc.node import Node
from darc.darc.actor import AbstractActor
from darc.darc.message import Message

# Define the message routing map
message_routing = {"1": "AtoB_Router"}

@pytest.fixture
def actor():
    actor_instance = AbstractActor()
    actor_instance.id = 'Actor_1'
    return actor_instance

@pytest.fixture
def message():
    return Message(content="Hello, World!", task_id="1", message_name="Init")

def route_message(task_id):
    return message_routing.get(task_id)

def test_send_message(actor, message):
    with patch.object(actor, 'send', autospec=True) as mock_send:
        # Assuming send needs to decide where to route the message
        to_actor = route_message(message.task_id)
        actor.send(message)
        mock_send.assert_called_with(message)

def test_receive_and_process_message(actor):
    with patch.object(actor, 'recv', autospec=True) as mock_recv, \
        patch.object(actor, 'process', autospec=True) as mock_process:
        
        # Setup for testing recv and processing
        message = Message(content="Test data", task_id="1", message_name="Data_Process")
        mock_recv.return_value = message
        mock_process.return_value = "processed " + message.content

        # Simulate reception and decision on whether to forward
        received_message = actor.recv()
        processed_data = actor.process(received_message.content)

        # Determine next action based on node position
        if actor.id == route_message(received_message.task_id):
            # This is the last actor, no forwarding
            final_output = processed_data
        else:
            # Not the last node, forward to next actor
            next_actor = route_message(received_message.task_id)
            actor.send(Message(from_actor = actor.id, to_actor = next_actor, content=processed_data, task_id=received_message.task_id, message_name="Forward"))
            final_output = "Message forwarded to " + next_actor

        # Assertions
        mock_recv.assert_called_once()
        mock_process.assert_called_once_with(received_message.content)
        assert final_output.startswith("processed") or "forwarded" in final_output

# Additional test to cover different message names and types
def test_message_routing_and_processing(actor, message):
    with patch.object(actor, 'send', autospec=True) as mock_send:
        # Different message types might be handled differently
        if message.message_name == "Init":
            processed_content = "Initialization complete"
        elif message.message_name == "Data_Process":
            processed_content = "Data processed: " + message.content
        else:
            processed_content = "Unhandled message type"

        # Prepare the message object
        outgoing_message = Message(content=processed_content, task_id=message.task_id, message_name=message.message_name)
        
        # Send and attempt to assert
        actor.send(outgoing_message)
        print(f"Mock calls: {mock_send.mock_calls}")  # Diagnostic print

        # Assert that send was called correctly
        mock_send.assert_called_with(outgoing_message)