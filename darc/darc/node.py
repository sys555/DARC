import logging
from abc import ABCMeta
from typing import Any, Callable, Dict, List

import pykka

from darc.darc.actor import AbstractActor
from darc.darc.message import Message


class Preprocessor(metaclass=ABCMeta):
    def pre_process(self, actor, message: Message) -> bool:
        return True  # Default behavior to always process messages


class Node(AbstractActor):
    _id_counter: int = 0
    message_handlers: Dict[
        str, List[Callable[..., Any]]
    ] = {}  # Class-level attribute shared by all instances
    message_types: List[List[str]] = []
    handler_call_by_message_types: Dict[Callable, List[str]] = {}

    def __init__(self, address, node_name):
        super().__init__()
        self.id: int = Node._id_counter
        Node._id_counter += 1
        self._node_type = "RealNode"
        self.node_name = node_name
        self._node_addr = address.addr
        self.handlers: Dict[str, Callable] = {}
        self.message_map: Dict[str, List[Message]] = {}

    def on_receive(self, message: Message):
        logging.info(message)
        self._message_box.append(message)
        # TODO callback

    def on_send(self, message: Message):
        self._message_box.append(message)
        self._node_gate.on_receive(message)
        if message.message_name not in self.message_map:
            self.message_map[message.message_name] = []
        self.message_map[message.message_name].append(message)
        message_list = self.handle_message(message)
        for message_item in message_list:
            if message_item.to_agent == "None":
                message_item.to_agent = self.random_choose(message_item)
            message_item.from_agent = self._node_addr
            message_item.task_id = message.task_id
        for msg in message_list:
            if msg.to_agent is None:
                # 广播
                ...
            else:
                self.send(msg, msg.to_agent)

    def set_node_gate_addr(self, node_gate_addr, node_gate):
        self._node_gate_addr = node_gate_addr
        self._node_gate = node_gate

    # 随机从地址簿中选择一个目标类型的 node 地址
    def random_choose(self, message: Message):
        parts = message.message_name.split(":")
        # 遍历分割后的部分，查找在address_book中第一个匹配的key，并返回对应的value
        to_type = parts[-1]
        # 遍历 address_book 中的键，找到第一个匹配的前缀为 to_type 的键值对，并返回对应的值
        # TODO: 匹配方式待改进
        for key in self._address_book:
            if key.lower().startswith(to_type.lower()):
                return key

        # 如果没有找到匹配的key，则返回None或者其他适当的值
        return None

    @classmethod
    def process(cls, message_type_list: List[str]) -> Callable:
        def decorator(func: Callable):
            cls.message_types.append(message_type_list)
            for message_type in message_type_list:
                if message_type not in cls.message_handlers:
                    cls.message_handlers[message_type] = []
                cls.message_handlers[message_type].append(func)

        return decorator

    def handle_message(self, message: Message, *args: Any, **kwargs: Any) -> Any:
        handled_messages = []
        if message.message_name not in self.message_handlers:
            # 无处理方法
            return []
        # 消息可触发多个处理方法
        for handler in self.message_handlers[message.message_name]:
            # 该处理方法所需的所有message
            type_list = Node.handler_call_by_message_types[handler]
            message_list = []
            # 逆序, 取新消息
            # TODO: message_map 更新策略, 同task id, message_name, 新消息覆盖旧消息
            # 按 type 顺序排 content
            for type in type_list:
                if type not in self.message_map:
                    # 没有相关历史消息
                    break
                # 从最新的开始找 message
                for past_message in reversed(self.message_map[type]):
                    if message.task_id == past_message.task_id:
                        message_list.append(past_message)
            if len(message_list) != len(type_list):
                # 当前 task 的所有前置消息未到达
                continue
            else:
                contents = [message.content for message in message_list]
                messages = handler(self, contents)
                handled_messages.extend(messages)
        return handled_messages

    def message_in_inbox(self, message: Message):
        if message.message_name in self.message_map:
            for item in self.message_map[message.message_name]:
                if item.__dict__ == message.__dict__:
                    return True
        return False

    def link_node(
        self,
        instance: List | pykka._ref.ActorRef = [],
        address: List | str = [],
    ):
        # 构建 self to instance 的实例关系, 关联码本与实例表)
        try:
            # 检查instance是否是Node类的实例
            if isinstance(instance, pykka._ref.ActorRef) and isinstance(address, str):
                self._address_book.add(address)
                self._instance[address] = instance
            elif isinstance(instance, List) and isinstance(address, List):
                for item_instance, addr in zip(instance, address):
                    self._address_book.add(addr)
                    self._instance[addr] = item_instance
        except BaseException as e:
            logging.error(f"{str(e)} ")
