import unittest

from darc.darc.router import Router
from darc.darc.node_gate import NodeGate
from darc.darc.multi_addr import MultiAddr
from darc.darc.message import Message
from darc.darc.node import Node

from tests.darc_test.test_base import PingPonger
import copy
import uuid

PingPongerMessage = Message(message_name="PingPonger--PingPonger")


TestPingMessage = PingPongerMessage(
    message_id=uuid.uuid4(),
    from_agent="alice_addr",
    content=f"broadcasting ... I am alice",
    task_id=uuid.uuid4(),
)


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

    def test_point_to_point_send(self):
        pingpong_router = Router(MultiAddr("PingPonger--PingPonger"))
        pingpong_node_gate = NodeGate("PingPonger", MultiAddr("PingPonger"))

        pingpong_node_gate.spawn_new_actor(PingPonger, [(1, ("alice",)), (1, ("bob",))])

        alice = pingpong_node_gate.get_node_instance("PingPonger_0")
        bob = pingpong_node_gate.get_node_instance("PingPonger_1")
        TestPingMessage.from_agent = alice._node_addr
        TestPingMessage.to_agent = bob._node_addr
        alice.on_send(TestPingMessage)

        self.assertEqual(alice._message_box[0].task_id, TestPingMessage.task_id)
        self.assertEqual(bob._message_box[0].task_id, TestPingMessage.task_id)

        self.assertEqual(
            pingpong_router._message_box[0].task_id, TestPingMessage.task_id
        )
        self.assertEqual(
            pingpong_node_gate._message_box[0].task_id, TestPingMessage.task_id
        )

    def test_broadcast_send(self):
        pingpong_router = Router(MultiAddr("PingPonger--PingPonger"))
        pingpong_node_gate = NodeGate("PingPonger", MultiAddr("PingPonger"))

        pingpong_node_gate.spawn_new_actor(PingPonger, [(1, ("alice",)), (3, ("bob",))])

        alice = pingpong_node_gate.get_node_instance("PingPonger_0")
        bob_1 = pingpong_node_gate.get_node_instance("PingPonger_1")
        bob_2 = pingpong_node_gate.get_node_instance("PingPonger_2")
        bob_3 = pingpong_node_gate.get_node_instance("PingPonger_3")
        TestPingMessage.from_agent = alice._node_addr
        alice.on_send(TestPingMessage)

        self.assertEqual(bob_1._message_box[0].task_id, TestPingMessage.task_id)
        self.assertEqual(bob_2._message_box[0].task_id, TestPingMessage.task_id)
        self.assertEqual(bob_3._message_box[0].task_id, TestPingMessage.task_id)

    def test_random_send(self):
        pingpong_router = Router(MultiAddr("PingPonger--PingPonger"))
        pingpong_node_gate = NodeGate("PingPonger", MultiAddr("PingPonger"))
        pingpong_node_gate.spawn_new_actor(PingPonger, [(1, ("alice",)), (3, ("bob",))])
        alice = pingpong_node_gate.get_node_instance("PingPonger_0")
        bob_1 = pingpong_node_gate.get_node_instance("PingPonger_1")
        bob_2 = pingpong_node_gate.get_node_instance("PingPonger_2")
        bob_3 = pingpong_node_gate.get_node_instance("PingPonger_3")
        TestPingMessage.from_agent = alice._node_addr
        TestPingMessage.broadcasting = False
        TestPingMessage.to_agent = "None"
        alice.on_send(TestPingMessage)

        total_message_count = 0
        for node_instance in [bob_1, bob_2, bob_3]:
            if node_instance._message_box:
                self.assertEqual(
                    node_instance._message_box[0].task_id, TestPingMessage.task_id
                )
                total_message_count += 1

        self.assertEqual(total_message_count, 1)

    def tearDown(self) -> None:
        NodeGate.clear_all_node_gate()


if __name__ == "__main__":
    unittest.main()
