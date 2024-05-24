import pytest

from unittest.mock import Mock, MagicMock, patch
from darc.darc.node import Node
from darc.darc.message import Message

import logging


class C(Node):
    @Node.process(["A:C", "B:C"])
    def handler_A_C_B_C(self, data: [str]) -> Message:
        result = f"C[A:C,B:C{data[:-1]}]"
        message = Message(message_name="C:A", content=result)
        target = []
        target.append(message)
        return target

    @Node.process(["A:C"])
    def handler_A_C(self, data: [str]) -> Message:
        result = f"C[A:C{data[:-1]}]"
        message = Message(message_name="C:B", content=result)
        target = []
        target.append(message)
        return target


@pytest.fixture
def config():
    a = Node.start(node_name="A_0", address="a_address")
    b = Node.start(node_name="B_0", address="b_address")
    c = C.start(node_name="C_0", address="c_address")

    a.proxy().link_node(c, "c_address")
    b.proxy().link_node(c, "c_address")
    c.proxy().link_node([a, b], ["a_address", "b_address"])

    yield a.proxy(), b.proxy(), c.proxy()

    a.stop()
    b.stop()
    c.stop()


def test_type_cross(config):
    # C : [["A:C", "B:C"],["A:C"]]
    # 期望消息流动顺序如下:
    # 1. A->C; 2. B->C and C->B; 3. C->A
    a, b, c = config

    a_to_c_message = Message(
        message_name="A:C",
        from_agent="a_address",
        to_agent="c_address",
        content="a_to_c_message",
    )
    b_to_c_message = Message(
        message_name="B:C",
        from_agent="b_address",
        to_agent="c_address",
        content="b_to_c_message",
    )

    c_to_a_message = Message(
        message_name="C:A",
        from_agent="c_address",
        to_agent="a_address",
        content="C[A:C,B:C['a_to_c_message', 'b_to_c_message']]",
    )
    c_to_b_message = Message(
        message_name="C:B",
        from_agent="c_address",
        to_agent="b_address",
        content="C[A:C['a_to_c_message']]",
    )

    # 1. a->c
    a.send(a_to_c_message, a_to_c_message.to_agent)

    import time

    time.sleep(1)

    # 2. c->b
    assert b.message_in_inbox(c_to_b_message).get() == True

    # 2. b->c
    b.send(b_to_c_message, b_to_c_message.to_agent)

    import time

    time.sleep(1)

    # 4. c->a
    assert a.message_in_inbox(c_to_a_message).get() == True


def test_type_cross_other_order(config):
    # C : [["A:C", "B:C"],["A:C"]]
    # 期望消息流动顺序如下:
    # 1. B->C; 2. A->C; 3. C->B and C->A
    a, b, c = config

    a_to_c_message = Message(
        message_name="A:C",
        from_agent="a_address",
        to_agent="c_address",
        content="a_to_c_message",
    )
    b_to_c_message = Message(
        message_name="B:C",
        from_agent="b_address",
        to_agent="c_address",
        content="b_to_c_message",
    )

    c_to_a_message = Message(
        message_name="C:A",
        from_agent="c_address",
        to_agent="a_address",
        content="C[A:C,B:C['a_to_c_message', 'b_to_c_message']]",
    )
    c_to_b_message = Message(
        message_name="C:B",
        from_agent="c_address",
        to_agent="b_address",
        content="C[A:C['a_to_c_message']]",
    )

    # 1. b->c
    b.send(b_to_c_message, b_to_c_message.to_agent)

    import time

    time.sleep(1)

    # 2. a->c
    a.send(a_to_c_message, a_to_c_message.to_agent)

    time.sleep(1)

    # 3. c->a and c->b
    assert a.message_in_inbox(c_to_a_message).get() == True
    assert b.message_in_inbox(c_to_b_message).get() == True
