import copy
import logging
import random
from typing import Any, Dict, List, Set, Tuple

from loguru import logger

from .actor import AbstractActor
from .message import Message
from .multi_addr import MultiAddr
from .node import Node


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
            self.node_addr = addr
            self._node_gate_type = node_gate_type
            self.__first_init__.add(node_gate_type)
            self._node_count = 0
            self._node_id_instance = {}

    def set_router_addr(
        self, node_gate_link_type, router_addr, router_instance
    ):
        if node_gate_link_type not in self._router_addr_dict:
            self._router_addr_dict[node_gate_link_type] = router_addr
            self.instance[router_addr] = router_instance
            self._address_book.add(router_addr)

    def on_receive(self, message: Message):
        try:
            self.message_box.append(message)
            bak_message = copy.deepcopy(message)
            bak_message.from_agent_type = self._node_type
            bak_message.from_node_type_name = self._node_gate_type
            # BUG: bak_message.from_node_type_name = self._node_gate_type 逻辑有误，
            # 当produce -> consumer 时,
            # consumer 收到的message
            # Message(message_name='Producer:Consumer', message_id='None',
            # from_agent='F84ZU7OmOLcXS4Qv', to_agent='wLnlAfRbMnIKqaGo',
            # content='None',
            # task_id='e1de2911-d577-4082-8033-6fd4129511d1',
            # from_agent_type='NodeGate',
            # from_node_type_name='Consumer', broadcasting=True)
            # from_node_type_name='Consumer' 不正确
            # 要么修改 from_node_type_name 要么 修改 from_node_type_name变更逻辑
            if message.from_agent_type == "Router":
                if message.to_agent != "None":
                    self.send(bak_message, message.to_agent)
                elif message.broadcasting:
                    linked_instance_list = [
                        _addr
                        for _addr in self.instance.keys()
                        if (
                            _addr not in self._router_addr_dict.values()
                            and _addr != message.from_agent
                        )
                    ]
                    self.send(bak_message, linked_instance_list)
                else:
                    # random sample
                    linked_instance_list = [
                        _addr
                        for _addr in self.instance.keys()
                        if _addr not in self._router_addr_dict.values()
                        and _addr != message.from_agent
                    ]
                    random_to_instance = random.choice(linked_instance_list)
                    self.send(bak_message, random_to_instance)

            elif message.from_agent_type == "RealNode":
                self.send(
                    bak_message, self._router_addr_dict[message.message_name]
                )

            else:
                raise NotImplementedError
        except Exception as e:
            logger.error(f"node gate on_receive {type(e)}, {str(e)}")

    def spawn_new_actor(self, cls, args) -> Any:
        # 单个 actor 的生成
        if args is None:
            args = ()
        # count 必须先自增 否则多次 spawn_new_actor 并发执行,
        # 会导致多个 new actor 的 node id 一样, 导致生成失败
        # 记录当前 gate 中的 node 数量
        self._node_count += 1
        # node_id 以 gate type + node count
        node_id = f"{self._node_gate_type}_{self._node_count}"
        # 根据 node_id 生成 node addr
        instance_addr = MultiAddr(node_id)
        # 根据 args, 生成 cls 对应的 node 实例
        instance = cls.start(instance_addr, *args)
        # gate 地址簿更新
        self._address_book.add(instance_addr.addr)
        # node 根据 addr 记录在 gate 的实例列表中
        self.instance[instance_addr.addr] = instance
        # 设置新生成的 node 的 gate
        instance.proxy().set_node_gate_addr(self.node_addr, self.actor_ref)
        # node 根据 node_id 记录在 gate 的node id instance表中
        self._node_id_instance[node_id] = instance
        return instance

    @property
    def get_addr(self):
        return self.node_addr

    def get_node_instance(self, node_id):
        return self._node_id_instance[node_id]

    def get_all_node_instance(self):
        return list(self._node_id_instance.values())

    @classmethod
    def clear_node_gate(cls, node_gate: "NodeGate"):
        del cls.__instance__[node_gate._node_gate_type]
        cls.__first_init__.discard(node_gate._node_gate_type)

    @classmethod
    def clear_all_node_gate(cls):
        cls.__instance__ = {}
        cls.__first_init__ = set()
