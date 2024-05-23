from .actor import AbstractActor
from .message import Message
from .multi_addr import MultiAddr


class Router(AbstractActor):
    def __init__(self, node_addr):
        super().__init__()
        self._node_type = "Router"
        self._node_addr = node_addr
        self._node_gate_type_address_dict = {}

    def on_receive(self, message: Message):
        self.message_box.append(message)
        # 区分几个事情：
        # message只能发送给NodeGate，区分这个message是从哪个NodeGate发送过来
        if message.from_agent_type == self._node_gate_left:
            self.send(
                message,
                self._node_gate_type_address_dict[self._node_gate_right],
            )

        elif message.from_agent_type == self._node_gate_right:
            self.send(
                message,
                self._node_gate_type_address_dict[self._node_gate_left],
            )

        else:
            raise NotImplementedError

    def spawn_new_actor(self, cls, node_gate_link_type):
        (
            self._node_gate_left,
            self._node_gate_right,
        ) = node_gate_link_type.split("--")

        # node_gate的实现是单例模式，因此，不会出现
        node_gate_left_instance = cls(
            self._node_gate_left, MultiAddr(name=self._node_gate_left)
        )
        self._address_book.add(node_gate_left_instance.get_addr)
        self._instance[node_gate_left_instance.get_addr] = (
            node_gate_left_instance
        )
        self._node_gate_type_address_dict[self._node_gate_left] = (
            node_gate_left_instance.get_addr
        )

        node_gate_right_instance = cls(
            self._node_gate_right, MultiAddr(name=self._node_gate_right)
        )
        self._address_book.add(node_gate_right_instance.get_addr)
        self._instance[node_gate_right_instance.get_addr] = (
            node_gate_right_instance
        )
        self._node_gate_type_address_dict[self._node_gate_right] = (
            node_gate_right_instance.get_addr
        )

        # 需要告诉NodeGate能够直接链接的路由节点
        node_gate_left_instance.set_router_addr(
            node_gate_link_type, self._node_addr
        )
        node_gate_right_instance.set_router_addr(
            node_gate_link_type, self._node_addr
        )
