from darc.darc.node_gate import NodeGate
from darc.darc.message import Message
import unittest
from unittest import mock
import uuid
from .test_base import PingPonger


RouterMessage = Message("PingPonger--PingPonger")


class TestNodeGate(unittest.TestCase):
    def setUp(self) -> None:
        # mock a router and two node
        self.node_gate = NodeGate("PingPongerGate", "test_ping_ponger_gate_addr")
        self.node_gate.spawn_new_actor(
            PingPonger, [("alice", "alice_addr"), ("bob", "bob_addr")]
        )
        self.alice = PingPonger("alice", "alice_addr")
        self.bob = PingPonger("bob", "bob_addr")
        return super().setUp()

    def test_spawn_new_actor(self):
        self.node_gate.get_address_book = mock.Mock(
            return_value={
                "alice_addr": PingPonger("alice", "alice_addr"),
                "bob_addr": PingPonger("bob", "bob_addr"),
            }
        )

        self.assertEqual(
            id(self.alice), id(self.node_gate.get_address_book()["alice_addr"])
        )
        self.assertEqual(
            id(self.bob), id(self.node_gate.get_address_book()["bob_addr"])
        )

    def test_send(self):
        # mock message from router
        mock_router_message = RouterMessage(
            message_id=uuid.uuid4(), from_agent="test_ping_ponger_router_addr", to_agent="test_ping_ponger_gate_addr"
        )
        

    def test_recv(self):
        pass

    def tearDown(self) -> None:
        return super().tearDown()
