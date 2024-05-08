import uuid

from darc.darc.node import Node
from darc.darc.message import Message


PingMessage = Message(message_name="PingMessage")
PongMessage = Message(message_name="PongMessage")
ArgueMessage = Message(message_name="ArgueMessage")

TestPingMessage = PingMessage(
    message_id=uuid.uuid4(),
    from_agent="alice_addr",
    content=f"broadcasting ... I am alice",
    task_id=uuid.uuid4(),
)


class PingPonger(Node):
    def __init__(self, node_name, address):
        super().__init__(node_name, address)

    def broadcast_ping(self):
        message_uid = uuid.uuid4()
        task_id = uuid.uuid4()
        ping_message = PingMessage(
            message_id=message_uid,
            from_agent=self._addr,
            content=f"broadcasting ... I am {self._node_name}",
            task_id=task_id,
        )
        self.send(ping_message)

    @Node.cast("PingMessage")
    def pong(self, message: Message):
        pong_message = PongMessage(
            message_id=message.message_id,
            from_agent=self._addr,
            to_agent=message.from_agent,
            content=f"hello, I am {self._node_name}",
            task_id=message.task_id,
        )
        self.send(pong_message)
        