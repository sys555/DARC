import pytest
from unittest.mock import Mock, MagicMock, patch
from darc.darc.node import Node, message_handler
from darc.darc.message import Message
from darc.darc.node_gate import NodeGate

from test_base import PingPonger

def test_pingpong():
    nodeGate = NodeGate()
    
    pingNode = PingPonger(node_name="pingNode", address="pingNode_addr")
    pongNode = PingPonger(node_name="pongNode", address="pongNode_addr")

    # Link nodes and NodeGate
    pingNode.set_gate(nodeGate)
    pongNode.set_gate(nodeGate)  # pingNode sends messages to NodeGate
    nodeGate.add_instance(pingNode)
    nodeGate.add_instance(pongNode)
    
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
    
