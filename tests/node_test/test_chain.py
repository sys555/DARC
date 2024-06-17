# import pytest
# import pykka
# from darc.node import Node
# from darc.message import Message
# from darc.router import Router
# from darc.node_gate import NodeGate
# from darc.multi_addr import MultiAddr
# import logging
# import uuid
# from loguru import logger


# class B(Node):
#     def __init__(self, node_addr=None, node_name="") -> None:
#         super().__init__(node_addr=node_addr, node_name=node_name)

#     @Node.process(["A:B"])
#     def handle_A2B(self, messages: [Message]) -> str:
#         data = messages[0].content
#         result = f"B[A:B[{data}]]"
#         Message2C = Message(message_name="B:C", content=result)
#         msgs = []
#         msgs.append(Message2C)
#         return msgs


# @pytest.fixture
# def scene0():
#     A_B_addr = MultiAddr("A:B")
#     A_B_router = Router.start(A_B_addr)

#     A_gate = NodeGate.start("A", MultiAddr("A"))
#     B_gate = NodeGate.start("B", MultiAddr("B"))

#     B_C_addr = MultiAddr("B:C")
#     B_C_router = Router.start(B_C_addr)

#     C_gate = NodeGate.start("C", MultiAddr("C"))

#     yield A_B_router.proxy(), A_gate.proxy(), B_gate.proxy(), B_C_router.proxy(), C_gate.proxy()

#     A_B_router.stop()
#     A_gate.stop()
#     B_gate.stop()
#     B_C_router.stop()
#     C_gate.stop()


# # @pytest.mark.skip("兼容一下现有的actor类")
# class TestChain:
#     # 链 scene0: A --> B, B --> C
#     def test_scene0(self, scene0):
#         A_B_router, A_gate, B_gate, B_C_router, C_gate = scene0

#         alice = A_gate.spawn_new_actor(Node, ("alice",)).get()
#         bob = B_gate.spawn_new_actor(B, ("bob",)).get()
#         coop = C_gate.spawn_new_actor(Node, ("coop",)).get()
#         import time

#         time.sleep(0.1)
#         initial_data = "DB data"
#         task_id = str(uuid.uuid4())
#         a_to_b_msg = Message(
#             message_name="A:B",
#             from_agent=alice.proxy().node_addr.get(),
#             to_agent=bob.proxy().node_addr.get(),
#             from_agent_type="RealNode",
#             content=initial_data,
#             task_id=task_id,
#         )

#         alice.proxy().on_send(a_to_b_msg)

#         time.sleep(1)

#         b_to_c_msg = Message(
#             message_name="B:C",
#             from_agent=alice.proxy().node_addr.get(),
#             to_agent="c_0_addr",
#             content=f"B[A:B[{initial_data}]]",
#         )

#         # 通过 判断 c 的邮箱中是否有与 BtoC_msg 完全相同的元素
#         # 判断C 是否接收到的 B 处理后发送的消息 BtoC_msg
#         assert coop.proxy().message_box.get()[0].task_id is task_id
#         assert (
#             coop.proxy().message_box.get()[0].content
#             == f"B[A:B[{initial_data}]]"
#         )
#         # assert c.message_in_inbox(b_to_c_msg).get() is True
