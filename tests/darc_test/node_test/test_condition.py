# # 条件分支 scene: A -> B, if B processed data is True then B -> C, else B -> A
# def test_scene3(scene3):
#     A, B, C = scene3
    
#     AtoB_msg = Message(message_name = "attack", from_agent = "A_0", to_agent = "B_0", content = "attack Q", tast_id = 1)
#     BtoC_msg = Message(message_name = 'attack', from_agent = 'B_0', to_agent = "C_0", content = 'rejected Q', tast_id = 1)
#     BtoD_msg = Message(message_name = 'attack', from_agent = 'B_0', to_agent = "D_0", content = 'accepted Q', task_id = 1)
    
#     A.send(AtoB_msg)
    
#     import time
#     time.sleep(2)
    
#     # # C 是否接收到的 B 处理后发送的消息 BtoC_msg
#     # B.on_receive.assert_called_once_with(BtoC_msg)
#     # # 
#     # C.on_receive.assert_called_once_with(BtoD_msg)

import pytest
import pykka
from loguru import logger
from unittest.mock import Mock, MagicMock, patch
from darc.darc.node import Node, message_handler
from darc.darc.message import Message
import logging

# 设置日志记录器的配置，包括日志级别和日志输出格式
logger.add("test.log", level="INFO", format="{time} {level} {message}")

class B(Node):
    def __init__(self, node_name, address) -> None:
        super().__init__(node_name=node_name, address=address)
        self.node_name = node_name
        self.address = address

    @Node.process(["A:B"])
    def handle_A2B(self, data: [str]) -> list:
        content = data[0]
        if self.sts(content):
            # pass, to C
            Message2C = Message(message_name='B:C', content=f'B[A:B[{content}]]')
            msgs = []
            msgs.append(Message2C)
        else:
            # back, to A
            Message2A = Message(message_name='B:A', content=f'B[A:B[{content}]]')
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
    
    a.proxy().address_book = {"B_0": "b_0_addr"}
    b.proxy().address_book = {
        "C_0": "c_0_addr",
        "A_0": "a_0_addr"
        }
    
    a.proxy().instance = {"b_0_addr": b}
    b.proxy().instance = {
        "c_0_addr": c,
        "a_0_addr": a,
        }
    
    yield a.proxy(), b.proxy(), c.proxy()
    
    a.stop()
    b.stop()
    c.stop()
    
class TestDespetch():
    # 条件分支 scene: A -> B, if B processed data is True then B -> C, else B -> A
    def test_scene3(self, scene3):
        a, b, c = scene3
        initail_data_a_pass = "attack Q"
        initial_data_a_back = "attackattackattackattack"
        AtoB_msg_pass = Message(message_name = "A:B", from_agent = "A_0", to_agent = "B_0", content = f"{initail_data_a_pass}", task_id = 0)
        
        AtoB_msg_back = Message(message_name = "A:B", from_agent = "A_0", to_agent = "B_0", content = f"{initial_data_a_back}", task_id = 1)
        
        a.send(AtoB_msg_pass)
        a.send(AtoB_msg_back)
        
        import time
        time.sleep(4)
        
        BtoC_msg = Message(message_name = 'B:C', from_agent = 'B_0', to_agent = "C_0", content = f'B[A:B[{initail_data_a_pass}]]', task_id = 0)
        BtoA_msg = Message(message_name = 'B:A', from_agent = 'B_0', to_agent = "A_0", content = f'B[A:B[{initial_data_a_back}]]', task_id = 1)
        logging.info(c.message_box.get()[0])
        logging.info(BtoC_msg)
        # 通过 判断 c, d 的邮箱中是否有与 BtoC_msg, BtoD_msg 完全相同的元素
        # 判断 c, d 是否接收到的 b 处理后发送的消息 BtoC_msg, BtoD_msg
        assert any(
            BtoC_msg.message_name == msg.message_name and
            BtoC_msg.from_agent == msg.from_agent and
            BtoC_msg.to_agent == msg.to_agent and
            BtoC_msg.content == msg.content
            for msg in c.message_box.get()
        )

