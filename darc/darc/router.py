from .actor import AbstractActor


class Router(AbstractActor):
    def __init__(self, address, name):
        super().__init__()
        self._addr = address
        self._router_name = name

    def get_address_book(self):
        pass

    def send(self, message):
        pass

    def recv(self):
        pass

    def spawn_new_actor(self, args_list):
        pass

    def _broadcast(self):
        pass

    def _point_to_point(self):
        pass

    def _random_sample(self):
        pass
