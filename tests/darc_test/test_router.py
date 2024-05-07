import unittest
from darc.darc.router import Router
from darc.darc.message import Message

from .test_base import PingPonger
import uuid

PingPong2PingPongMessage = Message("PingPong2PingPongMessage")


class TestRouter(unittest.TestCase):
    def setUp(self) -> None:
        self.alice_bob_router = Router("PingPonger -- PingPonger")
        self.alice_bob_router.get_address_book = unittest.mock(return_value={"PingPonger": "TestPingPongerAddr"}) 
        return super().setUp()


    def test_broadcast(self):
        pass

    def test_point_to_point(self):
        pass

    def test_random_sample(self):
        pass

    def test_send(self):
        pass

    def test_recv(self):
        pass

    def tearDown(self) -> None:
        del self.alice_bob_router
        return super().tearDown()


if __name__ == "__main__":
    unittest.main()
