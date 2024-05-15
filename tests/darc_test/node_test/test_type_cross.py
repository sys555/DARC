import pytest

from unittest.mock import Mock, MagicMock, patch
from darc.darc.node import Node
from darc.darc.message import Message

import logging


class C(Node):
    @Node.process(["A:C", "B:C"])
    def handler_A_C_B_C(self, data: [str]) -> Message:
        result = f"C[A:C,B:C{data}]"
        message = Message(message_name="C:A", content=result)
        target = []
        target.append(message)
        return target

    @Node.process(["A:C"])
    def handler_A_C(self, data: [str]) -> Message:
        result = f"C[A:C{data}]"
        message = Message(message_name="C:B", content=result)
        target = []
        target.append(message)
        return target


@pytest.fixture
def config():
    a = Node.start(node_name="A_0", address="a_address")
    b = Node.start(node_name="B_0", address="b_address")
    c = C.start(node_name="C_0", address="c_address")

    a.proxy().address_book = {"C_0": "c_address"}
    b.proxy().address_book = {"C_0": "c_address"}
    c.proxy().address_book = {"A_0": "a_address", "B_0": "b_address"}

    a.proxy().instance = {"c_address": c}
    b.proxy().instance = {"c_address": c}
    c.proxy().instance = {"a_address": a, "b_address": b}

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
        from_agent="A_0",
        to_agent="C_0",
        content="a_to_c_message",
    )
    b_to_c_message = Message(
        message_name="B:C",
        from_agent="B_0",
        to_agent="C_0",
        content="b_to_c_message",
    )

    c_to_a_message = Message(
        message_name="C:A",
        from_agent="C_0",
        to_agent="A_0",
        content="C[A:C,B:C['a_to_c_message', 'b_to_c_message']]",
    )
    c_to_b_message = Message(
        message_name="C:B",
        from_agent="C_0",
        to_agent="B_0",
        content="C[A:C['a_to_c_message']]",
    )

    # 1. a->c
    a.send(a_to_c_message)

    import time

    time.sleep(1)

    # 2. c->b
    assert b.message_in_inbox(c_to_b_message).get() == True

    # 2. b->c
    b.send(b_to_c_message)

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
        from_agent="A_0",
        to_agent="C_0",
        content="a_to_c_message",
    )
    b_to_c_message = Message(
        message_name="B:C",
        from_agent="B_0",
        to_agent="C_0",
        content="b_to_c_message",
    )

    c_to_a_message = Message(
        message_name="C:A",
        from_agent="C_0",
        to_agent="A_0",
        content="C[A:C,B:C['a_to_c_message', 'b_to_c_message']]",
    )
    c_to_b_message = Message(
        message_name="C:B",
        from_agent="C_0",
        to_agent="B_0",
        content="C[A:C['a_to_c_message']]",
    )

    # 1. b->c
    b.send(b_to_c_message)

    import time

    time.sleep(1)

    # 2. a->c
    a.send(a_to_c_message)

    time.sleep(1)

    # 3. c->a and c->b
    assert a.message_in_inbox(c_to_a_message).get() == True
    assert b.message_in_inbox(c_to_b_message).get() == True
