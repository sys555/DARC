import unittest
from unittest import mock


from darc.darc.router import Router
from darc.darc.node_gate import NodeGate
from .test_base import TestPingMessage


class TestRouter(unittest.TestCase):
    def setUp(self) -> None:
        self.alice_bob_router = Router(
            "PingPonger -- PingPonger", "PingPongerRouterAddr"
        )
        self.pingpong_node_gate = NodeGate(
            "ping_pong_node_gate", "test_ping_pong_node_gate_addr"
        )
        return super().setUp()

    def test_spawn_new_actor(self):
        self.alice_bob_router.spawn_new_actor(
            [("ping_pong_node_gate", "test_ping_pong_node_gate_addr")]
        )
        self.alice_bob_router._address_book = mock.Mock(
            return_value={"test_ping_pong_node_gate_addr": self.pingpong_node_gate}
        )

    def test_send(self):
        # mock data from node_gate to node gate
        self.alice_bob_router.send(TestPingMessage)
        self.pingpong_node_gate._message_box = mock.Mock(return_value=[TestPingMessage])

    def test_recv(self):
        self.pingpong_node_gate.send(TestPingMessage)
        self.alice_bob_router._message_box = mock.Mock(return_value=[TestPingMessage])

    def tearDown(self) -> None:
        del self.alice_bob_router
        return super().tearDown()


if __name__ == "__main__":
    unittest.main()
