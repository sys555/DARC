from abc import ABCMeta


class AbstractActor(metaclass=ABCMeta):
    def __init__(self):
        self._address_book = dict()
        self._message_box = []

    def recv(self):
        raise NotImplementedError

    def send(self, message):
        raise NotImplementedError

    def spawn_new_actor(self, args_list):
        raise NotImplementedError
