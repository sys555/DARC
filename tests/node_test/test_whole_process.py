# # 16 UserNode
# # 4 Filter
# # 4 Defence Node
# # 8 LLM
# # 1 Leader Board

# import pytest

# from unittest.mock import Mock, MagicMock, patch
# from darc.darc.node import Node
# from darc.darc.message import Message

# import logging

# class DBNode(Node):
#     # DB -> UserNode
#     # DB -> Filter
#     def __init__(self, node_name: str = "", address: str = ""):
#         super().__init__(node_name, address)

#     @Node.process(["Graph:DB"])
#     def process_db_data(self, usernode_address: [str]):
#         message_usernode = Message(message_name = "DB:UserNode", content="")
#         message_filter = Message(message_name = "DB:Filter", content="")
#         msgs = []
#         msgs.append(message_filter)
#         return msgs

# class UserNode(Node):
#     # UserNode -> Filter
#     def __init__(self, node_name: str = "", address: str = ""):
#         super().__init__(node_name, address)

#     @Node.process(["DB:UserNode"])
#     def process_db_data(self, db_data: [str]):
#         message_filter = Message(message_name = "UserNode:Filter", content="")
#         msgs = []
#         msgs.append(message_filter)
#         return msgs

# class FilterNode(Node):
#     # Filter -> Defence
#     # Filter -> LeaderBoard
#     def __init__(self, node_name: str = "", address: str = ""):
#         super().__init__(node_name, address)

#     @Node.process(["UserNode:Filter", "DB:Filter"])
#     def filt(self, data: [str]):
#         message_defence = Message(message_name = "Filter:Defence", content="")
#         message_LeaderBoard = Message(message_name = "Filter:LeaderBoard", content="")
#         msgs = []
#         msgs.append(message_defence)
#         return msgs

# class DefenceNode(Node):
#     # Defence -> LLM
#     def __init__(self, node_name: str = "", address: str = ""):
#         super().__init__(node_name, address)

#     @Node.process(["Filter:Defence"])
#     def defence(self, filter_data: [str]):
#         message_filter = Message(message_name = "Defence:LLM", content="")
#         msgs = []
#         msgs.append(message_filter)
#         return msgs

# class LLMNode(Node):
#     # LLM -> LeaderBoard
#     def __init__(self, node_name: str = "", address: str = ""):
#         super().__init__(node_name, address)

#     @Node.process(["Defence:LLM"])
#     def query(self, question: [str]):
#         message_leader_board = Message(message_name = "Defence:LeaderBoard", content="")
#         msgs = []
#         msgs.append(message_leader_board)
#         return msgs

# class LeaderBoard(Node):
#     def __init__(self, node_name: str = "", address: str = ""):
#         super().__init__(node_name, address)

#     @Node.process(["Filter:LeaderBoard", "LLM:LeaderBoard"])
#     def filt(self, llm_data: [str]):
#         # save
#         ...

# @pytest.fixture
# def config():
#     a = Node.start(node_name="A_0", address="a_0_addr")
#     b = B.start(node_name="B_0", address="b_0_addr")
#     c = Node.start(node_name="C_0", address="c_0_addr")
#     d = Node.start(node_name="D_0", address="d_0_addr")

#     a.proxy().link_node(b, b.proxy().address.get())
#     b.proxy().link_node(
#         [c, d], [c.proxy().address.get(), d.proxy().address.get()]
#     )

#     yield a.proxy(), b.proxy(), c.proxy(), d.proxy()

#     a.stop()
#     b.stop()
#     c.stop()
#     d.stop()

#     DBNode_clust, UserNode_clust,  FilterNode_clust, DefenceNode_clust, LLMNode_clust, LeaderBoard_clust = [], [], [], [], [], [], [], [],
#     for i in range(0, 6):
#         DBNode_clust.append(DBNode.start(node_name = f"DBNode{i}", address = f"dbnode_address_{i}"))
#         UserNode_clust.append(UserNode.start(node_name = f"UserNode{i}", address = f"usernode_address_{i}"))
#         FilterNode_clust.append(FilterNode.start(node_name = f"FilterNode{i}", address = f"filternode_address_{i}"))
#         DefenceNode_clust.append(DefenceNode.start(node_name = f"DefenceNode{i}", address = f"defencenode_address_{i}"))
#         LLMNode_clust.append(LLMNode.start(node_name = f"LLMNode{i}", address = f"llmnode_address_{i}"))
#         LeaderBoard_clust.append(LeaderBoard.start(node_name = f"LeaderBoard{i}", address = f"leaderboard_address_{i}"))

#     for db_node in DBNode_clust:
#         db_node.proxy().link_node(UserNode_clust)
#         db_node.proxy().link_node(FilterNode_clust)

#     for user_node in UserNode_clust:
#         user_node.proxy().link_node(FilterNode_clust)

#     for filternode_node in

# class TestWholeProcess:
#     def test_whole_process(self):
#         ...
