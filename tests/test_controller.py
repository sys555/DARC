import pytest


from darc.filter import Filter, ev
from darc.llm import LLM_with_PPL
from darc.leaderboard import LeaderBoard
from darc.controller import Task, Graph
from darc.database import DatasetDB
from darc.attacker import Attacker

from darc.evaluator import AttackEvaluator

import logging


# 配置和初始化
@pytest.fixture
def setup_graph():
    config = {
        "node": [
            DatasetDB,
            Attacker,
            Filter,
            LLM_with_PPL,
            AttackEvaluator,
            LeaderBoard,
        ],
        "edge": [
            (DatasetDB, Attacker),
            (DatasetDB, Filter),
            (DatasetDB, AttackEvaluator),
            (Attacker, DatasetDB),
            (Attacker, Filter),
            (Filter, LLM_with_PPL),
            (Filter, Attacker),
            (LLM_with_PPL, AttackEvaluator),
            (AttackEvaluator, DatasetDB),
            (AttackEvaluator, LeaderBoard),
        ],
        "args": [
            (
                DatasetDB,
                1,
                {"db": "chanllenge"},
            ),  # 实例化一个参数为{"db": "chanllenge"}的DatasetDB对象
            (
                LLM_with_PPL,
                2,
                {"llm": "GPT4"},
            ),  # 实例化两个参数为{"llm": "GPT4"}的LLM_with_PPL对象，用于流量控制
            (Attacker, 2, {}),
        ],  # 如果在args里面没有出现，但在node里面出现的实体，则使用默认参数，初始化一个默认实例
    }
    return Graph.init(config)


# 测试图的构建
@pytest.mark.skip(reason="MAS change")
def test_graph_initialization(setup_graph):
    assert isinstance(setup_graph, Graph)
    assert (
        len(setup_graph.nodes) == 8
    )  # 确保所有节点都已初始化， 根据config的args参数，一共7个节点 6类节点，其中llm有两个


# 测试节点查找功能
@pytest.fixture
def node_ids(setup_graph):
    attacker_nodes = setup_graph.find_type("Attacker")
    leaderboard_nodes = setup_graph.find_type("LeaderBoard")
    assert attacker_nodes is not None
    assert leaderboard_nodes is not None
    assert attacker_nodes[0].proxy().class_name.get() is "Attacker"
    assert leaderboard_nodes[0].proxy().class_name.get() is "LeaderBoard"
    # assert isinstance(attacker_nodes[0], Attacker)
    # assert isinstance(leaderboard_nodes[0], LeaderBoard)

    return {
        "attacker_node_id": (attacker_nodes[0] if attacker_nodes else None),
        "leaderboard_node_id": (
            leaderboard_nodes[0] if leaderboard_nodes else None
        ),
    }


@pytest.mark.skip(reason="MAS change")
def test_find_node_types(node_ids):
    assert node_ids["attacker_node_id"] is not None
    assert node_ids["leaderboard_node_id"] is not None


# 测试任务设置和执行
@pytest.fixture
def task(setup_graph, node_ids):
    task = Task(setup_graph)
    task.set_entry_node(node_ids["attacker_node_id"])
    task.set_exit_node(node_ids["leaderboard_node_id"])

    return task


@pytest.mark.skip(reason="MAS change")
# 测试任务初始化
def test_task_initialization(task):
    assert isinstance(task, Task)


@pytest.mark.skip(reason="MAS change")
# 测试设置入口和出口节点
def test_set_entry_and_exit_nodes(task, node_ids):
    # 这些设置在fixture中已经完成，此处确认它们是否设置正确
    assert (
        task.entry_node == node_ids["attacker_node_id"]
    )  # 向entry_node注入消息
    assert (
        task.exit_node == node_ids["leaderboard_node_id"]
    )  # 观察exit_node的改动


@pytest.mark.skip(reason="MAS change")
# 测试任务的执行
def test_task_execution(task):
    task.set_initial_input("Select data from * sample(10)")
    task.run()  # 假设run方法执行任务并更新task.result
    import time

    time.sleep(6)

    # 检查该任务是否在 出口节点 的邮箱中
    logging.info(task.exit_node.proxy().message_map.get())
    found_match = False
    for message in task.exit_node.proxy().message_map.get()[
        "AttackEvaluator:LeaderBoard"
    ]:
        if message.task_id == task.task_id:
            found_match = True
    assert found_match


@pytest.mark.skip(reason="MAS change")
# 测试结果的正确性
def test_result_correctness(task):
    expected_result = None  # 根据实际情况修改期望结果
    assert task.result == expected_result
