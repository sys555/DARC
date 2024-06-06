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

graph = Graph.init(new_config)

#TODO: find_node_with_name return id
# mas_logger = MASLogger()
alice = graph.find_node_with_name("Alice", "PM")

# demand = "请用python帮我生成一个贪吃蛇的小游戏"
demand = "hi"

task_id = str(uuid.uuid4())

bob = graph.find_node_with_name("Bob", "FeatureDev")

task = Task(
    graph = graph,
    task_id = task_id,
)
task.set_entry_node(alice)
task.set_exit_node(bob)
task.set_initial_input(demand)
graph.run(task)
    
import time
time.sleep(8)

logger.info(graph.get_log(task_id))
logger.info(graph.get_result(task_id))