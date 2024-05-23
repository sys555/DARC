import pytest
import pykka
from unittest.mock import Mock, MagicMock, patch
from darc.node import Node
from darc.message import Message
import logging


class C(Node):
    def __init__(self, node_name, address) -> None:
        super().__init__(node_name=node_name, address=address)
        self.node_name = node_name
        self.address = address

    @Node.process(["A:C", "B:C"])
    def handle_A2B(self, data: [str]) -> list:
        result = f"C[A:C,B:C{data}]"
        Message2D = Message(message_name="C:D", content=result)
        msgs = []
        msgs.append(Message2D)
        return msgs


@pytest.fixture
def scene1():
    a = Node.start(node_name="A_0", address="a_0_addr")
    b = Node.start(node_name="B_0", address="b_0_addr")
    c = C.start(node_name="C_0", address="c_0_addr")
    d = Node.start(node_name="D_0", address="d_0_addr")

    a.proxy().link_node(c, "c_0_addr")
    b.proxy().link_node(c, "c_0_addr")
    c.proxy().link_node(d, "d_0_addr")

    yield a.proxy(), b.proxy(), c.proxy(), d.proxy()

    a.stop()
    b.stop()
    c.stop()
    d.stop()


# @pytest.mark.skip("兼容一下现有的actor类")
class TestGather:
    # 多入度场景：
    #    ┌───────────┐     ┌───────────┐
    #    │     A     │     │     B     │
    #    └─────┬─────┘     └─────┬─────┘
    #          │                 │
    #          v                 v
    #          ┌───────────┐
    #          │     C     │
    #          └─────┬─────┘
    #                │
    #                v
    #          ┌───────────┐
    #          │     D     │
    #          └───────────┘

    def test_pass(self, scene1):
        a, b, c, d = scene1
        initial_data_a = "DB data"
        initail_data_b = "attack data"
        a_to_c_message = Message(
            message_name="A:C",
            from_agent="a_0_addr",
            to_agent="c_0_addr",
            content=f"{initial_data_a}",
            task_id=0,
        )
        b_to_c_message = Message(
            message_name="B:C",
            from_agent="b_0_addr",
            to_agent="c_0_addr",
            content=f"{initail_data_b}",
            task_id=0,
        )

        a.send(a_to_c_message, a_to_c_message.to_agent)
        b.send(b_to_c_message, b_to_c_message.to_agent)

        import time

        time.sleep(1)

        c_to_d_message = Message(
            message_name="C:D",
            from_agent="c_0_addr",
            to_agent="d_0_addr",
            content=f"C[A:C,B:C['{initial_data_a}', '{initail_data_b}']]",
            task_id=0,
        )

        # d 邮箱中有 CtoD_msg, 证明 b 收到了 AtoC_msg、BtoC_msg 并进行处理
        assert d.message_in_inbox(c_to_d_message).get() == True

    ## 不同task id 不会触发 C 发送消息
    def test_dif_task_id(self, scene1):
        a, b, c, d = scene1
        initial_data_a = "DB data"
        initail_data_b = "attack data"
        a_to_c_message = Message(
            message_name="A:C",
            from_agent="a_0_addr",
            to_agent="c_0_addr",
            content=f"{initial_data_a}",
            task_id=0,
        )
        b_to_c_message = Message(
            message_name="B:C",
            from_agent="b_0_addr",
            to_agent="c_0_addr",
            content=f"{initail_data_b}",
            task_id=2,
        )

        a.send(a_to_c_message, a_to_c_message.to_agent)
        b.send(b_to_c_message, b_to_c_message.to_agent)

        import time

        time.sleep(1)

        # 1. C 中有 AtoC_msg、BtoC_msg
        # 2. D 邮箱为空
        # 检查 C 中是否有与 AtoC_msg、BtoC_msg 属性相同的消息

        assert c.message_in_inbox(a_to_c_message).get() == True
        assert c.message_in_inbox(b_to_c_message).get() == True

        # 检查 D 中邮箱是否为空
        assert not d.message_map.get()
