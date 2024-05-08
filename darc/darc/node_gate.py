from .actor import AbstractActor
from darc.darc.message import Message
import random

class NodeGate(AbstractActor):
    def __init__(self):
        self.success_rate = 0.9  # 90% success rate by default
        self.messages = []
        self._instance = {}

    def recv(self, message):
        # Simulate network transmission with a success based on the success rate
        if random.random() < self.success_rate:
            self.send(message)
            self.messages.append((message, "success"))
        else:
            self.messages.append((message, "failure"))

    def set_success_rate(self, rate):
        self.success_rate = rate
    
    def add_instance(self, instance):
        self._instance[instance.node_name] = instance
        
    def _broadcast(self):
        pass

    def _random_sample(self):
        pass

    def _point_to_point(self):
        pass

    def send(self, message: Message):
        self._instance[message.to_agent].recv(message)

    def spawn_new_actor(self):
        pass
    
