import unittest
from unittest import mock

from darc.darc.node_gate import NodeGate
from .test_base import PingPonger, TestPingMessage


class TestNodeGate(unittest.TestCase):
    def setUp(self) -> None:
        # mock a router and two node
        self.node_gate = NodeGate("PingPongerGate", "test_ping_ponger_gate_addr")
        self.node_gate.spawn_new_actor(
            PingPonger, [("alice", "alice_addr"), ("bob", "bob_addr")]
        )
        self.alice = PingPonger("alice", "alice_addr")
        self.bob = PingPonger("bob", "bob_addr")
        self.cindy = PingPonger("cindy", "cindy_addr")
        return super().setUp()

    def test_spawn_new_actor(self):
        self.node_gate._address_book = mock.Mock(
            return_value={"alice_addr", "bob_addr", "cindy_addr"}
        )

    def test_send(self):
        # send mock message to node
        self.node_gate.send(TestPingMessage)
        self.bob._message_box = mock.Mock(return_value=[TestPingMessage])
        self.cindy._message_box = mock.Mock(return_value=[TestPingMessage])

    def test_recv(self):
        # mock message from alice
        self.alice.broadcast_ping()
        self.node_gate._message_box = mock.Mock(return_value=[TestPingMessage])

    def tearDown(self) -> None:
        return super().tearDown()


if __name__ == "__main__":
    unittest.main()
