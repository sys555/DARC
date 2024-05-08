import pytest
from unittest.mock import Mock, patch, MagicMock
from darc.darc.node import Node
from darc.darc.actor import AbstractActor
from darc.darc.message import Message
import logging

class Actor(AbstractActor):
    def __init__(self, name):
        super().__init__()
        self.name = name
        # 测试跟踪
        self.received_messages = []  # Add this to track received messages
        
    def register_actor(self, actor):
        # Register new actor to the address book and instance dictionary
        self._address_book[actor.name] = actor.actor_ref.actor_urn  # Assuming URN or some identifier
        self._instance[actor.actor_ref.actor_urn] = actor.actor_ref

    def on_receive(self, message):
        # 测试跟踪
        self.received_messages.append(message)  # Log each received message
        if message.to_agent in self._address_book:
            self.send(self._instance[self._address_book[message.to_agent]], message)
        else:
            ...

class TestActorCommunication:
    @pytest.fixture
    def alice_and_bob(self):
        # Start Alice and Bob actors
        alice = Actor.start("Alice")
        bob = Actor.start("Alice")
        # Alice registers Bob
        alice.proxy().register_actor(bob)
        # Bob registers Alice
        bob.proxy().register_actor(alice)
        
        # Return proxies for communication testing
        yield alice.proxy(), bob.proxy()
    
    ## 通过 send 启动通信，通过验证属性中的 received_messages 消息数量，验证 alice 和 bob 间的通信逻辑可行
    def test_actors_can_communicate(self, alice_and_bob):
        alice, bob = alice_and_bob

        # Create messages
        message_to_bob =  Message(message_name = "test_msg", to_agent = 'Bob', content = 'Hello, Bob!')
        message_to_alice = Message(message_name = "test_msg", to_agent = 'Alice', content = 'Hello, Alice!')

        # Send messages
        alice.send(bob.actor_ref, message_to_bob)
        bob.send(alice.actor_ref, message_to_alice)

        # Since messages are sent asynchronously, we might need to wait for them to be processed
        # This is a simple but not always reliable way to wait for messages to be processed
        import time
        time.sleep(2)

        # # Verify that each actor received the correct message
        assert len(alice.received_messages.get()) == 1
        assert alice.received_messages.get()[0] == message_to_alice
        assert len(bob.received_messages.get()) == 1
        assert bob.received_messages.get()[0] == message_to_bob