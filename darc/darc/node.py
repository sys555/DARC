from abc import abstractmethod, ABCMeta
from darc.darc.actor import AbstractActor
from darc.darc.message import Message
from typing import Callable, Dict, Set
from darc.darc.node_gate import NodeGate
import json

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
    def __init__(self, node_name, address, preprocessor=None):
        super().__init__()
        self.node_name = node_name
        self.address = address
        self.handlers: Dict[str, Callable] = {}
        self.gate = None
        self.preprocessor = preprocessor
        self._setup_handlers()

    def _setup_handlers(self):
        for name in dir(self):
            method = getattr(self, name)
            if hasattr(method, '_message_names'):
                for message_name in method._message_names:
                    self.handlers[message_name] = method

    def set_gate(self, gate):
        self.gate = gate

    def recv(self, message: Message):
        if self.preprocessor and self.preprocessor.pre_process(self, message):
            handler = self.handlers.get(message.message_name, None)
            if handler:
                handler(self, message)

    def send(self, message: Message):
        # All messages are sent to the 'gate' regardless of the 'to_agent' value.
        if self.gate and hasattr(self.gate, 'recv'):
            self.gate.recv(message)
        else:
            print("Gate is not set or does not have a 'recv' method.")

    @staticmethod
    def cast(message_type):
        def decorator(func):
            if not hasattr(func, '_message_names'):
                func._message_names = []
            func._message_names.append(message_type)
            return func
        return decorator
