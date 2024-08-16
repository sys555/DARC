import uuid
import json
from datetime import datetime

from mas import MAS

# 定义 Actor 和 Edge 数据结构
class MockActor:
    def __init__(self, uid, name, role, age, graph_id):
        self.uid = uid
        self.name = name
        self.role = role
        self.age = age
        self.graph_id = graph_id
        self.inserted_at = datetime.utcnow().isoformat()
        self.updated_at = datetime.utcnow().isoformat()

class MockEdge:
    def __init__(self, uid, since, graph_id, from_uid, to_uid):
        self.uid = uid
        self.since = since
        self.graph_id = graph_id
        self.from_uid = from_uid
        self.to_uid = to_uid
        self.inserted_at = datetime.utcnow().isoformat()
        self.updated_at = datetime.utcnow().isoformat()

def generate_mock_data(db_url):
    graph_id = uuid.uuid4()
    
    # 创建四个 Actor
    actor1 = MockActor(uid=uuid.uuid4(), name='Actor 1', role='hero', age=30, graph_id=graph_id)
    actor2 = MockActor(uid=uuid.uuid4(), name='Actor 2', role='villain', age=28, graph_id=graph_id)
    actor3 = MockActor(uid=uuid.uuid4(), name='Actor 3', role='sidekick', age=25, graph_id=graph_id)
    actor4 = MockActor(uid=uuid.uuid4(), name='Actor 4', role='mentor', age=50, graph_id=graph_id)
    
    actors = [actor1, actor2, actor3, actor4]
    
    # 创建全连接的 Edge
    edges = []
    for i in range(len(actors)):
        for j in range(len(actors)):
            if i != j:
                edges.append(MockEdge(
                    uid=uuid.uuid4(), 
                    since=2023, 
                    graph_id=graph_id, 
                    from_uid=actors[i].uid, 
                    to_uid=actors[j].uid
                ))
    
    # 使用 MAS 类将数据插入数据库
    with MAS(db_url) as mas:
        # 清空表内容
        mas.clear_tables()
        
        for actor in actors:
            mas.add_actor(uid=actor.uid, name=actor.name, role=actor.role, age=actor.age, graph_id=actor.graph_id)
        
        for edge in edges:
            mas.add_edge(uid=edge.uid, since=edge.since, graph_id=edge.graph_id, from_uid=edge.from_uid, to_uid=edge.to_uid)
    
    # 准备 JSON 数据
    data = {
        'actors': [{'uid': str(actor.uid), 'name': actor.name, 'role': actor.role, 'age': actor.age, 'graph_id': str(actor.graph_id), 'inserted_at': actor.inserted_at, 'updated_at': actor.updated_at} for actor in actors],
        'edges': [{'uid': str(edge.uid), 'since': edge.since, 'graph_id': str(edge.graph_id), 'from_uid': str(edge.from_uid), 'to_uid': str(edge.to_uid), 'inserted_at': edge.inserted_at, 'updated_at': edge.updated_at} for edge in edges]
    }
    
    # 将数据写入 JSON 文件
    with open('mock_graph_data.json', 'w') as json_file:
        json.dump(data, json_file, indent=4)
    
    print("Mock graph data written to mock_graph_data.json")

if __name__ == "__main__":
    db_url = 'postgresql+psycopg2://postgres:123456@localhost:5432/ain_repo'
    generate_mock_data(db_url)