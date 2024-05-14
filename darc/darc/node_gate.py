from typing import List, Tuple, Dict, Set

from darc.darc.message import Message
from .actor import AbstractActor
from .multi_addr import MultiAddr


class NodeGate(AbstractActor):
    __instance__: Dict[str, "NodeGate"] = {}
    __first_init__: Set[str] = set()

    def __new__(cls, node_gate_type, *args, **kwargs):
        if node_gate_type not in cls.__instance__:
            cls.__instance__[node_gate_type] = super().__new__()
        return cls.__instance__[node_gate_type]

    def __init__(self, node_gate_type, addr):
        if node_gate_type not in self.__first_init__:
            super().__init__()
            self._node_type = "NodeGate"
            self._router_addr_dict = {}
            self._node_addr = addr
            self._node_gate_type = node_gate_type
            self.__first_init__.add(node_gate_type)

    def set_router_addr(self, node_gate_link_type, router_addr, router_instance):
        if node_gate_link_type not in self._router_addr_dict:
            self._router_addr_dict[node_gate_link_type] = router_addr
            self._instance[router_addr] = router_instance
            self._address_book.add(router_addr)

    def on_receive(self, message: Message):
        self._message_box.append(message)
        if message.from_agent_type == "Router":
            if message.to_agent != "None":
                self.send(message, message.to_agent)
            else:
                linked_instance_list = [
                    _addr
                    for _addr in self._instance.keys
                    if _addr not in self._router_addr_dict.values()
                ]

                self.send(message, linked_instance_list)
        elif message.from_agent_type == "RealNode":
            self.send(message, self._router_addr_dict[message.message_name])

        else:
            raise NotImplementedError

    def spawn_new_actor(self, cls, args):
        for number, instance_args in args:
            for _ in range(number):
                instance_addr = MultiAddr()
                instance = cls(instance_addr, *instance_args)
                self._address_book.add(instance_addr)
                self._instance[instance_addr] = instance
                instance.set_node_gate_addr(self._node_addr, self)

    @property
    def get_addr(self):
        return self._node_addr
