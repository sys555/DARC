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
    def handle_A2B(self, data) -> list:
        content = data[0]
        if self.sts(content):
            # pass, to C
            Message2C = Message(message_name="B:C", content=f"B[A:B[{content}]]")
            msgs = []
            msgs.append(Message2C)
        else:
            # back, to A
            Message2A = Message(message_name="B:A", content=f"B[A:B[{content}]]")
            msgs = []
            msgs.append(Message2A)
        return msgs

    def sts(self, content) -> bool:
        if len(content) > 10:
            return False
        else:
            return True


@pytest.fixture
def scene3():
    a = Node.start(node_name="A_0", address="a_0_addr")
    b = B.start(node_name="B_0", address="b_0_addr")
    c = Node.start(node_name="C_0", address="c_0_addr")

    a.proxy().link_node(b, "b_0_addr")
    b.proxy().link_node([c, a], ["c_0_addr", "a_0_addr"])

    yield a.proxy(), b.proxy(), c.proxy()

    a.stop()
    b.stop()
    c.stop()


# @pytest.mark.skip("兼容一下现有的actor类")
class TestCondition:
    # 条件分支 scene: A -> B, if B processed data is True then B -> C, else B -> A

    def test_pass(self, scene3):
        a, b, c = scene3
        initail_data_a_pass = "attack Q"
        initial_data_a_back = "attackattackattackattack"
        AtoB_msg_pass = Message(
            message_name="A:B",
            from_agent="a_0_addr",
            to_agent="b_0_addr",
            content=f"{initail_data_a_pass}",
            task_id=0,
        )

        AtoB_msg_pass = Message(
            message_name="A:B",
            from_agent="a_0_addr",
            to_agent="b_0_addr",
            content=f"{initail_data_a_pass}",
            task_id=0,
        )

        a.send(AtoB_msg_pass, "b_0_addr")

        import time

        time.sleep(1)

        b_to_c_msg = Message(
            message_name="B:C",
            from_agent="b_0_addr",
            to_agent="c_0_addr",
            content=f"B[A:B[{initail_data_a_pass}]]",
            task_id=0,
        )
        b_to_a_msg = Message(
            message_name="B:A",
            from_agent="b_0_addr",
            to_agent="a_0_addr",
            content=f"B[A:B[{initial_data_a_back}]]",
            task_id=0,
        )

        # a -> b -> c
        # 1. c 中 有 与 BtoC_msg 相同的消息
        # 2. a 中 没有 与 BtoA_msg 相同的消息
        assert c.message_in_inbox(b_to_c_msg).get() == True
        assert a.message_in_inbox(b_to_a_msg).get() == False

    def test_back(self, scene3):
        a, b, c = scene3
        initail_data_a_pass = "attack Q"
        initial_data_a_back = "attackattackattackattack"
        # AtoB_msg_pass = Message(message_name = "A:B", from_agent = "A_0", to_agent = "B_0", content = f"{initail_data_a_pass}", task_id = 0)

        a_to_b_msg_back = Message(
            message_name="A:B",
            from_agent="a_0_addr",
            to_agent="b_0_addr",
            content=f"{initial_data_a_back}",
            task_id=1,
        )

        # a.send(AtoB_msg_pass)
        a.send(a_to_b_msg_back, "b_0_addr")

        import time

        time.sleep(1)

        b_to_c_msg = Message(
            message_name="B:C",
            from_agent="b_0_addr",
            to_agent="c_0_addr",
            content=f"B[A:B[{initail_data_a_pass}]]",
            task_id=1,
        )
        b_to_a_msg = Message(
            message_name="B:A",
            from_agent="b_0_addr",
            to_agent="a_0_addr",
            content=f"B[A:B[{initial_data_a_back}]]",
            task_id=1,
        )

        # a -> c -> a
        # 1. c 中 没有 与 BtoC_msg 相同的消息
        # 2. a 中 有 与 BtoA_msg 相同的消息
        assert c.message_in_inbox(b_to_c_msg).get() == False
        assert a.message_in_inbox(b_to_a_msg).get() == True
