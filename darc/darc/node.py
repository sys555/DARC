from abc import abstractmethod, ABCMeta
from darc.darc.actor import AbstractActor
from darc.darc.message import Message
from typing import Any, Callable, Dict, List
import json
import logging

def message_handler(message_names):
    def decorator(func):
        func._message_names = message_names
        return func
    return decorator

class Preprocessor(metaclass=ABCMeta):
    @abstractmethod
    def pre_process(self, message: Message) -> bool:
        pass

class DefaultPreprocessor(Preprocessor):
    def pre_process(self, message: Message) -> bool:
        message.content = f"Processed content: {message.content}"
        return True

# class GatherPreprocessor(Preprocessor):
#     def __init__(self):
#         self.messages = defaultdict(list)

#     def pre_process(self, actor, message: Message) -> bool:
#         # Assume the message content is a JSON string with a task_id
#         content = json.loads(message.content)
#         task_id = content['task_id']
#         self.messages[task_id].append(content['data'])

#         # Check if all parts are gathered, for demonstration assume a fixed number
#         if len(self.messages[task_id]) >= 3:  # Assuming we wait for 3 parts
#             # When all parts are gathered, we call the process method
#             full_message = ' '.join(self.messages[task_id])
#             processed_data = actor.process(full_message)
#             actor.send(Message(content=processed_data, to_actor=message._to))
#             del self.messages[task_id]  # Clear the gathered messages for this task_id
#             return False  # Indicates that the message should not be processed further
#         return False  # Processing is not complete, do not call process yet


class Preprocessor(metaclass=ABCMeta):
    def pre_process(self, actor, message: Message) -> bool:
        return True  # Default behavior to always process messages
    
class Node(AbstractActor):
    _id_counter: int = 0
    message_handlers: Dict[str, List[Callable[..., Any]]] = (
        {}
    )  # Class-level attribute shared by all instances
    message_types: List[List[str]] = []
    
    def __init__(self, node_name, address):
        super().__init__()
        self.id: int = Node._id_counter
        Node._id_counter += 1
        
        self.node_name = node_name
        self.addr = address
        self.handlers: Dict[str, Callable] = {}

    def on_receive(self, message: Message):
        logging.info(message)
        self.message_box.append(message)
        # if self.preprocessor and self.preprocessor.pre_process(self, message):
            # handler = self.message_handlers.get(message.message_name, None)
            # if handler:
                # handler(self, message)
        # pre_process : gather
        # cast
        # 最先匹配
        message_list = self.handle_message(message)
        for message in message_list:
            message.to_agent = self.parse_and_lookup_name(message)
            message.from_agent = self.node_name
        logging.info(message_list)
        for msg in message_list:
            if msg.to_agent == None:
                ## 广播
                ...
            else:
                logging.info(msg)
                self.send(msg)
    
    def parse_and_lookup_name(self, message: Message):
        parts = message.message_name.split(":")
        # 遍历分割后的部分，查找在address_book中第一个匹配的key，并返回对应的value
        to_type = parts[-1]
        # 遍历 address_book 中的键，找到第一个匹配的前缀为 to_type 的键值对，并返回对应的值
        # TODO: 匹配方式待改进
        for key in self.address_book:
            if key.startswith(to_type):
                return key

        # 如果没有找到匹配的key，则返回None或者其他适当的值
        return None
    
    @classmethod
    def process(cls, message_type_list: List[str]) -> Callable:
        def decorator(func: Callable) -> Callable:
            cls.message_types.append(message_type_list)
            for message_type in message_type_list:
                if message_type not in cls.message_handlers:
                    cls.message_handlers[message_type] = []
                cls.message_handlers[message_type].append(func)
            return func

        return decorator

    def handle_message(
        self, message: Message, *args: Any, **kwargs: Any
    ) -> Any:
        res = self.check_message_types(message)
        logging.info(self.node_name)
        logging.info(res)
        if len(res) != 0 and message.message_name in self.message_handlers:
            for handler in self.message_handlers[message.message_name]:
                return handler(self, res)
        ## 没有处理方法返回空消息队列
        return []
        # raise ValueError(f"No handler for message type: {message_type}")

    def check_message_types(self, message):
        # 初始化用于存储打包消息的列表
        packed_messages = []

        # 初始化用于存储已经打包的消息类型的集合
        packed_message_types = set()

        # 遍历 message_types 中的每个子列表 sub_list
        for sub_list in self.message_types:
            # 检查 message 的 message_name 是否在 sub_list 中
            if message.message_name in sub_list:
                # 检查 sub_list 中其他的 message_name 是否在 message_box 中
                if all(any(msg.message_name == msg_type and msg.task_id == message.task_id for msg in self.message_box) for msg_type in sub_list if msg_type != message.message_name):
                    # 在 message_box 中找到符合条件的消息并打包
                    for msg_type in sub_list:
                        if msg_type != message.message_name and (msg_type, message.task_id) not in packed_message_types:
                            # 添加符合条件的消息到打包列表中
                            packed_messages.extend([msg.content for msg in self.message_box if msg.message_name == msg_type and msg.task_id == message.task_id])
                            # 记录已经打包的消息类型和任务ID
                            packed_message_types.add((msg_type, message.task_id))
                    
                    # 最后添加 message 本身到打包列表中
                    packed_messages.append(message.content)

                    return packed_messages  # 返回打包后的消息列表

        return packed_messages  # 如果没有符合条件的消息，则返回空列表

