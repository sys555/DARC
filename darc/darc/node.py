from darc.darc.actor import AbstractActor, Preprocessor, defaultdict
from darc.darc.message import Message
import json

def message_handler(message_names):
    def decorator(func):
        func._message_names = message_names
        return func
    return decorator

class GatherPreprocessor(Preprocessor):
    def __init__(self):
        self.messages = defaultdict(list)

    def pre_process(self, actor, message: Message) -> bool:
        # Assume the message content is a JSON string with a task_id
        content = json.loads(message.content)
        task_id = content['task_id']
        self.messages[task_id].append(content['data'])

        # Check if all parts are gathered, for demonstration assume a fixed number
        if len(self.messages[task_id]) >= 3:  # Assuming we wait for 3 parts
            # When all parts are gathered, we call the process method
            full_message = ' '.join(self.messages[task_id])
            processed_data = actor.process(full_message)
            actor.send(Message(content=processed_data, to_actor=message._to))
            del self.messages[task_id]  # Clear the gathered messages for this task_id
            return False  # Indicates that the message should not be processed further
        return False  # Processing is not complete, do not call process yet


class Node(AbstractActor):
    def __init__(self):
        self.handlers = {}
        for name in dir(self):
            method = getattr(self, name)
            if hasattr(method, '_message_names'):
                for message_name in method._message_names:
                    self.handlers[message_name] = method
        
        self.memory = []
        self._prefix = {}
        # {
        #     "attack match": ["attack node", "normal q"],
        #     "defence match": ["danger q"]
        # }
        self._next = {}
        # {      
        #     "attack match": ["LLM"],
        #     "defence match": ["attack node"]
        # }
        self.preprocessor = GatherPreprocessor()
        
    def process(self, message):
        handler = self.handlers.get(message.message_name, self.default_handler)
        return handler(message)

    def default_handler(self, message):
        return f"No handler for {message.message_name}"

    @message_handler(["Init"])
    def handle_init(self, message):
        return f"Initialized with {message.content}"

    @message_handler(["Data_Process"])
    def handle_data_processing(self, message):
        return f"Data processed: {message.content}"
    
    def handle_message(self, contents, message_name):
        # Dummy handler function
        return f"Handled {message_name} with contents: {', '.join(contents)}"