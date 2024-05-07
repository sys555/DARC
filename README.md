
# DARC: Decentralized Agent Relay for Communication and Optimization
[![codecov](https://codecov.io/gh/SACLabs/darc/branch/main/graph/badge.svg?token=darc_token_here)](https://codecov.io/gh/SACLabs/darc)
[![CI](https://github.com/SACLabs/darc/actions/workflows/main.yml/badge.svg)](https://github.com/SACLabs/darc/actions/workflows/main.yml)




<!--  DELETE THE LINES ABOVE THIS AND WRITE YOUR PROJECT README BELOW -->

---
# Usage: LLM Safety Challenge

A typical application of our system. 

## Difficulties:
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
from dataset import DatasetDB
from attacker import Attacker
from filter import Filter
from llm import LLM_with_PPL
from attack_evaluator import Evaluator
from leaderboard import LeaderBoard

"""Step2: 关系定义，使用json
"""
config = {
"node": [DatasetDB, Attacker, Filter, LLM_with_PPL, Evaluator, LeaderBoard]
"edge": [(DatasetDB, Attacker), (DatasetDB, Filter), (DatasetDB, Evaluator), 
(Attacker, Filter), 
(Filter, LLM_with_PPL), (Filter, Attacker),
(LLM_with_PPL, Evaluator),
(AttackEvaluator, DatasetDB), (Evaluator, LeaderBoard), 
]
"args": [(DatasetDB, 1, {"db":"NormalQ"}), (DatasetDB, 1, {"db":"NormalA"}),
 (DatasetDB, 1, {"db":"BadQ"}), (DatasetDB, 1, {"db":"BadA"}), 
 (Evaluator, 1, {"mode":"Attack"}), 
 (LLM_with_PP, 1, {"llm": "GPT4"})
 ]

"""Step3：设置任务，开始运行
1. 建立运行图
2. 设定入口agent和出口agent
2. 设置初始输入
3. 自动运行
"""

Graph.check(config)  
graph = Graph.init(config)

graph.find_type("DatasetDB")
> DatasetDB(id="12345", db="NormalQ"), DatasetDB(id="54321", db="NormalA").....

graph.find_type(LeaderBoard)
> LeaderBoard(id="67891")

task = Task(graph)
task.set_entry_node("12345") #指定入口节点
task.set_exit_node("67891") #指定出口节点
task.set_initial_input("Select data from * sample(10)") # 指定初始条件
task.run()


""" 数据记录导出
"""
task.save(path = ".......")
```



# Kernel System: DARC Arch
The kernel of our system.

## Communication

## Optimization

## Development

Read the [CONTRIBUTING.md](CONTRIBUTING.md) file.