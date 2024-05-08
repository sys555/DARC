from .actor import AbstractActor
from typing import Dict, Set


class NodeGate(AbstractActor):
    __instances__: Dict[str, "NodeGate"] = dict()
    __first_init__: Set[str] = set()

    def __new__(cls, gate_type, addr, *args, **kwargs):
        if addr not in cls.__first_init__:
            cls.__instances__[addr] = super().__new__(cls)
        return cls.__instances__[addr]

    def __init__(self, gate_type, addr):
        if addr not in self.__first_init__:
            super().__init__()
            self._gate_type = gate_type
            self._addr = addr

    def _broadcast(self):
        pass

    def _random_sample(self):
        pass

    def _point_to_point(self):
        pass

    def send(self):
        pass

    def recv(self):
        pass

    def spawn_new_actor(self, cls, args_list):
        pass

    def get_address_book(self):
        pass

    def retrieve_node(self, node_addr):
        return self._addr[node_addr]
