from darc.actor import AbstractActor


class Node(AbstractActor):
    def __init__(self):
        super().__init__()

    def send(self):
        pass

    def recv(self):
        pass

    def spawn_new_actor(self):
        pass
