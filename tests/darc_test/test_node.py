import pytest
from unittest.mock import Mock, MagicMock, patch
from darc.darc.node import Node, message_handler
from darc.darc.message import Message
from darc.darc.node_gate import NodeGate

from test_base import PingPonger, TestPingMessage
 
def test_pingpong():
   # 如果你是通过NodeGate spawn actor函数生成的Node，那么这个Node的地址中有一个NodeGate的地址
    # 手动生成Node，则父亲就是None
    
    
    pingNode = PingPonger(node_name="pingNode", address="pingNode_addr")
    pongNode = PingPonger(node_name="pongNode", address="pongNode_addr")
    # mock 一下pingNode pongNode的NodeGate地址
    pingNode._address_book = mock.Mock(return_value = {"mock_gate_node"}
    pongNode._address_book = mock.Mock(return_value = {"mock_gate_node"})                                   
    
    pingNode.broadcast_ping(TestPingMessage)
    pongNode._mailbox = mock.Mock(return_value = [TestPingMessage])
    # 我实现了acoto r send函数，定义send(to_addr, messacage)
    # actor1(router), actor2(node gate)
    # actor1.send(to_addr, message), actor2
    # 
    
    
    for i in range(0,3):
        # Test successful transmission
        nodeGate.set_success_rate(1.0)  # Ensure 100% success rate for this test part
        message_success = Message(message_name="PingMessage", from_agent="pingNode", to_agent="pongNode")
        pingNode.send(message_success)

    for i in range(0, 2):
        # Test failed transmission
        nodeGate.set_success_rate(0.0)  # Ensure 0% success rate for this part
        message_failure = Message(message_name="PingMessage", from_agent="pingNode", to_agent="pongNode")
        pingNode.send(message_failure)

    # Check results
    success_messages = [msg for msg, status in nodeGate.messages if status == "success"]
    failed_messages = [msg for msg, status in nodeGate.messages if status == "failure"]
    print("Successes:", len(success_messages))
    print("Failures:", len(failed_messages))

# ## scene: A -> B
# def test_scene0():
#     actorA = Node("A", "A_addr")
#     actorB = Node("B", "B_addr")
    
#     message = Message(content = 'data', from_actor = 'A', to_actor = 'B')
    
