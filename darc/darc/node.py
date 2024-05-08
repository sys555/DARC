from darc.darc.actor import AbstractActor

def message_handler(message_names):
    def decorator(func):
        func._message_names = message_names
        return func
    return decorator

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
        
    def gather(self, message):
        task_id = message.task_id
        message_name = message.message_name

        # Check if all messages for the task_id have been received
        required_nodes = set(self._prefix.get(message_name, []))
        received_nodes = set(msg.message_name for msg in self.memory if msg.task_id == task_id)

        if required_nodes.issubset(received_nodes):
            # All required messages are received
            contents = [msg.content for msg in self.memory if msg.task_id == task_id]
            self.memory = [msg for msg in self.memory if msg.task_id != task_id]  # Clear memory for this task
            return self.handle_message(contents, message_name)
        else:
            # Not all messages are received, store the current message
            self.memory.append(message)
            return "Waiting for more messages"

    def pre_process(self, message):
        self.gather(message)
    
    def handle_message(self, contents, message_name):
        # Dummy handler function
        return f"Handled {message_name} with contents: {', '.join(contents)}"