# import pytest
# import pykka
# from unittest.mock import Mock, MagicMock, patch
# from darc.darc.node import Node
# from darc.darc.message import Message
# import logging


# class B(Node):
#     def __init__(self, node_name, address) -> None:
#         super().__init__(node_name=node_name, address=address)

#     @Node.process(["A:B"])
#     def handle_A2B(self, data: [str]) -> str:
#         result = f"B[A:B[{data[0]}]]"
#         Message2C = Message(message_name="B:C", content=result)
#         Message2C = Message(message_name="B:C", content=result)
#         msgs = []
#         msgs.append(Message2C)
#         return msgs


# @pytest.fixture
# def scene0():
#     a = Node.start(node_name="A_0", address="a_0_addr")
#     b = B.start(node_name="B_0", address="b_0_addr")
#     c = Node.start(node_name="C_0", address="c_0_addr")

#     a.proxy().link_node(b, b.proxy().address.get())
#     b.proxy().link_node(c, c.proxy().address.get())

#     yield a.proxy(), b.proxy(), c.proxy()

#     a.stop()
#     b.stop()
#     c.stop()



# class TestChain:
#     # 链 scene0: A --> B, B --> C
#     def test_scene0(self, scene0):
#         a, b, c = scene0
#         initial_data = "DB data"
#         a_to_b_msg = Message(
#             message_name="A:B",
#             from_agent="a_0_addr",
#             to_agent="b_0_addr",
#             content=initial_data,
#         )

#         a.send(a_to_b_msg, a_to_b_msg.to_agent)

#         import time

#         time.sleep(1)

#         b_to_c_msg = Message(
#             message_name="B:C",
#             from_agent="b_0_addr",
#             to_agent="c_0_addr",
#             content=f"B[A:B[{initial_data}]]",
#         )

#         # 通过 判断 c 的邮箱中是否有与 BtoC_msg 完全相同的元素
#         # 判断C 是否接收到的 B 处理后发送的消息 BtoC_msg
#         assert c.message_in_inbox(b_to_c_msg).get() is True
