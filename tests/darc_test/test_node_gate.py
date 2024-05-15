import unittest
from darc.darc.router import Router
from darc.darc.node_gate import NodeGate
from darc.darc.multi_addr import MultiAddr

from tests.darc_test.test_base import TestPingMessage
import copy


class TestNodeGate(unittest.TestCase):
    def setUp(self):
        self.test_router = Router(MultiAddr("Questioner--Answer"))
        self.test_questioner_gate = NodeGate("Questioner", MultiAddr("Questioner"))
        self.test_answer_gate = NodeGate("Answer", MultiAddr("Answer"))
        self.test_message = copy.deepcopy(TestPingMessage)
        self.test_message.message_name = "Questioner--Answer"

    def test_unique(self):
        node_gate_instance_addr = self.test_router._node_gate_type_address_dict[
            "Questioner"
        ]
        node_gate_instance = self.test_router._instance[node_gate_instance_addr]
        self.assertEqual(id(self.test_questioner_gate), id(node_gate_instance))

    def test_message_send(self):
        self.test_questioner_gate.on_receive(self.test_message)
