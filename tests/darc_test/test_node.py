import pytest
import pykka
from loguru import logger
from unittest.mock import Mock, MagicMock, patch
from darc.darc.node import Node, message_handler
from darc.darc.message import Message
from darc.darc.node_gate import NodeGate
from test_base import PingPonger, TestPingMessage


# 设置日志记录器的配置，包括日志级别和日志输出格式
logger.add("test.log", level="INFO", format="{time} {level} {message}")

@pytest.fixture
def ping_pong_nodes():
    pingPongGate = Mock()

    pingNode = PingPonger.start(node_name="pingNode", address="pingNode_addr")
    pongNode = PingPonger.start(node_name="pongNode", address="pongNode_addr")
    
    # mock 一下pingNode pongNode的NodeGate地址
    pingNode._address_book = {"pongNode": "pingPongGate_addr"}
    pongNode._address_book = {"pingNode": "pingPongGate_addr"}                                 
    
    pingNode._instance = {"pingPongGate_addr": pingPongGate}
    pongNode._instance = {"pingPongGate_addr": pingPongGate}
    
    yield pingNode.proxy(), pongNode.proxy(), pingPongGate
    
    pingNode.stop()
    pongNode.stop()
    
@pytest.fixture
def scene0():
    A_Gate = Mock()
    B_Gate = Mock()
    C_Gate = Mock()

    A = Node.start(node_name="A_0", address="a_0_addr")
    B = Node.start(node_name="B_0", address="b_0_addr")
    C = Node.start(node_name="C_0", address="c_0_addr")
    
    # mock 一下pingNode pongNode的NodeGate地址
    A._address_book = {"B_0": "b_0_addr"}
    B._address_book = {"C_0": "c_0_addr"}                                 
    C._address_book = {}                                 
    
    A._instance = {"b_0_addr": A_Gate}
    B._instance = {"c_0_addr": B_Gate}
    C._instance = {}
    
    yield A.proxy(), B.proxy(), C.proxy()
    
    A.stop()
    B.stop()
    C.stop()

@pytest.fixture
def scene1():
    A_Gate = Mock()
    B_Gate = Mock()
    C_Gate = Mock()
    D_Gate = Mock()

    A = Node.start(node_name="A_0", address="a_0_addr")
    B = Node.start(node_name="B_0", address="b_0_addr")
    C = Node.start(node_name="C_0", address="c_0_addr")
    D = Node.start(node_name="D_0", address="d_0_addr")
    
    # mock 一下pingNode pongNode的NodeGate地址
    A._address_book = {"C_0": "c_0_addr"}
    B._address_book = {"C_0": "c_0_addr"}                                 
    C._address_book = {"D_0": "d_0_addr"}                                 
    
    A._instance = {"c_0_addr": A_Gate}
    B._instance = {"c_0_addr": B_Gate}
    C._instance = {"d_0_addr": C_Gate}
    
    yield A.proxy(), B.proxy(), C.proxy()
    
    A.stop()
    B.stop()
    C.stop()

@pytest.fixture
def scene2():
    A_Gate = Mock()
    B_Gate = Mock()
    C_Gate = Mock()
    D_Gate = Mock()

    A = Node.start(node_name="A_0", address="a_0_addr")
    B = Node.start(node_name="B_0", address="b_0_addr")
    C = Node.start(node_name="C_0", address="c_0_addr")
    D = Node.start(node_name="D_0", address="d_0_addr")
    
    # mock 一下pingNode pongNode的NodeGate地址
    A._address_book = {"B_0": "c_0_addr"}
    B._address_book = {"C_0": "c_0_addr", "D_0": "d_0_addr"}                                 
    C._address_book = {}                                 
    D._address_book = {}                                 
    
    A._instance = {"b_0_addr": A_Gate}
    B._instance = {"c_0_addr": B_Gate, "d_0_addr": B_Gate}
    C._instance = {}
    D._instance = {}
    
    yield A.proxy(), B.proxy(), C.proxy(), D.proxy()
    
    A.stop()
    B.stop()
    C.stop()
    D.stop()

@pytest.fixture
def scene3():
    A_Gate = Mock()
    B_Gate = Mock()
    C_Gate = Mock()

    A = Node.start(node_name="A_0", address="a_0_addr")
    B = Node.start(node_name="B_0", address="b_0_addr")
    C = Node.start(node_name="C_0", address="c_0_addr")
    
    # mock 一下pingNode pongNode的NodeGate地址
    A._address_book = {"B_0": "c_0_addr"}
    B._address_book = {"A_0": "a_0_addr", "C_0": "c_0_addr"}                                 
    C._address_book = {}                                                                 
    
    A._instance = {"b_0_addr": A_Gate}
    B._instance = {"C_0_addr": B_Gate, "A_0_addr": B_Gate}
    C._instance = {}
    
    yield A.proxy(), B.proxy(), C.proxy()
    
    A.stop()
    B.stop()
    C.stop()

