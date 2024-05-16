import unittest

import os
import sys

sys.path.append("/home/PJLAB/chenliang/Desktop/AIlab/DARC")

from darc.darc.router import Router
from darc.darc.node_gate import NodeGate
from darc.darc.multi_addr import MultiAddr
import uuid

# from tests.darc_test.test_base import TestPingMessage

import copy

from darc.darc.message import Message


PingPongerMessage = Message(message_name="PingPonger--PingPonger")


TestPingMessage = PingPongerMessage(
    message_id=uuid.uuid4(),
    from_agent="alice_addr",
    content=f"broadcasting ... I am alice",
    task_id=uuid.uuid4(),
)


class TestRouter(unittest.TestCase):
    def setUp(self):
        self.test_multi_addr = MultiAddr("PingPonger--PingPonger")
        self.test_router = Router(self.test_multi_addr)

    def test_addr(self):
        # spawn的node gate实例
        node_gate_instance_addr = self.test_router._node_gate_type_address_dict[
            "PingPonger"
        ]
        node_gate_instance = self.test_router._instance[node_gate_instance_addr]
        # 对比node gate实例的address book
        self.assertEqual(
            id(node_gate_instance._instance[self.test_router._node_addr]),
            id(self.test_router),
        )

    def test_router_nodegate_receieve(self):
        test_router_message = copy.deepcopy(TestPingMessage)
        test_router_message.from_agent_type = "NodeGate"
        test_router_message.from_node_type_name = "PingPonger"
        self.test_router.on_receive(test_router_message)
        # nodegate -- router
        mailbox = self.test_router._message_box
        self.assertEqual(TestPingMessage.task_id, mailbox[0].task_id)

    def test_multi_router_nodegate_receieve(self):
        question_answer_router = Router(MultiAddr("Questioner--Answer"))

        critic_answer_router = Router(MultiAddr("Critic--Answer"))

        answer_checker_router = Router(MultiAddr("Answer--Checker"))

        questioner_answer_message = Message(
            "Questioner--Answer",
            from_agent_type="NodeGate",
            task_id=uuid.uuid4(),
            from_node_type_name="Questioner",
        )

        critic_answer_message = Message(
            "Critic--Answer",
            from_agent_type="NodeGate",
            task_id=uuid.uuid4(),
            from_node_type_name="Critic",
        )

        answer_checker_message = Message(
            "Answer--Checker",
            from_agent_type="NodeGate",
            task_id=uuid.uuid4(),
            from_node_type_name="Answer",
        )

        question_answer_router.on_receive(questioner_answer_message)
        critic_answer_router.on_receive(critic_answer_message)
        answer_checker_router.on_receive(answer_checker_message)

        answer_node_gate = NodeGate("Answer", MultiAddr("Answer"))
        answer_node_gate_mailbox = answer_node_gate._message_box
        self.assertEqual(len(answer_node_gate_mailbox), 2)
        self.assertEqual(
            answer_node_gate_mailbox[0].task_id, questioner_answer_message.task_id
        )
        self.assertEqual(
            answer_node_gate_mailbox[1].task_id, critic_answer_message.task_id
        )

        checker_node_gate = NodeGate("Checker", MultiAddr("Checker"))
        checker_node_gate_mailbox = checker_node_gate._message_box
        self.assertEqual(len(checker_node_gate_mailbox), 1)
        self.assertEqual(
            checker_node_gate_mailbox[0].task_id, answer_checker_message.task_id
        )

    def tearDown(self) -> None:
        NodeGate.clear_all_node_gate()
        return super().tearDown()


if __name__ == "__main__":
    unittest.main()
