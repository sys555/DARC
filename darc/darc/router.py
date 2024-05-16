from typing import List
import copy
from .message import Message
from .actor import AbstractActor
from .multi_addr import MultiAddr
from .node_gate import NodeGate


class Router(AbstractActor):
    def __init__(self, node_addr):
        super().__init__()
        self._node_type = "Router"
        self._node_addr = node_addr
        self._node_gate_type_address_dict = {}
        self.spawn_new_actor(NodeGate, self._node_addr.name)

    def on_receive(self, message: Message):
        self._message_box.append(message)
        bak_message = copy.deepcopy(message)
        bak_message.from_agent_type = self._node_type
        # 区分几个事情：
        # message只能发送给NodeGate，区分这个message是从哪个NodeGate发送过来
        if message.from_node_type_name == self._node_gate_left:
            self.send(
                bak_message, self._node_gate_type_address_dict[self._node_gate_right]
            )

        elif message.from_node_type_name == self._node_gate_right:
            self.send(
                bak_message, self._node_gate_type_address_dict[self._node_gate_left]
            )

        else:
            raise NotImplementedError

    def spawn_new_actor(self, cls, node_gate_link_type):
        self._node_gate_left, self._node_gate_right = node_gate_link_type.split("--")

        # node_gate的实现是单例模式，因此，不会出现
        node_gate_left_instance = cls(
            self._node_gate_left, MultiAddr(name=self._node_gate_left)
        )
        self._address_book.add(node_gate_left_instance.get_addr)
        self._instance[node_gate_left_instance.get_addr] = node_gate_left_instance
        self._node_gate_type_address_dict[
            self._node_gate_left
        ] = node_gate_left_instance.get_addr

        node_gate_right_instance = cls(
            self._node_gate_right, MultiAddr(name=self._node_gate_right)
        )
        self._address_book.add(node_gate_right_instance.get_addr)
        self._instance[node_gate_right_instance.get_addr] = node_gate_right_instance
        self._node_gate_type_address_dict[
            self._node_gate_right
        ] = node_gate_right_instance.get_addr

        # 需要告诉NodeGate能够直接链接的路由节点
        node_gate_left_instance.set_router_addr(
            node_gate_link_type, self._node_addr, self
        )
        node_gate_right_instance.set_router_addr(
            node_gate_link_type, self._node_addr, self
        )
