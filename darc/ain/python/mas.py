import uuid
import json
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session

from darc.ain.python.module import Base, Actor, Edge

import grpc
import darc.ain.python.masrpc_pb2 as masrpc_pb2
import darc.ain.python.masrpc_pb2_grpc as masrpc_pb2_grpc

from loguru import logger
import time
import importlib

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
        
        # self.load_data()

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
    
    def send(self, uid, message, after=0):
        time.sleep(after)
        send_request = masrpc_pb2.SendRequest(uid=uid, message={"content": message})
        send_response = self.stub.Send(send_request)
        print("Send response:", send_response.status)
    
    def get_log(self, actor_uid):
        get_log_request = masrpc_pb2.GetLogRequest(uid=actor_uid)
        get_log_response = self.stub.GetLog(get_log_request)
        print("GetLog response:", get_log_response.status)
        print("Logs:", get_log_response.logs)
        data = []
        for log in get_log_response.logs:
            data.append(json.loads(log))
        return data
            
    def config_db(self, config):
        actors, edges = self.parse_config(config)
        self.add_to_database(actors, edges)
        # 同一个config 同一张图，默认加载
        self.load(str(actors[0]["graph_id"]))
        self.load_data()

    def parse_config(self, config):
        roles = config.get("role", [])
        edges = config.get("edge", [])
        args = dict(config.get("args", []))
        graph_id = uuid.uuid4()
        # Create actor instances
        actor_instances = []
        for role in roles:
            num_actors = args.get(role, 1)  # Default to 1 actor if not specified
            for _ in range(num_actors):
                actor = {
                    "uid": uuid.uuid4(),
                    "name": f"{role}_{uuid.uuid4()}",
                    "role": role,
                    "age": 0,  # Assuming age is not relevant for now
                    "graph_id": graph_id
                }
                actor_instances.append(actor)

        # Create edge instances
        edge_instances = []
        for from_role, to_role in edges:
            from_actors = [actor for actor in actor_instances if actor["role"] == from_role]
            to_actors = [actor for actor in actor_instances if actor["role"] == to_role]
            for from_actor in from_actors:
                for to_actor in to_actors:
                    if from_actor == to_actor:
                        continue
                    edge = {
                        "uid": uuid.uuid4(),
                        "since": 2023,  # Assuming a default year
                        "graph_id": from_actor["graph_id"],
                        "from_uid": from_actor["uid"],
                        "to_uid": to_actor["uid"]
                    }
                    edge_instances.append(edge)
                    
        return actor_instances, edge_instances

    def batch_add_actors(self, actors):
        actor_objects = [
            Actor(
                uid=actor["uid"],
                name=actor["name"],
                role=actor["role"],
                age=actor["age"],
                graph_id=actor["graph_id"]
            )
            for actor in actors
        ]
        self.session.add_all(actor_objects)
        self.session.commit()
        print(f"{len(actors)} actors added successfully.")

    def batch_add_edges(self, edges):
        edge_objects = [
            Edge(
                uid=edge["uid"],
                since=edge["since"],
                graph_id=edge["graph_id"],
                from_uid=edge["from_uid"],
                to_uid=edge["to_uid"]
            )
            for edge in edges
        ]
        self.session.add_all(edge_objects)
        self.session.commit()
        print(f"{len(edges)} edges added successfully.")
    
    def add_to_database(self, actors, edges):
        self.batch_add_actors(actors)
        self.batch_add_edges(edges)
            
    def find_with_role(self, role):
        with self.Session() as session:
            return session.query(Actor).filter(Actor.role == role).all()

    def role_intro(self, role):
        try:
            # Dynamically import the role module
            module_path = f"priv.{role}.role"
            role_module = importlib.import_module(module_path)
            
            # Call the intro function from the module
            intro_function = getattr(role_module, 'intro')
            return intro_function()
        
        except (ModuleNotFoundError, AttributeError) as e:
            return f"Error: {e}"
        
    def bind_system_prompt(self, actors, prompt_path, output_path):
        # 读取 prompt_path 中的 prompt 数据
        prompts = []
        try:
            with open(prompt_path, 'r', encoding='utf-8') as file:
                for line in file:
                    if len(prompts) < len(actors):
                        data = json.loads(line)
                        prompts.append(data['persona'])
            # 确保 actors 和 prompts 数量一致
            if len(actors) != len(prompts):
                raise ValueError("The number of actors and prompts must be the same.")

            # 将每个 actor 的 uuid 与 prompt 进行绑定，并写入 output_path 文件
            with open(output_path, 'w', encoding='utf-8') as output_file:
                for actor, prompt in zip(actors, prompts):
                    actor_uid = str(actor.uid)
                    binding = {
                        "uid": actor_uid,
                        "prompt": prompt
                    }
                    output_file.write(json.dumps(binding, ensure_ascii=False) + '\n')
                    print(f"Bound actor {actor_uid} with prompt: {prompt}")
        except Exception as e:
            print(str(e))
        
        

# 示例调用
if __name__ == "__main__":
    db_url = 'postgresql+psycopg2://postgres:123456@localhost:5432/ain_repo'
    
    try:
        with MAS(db_url) as mas:
            mas.clear_tables()
            
            config = {
                "role": [
                    "RepoSketcher",
                    "FileSketcher",
                    "SketchFiller",
                    "Packer",
                    "Evaluator",
                ],
                "edge": [
                    ("RepoSketcher", "FileSketcher"),
                    ("FileSketcher", "SketchFiller"),
                    ("Packer", "Evaluator"),
                ],
                "args": [
                    ("FileSketcher", 4),
                    ("SketchFiller", 4),
                ]
            }
            
            readme_content = """
            
            # Flameshow

            Flameshow is a terminal Flamegraph viewer.

            ## Features

            - Renders Flamegraphs in your terminal
            - Supports zooming in and displaying percentages
            - Keyboard input is prioritized
            - All operations can also be performed using the mouse.
            - Can switch to different sample types

            ## Usage

            View golang's goroutine dump:

            ```shell
            $ curl http://localhost:9100/debug/pprof/goroutine -o goroutine.out
            $ flameshow goroutine.out
            ```

            After entering the TUI, the available actions are listed on Footer:

            - <kbd>q</kbd> for quit
            - <kbd>j</kbd> <kbd>i</kbd> <kbd>j</kbd> <kbd>k</kbd> or <kbd>←</kbd>
            <kbd>↓</kbd> <kbd>↑</kbd> <kbd>→</kbd> for moving around, and <kbd>Enter</kbd>
            for zoom in, then <kbd>Esc</kbd> for zoom out.
            - You can also use a mouse, hover on a span will show it details, and click will
            zoom it.

            ## Supported Formats

            As far as I know, there is no standard specification for profiles. Different
            languages or tools might generate varying profile formats. I'm actively working
            on supporting more formats. Admittedly, I might not be familiar with every tool
            and its specific format. So, if you'd like Flameshow to integrate with a tool
            you love, please feel free to reach out and submit an issue.

            - Golang pprof
            - [Brendan Gregg's Flamegraph](https://www.brendangregg.com/flamegraphs.html)
            
            """
            repo_name = "flameshow"
            mas.config_db(config)
            
            # mas.role_intro("RepoSketcher")
            
            actors = mas.find_with_role("RepoSketcher")
            mas.send(str(actors[0].uid), readme_content, after=120)
            
            actors = mas.find_with_role("Packer")
            # mas.send(str(actors[0].uid), repo_name, after=160)
            
    except Exception as e:
        print(e)
