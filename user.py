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
            2,
            [("Alice",),("io",)],
        ),  
        (
            FeatureDev,
            2,
            [("Bob",),("ki",)],
        ),  
        (
            QADev,
            2,
            [("Coob",),("vi",)],
        ),  
    ],
}

logger.debug(config)

# 将配置转换为networkx图
G = config_to_networkx(config)

# 将networkx图转换回配置
new_config = networkx_to_config(G)

graph = Graph.init(new_config)

import time
time.sleep(1)

logger.debug(graph.nodes)
#TODO: find_node_with_name return id
# mas_logger = MASLogger()
alice = graph.find_node_with_name("Alice", "PM")

# demand = "请用python帮我生成一个贪吃蛇的小游戏"
demand = "请用python帮我生成一个整数加法函数"

for _ in range(1):
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
time.sleep(160)

logger.info(graph.get_log(task_id))
logger.info(graph.get_result(task_id))