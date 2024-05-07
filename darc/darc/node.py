class Node:
    def __init__(self, id):
        self.id = id
        self.process_handlers = {}

    def process(self, message_type):
        def decorator(func):
            self.process_handlers[message_type] = func
            def wrapper(*args, **kwargs):
                return func(*args, **kwargs)
            return wrapper
        return decorator

    def handle_message(self, message_type, *args, **kwargs):
        if message_type in self.process_handlers:
            return self.process_handlers[message_type](self, *args, **kwargs)
        else:
            raise ValueError(f"No handler for message type {message_type}")
