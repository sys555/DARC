from typing import List, Tuple, Dict, Set

from darc.darc.message import Message
from .actor import AbstractActor
from .multi_addr import MultiAddr
import random
import copy


class NodeGate(AbstractActor):
    __instance__: Dict[str, "NodeGate"] = {}
    __first_init__: Set[str] = set()

    def __new__(cls, node_gate_type, *args, **kwargs):
        if node_gate_type not in cls.__instance__:
            cls.__instance__[node_gate_type] = super().__new__(cls)
        return cls.__instance__[node_gate_type]

    def __init__(self, node_gate_type, addr):
        if node_gate_type not in self.__first_init__:
            super().__init__()
            self._node_type = "NodeGate"
            self._router_addr_dict = {}
            self._node_addr = addr
            self._node_gate_type = node_gate_type
            self.__first_init__.add(node_gate_type)
            self._node_count = 0
            self._node_id_instance = {}

    def set_router_addr(self, node_gate_link_type, router_addr, router_instance):
        if node_gate_link_type not in self._router_addr_dict:
            self._router_addr_dict[node_gate_link_type] = router_addr
            self._instance[router_addr] = router_instance
            self._address_book.add(router_addr)

    def on_receive(self, message: Message):
        self._message_box.append(message)
        bak_message = copy.deepcopy(message)
        bak_message.from_agent_type = self._node_type
        bak_message.from_node_type_name = self._node_gate_type
        if message.from_agent_type == "Router":
            if message.to_agent != "None":
                self.send(bak_message, message.to_agent)
            elif message.broadcasting:
                linked_instance_list = [
                    _addr
                    for _addr in self._instance.keys()
                    if _addr not in self._router_addr_dict.values()
                    and _addr != message.from_agent
                ]

                self.send(bak_message, linked_instance_list)
            else:
                # random sample
                linked_instance_list = [
                    _addr
                    for _addr in self._instance.keys()
                    if _addr not in self._router_addr_dict.values()
                    and _addr != message.from_agent
                ]
                random_to_instance = random.choice(linked_instance_list)
                self.send(bak_message, random_to_instance)

        elif message.from_agent_type == "RealNode":
            self.send(bak_message, self._router_addr_dict[message.message_name])

        else:
            raise NotImplementedError

    def spawn_new_actor(self, cls, args):
        for number, instance_args in args:
            for _ in range(number):
                node_id = f"{self._node_gate_type}_{self._node_count}"
                instance_addr = MultiAddr(node_id)
                instance = cls(instance_addr, *instance_args)
                self._address_book.add(instance_addr.addr)
                self._instance[instance_addr.addr] = instance
                instance.set_node_gate_addr(self._node_addr, self)
                self._node_id_instance[node_id] = instance
                self._node_count += 1

    @property
    def get_addr(self):
        return self._node_addr

    def get_node_instance(self, node_id):
        return self._node_id_instance[node_id]

    @classmethod
    def clear_node_gate(cls, node_gate: "NodeGate"):
        del cls.__instance__[node_gate._node_gate_type]
        cls.__first_init__.discard(node_gate._node_gate_type)

    @classmethod
    def clear_all_node_gate(cls):
        cls.__instance__ = {}
        cls.__first_init__ = set()
