import pytest
import pykka
from darc.node import Node
from darc.message import Message
from darc.router import Router
from darc.node_gate import NodeGate
from darc.multi_addr import MultiAddr
import logging
import uuid
from loguru import logger
from typing import List


class B(Node):
    def __init__(self, node_name, address) -> None:
        super().__init__(node_name=node_name, address=address)
        self.node_name = node_name
        self.address = address

    @Node.process(["A:B"])
    def handle_A2B(self, messages: List[Message]) -> list:
        content = messages[0].content
        if len(content) < 10:
            # pass, to C
            Message2C = Message(
                message_name="B:C", content=f"B[A:B[{content}]]"
            )
            msgs = []
            msgs.append(Message2C)
        else:
            # back, to A
            Message2A = Message(
                message_name="B:A", content=f"B[A:B[{content}]]"
            )
            msgs = []
            msgs.append(Message2A)
        return msgs


class B(Node):
    def __init__(self, node_addr=None, node_name="") -> None:
        super().__init__(node_addr=node_addr, node_name=node_name)

    @Node.process(["A:B"])
    def handle_A2B(self, messages: [Message]) -> str:
        content = messages[0].content
        if len(content) < 10:
            # pass, to C
            Message2C = Message(
                message_name="B:C", content=f"B[A:B[{content}]]"
            )
            msgs = []
            msgs.append(Message2C)
        else:
            # back, to A
            Message2A = Message(
                message_name="B:A", content=f"B[A:B[{content}]]"
            )
            msgs = []
            msgs.append(Message2A)
        return msgs


@pytest.fixture
def scene3():
    A_B_addr = MultiAddr("A:B")
    A_B_router = Router.start(A_B_addr)

    A_gate = NodeGate.start("A", MultiAddr("A"))
    B_gate = NodeGate.start("B", MultiAddr("B"))

    B_C_addr = MultiAddr("B:C")
    B_C_router = Router.start(B_C_addr)

    C_gate = NodeGate.start("C", MultiAddr("C"))

    yield A_B_router.proxy(), A_gate.proxy(), B_gate.proxy(), B_C_router.proxy(), C_gate.proxy()

    A_B_router.stop()
    A_gate.stop()
    B_gate.stop()
    B_C_router.stop()
    C_gate.stop()


@pytest.mark.skip("兼容一下现有的actor类")
class TestCondition:
    # 条件分支 scene: A -> B, if B processed data is True then B -> C, else B -> A
    @pytest.mark.skip("兼容一下现有的actor类")
    def test_pass(self, scene3):
        A_B_router, A_gate, B_gate, B_C_router, C_gate = scene3

        initail_data_a_pass = "attack Q"
        initial_data_a_back = "attackattackattackattack"

        alice = A_gate.spawn_new_actor(Node, ("alice",)).get()
        bob = B_gate.spawn_new_actor(B, ("bob",)).get()
        coop = C_gate.spawn_new_actor(Node, ("coop",)).get()
        logger.error(coop)
        import time

        time.sleep(0.1)
        initial_data = "DB data"
        task_id = str(uuid.uuid4())
        a_to_b_msg = Message(
            message_name="A:B",
            from_agent=alice.proxy().node_addr.get(),
            to_agent=bob.proxy().node_addr.get(),
            from_agent_type="RealNode",
            content=initail_data_a_pass,
            task_id=task_id,
        )

        alice.proxy().on_send(a_to_b_msg)

        time.sleep(1)

        b_to_c_msg = Message(
            message_name="B:C",
            from_agent=alice.proxy().node_addr.get(),
            to_agent="c_0_addr",
            content=f"B[A:B[{initial_data}]]",
        )

        # 通过 判断 c 的邮箱中是否有与 BtoC_msg task_id, content 的消息
        # 判断C 是否接收到的 B 处理后发送的消息 BtoC_msg
        assert alice.proxy().message_box.get()[0].task_id is task_id
        assert (
            alice.proxy().message_box.get()[0].content
            == f"B[A:B[{initial_data}]]"
        )

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

    @pytest.mark.skip("兼容一下现有的actor类")
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
