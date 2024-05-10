import pytest
import pykka
from loguru import logger
from unittest.mock import Mock, MagicMock, patch
from darc.darc.node import Node, message_handler
from darc.darc.message import Message
import logging

# 设置日志记录器的配置，包括日志级别和日志输出格式
logger.add("test.log", level="INFO", format="{time} {level} {message}")

class C(Node):
    def __init__(self, node_name, address) -> None:
        super().__init__(node_name=node_name, address=address)
        self.node_name = node_name
        self.address = address

    @Node.process(["A:C", "B:C"])
    def handle_A2B(self, data: [str]) -> list:
        result = f"C[A:C,B:C[{data}]]"
        Message2D = Message(message_name='C:D', content=result)
        msgs = []
        msgs.append(Message2D)
        return msgs
    
@pytest.fixture
def scene1():
    a = Node.start(node_name="A_0", address="a_0_addr")
    b = Node.start(node_name="B_0", address="b_0_addr")
    c = C.start(node_name="C_0", address="c_0_addr")
    d = Node.start(node_name="D_0", address="d_0_addr")
    
    a.proxy().address_book = {"C_0": "c_0_addr"}
    b.proxy().address_book = {"C_0": "c_0_addr"}
    c.proxy().address_book = {"D_0": "d_0_addr"}
    
    a.proxy().instance = {"c_0_addr": c}
    b.proxy().instance = {"c_0_addr": c}
    c.proxy().instance = {"d_0_addr": d}
    
    yield a.proxy(), b.proxy(), c.proxy(), d.proxy()
    
    a.stop()
    b.stop()
    c.stop()
    d.stop()
    
class TestDespetch():
    # 多入度 scene1: A --> C, B --> C, C --> D
    def test_scene1(self, scene1):
        a, b, c, d = scene1
        initial_data_a = "DB data"
        initail_data_b = "attack data"
        AtoC_msg = Message(message_name = "A:C", from_agent = "A_0", to_agent = "C_0", content = f"{initial_data_a}", task_id = 0)
        BtoC_msg = Message(message_name = 'B:C', from_agent = 'B_0', to_agent = "C_0", content = f"{initail_data_b}", task_id = 0)
        
        a.send(AtoC_msg)
        b.send(BtoC_msg)
        
        import time
        time.sleep(4)
        
        CtoD_msg = Message(message_name = 'C:D', from_agent = 'C_0', to_agent = "D_0", content = f'C[A:C,B:C[[\'{initial_data_a}\', \'{initail_data_b}\']]]', task_id = 0)
        
        # 通过 判断 c, d 的邮箱中是否有与 BtoC_msg, BtoD_msg 完全相同的元素
        # 判断 c, d 是否接收到的 b 处理后发送的消息 BtoC_msg, BtoD_msg
        assert any(
            CtoD_msg.message_name == msg.message_name and
            CtoD_msg.from_agent == msg.from_agent and
            CtoD_msg.to_agent == msg.to_agent and
            CtoD_msg.content == msg.content
            for msg in d.message_box.get()
        )

