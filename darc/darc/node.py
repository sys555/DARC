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
        
    def process_message(self, message):
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
        
    