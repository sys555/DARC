from .actor import AbstractActor


class Router(AbstractActor):
    def __init__(self, address, name):
        super().__init__()
        self._address = address
        self._name = name

    def get_address_book(self):
        pass

    def send(self):
        pass

    def recv(self):
        pass

    def spawn_new_actor(self):
        return super().spawn_new_actor()

    def _broadcast(self):
        pass

    def _point_to_point(self):
        pass

    def _random_sample(self):
        pass
