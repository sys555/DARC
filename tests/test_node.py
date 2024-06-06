import unittest

from darc.router import Router
from darc.node_gate import NodeGate
from darc.multi_addr import MultiAddr
import uuid

from tests.test_base import Producer, Consumer, compare_messages

import copy

from darc.message import Message
import pytest

from loguru import logger


@pytest.fixture(scope="module")
def config():
    addr = MultiAddr("Producer:Consumer")
    router = Router.start(addr)

    producer_gate = NodeGate.start("Producer", MultiAddr("Producer"))
    consumer_gate = NodeGate.start("Consumer", MultiAddr("Consumer"))

    yield router.proxy(), producer_gate.proxy(), consumer_gate.proxy()

    router.stop()
    producer_gate.stop()
    consumer_gate.stop()


def test_handler(config):
    _, producer_gate, consumer_gate = config

    alice = producer_gate.spawn_new_actor(Producer, ("alice",)).get()
    bob = consumer_gate.spawn_new_actor(Consumer, ("bob",)).get()

    alice_to_bob_message = Message(
        message_name="Producer:Consumer",
        from_agent=alice.proxy().node_addr.get(),
        to_agent=bob.proxy().node_addr.get(),
        from_agent_type="RealNode",
        task_id=str(uuid.uuid4()),
    )

    alice.proxy().on_send(alice_to_bob_message)

    import time

    time.sleep(2)

    assert (
        alice.proxy().message_box.get()[1].task_id
        == alice_to_bob_message.task_id
    )

    alice.stop()
    bob.stop()
