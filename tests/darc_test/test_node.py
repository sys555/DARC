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
    
def test_pingpong_interaction():
    pingNode = PingPonger(node_name="pingNode", address="pingNode_addr")
    pongNode = PingPonger(node_name="pongNode", address="pongNode_addr")

    # Setup connections between nodes through NodeGate
    gate = NodeGate()
    pingNode.set_gate(gate)
    pongNode.set_gate(gate)  # pingNode sends messages to NodeGate
    gate.add_instance(pingNode)
    gate.add_instance(pongNode)

    # Simulate message passing
    message_success = Message(message_name="PingMessage", from_agent="pingNode", to_agent="pongNode")
    pingNode.send(message_success)  # This should trigger pongNode to send a pong response

    # Since we're simulating, we might just print outputs in handlers or check state changes
    # For a more thorough testing environment, we might want to capture outputs or states



# ## scene: A -> B
# def test_scene0():
#     actorA = Node("A", "A_addr")
#     actorB = Node("B", "B_addr")
    
#     message = Message(content = 'data', from_actor = 'A', to_actor = 'B')
    
