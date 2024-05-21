from darc.filter import Filter
from darc.llm import LLM_with_PPL
from darc.leaderboard import LeaderBoard
from darc.darc.controller import Task, Graph
from darc.database import DatasetDB
from darc.evaluator import Evaluator, AttackEvaluator
from darc.attacker import Attacker

from loguru import logger

# """Step1: 组件引入，先将所有的组件的入口Class全部import
# """
# from dataset import DatasetDB
# from attacker import Attacker
# from filter import Filter
# from llm import LLM_with_PPL
# from attack_evaluator import Evaluator
# from leaderboard import LeaderBoard

# """Step2: 关系定义，使用json
# """
# config = {
# "node": [DatasetDB, Attacker, Filter, LLM_with_PPL, Evaluator, LeaderBoard]
# "edge": [(DatasetDB, Attacker), (DatasetDB, Filter), (DatasetDB, Evaluator), 
# (Attacker, Filter), 
# (Filter, LLM_with_PPL), (Filter, Attacker),
# (LLM_with_PPL, Evaluator),
# (AttackEvaluator, DatasetDB), (Evaluator, LeaderBoard), 
# ]
# "args": [(DatasetDB, 1, {"db":"NormalQ"}), (DatasetDB, 1, {"db":"NormalA"}),
#  (DatasetDB, 1, {"db":"BadQ"}), (DatasetDB, 1, {"db":"BadA"}), 
#  (Evaluator, 1, {"mode":"Attack"}), 
#  (LLM_with_PP, 1, {"llm": "GPT4"})
#  (Attacker, 2, {})]
#  }

# """Step3：设置任务，开始运行
# 1. 建立运行图
# 2. 设定入口agent和出口agent
# 2. 设置初始输入
# 3. 自动运行
# """

# Graph.check(config)  
# graph = Graph.init(config)

# ## todo: node
# ## graph.show()

# graph.find_type("DatasetDB")
# > DatasetDB(id="12345", db="NormalQ"), DatasetDB(id="54321", db="NormalA").....

# graph.find_type(LeaderBoard)
# > LeaderBoard(id="67891")

# task = Task(graph)
# task.set_entry_node("12345") #指定入口节点
# task.set_exit_node("67891") #指定出口节点
# task.set_initial_input("Select data from * sample(10)") # 指定初始条件
# task.run()

# """ 数据记录导出
# """
# task.save(path = ".......")

# if __name__ == '__main__':
#     graph = create_graph()
#     task = None
#     for i in range(10):
#         task = Task(graph)
#         task.entry_node = graph.find_type("Attacker")[i % 2]
#         task.exit_node = graph.find_type("LeaderBoard")[0]
#         task.initial_input = "task"
#         task.run()
        

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
    for i in range(10):
        task = Task(graph)
        task.entry_node = graph.find_type("Attacker")[i % 2]
        task.exit_node = graph.find_type("LeaderBoard")[0]
        task.initial_input = "task"
        task.run()
    
    import time
    time.sleep(2)
    
    logger.info(task.exit_node.proxy().leaderboard.get())
    