def test_pingpong(ping_pong_nodes):
    pingNode, pongNode, pingPongGate = ping_pong_nodes
    
    msg = Message(message_name = "PingMessage", from_agent = "pingNode", to_agent = "pongNode", content = "empty")
    
    pingNode.send(msg)

    # Trigger the on_receive method for PongNode with the mock message
    pongNode.on_receive(msg)
    
    import time
    time.sleep(2)
    
    # 经过 mock 流转后到达 pongNode，assert pongNode 是否使用了 def pong 处理消息
    pingPongGate.on_receive.assert_called_once_with(msg)
    pingPongGate.send.assert_called_once_without(msg)
    pongNode.pong.assert_called_once_with(msg)

# 链 scene0: A --> B, B --> C
def test_scene0(scene0):
    A, B, C = scene0
    
    msg = Message(message_name = "attack", from_agent = "A_0", to_agent = "B_0", content = "DB data")
    
    A.send(msg)
    
    import time
    time.sleep(2)
    
    BtoC_msg = Message(message_name = 'attack', from_agent = 'B_0', content = 'attack Q')
    
    # C 是否接收到的 B 处理后发送的消息 BtoC_msg
    C.on_receive.assert_called_once_with(BtoC_msg)

# 多入度 scene1: A --> C, B --> C, C --> D
def test_scene1(scene1):
    A, B, C, D = scene1
    
    AtoC_msg = Message(message_name = "attack", from_agent = "A_0", to_agent = "B_0", content = "DB data", task_id = 1)
    BtoC_msg = Message(message_name = 'attack', from_agent = 'B_0', to_agent = "C_0", content = 'attack Q', task_id = 1)
    CtoD_msg = Message(message_name = 'attack', from_agent = 'C_0', to_agent = "B_0", content = 'accepted attack Q', task_id = 1)
    
    A.send(AtoC_msg)
    B.send(BtoC_msg)
    
    import time
    time.sleep(2)
    

    gather_calls = C.gather.call_args_list
    first_call_args = gather_calls[0][0]
    second_call_args = gather_calls[1][0]
    
    assert AtoC_msg in C._message_box
    assert BtoC_msg in C._message_box
    
    # 仅接受到 AtoC_msg.content or BtoC_msg.content
    # returns False
    assert first_call_args[0] == AtoC_msg.content
    assert first_call_args[1] is False
    
    # AtoC_msg.content and BtoC_msg.content 均接收到
    # return (True, [AtoC_msg.content, BtoC_msg_content])
    assert second_call_args[0] == BtoC_msg.content
    assert second_call_args[1] is True
    
    D.on_receive.assert_called_once_with(CtoD_msg)
    
    
# 同一信息处理后分发 scene: A -> B, then B -> C and B -> D
def test_scene2(scene2):
    A, B, C, D = scene2
    
    AtoB_msg = Message(message_name = "attack", from_agent = "A_0", to_agent = "B_0", content = "DB data", tast_id = 1)
    BtoC_msg = Message(message_name = 'attack', from_agent = 'B_0', to_agent = "C_0", content = 'attack Q', tast_id = 1)
    BtoD_msg = Message(message_name = 'attack', from_agent = 'B_0', to_agent = "D_0", content = 'attack Q', task_id = 1)
    
    A.send(AtoB_msg)
    
    import time
    time.sleep(2)
    
    ## TODO: check C 内部分发逻辑
    
    # C 是否接收到的 B 处理后发送的消息 BtoC_msg
    C.on_receive.assert_called_once_with(BtoC_msg)
    # 
    D.on_receive.assert_called_once_with(BtoD_msg)
    
# 条件分支 scene: A -> B, if B processed data is True then B -> C, else B -> A
def test_scene3(scene3):
    A, B, C = scene3
    
    AtoB_msg = Message(message_name = "attack", from_agent = "A_0", to_agent = "B_0", content = "attack Q", tast_id = 1)
    BtoC_msg = Message(message_name = 'attack', from_agent = 'B_0', to_agent = "C_0", content = 'rejected Q', tast_id = 1)
    BtoD_msg = Message(message_name = 'attack', from_agent = 'B_0', to_agent = "D_0", content = 'accepted Q', task_id = 1)
    
    A.send(AtoB_msg)
    
    import time
    time.sleep(2)
    
    # # C 是否接收到的 B 处理后发送的消息 BtoC_msg
    # B.on_receive.assert_called_once_with(BtoC_msg)
    # # 
    # C.on_receive.assert_called_once_with(BtoD_msg)