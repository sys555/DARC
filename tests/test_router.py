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

    yield router.proxy()

    router.stop()


# @pytest.mark.skip('pass')
def test_gate_take_correct_router(config):
    router: Router = config
    # 验证 gate 中的 producer gate, consumer gate 保存的 router 对象是否正确
    producer_gate_instance_addr = router.node_gate_type_address_dict.get()[
        "Producer"
    ]
    producer_gate_instance: NodeGate = router.instance.get()[
        producer_gate_instance_addr
    ]
    assert (
        producer_gate_instance.proxy()
        .instance.get()[router.node_addr.get()]
        .actor_urn
        == router.actor_ref.actor_urn
    )

    consumer_gate_instance_addr = router.node_gate_type_address_dict.get()[
        "Consumer"
    ]
    consumer_gate_instance: NodeGate = router.instance.get()[
        consumer_gate_instance_addr
    ]
    assert (
        consumer_gate_instance.proxy()
        .instance.get()[router.node_addr.get()]
        .actor_urn
        == router.actor_ref.actor_urn
    )


# @pytest.mark.skip('pass')
def test_gate_transport_message(config):
    router: Router = config
    # 验证 gate 中的 producer gate, consumer gate 保存的 router 对象是否正确
    producer_gate_instance_addr = router.node_gate_type_address_dict.get()[
        "Producer"
    ]
    producer_gate_instance: NodeGate = router.instance.get()[
        producer_gate_instance_addr
    ]

    consumer_gate_instance_addr = router.node_gate_type_address_dict.get()[
        "Consumer"
    ]
    consumer_gate_instance: NodeGate = router.instance.get()[
        consumer_gate_instance_addr
    ]

    task_id = uuid.uuid4()

    producer_to_consumer_message = Message(
        message_name="Producer:Message",
        from_agent_type="NodeGate",
        task_id=task_id,
        from_node_type_name="Producer",
    )

    consumer_to_producer_message = Message(
        message_name="Message:Producer",
        from_agent_type="NodeGate",
        task_id=uuid.uuid4(),
        from_node_type_name="Message",
    )

    producer_gate_instance.proxy().send(
        producer_to_consumer_message, router.node_addr.get()
    )

    # 等待消息传递
    import time

    time.sleep(0.1)

    router_to_consumer_message = Message(
        message_name="Producer:Message",
        from_agent_type="Router",
        task_id=task_id,
        from_node_type_name="Producer",
    )
    assert compare_messages(
        consumer_gate_instance.proxy().message_box.get(),
        router_to_consumer_message,
    )


# @pytest.mark.skip("pass")
def test_node_instance_spawn(config):
    router: Router = config
    router.spawn_real_instance(Producer, ("alice",))
    producer_gate = NodeGate.start("Producer", MultiAddr("Producer"))

    # 等待 spawn 操作完成
    import time

    time.sleep(0.1)

    assert (
        producer_gate.proxy()
        .get_node_instance("Producer_1")
        .get()
        .proxy()
        .node_name.get()
        == "alice"
    )


# @pytest.mark.skip("pass")
def test_multi_router_nodegate_receive():
    question_answer_router = Router.start(MultiAddr("Questioner:Answer"))

    critic_answer_router = Router.start(MultiAddr("Critic:Answer"))

    answer_checker_router = Router.start(MultiAddr("Answer:Checker"))

    questioner_answer_message = Message(
        "Questioner:Answer",
        from_agent_type="NodeGate",
        task_id=uuid.uuid4(),
        from_node_type_name="Questioner",
    )

    critic_answer_message = Message(
        "Critic:Answer",
        from_agent_type="NodeGate",
        task_id=uuid.uuid4(),
        from_node_type_name="Critic",
    )

    answer_checker_message = Message(
        "Answer:Checker",
        from_agent_type="NodeGate",
        task_id=uuid.uuid4(),
        from_node_type_name="Answer",
    )

    question_answer_router.proxy().on_receive(questioner_answer_message)
    critic_answer_router.proxy().on_receive(critic_answer_message)
    answer_checker_router.proxy().on_receive(answer_checker_message)

    # 等待消息传递
    import time

    time.sleep(0.1)

    answer_node_gate = NodeGate.start("Answer", MultiAddr("Answer"))
    answer_node_gate_mailbox = answer_node_gate.proxy().message_box.get()

    assert len(answer_node_gate_mailbox) == 2
    # 创建一个从answer_node_gate_mailbox中提取task_id的集合
    received_task_ids = {msg.task_id for msg in answer_node_gate_mailbox}
    # 创建一个包含预期task_id的集合
    expected_task_ids = {
        questioner_answer_message.task_id,
        critic_answer_message.task_id,
    }
    # 确保每个预期的task_id都在收到的消息中
    assert received_task_ids == expected_task_ids

    checker_node_gate = NodeGate.start("Checker", MultiAddr("Checker"))
    checker_node_gate_mailbox = checker_node_gate.proxy().message_box.get()
    assert len(checker_node_gate_mailbox) == 1
    assert (
        checker_node_gate_mailbox[0].task_id == answer_checker_message.task_id
    )
