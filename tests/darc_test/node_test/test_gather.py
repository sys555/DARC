import pytest
import pykka
from unittest.mock import Mock, MagicMock, patch
from darc.darc.node import Node
from darc.darc.message import Message
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

    a.proxy().address_book = {"C_0": "c_0_addr"}
    b.proxy().address_book = {"C_0": "c_0_addr"}
    c.proxy().address_book = {"D_0": "d_0_addr"}

    a.proxy().instance = {"c_0_addr": c}
    b.proxy().instance = {"c_0_addr": c}
    c.proxy().instance = {"d_0_addr": d}

    yield a.proxy(), b.proxy(), c.proxy(), d.proxy()

    a.stop()
    b.stop()
    c.stop()
    d.stop()


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
        AtoC_msg = Message(
            message_name="A:C",
            from_agent="A_0",
            to_agent="C_0",
            content=f"{initial_data_a}",
            task_id=0,
        )
        BtoC_msg = Message(
            message_name="B:C",
            from_agent="B_0",
            to_agent="C_0",
            content=f"{initail_data_b}",
            task_id=0,
        )

        a.send(AtoC_msg)
        b.send(BtoC_msg)

        import time

        time.sleep(4)

        CtoD_msg = Message(
            message_name="C:D",
            from_agent="C_0",
            to_agent="D_0",
            content=f"C[A:C,B:C['{initial_data_a}', '{initail_data_b}']]",
            task_id=0,
        )

        # d 邮箱中有 CtoD_msg, 证明 b 收到了 AtoC_msg、BtoC_msg 并进行处理
        assert any(
            CtoD_msg.message_name == msg.message_name
            and CtoD_msg.from_agent == msg.from_agent
            and CtoD_msg.to_agent == msg.to_agent
            and CtoD_msg.content == msg.content
            for msg in d.message_box.get()
        )

    ## 不同task id 不会触发 C 发送消息
    def test_dif_task_id(self, scene1):
        a, b, c, d = scene1
        initial_data_a = "DB data"
        initail_data_b = "attack data"
        AtoC_msg = Message(
            message_name="A:C",
            from_agent="A_0",
            to_agent="C_0",
            content=f"{initial_data_a}",
            task_id=0,
        )
        BtoC_msg = Message(
            message_name="B:C",
            from_agent="B_0",
            to_agent="C_0",
            content=f"{initail_data_b}",
            task_id=2,
        )

        a.send(AtoC_msg)
        b.send(BtoC_msg)

        import time

        time.sleep(4)

        # 1. C 中有 AtoC_msg、BtoC_msg
        # 2. D 邮箱为空
        # 检查 C 中是否有与 AtoC_msg、BtoC_msg 属性相同的消息
        assert any(
            msg.message_name == AtoC_msg.message_name
            and msg.from_agent == AtoC_msg.from_agent
            and msg.to_agent == AtoC_msg.to_agent
            and msg.content == AtoC_msg.content
            and msg.task_id == AtoC_msg.task_id
            for msg in c.message_box.get()
        )
        assert any(
            msg.message_name == BtoC_msg.message_name
            and msg.from_agent == BtoC_msg.from_agent
            and msg.to_agent == BtoC_msg.to_agent
            and msg.content == BtoC_msg.content
            and msg.task_id == BtoC_msg.task_id
            for msg in c.message_box.get()
        )

        # 检查 D 中邮箱是否为空
        assert not d.message_box.get()
