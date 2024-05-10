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
    def handle_A2B(self, data: [str]) -> str:
        result = f"B[A:B[{data[0]}]]"
        Message2C = Message(message_name='B:C', content=result)
        Message2D = Message(message_name='B:D', content=result)
        msgs = []
        msgs.append(Message2C)
        msgs.append(Message2D)
        return msgs
    
@pytest.fixture
def scene2():
    a = Node.start(node_name="A_0", address="a_0_addr")
    b = B.start(node_name="B_0", address="b_0_addr")
    c = Node.start(node_name="C_0", address="c_0_addr")
    d = Node.start(node_name="D_0", address="d_0_addr")
    
    a.proxy().address_book = {"B_0": "b_0_addr"}
    b.proxy().address_book = {
        "C_0": "c_0_addr",
        "D_0": "d_0_addr",
        }
    
    a.proxy().instance = {"b_0_addr": b}
    b.proxy().instance = {
        "c_0_addr": c,  
        "d_0_addr": d
        }
    
    yield a.proxy(), b.proxy(), c.proxy(), d.proxy()
    
    a.stop()
    b.stop()
    c.stop()
    d.stop()
    
class TestDespetch():
    # 同一信息处理后分发 scene: A -> B, then B -> C and B -> D
    def test_scene2(self, scene2):
        a, b, c, d = scene2
        initial_data = "DB data"
        msg = Message(message_name = "A:B", from_agent = "A_0", to_agent = "B_0", content = initial_data)
        
        a.send(msg)
        
        import time
        time.sleep(4)
        
        BtoC_msg = Message(message_name = 'B:C', from_agent = 'B_0', to_agent = "C_0", content = f'B[A:B[{initial_data}]]')
        BtoD_msg = Message(message_name = 'B:D', from_agent = 'B_0', to_agent = "D_0", content = f'B[A:B[{initial_data}]]')
        
        # 通过 判断 c, d 的邮箱中是否有与 BtoC_msg, BtoD_msg 完全相同的元素
        # 判断 c, d 是否接收到的 b 处理后发送的消息 BtoC_msg, BtoD_msg
        assert any(
            BtoC_msg.message_name == msg.message_name and
            BtoC_msg.from_agent == msg.from_agent and
            BtoC_msg.to_agent == msg.to_agent and
            BtoC_msg.content == msg.content
            for msg in c.message_box.get()
        )
        
        assert any(
            BtoD_msg.message_name == msg.message_name and
            BtoD_msg.from_agent == msg.from_agent and
            BtoD_msg.to_agent == msg.to_agent and
            BtoD_msg.content == msg.content
            for msg in d.message_box.get()
        )
