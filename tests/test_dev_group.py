from darc.node import Node
from darc.message import Message
from darc.multi_addr import MultiAddr
from darc.router import Router
from darc.node_gate import NodeGate
from darc.logger import MASLogger
from darc.controller import Graph, Task, config_to_networkx, networkx_to_config
from darc.llm.proxy import get_answer_sync
from darc.agent.dev import PM, FeatureDev

from loguru import logger

import pytest
import uuid
import os


@pytest.fixture(scope="module")
def config():
    addr = MultiAddr("PM:FeatureDev")
    router = Router.start(addr)

    pm_gate = NodeGate.start("PM", MultiAddr("PM"))
    feature_dev_gate = NodeGate.start("FeatureDev", MultiAddr("FeatureDev"))

    yield router.proxy(), pm_gate.proxy(), feature_dev_gate.proxy()

    router.stop()
    pm_gate.stop()
    feature_dev_gate.stop()


@pytest.fixture(scope="module")
def user_case_config():
    config = {
        "node": [
            PM,
            FeatureDev,
        ],
        "edge": [
            (PM, FeatureDev),
        ],
        "args": [
            (
                PM,
                1,
                [("Alice",)],
            ),
            (
                FeatureDev,
                1,
                [("Bob",)],
            ),
        ],
    }

    # 将配置转换为networkx图
    G = config_to_networkx(config)

    # 将networkx图转换回配置
    new_config = networkx_to_config(G)
    yield Graph.init(new_config)


def test_graph_use_case(user_case_config):
    graph = user_case_config
    mas_logger = MASLogger()
    alice = graph.find_node_with_name("Alice", "PM")

    demand = "hi"
    task_id = str(uuid.uuid4())
    task_to_pm_message = Message(
        message_name="Task:PM",
        content=demand,
        task_id=task_id,
    )

    # alice.proxy().on_receive(task_to_pm_message)
    bob = graph.find_node_with_name("Bob", "FeatureDev")

    task = Task(graph=graph, task_id=task_id)
    task.set_entry_node(alice)
    task.set_exit_node(bob)
    task.set_initial_input(demand)
    graph.run(task)

    import time

    time.sleep(1)

    # 'PM:FeatureDev'
    # 'FeatureDev:END'
    assert len(bob.proxy().message_box.get()) is 2
    # PM 2, FeatureDev 3
    assert len(mas_logger.logbook) is 5
