class NodeMeta(type):
    def __new__(cls, name, bases, attrs):
        new_class = super(NodeMeta, cls).__new__(cls, name, bases, attrs)
        new_class.process_handlers = {}
        for key, value in attrs.items():
            if hasattr(value, "_message_type"):
                new_class.process_handlers[value._message_type] = value
        return new_class


class Node(metaclass=NodeMeta):
    def __init__(self, id):
        self.id = id

    @staticmethod
    def process(message_type):
        def decorator(func):
            func._message_type = message_type
            return func

        return decorator

    def handle_message(self, message_type, *args, **kwargs):
        if message_type in self.process_handlers:
            method = getattr(
                self, self.process_handlers[message_type].__name__
            )
            return method(*args, **kwargs)
        else:
            raise ValueError(f"No handler for message type {message_type}")
