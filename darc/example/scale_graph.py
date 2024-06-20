import json
import os
import random
import time
import uuid

import matplotlib.pyplot as plt
import networkx as nx
import psutil
import pytest
from loguru import logger

from darc.agent.dev import PM, FeatureDev, QADev
from darc.controller import Graph, Task
from darc.logger import MASLogger
from darc.node import Node

# 定义角色和颜色
roles = ["PM", "FeatureDev", "QADev"]
roles_map = {
    "PM": PM,
    "FeatureDev": FeatureDev,
    "QADev": QADev,
}
colors = ["red", "green", "blue"]

# 创建随机分区图
sizes = [150, 200, 150]  # 每个 group 节点数量
p_in = 0.5
p_out = 0.05
G = nx.random_partition_graph(sizes, p_in, p_out, seed=42)

# 转换为 MultiDiGraph
MDG = nx.MultiDiGraph()
for i, block in enumerate(G.graph["partition"]):
    role = roles[i]
    for node in block:
        MDG.add_node(node, role=role, name=f"Node{node}-{role}")

# 添加边，只添加社区间单向边
for u, v in G.edges():
    if MDG.nodes[u]["role"] != MDG.nodes[v]["role"]:
        if roles.index(MDG.nodes[u]["role"]) < roles.index(
            MDG.nodes[v]["role"]
        ):
            MDG.add_edge(u, v)

# 重构args部分
args = []
for role in roles:
    nodes_in_role = [
        node for node in MDG.nodes() if MDG.nodes[node]["role"] == role
    ]
    names_in_role = [(MDG.nodes[node]["name"],) for node in nodes_in_role]
    args.append((roles_map[role], len(nodes_in_role), names_in_role))

# 构建配置字典
config = {
    "node": [roles_map[role] for role in roles],
    "edge": [
        (PM, FeatureDev),
        (FeatureDev, QADev),
        (QADev, PM),
    ],
    "args": args,
}

logger.debug(config)

# # 绘制图形
# pos = nx.spring_layout(MDG)  # 为有向图计算布局
# for role, color in zip(roles, colors):
#     nx.draw_networkx_nodes(MDG, pos, nodelist=[n for n in MDG.nodes if MDG.nodes[n]['role'] == role],
#                         node_color=color, node_size=100, label=role)
# nx.draw_networkx_edges(MDG, pos, arrowstyle='-|>', arrowsize=10, width=1)
# nx.draw_networkx_labels(MDG, pos, labels={n: MDG.nodes[n]['name'] for n in MDG.nodes()})
# plt.title("MultiDiGraph Visualization")
# plt.legend()
# plt.show()

graph = Graph.init(config)

import time

time.sleep(1)

logger.debug(graph.nodes)

alice = graph.find_node_with_name("Node0-PM", "PM")

pm_group = graph.find_type("PM")
qadev_group = graph.find_type("QADev")

demand = "请用python帮我随便生成一些简单的python教程入门代码"

for i in range(10000):
    if i % 1000 == 0:
        logger.info(i)
    task_id = str(uuid.uuid4())

    task = Task(
        graph=graph,
        task_id=task_id,
    )
    task.set_entry_node(random.choice(pm_group))
    task.set_exit_node(random.choice(qadev_group))
    task.set_initial_input(demand)
    graph.run(task)


import psutil
import time

def average_cpu_memory_for_current_process(duration=30, interval=1):
    # 获取当前进程的引用
    current_process = psutil.Process()

    cpu_percentages = []
    memory_percentages = []

    # 计算测量的次数
    num_iterations = int(duration / interval)

    # 每隔一定时间(interval秒)，收集当前进程的CPU和内存使用率
    for _ in range(num_iterations):
        # 收集当前进程的CPU使用率
        # 注意：由于psutil的特性，cpu_percent()调用应当设置interval=None来直接获取当前时刻的CPU使用率
        cpu_usage = current_process.cpu_percent(interval=None)
        cpu_percentages.append(cpu_usage)

        # 收集当前进程的内存使用率
        memory_info = current_process.memory_percent()
        memory_percentages.append(memory_info)

        print(f"Collected CPU: {cpu_usage}%, Memory: {memory_info}%")

        # 等待interval秒
        time.sleep(interval)

    # 计算平均使用率
    average_cpu = sum(cpu_percentages) / len(cpu_percentages)
    average_memory = sum(memory_percentages) / len(memory_percentages)

    return average_cpu, average_memory

# 运行函数并打印结果
duration = 128
average_cpu, average_memory = average_cpu_memory_for_current_process(duration=duration, interval=8)
print(f"Average CPU Usage of current process over {duration} seconds: {average_cpu}%")
print(f"Average Memory Usage of current process over {duration} seconds: {average_memory}%")
