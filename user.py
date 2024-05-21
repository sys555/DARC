from darc.filter import Filter
from darc.llm import LLM_with_PPL
from darc.leaderboard import LeaderBoard
from darc.darc.controller import Task, Graph
from darc.database import DatasetDB
from darc.evaluator import AttackEvaluator
from darc.attacker import Attacker

from loguru import logger
        

def create_graph():
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
            ( Attacker,
                2,
                {},
            ),
        ],  # 如果在args里面没有出现，但在node里面出现的实体，则使用默认参数，初始化一个默认实例
    }
    return Graph.init(config)

def node_ids(setup_graph):
    attacker_nodes = setup_graph.find_type("Attacker")
    leaderboard_nodes = setup_graph.find_type("LeaderBoard")

    return {
        "attacker_node_id": (
            attacker_nodes[0] if attacker_nodes else None
        ),
        "leaderboard_node_id": (
            leaderboard_nodes[0]
            if leaderboard_nodes
            else None
        ),
    }

if __name__ == '__main__':
    graph = create_graph()
    task = None
    [logger.info(node) for node in graph.show()]
    for i in range(6):
        task = Task(graph)
        task.entry_node = graph.find_type("Attacker")[i % 2]
        task.exit_node = graph.find_type("LeaderBoard")[0]
        task.initial_input = "task"
        task.run()
    
    import time
    time.sleep(3)
    
    logger.info(task.exit_node.proxy().leaderboard.get())
    