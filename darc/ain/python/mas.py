import uuid
import json
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session

from module import Base, Actor, Edge

import grpc
import masrpc_pb2 as masrpc_pb2
import masrpc_pb2_grpc as masrpc_pb2_grpc


class MAS:
    def __init__(self, db_url):
        self.engine = create_engine(db_url, echo=True)
        Base.metadata.create_all(self.engine)
        self.Session = scoped_session(sessionmaker(bind=self.engine))
        
        self.actors = []
        self.edges = []
        # gRpc client
        self.channel = grpc.insecure_channel("localhost:50051")
        self.stub = masrpc_pb2_grpc.MasRPCStub(self.channel)
        
        self.load_data()

    def __enter__(self):
        self.session = self.Session()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.session.close()
        self.Session.remove()
    
    def load_data(self):
        with self.Session() as session:
            self.actors = session.query(Actor).all()
            self.edges = session.query(Edge).all()
    
    def initialize_actors(self):
        for actor in self.actors:
            try:
                uuid = self.execute_elixir_function('start', actor.name)
                print(f"Initialized actor {actor.name} with UUID: {uuid}")
            except Exception as e:
                print(f"Failed to initialize actor {actor.name}: {e}")
    
    def add_actor(self, uid, name, role, age, graph_id):
        actor = Actor(
            uid=uid, 
            name=name, 
            role=role, 
            age=age, 
            graph_id=graph_id
        )
        self.session.add(actor)
        self.session.commit()
        print(f"Actor {name} added successfully.")

    def add_edge(self, uid, since, graph_id, from_uid, to_uid):
        edge = Edge(
            uid=uid, 
            since=since, 
            graph_id=graph_id, 
            from_uid=from_uid, 
            to_uid=to_uid
        )
        self.session.add(edge)
        self.session.commit()
        print(f"Edge from {from_uid} to {to_uid} added successfully.")
    
    def load(self, graph_id):
        load_request = masrpc_pb2.LoadRequest(graph_id=graph_id)
        load_response = self.stub.Load(load_request)
        print("Load response:", load_response.status)
    
    def clear_tables(self):
        self.session.query(Edge).delete()
        self.session.query(Actor).delete()
        self.session.commit()
        print("Tables cleared successfully.")
    
    def send(self, uuid, message):
        send_request = masrpc_pb2.SendRequest(uid="2d934217-d28e-48fd-aafc-1a61675afa10", message={"content": message})
        send_response = self.stub.Send(send_request)
        print("Send response:", send_response.status)
        
    def test(self, arg1, arg2):
        self.execute_elixir_function('test', arg1, arg2)
        
    def start(self):
        self.execute_elixir_function('start')
    
    def get_log(self, actor_uid):
        get_log_request = masrpc_pb2.GetLogRequest(uid="2d934217-d28e-48fd-aafc-1a61675afa10")
        get_log_response = self.stub.GetLog(get_log_request)
        print("GetLog response:", get_log_response.status)
        print("Logs:", get_log_response.logs)
        for log in get_log_response.logs:
            data = json.loads(log)
            print(data)

# 示例调用
if __name__ == "__main__":
    db_url = 'postgresql+psycopg2://postgres:123456@localhost:5432/ain_repo'
    
    try:
        with MAS(db_url) as mas:
            actor_uid = "2d934217-d28e-48fd-aafc-1a61675afa10"
            graph_id = "36f9144c-e071-4e6f-a6fa-e020eca699c3"
            
            mas.load(graph_id)
            mas.send(actor_uid, "hi")
            # mas.test("1", "2")
            import time
            time.sleep(4)
            mas.get_log(actor_uid)
            
            # mas.add_actor("uid", "name", "role", "age", graph_id)
            # mas.add_edge("uid", "since", graph_id, "from_uid", "to_uid")
    except Exception as e:
        print(e)
