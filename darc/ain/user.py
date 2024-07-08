# config
graph = {
    "nodes": {
        "node1": {
            "init": "addr1",
            "env": "pm",
        },
        "node2": {
            "init": "addr2",
            "env": "dev",
        },
        "node3": {
            "init": "addr3",
            "env": "qa",
        },
    },
    "edges": {
        "node1:node3",
        "node2:node3",
    },
    "data": {
        "node1": "Initial message from node1",
        "node2": "Initial message from node2",
    },
}

from loguru import logger
# 图预配置与运行
DAG.launch(graph)

# 获取某节点日志
DAG.get_logs("node1")

# 获取图所有日志
DAG.get_logs()

# env:pm 对应 pm.py
# pm.py
def compute(input):
    try:
        data = query(input)
    except Exception as e:
        logger.error(f"long_counter, {e}")
    logger.info(f"return, {data}")
    return data
