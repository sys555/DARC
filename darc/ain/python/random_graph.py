import networkx as nx
import random
from darc.ain.python.mas import MAS
import uuid

# 生成小世界图
n = 100  # 节点数
k = 20    # 每个节点相连的最近邻居节点数
p = 0.1  # 重连概率
G = nx.watts_strogatz_graph(n, k, p)

# 定义角色配比
roles_distribution = [
    ("DistributedPM", 10),
    ("DistributedDev", 55),
    ("DistributedTester", 25),
    ("DistributedDoc", 10),
]

# 创建角色列表
roles = []
for role, count in roles_distribution:
    roles.extend([role] * count)

# 随机打乱角色列表
random.shuffle(roles)

# 初始化 MAS 对象
db_url = 'postgresql+psycopg2://postgres:123456@localhost:5432/ain_repo'
with MAS(db_url) as mas_system:
    mas_system.clear_tables()
    graph_id = uuid.uuid4()  # 使用 UUID 作为 graph_id

    # 创建节点 UUID 映射
    node_uuid_map = {}

    # 添加节点到 MAS
    for node in G.nodes():
        role = roles[node]
        node_uuid = uuid.uuid4()
        node_uuid_map[node] = node_uuid
        mas_system.add_actor(
            uid=node_uuid,
            name=f"Actor_{node}",
            role=role,
            age=30,
            graph_id=graph_id
        )
    
    # 添加边到 MAS
    for edge in G.edges():
        from_uid = node_uuid_map[edge[0]]
        to_uid = node_uuid_map[edge[1]]
        mas_system.add_edge(
            uid=uuid.uuid4(),
            since=20,
            graph_id=graph_id,
            from_uid=from_uid,
            to_uid=to_uid
        )
        
        mas_system.add_edge(
            uid=uuid.uuid4(),
            since=20,
            graph_id=graph_id,
            from_uid=to_uid,
            to_uid=from_uid
        )
