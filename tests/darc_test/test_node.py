import pytest
from unittest.mock import Mock
from darc.darc.node import Node

@pytest.fixture
def node():
    return Node()

@pytest.fixture
def message():
    def _message(content, name):
        return Mock(content=content, message_name=name)
    return _message

def test_handle_init(node, message):
    msg = message("Hello, World!", "Init")
    assert node.process_message(msg) == "Initialized with Hello, World!"

def test_handle_data_processing(node, message):
    msg = message("Hello, Data!", "Data_Process")
    assert node.process_message(msg) == "Data processed: Hello, Data!"

def test_no_handler(node, message):
    msg = message("Hello, Unknown!", "Unknown")
    assert node.process_message(msg) == "No handler for Unknown"
