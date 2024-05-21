
# DARC for LLM Safety Challenge
[![codecov](https://codecov.io/gh/SACLabs/darc/branch/main/graph/badge.svg?token=darc_token_here)](https://codecov.io/gh/SACLabs/darc)
[![CI](https://github.com/SACLabs/darc/actions/workflows/main.yml/badge.svg)](https://github.com/SACLabs/darc/actions/workflows/main.yml)


# 研发专区
## 文件目录说明
仓库目录主要分为三块，分别是docs、darc以及tests。其中darc文件夹为代码文件，test为测试代码文件，doc为文档。

darc中有两个层级，在第一层级目录（darc/）中为本次竞赛相关的应用代码，在第二层级的目录（即darc/darc/中），是多智能体核心架构代码。

## PR提交说明
所有改动请先从dev新建分支，然后向dev提交PR，review过后进行分支合并。
请见[飞书文档](https://aicarrier.feishu.cn/docx/HNw9deXBtojuv6xIZXTck6Zfnfg?from=from_copylink)

<!--  DELETE THE LINES ABOVE THIS AND WRITE YOUR PROJECT README BELOW -->

---
# 用户使用说明: 

A typical application of our system. 

## 场景难点:
1. multiple heterogeneous intelligences
2. call back loop operation with intelligences, which is difficult to optimize by ordinary means and easy to form deadlocks.
3. asynchronous message merge operation of intelligences
4. intelligent message fork operation
5. there are conditional smart body decisions
6. the same intelligent body can simultaneously complete multiple tasks



## Pre-requisites

1. Install [conda](https://docs.conda.io/en/latest/miniconda.html) if you want to keep your environment clean. 
Then create a conda environment.

```bash
conda create -n last python=3.10
conda activate your_env_name
```
2. Install [poetry](https://python-poetry.org/docs/#installation)

## Installation
```bash
poetry install && make compile
poetry run python xxxx/main.py
```

## Usage
```py
"""Step1: 组件引入，先将所有的组件的入口Class全部import
"""
from darc.filter import Filter
from darc.llm import LLM_with_PPL
from darc.leaderboard import LeaderBoard
from darc.darc.controller import Task, Graph
from darc.database import DatasetDB
from darc.evaluator import AttackEvaluator
from darc.attacker import Attacker

from loguru import logger

"""Step2: 关系定义，使用json
"""
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
            ),  # 实例化两个参数为{"llm": "GPT4"}的LLM_with_PPL对象，作为被攻击者
            ( Attacker,
                2,
                {},
                # 实例化两个默认参数的Attacker 作为攻击赛道的比赛参与者
            ),
        ],  # 如果在args里面没有出现，但在node里面出现的实体，则使用默认参数，初始化一个默认实例
    }
    return Graph.init(config)

"""Step3：设置任务，开始运行
1. 建立运行图
2. 设定入口agent和出口agent
2. 设置初始输入
3. 自动运行
"""
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
    
    # 等待 Actor 数据处理与消息流通
    import time
    time.sleep(3)
    
    # 获取并记录出口节点，即 LeaderBoard 节点，的数据
    logger.info(task.exit_node.proxy().leaderboard.get())


# 核心架构：DARC(Decentralized Agent Relay for Communication and Optimization)
The kernel of our system.

## Communication
TBD
## Optimization
TBD
## Development

Read the [CONTRIBUTING.md](CONTRIBUTING.md) file.
```

## 组件实现样例
### LLM Class
``` py
class LLM_with_PPL(Node):
    def __init__(self, llm="GPT-4"):
        super().__init__()
        self.llm = llm
        self.num_llm_batch = 32
        self.llm_batch_msg = []

    @Node.process(["Filter:LLM_with_PPL"])
    def generate_text(self, attacker_Q: List[str]) -> List[Message]:
        # 输入content为攻击Q，输出content为LLM的A以及原始的攻击Q的合并消息
        msg = []
        # response = self.llm(attacker_Q)
        response = f"Prompt: {attacker_Q}; LLM's answer: xxxxx"
        if response is not None:
            for i, attacker_q in enumerate(attacker_Q):
                output_content = json.dumps([attacker_q, response[i]])
                # 将Q和对应的A以某种用户定义的形式进行拼接
                msg.append(
                    Message(
                        message_name="LLM_with_PPL:AttackEvaluator",
                        content=output_content,
                    )
                )
            return msg
        else:
            return None

    # LLM函数内部支持batch操作
    def llm(self, inp: str):
        responces = None
        self.llm_batch_msg.append(inp)
        if len(self.llm_batch_msg) >= self.num_llm_batch:
            responces = self.batch_llm(self.llm_batch_msg)
        return responces

    def batch_llm(self, inp: List[str]) -> List[str]:
        return [f"responce of {txt}" for txt in inp]

```
### Attacker Class
``` py
class Attacker(Node):
    @Node.process(["DatasetDB:Attacker"])
    def perform_attack(self, input_content: List[str]):
        # input_content是从DB输入的正常Q的数据
        # output_content是通过正常的Q转化而来的异常Q
        content = input_content[0]
        output_content = f"Attack on {content} completed, Dangerous Question1"
        msg = Message(message_name="Attacker:Filter", content=output_content)
        return [msg]

    @Node.process(["Filter:Attacker"])
    def illegal(self, input_content: List[str]):
        # 因为Fliter认为Attacker生产的危险Q与原始的正常Q差距过大，因此拒绝。
        # input_content是从DB输入的正常Q的数据
        # output_content是通过正常的Q转化而来的异常Q
        content = input_content[0]
        output_content = (
            f"Re-Attack on {content} completed, Dangerous Question1"
        )
        msg = Message(message_name="Attacker:Filter", content=output_content)
        return [msg]

    @Node.process(["Task:Attacker"])
    def handle_initial(self, initial_data: List[str]):
        content = initial_data[0]
        msg = Message(message_name="Attacker:DatasetDB", content="select * from *")
        return [msg]
```