from abc import ABCMeta, abstractmethod
from typing import Dict, List
from darc.darc.message import Message

class Preprocessor(metaclass=ABCMeta):
    @abstractmethod
    def pre_process(self, message: Message) -> bool:
        pass

class StopPreprocessor(Preprocessor):
    def pre_process(self, message: Message) -> bool:
        return message.content != "stop"

class DefaultPreprocessor(Preprocessor):
    def pre_process(self, message: Message) -> bool:
        message.content = f"Processed content: {message.content}"
        return True

class AbstractActor(metaclass=ABCMeta):
    def __init__(self, preprocessor: Preprocessor = None):
        self._address_book: Dict[str, str] = dict()
        self._instance: Dict[str, str] = dict()
        self.preprocessor = preprocessor or DefaultPreprocessor()

    def recv(self, message: Message):
        if self.preprocessor.pre_process(message):
            processed_data = self.process(message.content)
            self.send(Message(content=processed_data, to_actor=message._to))
        else:
            print("Message processing stopped by preprocessor.")

    def send(self, message: Message):
        agent_identifier = self._address_book.get(message._to)
        if agent_identifier:
            actor = self._instance.get(agent_identifier)
            if actor:
                actor.recv(message)
            else:
                print(f"No actor found with identifier {agent_identifier}")
        else:
            print(f"No agent found with name {message._to}")

    def set_preprocessor(self, preprocessor: Preprocessor):
        self.preprocessor = preprocessor

    def process(self, data: str) -> str:
        return "process " + data