from abc import ABCMeta
from typing import Dict, List
from darc.darc.message import Message

class AbstractActor(metaclass=ABCMeta):
    def __init__(self):
        self._address_book: Dict[str, str] = dict()
        self._instance: Dict[str, str] = dict()  # Maps agent identifiers to pykka actor instances

    def recv(self, message):
        # 预操作, 如 node 的 gather
        pre_result = self.pre_process(message)
        if pre_result is False:
            # 预操作返回False，停止处理
            return
        # 预操作返回了数据，调用process处理
        processed_data = self.process(pre_result)
        self.send(Message(content=processed_data, to_actor=message._to))


    def pre_process(self, message):
        # 这里实现预处理逻辑，根据实际需求调整
        # 示例：假设如果消息内容为"stop", 则返回False
        if message.content == "stop":
            return False
        # 否则返回处理后的数据
        return f"Processed content: {message.content}"
    
    def send(self, message: Message):
        # Retrieve the identifier of the actor to which the message should be sent
        agent_identifier = self._address_book.get(message._to)
        if agent_identifier:
            # Retrieve the actor instance using the identifier
            actor = self._instance.get(agent_identifier)
            if actor:
                actor.recv(message)
                # actor.tell(message)
                ...
            else:
                print(f"No actor found with identifier {agent_identifier}")
        else:
            print(f"No agent found with name {message._to}")
    
    def spawn_new_actor(self):
        ...

    def process(self, data: str) -> str:
        return "process " + data
    