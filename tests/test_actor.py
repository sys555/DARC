import pytest
from unittest.mock import Mock, patch, MagicMock
from darc.node import Node
from darc.actor import AbstractActor
from darc.message import Message
import logging


class Actor(AbstractActor):
    def __init__(self, name, addr):
        super().__init__()
        self.name = name
        self.addr = addr


@pytest.fixture
def alice_and_bob():
    # Start Alice and Bob actors
    alice = Actor.start("Alice", "100")
    bob = Actor.start("Bob", "200")

    alice.proxy().address_book = {"Bob": "200"}
    alice.proxy().instance = {"200": bob}
    logging.info(alice.proxy().address_book)
    bob.proxy().address_book = {"Alice": "100"}
    bob.proxy().instance = {"100": alice}

    # Return proxies for communication testing
    yield alice.proxy(), bob.proxy()

    alice.stop()
    bob.stop()


class TestActorCommunication:
    ## 通过 send 启动通信，通过验证属性中的 received_messages 消息数量，验证 alice 和 bob 间的通信逻辑可行
    def test_actors_can_communicate(self, alice_and_bob):
        alice, bob = alice_and_bob
        # Create messages
        message_to_bob = Message(
            message_name="test_msg", to_agent="Bob", content="Hello, Bob!"
        )
        message_to_alice = Message(
            message_name="test_msg", to_agent="Alice", content="Hello, Alice!"
        )

        # Send messages
        alice.send(message_to_bob)
        bob.send(message_to_alice)

        # Since messages are sent asynchronously, we might need to wait for them to be processed
        # This is a simple but not always reliable way to wait for messages to be processed
        import time

        time.sleep(2)

        # # # Verify that each actor received the correct message
        assert len(alice.message_box.get()) == 1
        assert alice.message_box.get()[0] == message_to_alice
        assert len(bob.message_box.get()) == 1
        assert bob.message_box.get()[0] == message_to_bob
