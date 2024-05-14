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
    # 1. A->C; 2. B->C and C->B; 4. C->A
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

    a.send(a_to_c_message)
    b.send(b_to_c_message)

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

    import time

    time.sleep(4)

    # logging.info(c.message_map.get())
    # logging.info(c.handler_call_by_message_types.get())

    # logging.info(c.message_box.get())
    logging.info(a.message_box.get())
    logging.info(b.message_box.get())
    logging.info(c_to_a_message)
    assert any(
        c_to_a_message.message_name == msg.message_name
        and c_to_a_message.from_agent == msg.from_agent
        and c_to_a_message.to_agent == msg.to_agent
        and c_to_a_message.content == msg.content
        for msg in a.message_box.get()
    )

    assert any(
        c_to_b_message.message_name == msg.message_name
        and c_to_b_message.from_agent == msg.from_agent
        and c_to_b_message.to_agent == msg.to_agent
        and c_to_b_message.content == msg.content
        for msg in b.message_box.get()
    )
