# import pytest
# import pykka
# from unittest.mock import Mock, MagicMock, patch
# from node import Node
# from message import Message
# import logging
# import time


# class A(Node):
#     def __init__(self, node_name, address) -> None:
#         super().__init__(node_name=node_name, address=address)
#         self.node_name = node_name
#         self.address = address
#         self.block_time = 2

#     def _send(self, message: Message, next_hop_address):
#         time.sleep(self.block_time * time.Second)
#         return super()._send(message, next_hop_address)

# class B(Node):
#     def __init__(self, node_name, address) -> None:
#         super().__init__(node_name=node_name, address=address)
#         self.node_name = node_name
#         self.address = address
#         self.block_time = 2

#     def _send(self, message: Message, next_hop_address):
#         time.sleep(self.block_time * time.Second)
#         return super()._send(message, next_hop_address)

# class C(Node):
#     def __init__(self, node_name, address) -> None:
#         super().__init__(node_name=node_name, address=address)
#         self.node_name = node_name
#         self.address = address

#     @Node.process(["A:C", "B:C"])
#     def handle_A2B(self, data: [str]) -> list:
#         result = f"C[A:C,B:C{data[:-1]}]"
#         Message2D = Message(message_name="C:D", content=result)
#         msgs = []
#         msgs.append(Message2D)
#         return msgs

# class D(Node):
#     @Node.Process(["C:D"])
#     def handle_C2D(self, data):
#         logging.info(time.time())

# @pytest.fixture
# def config():
#     a = A.start(node_name="A_0", address="a_0_addr")
#     b = B.start(node_name="B_0", address="b_0_addr")
#     c = C.start(node_name="C_0", address="c_0_addr")
#     d = Node.start(node_name="D_0", address="d_0_addr")

#     a.proxy().link_node(c, "c_0_addr")
#     b.proxy().link_node(c, "c_0_addr")
#     c.proxy().link_node(d, "d_0_addr")

#     yield a.proxy(), b.proxy(), c.proxy(), d.proxy()

#     a.stop()
#     b.stop()
#     c.stop()
#     d.stop()


# @pytest.mark.skip("skip skip")
# class TestGather:
#     # 多入度场景:
#     #    ┌───────────┐     ┌───────────┐
#     #    │     A     │     │     B     │
#     #    └─────┬─────┘     └─────┬─────┘
#     #          │                 │
#     #          v                 v
#     #          ┌───────────┐
#     #          │     C     │
#     #          └─────┬─────┘
#     #                │
#     #                v
#     #          ┌───────────┐
#     #          │     D     │
#     #          └───────────┘

#     def test_pass(self, config):
#         a, b, c, d = config
#         initial_data_a = "DB data"
#         initail_data_b = "attack data"
#         a_to_c_message = Message(
#             message_name="A:C",
#             from_agent="a_0_addr",
#             to_agent="c_0_addr",
#             content=f"{initial_data_a}",
#             task_id=str(0),
#         )
#         b_to_c_message = Message(
#             message_name="B:C",
#             from_agent="b_0_addr",
#             to_agent="c_0_addr",
#             content=f"{initail_data_b}",
#             task_id=str(0),
#         )

#         a.block_time = 1
#         b.block_time = 2

#         a.send(a_to_c_message, a_to_c_message.to_agent)
#         b.send(b_to_c_message, b_to_c_message.to_agent)

#         import time

#         time.sleep(3)

#         c_to_d_message = Message(
#             message_name="C:D",
#             from_agent="c_0_addr",
#             to_agent="d_0_addr",
#             content=f"C[A:C,B:C['{initial_data_a}', '{initail_data_b}']]",
#             task_id=str(0),
#         )

#         # d 邮箱中有 CtoD_msg, 证明 b 收到了 AtoC_msg、BtoC_msg 并进行处理
#         assert d.message_in_inbox(c_to_d_message).get() == True


#         a_to_c_message = Message(
#             message_name="A:C",
#             from_agent="a_0_addr",
#             to_agent="c_0_addr",
#             content=f"{initial_data_a}",
#             task_id=str(1),
#         )
#         b_to_c_message = Message(
#             message_name="B:C",
#             from_agent="b_0_addr",
#             to_agent="c_0_addr",
#             content=f"{initail_data_b}",
#             task_id=str(1),
#         )

#         a.block_time = 2
#         b.block_time = 1

#         a.send(a_to_c_message, a_to_c_message.to_agent)
#         b.send(b_to_c_message, b_to_c_message.to_agent)

#         import time

#         time.sleep(3)

#         c_to_d_message = Message(
#             message_name="C:D",
#             from_agent="c_0_addr",
#             to_agent="d_0_addr",
#             content=f"C[A:C,B:C['{initial_data_a}', '{initail_data_b}']]",
#             task_id=str(1),
#         )

#         # d 邮箱中有 CtoD_msg, 证明 b 收到了 AtoC_msg、BtoC_msg 并进行处理
#         assert d.message_in_inbox(c_to_d_message).get() == True
