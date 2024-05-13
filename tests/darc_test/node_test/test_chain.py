import pytest
import pykka
from unittest.mock import Mock, MagicMock, patch
from darc.darc.node import Node
from darc.darc.message import Message
import logging

class B(Node):
    def __init__(self, node_name, address) -> None:
        super().__init__(node_name=node_name, address=address)
        self.node_name = node_name
        self.address = address

    @Node.process(["A:B"])
    def handle_A2B(self, data: [str]) -> str:
        result = f"B[A:B[{data[0]}]]"
        Message2C = Message(message_name='B:C', content=result)
        msgs = []
        msgs.append(Message2C)
        return msgs
    
@pytest.fixture
def scene0():
    a = Node.start(node_name="A_0", address="a_0_addr")
    b = B.start(node_name="B_0", address="b_0_addr")
    c = Node.start(node_name="C_0", address="c_0_addr")
    
    a.proxy().address_book = {"B_0": "b_0_addr"}
    b.proxy().address_book = {"C_0": "c_0_addr"}                                 
    c.proxy().address_book = {}
    
    a.proxy().instance = {"b_0_addr": b}
    b.proxy().instance = {"c_0_addr": c}
    c.proxy().instance = {}
    
    yield a.proxy(), b.proxy(), c.proxy()
    
    a.stop()
    b.stop()
    c.stop()
    
class TestChain():
    # 链 scene0: A --> B, B --> C
    def test_scene0(self, scene0):
        a, b, c = scene0
        initial_data = "DB data"
        AtoB_msg = Message(message_name = "A:B", from_agent = "A_0", to_agent = "B_0", content = initial_data)
        
        a.send(AtoB_msg)
        
        import time
        time.sleep(4)
        
        BtoC_msg = Message(message_name = 'B:C', from_agent = 'B_0', to_agent = "C_0", content = f'B[A:B[{initial_data}]]')
        logging.info(c.message_box.get()[0])
        logging.info(BtoC_msg)
        
        # 通过 判断 c 的邮箱中是否有与 BtoC_msg 完全相同的元素
        # 判断C 是否接收到的 B 处理后发送的消息 BtoC_msg
        assert any(
            BtoC_msg.message_name == msg.message_name and
            BtoC_msg.from_agent == msg.from_agent and
            BtoC_msg.to_agent == msg.to_agent and
            BtoC_msg.content == msg.content
            for msg in c.message_box.get()
        )
        
