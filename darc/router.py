import copy
from typing import Any, List, Tuple

import pykka
from loguru import logger

from darc.actor import AbstractActor
from darc.message import Message
from darc.multi_addr import MultiAddr
from darc.node import Node
from darc.node_gate import NodeGate


class Router(AbstractActor):
    def __init__(self, node_addr):
        super().__init__()
        self._node_type = "Router"
        self.node_addr = node_addr
        self.node_gate_type_address_dict = {}
        self.spawn_new_actor(NodeGate, self.node_addr.name)

    def on_receive(self, message: Message):
        logger.info(message)
        self.message_box.append(message)
        bak_message = copy.deepcopy(message)
        bak_message.from_agent_type = self._node_type
        # 区分几个事情：
        # message只能发送给NodeGate，区分这个message是从哪个NodeGate发送过来
        if message.from_node_type_name == self._node_gate_left:
            self.send(
                bak_message,
                self.node_gate_type_address_dict[self._node_gate_right],
            )

        elif message.from_node_type_name == self._node_gate_right:
            self.send(
                bak_message,
                self.node_gate_type_address_dict[self._node_gate_left],
            )

        else:
            raise NotImplementedError

    def spawn_new_actor(self, cls, node_gate_link_type):
        self._node_gate_left, self._node_gate_right = (
            node_gate_link_type.split(":")
        )

        # node_gate的实现是单例模式，因此，不会出现
        node_gate_left_instance = cls.start(
            self._node_gate_left, MultiAddr(name=self._node_gate_left)
        )
        self._address_book.add(node_gate_left_instance.proxy().get_addr.get())
        self.instance[node_gate_left_instance.proxy().get_addr.get()] = (
            node_gate_left_instance
        )
        self.node_gate_type_address_dict[self._node_gate_left] = (
            node_gate_left_instance.proxy().get_addr.get()
        )

        node_gate_right_instance = cls.start(
            self._node_gate_right, MultiAddr(name=self._node_gate_right)
        )
        self._address_book.add(node_gate_right_instance.proxy().get_addr.get())
        self.instance[node_gate_right_instance.proxy().get_addr.get()] = (
            node_gate_right_instance
        )
        self.node_gate_type_address_dict[self._node_gate_right] = (
            node_gate_right_instance.proxy().get_addr.get()
        )

        # 需要告诉NodeGate能够直接链接的路由节点
        node_gate_left_instance.proxy().set_router_addr(
            node_gate_link_type, self.node_addr, self.actor_ref
        )
        node_gate_right_instance.proxy().set_router_addr(
            node_gate_link_type, self.node_addr, self.actor_ref
        )

        # router 应支持 双向连接
        node_gate_reverse_link_type = (
            self._node_gate_right + ":" + self._node_gate_left
        )
        node_gate_left_instance.proxy().set_router_addr(
            node_gate_reverse_link_type, self.node_addr, self.actor_ref
        )
        node_gate_right_instance.proxy().set_router_addr(
            node_gate_reverse_link_type, self.node_addr, self.actor_ref
        )

    def _get_nodegate_instance(self, nodegate_name) -> Any:
        nodegate_addr = self.node_gate_type_address_dict[nodegate_name]
        nodegate_instance = self.instance[nodegate_addr]
        return nodegate_instance

    def spawn_real_instance(self, cls, args) -> Any:
        cls_name = cls.__name__
        nodegate_instance = self._get_nodegate_instance(cls_name)
        return nodegate_instance.proxy().spawn_new_actor(cls, args).get()

    def get_all_node_instance(self, cls_name) -> Any:
        nodegate_instance = self._get_nodegate_instance(cls_name)
        return nodegate_instance.proxy().get_all_node_instance().get()
