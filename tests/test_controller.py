import pytest

from darc.database import DatasetDB
from darc.attacker import Attacker
from darc.filter import Filter
from darc.llm import LLM_with_PPL
from darc.evaluator import Evaluator
from darc.leaderboard import LeaderBoard
from darc.darc.controller import Task, Graph


# 配置和初始化
@pytest.fixture
def setup_graph():
    config = {
        "node": [
            DatasetDB,
            Attacker,
            Filter,
            LLM_with_PPL,
            Evaluator,
            LeaderBoard,
        ],
        "edge": [
            (DatasetDB, Attacker),
            (DatasetDB, Filter),
            (DatasetDB, Evaluator),
            (Attacker, Filter),
            (Filter, LLM_with_PPL),
            (Filter, Attacker),
            (LLM_with_PPL, Evaluator),
            (Evaluator, DatasetDB),
            (Evaluator, LeaderBoard),
        ],
        "args": [
            (DatasetDB, 1, {"db": "NormalQ"}),
            (DatasetDB, 1, {"db": "NormalA"}),
            (DatasetDB, 1, {"db": "BadQ"}),
            (DatasetDB, 1, {"db": "BadA"}),
            (Evaluator, 1, {"mode": "Attack"}),
            (LLM_with_PPL, 2, {"llm": "GPT4"}),
        ],
    }
    return Graph.init(config)


# 测试图的构建
def test_graph_initialization(setup_graph):
    assert isinstance(setup_graph, Graph)
    assert (
        len(setup_graph.nodes) == 7
    )  # 确保所有节点都已初始化,其中LLM节点被初始化两份，用于流量均衡，所以一共7个节点


# 测试节点查找功能
@pytest.fixture
def node_ids(setup_graph):
    dataset_nodes = setup_graph.find_type("DatasetDB")
    leaderboard_nodes = setup_graph.find_type("LeaderBoard")
    assert dataset_nodes is not None
    assert leaderboard_nodes is not None
    assert isinstance(dataset_nodes[0], DatasetDB)
    assert isinstance(leaderboard_nodes[0], LeaderBoard)

    return {
        "dataset_node_id": dataset_nodes[0].id if dataset_nodes else None,
        "leaderboard_node_id": (
            leaderboard_nodes[0].id if leaderboard_nodes else None
        ),
    }


def test_find_node_types(node_ids):
    assert node_ids["dataset_node_id"] is not None
    assert node_ids["leaderboard_node_id"] is not None


# 测试任务设置和执行
@pytest.fixture
def task(setup_graph, node_ids):
    task = Task(setup_graph)
    task.set_entry_node(node_ids["entry_node_id"])
    task.set_exit_node(node_ids["exit_node_id"])
    return task


# 测试任务初始化
def test_task_initialization(task):
    assert isinstance(task, Task)


# 测试设置入口和出口节点
def test_set_entry_and_exit_nodes(task, node_ids):
    # 这些设置在fixture中已经完成，此处确认它们是否设置正确
    assert task.entry_node == node_ids["entry_node_id"]
    assert task.exit_node == node_ids["exit_node_id"]


# 测试任务的执行
def test_task_execution(task):
    task.set_initial_input("Select data from * sample(10)")
    task.run()  # 假设run方法执行任务并更新task.result
    assert task.result is not None  # 检查结果是否非空


# 测试结果的正确性
def test_result_correctness(task):
    expected_result = "expected task result"  # 根据实际情况修改期望结果
    assert task.result == expected_result
