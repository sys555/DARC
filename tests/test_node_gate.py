import unittest

from darc.router import Router
from darc.node_gate import NodeGate
from darc.multi_addr import MultiAddr
import uuid

from tests.test_base import Producer, Consumer, compare_messages

import copy

from darc.message import Message
import pytest

from loguru import logger


@pytest.fixture(scope="module")
def config():
    addr = MultiAddr("Producer:Consumer")
    router = Router.start(addr)

    producer_gate = NodeGate.start("Producer", MultiAddr("Producer"))
    consumer_gate = NodeGate.start("Consumer", MultiAddr("Consumer"))

    yield router.proxy(), producer_gate.proxy(), consumer_gate.proxy()

    router.stop()
    producer_gate.stop()
    consumer_gate.stop()


# @pytest.mark.skip("pass")
def test_unique(config):
    router, producer_gate, _ = config
    import time

    time.sleep(0.1)
    node_gate_instance_addr = router.node_gate_type_address_dict.get()[
        "Producer"
    ]
    node_gate_instance = router.instance.get()[node_gate_instance_addr]

    assert node_gate_instance.actor_urn == producer_gate.actor_ref.actor_urn


# @pytest.mark.skip("pass")
def test_point_to_point_send(config):
    router, producer_gate, consumer_gate = config

    alice = producer_gate.spawn_new_actor(Producer, ("alice",)).get()
    bob = consumer_gate.spawn_new_actor(Consumer, ("bob",)).get()

    import time

    time.sleep(0.1)

    from_agent = alice.proxy().node_addr.get()
    to_agent = bob.proxy().node_addr.get()
    alice_to_bob_message = Message(
        message_name="Producer:Consumer",
        from_agent=alice.proxy().node_addr.get(),
        to_agent=bob.proxy().node_addr.get(),
        from_agent_type="RealNode",
        task_id=str(uuid.uuid4()),
    )
    alice.proxy().on_send(alice_to_bob_message)

    # 等待消息传递
    import time

    time.sleep(0.1)

    # assert compare_messages(alice_to_bob_message, bob.proxy().message_box.get()[0])
    assert (
        alice_to_bob_message.task_id
        == bob.proxy().message_box.get()[0].task_id
    )


# def test_broadcast_send(config):
#     router, producer_gate, consumer_gate = config

#     producer_gate.spawn_new_actor(Producer, ("alice",))
#     consumer_gate.spawn_new_actor(Consumer, ("bob",))
#     consumer_gate.spawn_new_actor(Consumer, ("dave",))
#     import time

#     time.sleep(0.1)
#     # TODO: 完成广播测试
#     assert True


# import unittest


# from gmaf.router import Router
# from gmaf.node_gate import NodeGate
# from gmaf.multi_addr import MultiAddr
# from gmaf.message import Message
# from tests.test_base import PingPonger
# import copy
# import uuid


# PingPongerMessage = Message(message_name="PingPonger--PingPonger")


# TestPingMessage = PingPongerMessage(
#     message_id=uuid.uuid4(),
#     from_agent="alice_addr",
#     content=f"broadcasting ... I am alice",
#     task_id=uuid.uuid4(),
# )


# class TestNodeGate(unittest.TestCase):
#     def setUp(self):
#         self.test_router = Router(MultiAddr("Questioner--Answer"))
#         self.test_questioner_gate = NodeGate("Questioner", MultiAddr("Questioner"))
#         self.test_answer_gate = NodeGate("Answer", MultiAddr("Answer"))
#         self.test_message = copy.deepcopy(TestPingMessage)
#         self.test_message.message_name = "Questioner--Answer"

#     def test_unique(self):
#         node_gate_instance_addr = self.test_router._node_gate_type_address_dict[
#             "Questioner"
#         ]
#         node_gate_instance = self.test_router._instance[node_gate_instance_addr]
#         self.assertEqual(id(self.test_questioner_gate), id(node_gate_instance))

#     def test_point_to_point_send(self):
#         pingpong_router = Router(MultiAddr("PingPonger--PingPonger"))
#         pingpong_node_gate = NodeGate("PingPonger", MultiAddr("PingPonger"))

#         pingpong_node_gate.spawn_new_actor(PingPonger, [(1, ("alice",)), (1, ("bob",))])

#         alice = pingpong_node_gate.get_node_instance("PingPonger_0")
#         bob = pingpong_node_gate.get_node_instance("PingPonger_1")
#         TestPingMessage.from_agent = alice._node_addr
#         TestPingMessage.to_agent = bob._node_addr
#         alice.on_send(TestPingMessage)

#         self.assertEqual(alice._message_box[0].task_id, TestPingMessage.task_id)
#         self.assertEqual(bob._message_box[0].task_id, TestPingMessage.task_id)

#         self.assertEqual(
#             pingpong_router._message_box[0].task_id, TestPingMessage.task_id
#         )
#         self.assertEqual(
#             pingpong_node_gate._message_box[0].task_id, TestPingMessage.task_id
#         )

#     def test_broadcast_send(self):
#         pingpong_router = Router(MultiAddr("PingPonger--PingPonger"))
#         pingpong_node_gate = NodeGate("PingPonger", MultiAddr("PingPonger"))

#         pingpong_node_gate.spawn_new_actor(PingPonger, [(1, ("alice",)), (3, ("bob",))])

#         alice = pingpong_node_gate.get_node_instance("PingPonger_0")
#         bob_1 = pingpong_node_gate.get_node_instance("PingPonger_1")
#         bob_2 = pingpong_node_gate.get_node_instance("PingPonger_2")
#         bob_3 = pingpong_node_gate.get_node_instance("PingPonger_3")
#         TestPingMessage.from_agent = alice._node_addr
#         alice.on_send(TestPingMessage)

#         self.assertEqual(bob_1._message_box[0].task_id, TestPingMessage.task_id)
#         self.assertEqual(bob_2._message_box[0].task_id, TestPingMessage.task_id)
#         self.assertEqual(bob_3._message_box[0].task_id, TestPingMessage.task_id)

#     def test_random_send(self):
#         pingpong_router = Router(MultiAddr("PingPonger--PingPonger"))
#         pingpong_node_gate = NodeGate("PingPonger", MultiAddr("PingPonger"))
#         pingpong_node_gate.spawn_new_actor(PingPonger, [(1, ("alice",)), (3, ("bob",))])
#         alice = pingpong_node_gate.get_node_instance("PingPonger_0")
#         bob_1 = pingpong_node_gate.get_node_instance("PingPonger_1")
#         bob_2 = pingpong_node_gate.get_node_instance("PingPonger_2")
#         bob_3 = pingpong_node_gate.get_node_instance("PingPonger_3")
#         TestPingMessage.from_agent = alice._node_addr
#         TestPingMessage.broadcasting = False
#         TestPingMessage.to_agent = "None"
#         alice.on_send(TestPingMessage)

#         total_message_count = 0
#         for node_instance in [bob_1, bob_2, bob_3]:
#             if node_instance._message_box:
#                 self.assertEqual(
#                     node_instance._message_box[0].task_id, TestPingMessage.task_id
#                 )
#                 total_message_count += 1

#         self.assertEqual(total_message_count, 1)

#     def tearDown(self) -> None:
#         NodeGate.clear_all_node_gate()


# if __name__ == "__main__":
#     unittest.main()
