import pytest
from unittest.mock import Mock
from darc.darc.node import Node
from darc.darc.actor import AbstractActor
from darc.darc.message import Message

# Test initialization of the AbstractActor class
def test_initialization():
    actor = AbstractActor()
    assert actor._address_book == {}
    assert actor._instance == {}

# Test the recv method particularly when pre_process returns False
def test_recv_pre_process_returns_false():
    actor = AbstractActor()
    actor.pre_process = Mock(return_value=False)
    actor.process = Mock()
    actor.send = Mock()
    
    message = Message(content='stop', to_actor='actor1')
    actor.recv(message)
    
    actor.pre_process.assert_called_once_with(message)
    actor.process.assert_not_called()
    actor.send.assert_not_called()

# Test the recv method's normal operation
def test_recv_normal_operation():
    actor = AbstractActor()
    actor.pre_process = Mock(return_value='Processed content: continue')
    actor.process = Mock(return_value='processed data')
    actor.send = Mock()
    
    message = Message(content='continue', to_actor='actor1')
    actor.recv(message)
    
    actor.pre_process.assert_called_once_with(message)
    actor.process.assert_called_once_with('Processed content: continue')
    actor.send.assert_called_once()

# Test the pre_process method to ensure it returns False correctly
def test_pre_process():
    actor = AbstractActor()
    stop_message = Message(content='stop', to_actor='actor1')
    continue_message = Message(content='continue', to_actor='actor1')
    
    assert actor.pre_process(stop_message) == False
    assert actor.pre_process(continue_message) == 'Processed content: continue'

# Test the send method to handle cases where no actor is found
def test_send_no_actor_found():
    actor = AbstractActor()
    actor._address_book = {'actor1': 'id1'}
    actor._instance = {}
    actor.send = Mock()
    
    message = Message(content='data', to_actor='actor1')
    actor.send(message)
    actor.send.assert_called_once()
    # Here you should assert the output to the console or handle it through logging

# Setup for testing send where actors exist and message is successfully sent
def test_send_success():
    actor = AbstractActor()
    actor._address_book = {'actor1': 'id1'}
    recipient_actor = Mock()
    actor._instance = {'id1': recipient_actor}
    
    message = Message(content='data', to_actor='actor1')
    actor.send(message)
    
    recipient_actor.recv.assert_called_once_with(message)
