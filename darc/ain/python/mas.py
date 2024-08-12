import uuid
import json
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session

from module import Base, Actor, Edge

import grpc
import masrpc_pb2 as masrpc_pb2
import masrpc_pb2_grpc as masrpc_pb2_grpc

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
    
    def send(self, uid, message, after=0):
        time.sleep(after)
        send_request = masrpc_pb2.SendRequest(uid=uid, message={"content": message})
        send_response = self.stub.Send(send_request)
        print("Send response:", send_response.status)
        
    def test(self, arg1, arg2):
        self.execute_elixir_function('test', arg1, arg2)
        
    def start(self):
        self.execute_elixir_function('start')
    
    def get_log(self, actor_uid):
        get_log_request = masrpc_pb2.GetLogRequest(uid=actor_uid)
        get_log_response = self.stub.GetLog(get_log_request)
        print("GetLog response:", get_log_response.status)
        print("Logs:", get_log_response.logs)
        for log in get_log_response.logs:
            data = json.loads(log)
            print(data)
            
    def config_db(self, config):
        actors, edges = self.parse_config(config)
        self.actors.extend(actors)
        self.edges.extend(edges)
        self.add_to_database(actors, edges)
        self.load(str(actors[0]["graph_id"]))

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
                    edge = {
                        "uid": uuid.uuid4(),
                        "since": 2023,  # Assuming a default year
                        "graph_id": from_actor["graph_id"],
                        "from_uid": from_actor["uid"],
                        "to_uid": to_actor["uid"]
                    }
                    edge_instances.append(edge)
                    
        return actor_instances, edge_instances

    def add_to_database(self, actors, edges):
        for actor in actors:
            self.add_actor(
                uid=actor["uid"],
                name=actor["name"],
                role=actor["role"],
                age=actor["age"],
                graph_id=actor["graph_id"]
            )

        for edge in edges:
            self.add_edge(
                uid=edge["uid"],
                since=edge["since"],
                graph_id=edge["graph_id"],
                from_uid=edge["from_uid"],
                to_uid=edge["to_uid"]
            )
            
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
            
            readme_content = "# EasyLiterature\n**EasyLiterature** is a Python-based command line tool for automatic literature management. Welcome star or contribute!\n\nSimply list the paper titles (or ids) you want to read in a markdown file and it will automatically `collect and refine its information in the markdown file`, `download the pdf to your local machine`, and `link the pdf to your paper in the markdown file`. You can forever keep your notes within the pdfs and mds on your local machine or cloud driver.\n\nInspired by [Mu Li](https://www.bilibili.com/video/BV1nA41157y4), adapted from [autoLiterature](https://github.com/wilmerwang/autoLiterature). \nCompared to autoLiterature, **EasyLiterature** is much easier to use and supports a wider range of features, such as `title-based paper match`, `paper search and download on Google Scholar and DBLP` (the two main sites for scholars), `citation statistics`, `mannual information update assitant`, etc. **EasyLiterature covers almost all papers thanks to the support of Google Scholar and DBLP!**\n\n## A simple example\n1. Have the python installed on your local machine (preferably >= 3.7).\n2. Run `pip install easyliter` in your command line to install.\n3. Prepare your markdown note file (e.g., `Note.md`). <br>**Attention:** You may need to download a markdown editor to create/edit this file. I am using [Typora](https://typora.io/), which is not totally free. You can also choose other alternatives.\n4. List the formated papers titles in your markdown note file according to the Section 4 below (Recognition Rules). e.g.,<br>\n  \\- {{BERT: Pre-training of Deep Bidirectional Transformers for Language Understanding.}}<br>\n  \\- {{Xlnet: Generalized autoregressive pretraining for language understanding.}}<br>\n  **(pay attention to the space after \u2018\\-\u2019)** \n5. Create a folder to store the downloaded pdfs (e.g., `PDFs/`).\n6. Run `easyliter -i <path to your md file> -o <path to your pdf folder>`. \n<br> (Replace `<path to your md file>` with the actual path to your markdown note file, `<path to your pdf folder>` with the actual path to your pdf folder)\n<br>e.g., `easyliter -i \"/home/Note.md\" -o \"/home/PDFs\"`\n7. Your should able to see that the updated information and downloaded pdf files if no error is reported.\n8. This is a simple and common use case. For other features, please read the below sections carefully and follow the instructions.\n\n## Arguments\n```bash\neasyliter\n\noptional arguments:\n\n  -h, --help            show this help message and exit\n  \n  -i INPUT, --input INPUT\n  The path to the note file or note file folder.\n\n  -o OUTPUT, --output OUTPUT\n  Folder path to save paper pdfs and images. NOTE: MUST BE FOLDER.\n\n  -p PROXY, --proxy PROXY\n  The proxy. e.g. 127.0.0.1:1080. If this argument is specified, the google scholar will automatically use a free proxy (not necessarily using the specified proxy address). To use other proxies for google scholar, specify the -gp option. If you want to set up the proxies mannually, change the behaviour in GoogleScholar.set_proxy(). See more at https://scholarly.readthedocs.io/en/stable/ProxyGenerator.html.\n\n  -gp GPROXY_MODE, --gproxy_mode GPROXY_MODE\n  The proxy type used for scholarly. e.g., free, single, Scraper. (Note: 1. <free> will automatically choose a free proxy address to use, which is free, but may not be fast. 2. <single> will use the proxy address you specify. 3. <Scraper> is not free to use and need to buy the api key.).\n\n  -d, --delete\n  Delete unreferenced attachments in notes. Use with caution, when used, -i must be a folder path including all notes.\n\n  -m MIGRATION, --migration MIGRATION\n  The pdf folder path you want to reconnect to.\n```\n\n## Recognition Rules\n- If the notes file contains `- {paper_id}`, it will download the information of that literature, but not the PDF.\n- If the notes file contains `- {{paper_id}}`, it will download both the information of that literature and the PDF.\n\n- Note: `paper_id` supports `article title`, published articles' `doi`, and pre-published articles' `arvix_id`, `biorvix_id`, and `medrvix_id`. It will try all the possible sources online.\n\n## Usage\n### Basic Usage\nAssuming `input` is the folder path of the literature notes (.md files) and `output` is the folder path where you want to save the PDFs.\n\n```bash\n# Update all md files in the input folder\neasyliter -i input -o output \n\n# Only update the input/example.md file\neasyliter -i input/example.md -o output  \n\n# -d is an optional flag, when -i is a folder path, using -d will delete unrelated pdf files in the PDF folder from the literature notes content\neasyliter -i input -o output -d\n```\n\n### Migrating Notes and PDF Files\nWhen you need to move the literature notes or the PDF folder, the links to the PDFs in the literature notes might become unusable. You can use `-m` to re-link the PDF files with the literature notes.\n\n```bash\n# Update all md files in the input folder\neasyliter -i input -m movedPDFs/\n\n# Only update the input/example.md file\neasyliter -i input/example.md -m movedPDFs/  \n```"
            repo_name = "CVE-2023-44487"
            mas.config_db(config)
            
            # mas.role_intro("RepoSketcher")
            
            actors = mas.find_with_role("RepoSketcher")
            mas.send(str(actors[0].uid), readme_content, after=40)
            
            actors = mas.find_with_role("Packer")
            mas.send(str(actors[0].uid), repo_name, after=120)
            
    except Exception as e:
        print(e)
