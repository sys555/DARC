import pytest
import pykka
from unittest.mock import Mock, MagicMock, patch
from darc.node import Node
from darc.message import Message
import logging


class B(Node):
    def __init__(self, node_name, address) -> None:
        super().__init__(node_name=node_name, address=address)
        self.node_name = node_name
        self.address = address

    @Node.process(["A:B"])
    def handle_A2B(self, data: [str]) -> str:
        result = f"B[A:B[{data[0]}]]"
        Message2C = Message(message_name="B:C", content=result)
        Message2D = Message(message_name="B:D", content=result)
        msgs = []
        msgs.append(Message2C)
        msgs.append(Message2D)
        return msgs


@pytest.fixture
def scene2():
    a = Node.start(node_name="A_0", address="a_0_addr")
    b = B.start(node_name="B_0", address="b_0_addr")
    c = Node.start(node_name="C_0", address="c_0_addr")
    d = Node.start(node_name="D_0", address="d_0_addr")

    a.proxy().link_node(b, b.proxy().address.get())
    b.proxy().link_node(
        [c, d], [c.proxy().address.get(), d.proxy().address.get()]
    )

    yield a.proxy(), b.proxy(), c.proxy(), d.proxy()

    a.stop()
    b.stop()
    c.stop()
    d.stop()


@pytest.mark.skip("兼容一下现有的actor类")
class TestDespetch:
    # 同一信息处理后分发场景：
    #    ┌───────────┐
    #    │     A     │
    #    └─────┬─────┘
    #          │
    #          v
    #    ┌───────────┐
    #    │     B     │
    #    ├─────┬─────┤
    #    │     │     │
    #    v     v     v
    # ┌─────┐ ┌─────┐ ┌─────┐
    # │  C  │ │  D  │ │ ... │
    # └─────┘ └─────┘ └─────┘
    @pytest.mark.skip("兼容一下现有的actor类")
    def test_despetch(self, scene2):
        a, b, c, d = scene2
        initial_data = "DB data"
        AtoB_msg = Message(
            message_name="A:B",
            from_agent="a_0_addr",
            to_agent="b_0_addr",
            content=initial_data,
        )

        a.send(AtoB_msg, AtoB_msg.to_agent)

        import time

        time.sleep(1)

        b_to_c_message = Message(
            message_name="B:C",
            from_agent="b_0_addr",
            to_agent="c_0_addr",
            content=f"B[A:B[{initial_data}]]",
        )
        b_to_d_message = Message(
            message_name="B:D",
            from_agent="b_0_addr",
            to_agent="d_0_addr",
            content=f"B[A:B[{initial_data}]]",
        )

        # 1. c 邮箱中有 与 BtoC_msg 相同的消息
        # 2. d 邮箱中有 与 BtoD_msg 相同的消息
        assert c.message_in_inbox(b_to_c_message).get() == True
        assert d.message_in_inbox(b_to_d_message).get() == True
