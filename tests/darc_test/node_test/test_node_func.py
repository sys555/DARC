import pytest

from unittest.mock import Mock, MagicMock, patch
from darc.darc.node import Node
from darc.darc.message import Message

import logging


class C(Node):
    @Node.process(["A:C", "B:C"])
    def handler_A_C_B_C(self, data: [str]) -> Message: ...

    @Node.process(["A:C"])
    def handler_A_C(self, data: [str]) -> Message: ...


@pytest.fixture
def config():
    a = Node.start(node_name="a", address="a_address")
    b = Node.start(node_name="b", address="b_address")
    c = C.start(node_name="c", address="c_address")

    a.address_book = {"c": "c_address"}
    b.address_book = {"c": "c_address"}

    a.instance = {"c": "c_instance"}
    b.instance = {"c": "c_instance"}

    # 模拟 Message 类的返回值
    mock_message_a = MagicMock(spec=Message)
    mock_message_a.message_name = "A:C"
    mock_message_a.return_value = mock_message_a()

    mock_message_b = MagicMock(spec=Message)
    mock_message_b.message_name = "B:C"
    mock_message_b.return_value = mock_message_b()

    yield a.proxy(), b.proxy(), c.proxy(), mock_message_a, mock_message_b

    a.stop()
    b.stop()
    c.stop()


def test_type_cross(config):
    # C : [["A:C", "B:C"],["A:C"]]
    # 假设消息发送与接收顺序如下:
    # 1. A->C; 2. B->C;
    a, b, c, mock_message_a, mock_message_b = config

    # Mock the handler functions
    handler_a_c = MagicMock()
    handler_a_c_b_c = MagicMock()
    C.message_handlers["A:C"] = [handler_a_c_b_c, handler_a_c]

    # Mock the send method
    a.send = MagicMock()
    b.send = MagicMock()

    # Mock call
    handler_a_c_b_c(C, [])
    handler_a_c(C, [])

    # Check if the handler functions were called once
    handler_a_c.assert_called_once()
    handler_a_c_b_c.assert_called_once()
