class Message():
    def __init__(self, from_actor: str = "", to_actor: str = "", content: str = "", task_id: str = "", message_name: str = ""):
        self._from = from_actor
        self._to = to_actor
        self.content = content
        self.task_id = task_id
        self.message_name = message_name