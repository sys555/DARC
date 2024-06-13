from darc.node import Node
from darc.message import Message
from darc.multi_addr import MultiAddr
from darc.router import Router
from darc.node_gate import NodeGate
from darc.logger import MASLogger
from darc.controller import Graph, Task, config_to_networkx, networkx_to_config
from darc.llm.proxy import get_answer_sync
from darc.agent.dev import PM, FeatureDev, QADev

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
    qadev_gate = NodeGate.start("QADev", MultiAddr("QADev"))

    yield router.proxy(), pm_gate.proxy(), feature_dev_gate.proxy(), qadev_gate.proxy()

    router.stop()
    pm_gate.stop()
    feature_dev_gate.stop()
    qadev_gate.stop()


@pytest.fixture(scope="module")
def user_case_config():
    config = {
        "node": [
            PM,
            FeatureDev,
            QADev,
        ],
        "edge": [
            (PM, FeatureDev),
            (FeatureDev, QADev),
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
            (
                QADev,
                1,
                [("Coob",)],
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

    # demand = "请用python帮我生成一个贪吃蛇的小游戏"
    demand = "请用python帮我生成一个整数加法函数"

    task_id = str(uuid.uuid4())

    bob = graph.find_node_with_name("Bob", "FeatureDev")
    coob = graph.find_node_with_name("Coob", "QADev")

    task = Task(
        graph = graph,
        task_id = task_id,
    )
    task.set_entry_node(alice)
    task.set_exit_node(coob)
    task.set_initial_input(demand)
    graph.run(task)

    import time

    time.sleep(1)

    # 'FeatureDev:QADev'
    # 'QADev:END
    assert len(coob.proxy().message_box.get()) is 2
    # PM 2, FeatureDev 2, QADev 3
    assert len(mas_logger.logbook) is 7
