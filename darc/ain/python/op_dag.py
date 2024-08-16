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

from darc.ain.python.mas import MAS


db_url = 'postgresql+psycopg2://postgres:123456@localhost:5432/ain_repo'
    
try:
    with MAS(db_url) as mas:
        mas.clear_tables()
            
        distribut_config = {
                "role": [
                    "DistributedPM",
                    "DistributedDev",
                    "DistributedTester",
                    "DistributedDoc",
                ],
                "edge": [
                    ("DistributedPM", "DistributedPM"),
                    ("DistributedPM", "DistributedDev"),
                    ("DistributedPM", "DistributedDoc"),
                    ("DistributedPM", "DistributedTester"),
                    
                    ("DistributedDev", "DistributedPM"),
                    ("DistributedDev", "DistributedDev"),
                    ("DistributedDev", "DistributedDoc"),
                    ("DistributedDev", "DistributedTester"),
                    
                    ("DistributedTester", "DistributedPM"),
                    ("DistributedTester", "DistributedDev"),
                    ("DistributedTester", "DistributedDoc"),
                    ("DistributedTester", "DistributedTester"),
                    
                    ("DistributedDoc", "DistributedPM"),
                    ("DistributedDoc", "DistributedDev"),
                    ("DistributedDoc", "DistributedDoc"),
                    ("DistributedDoc", "DistributedTester"),
                ],
                "args": [
                    ("DistributedPM", 1),
                    ("DistributedDev", 5),
                    ("DistributedTester", 3),
                    ("DistributedDoc", 1),
                ]
            }
        
        central_config = {
                "role": [
                    "DistributedPM",
                    "DistributedDev",
                    "DistributedTester",
                    "DistributedDoc",
                ],
                "edge": [
                    ("DistributedPM", "DistributedPM"),
                    ("DistributedPM", "DistributedDev"),
                    ("DistributedPM", "DistributedDoc"),
                    ("DistributedPM", "DistributedTester"),
                    
                    ("DistributedDev", "DistributedPM"),
                    
                    ("DistributedTester", "DistributedPM"),
                    
                    ("DistributedDoc", "DistributedPM"),
                ],
                "args": [
                    ("DistributedPM", 1),
                    ("DistributedDev", 5),
                    ("DistributedTester", 3),
                    ("DistributedDoc", 1),
                ]
            }
        
        layer_config = {
                "role": [
                    "TopPM",
                    "DistributedPM",
                    "DistributedDev",
                    "DistributedTester",
                    "DistributedDoc",
                ],
                "edge": [
                    ("TopPM", "DistributedPM"),
                    
                    ("DistributedPM", "TopPM"),
                    ("DistributedPM", "DistributedDev"),
                    ("DistributedPM", "DistributedTester"),
                    
                    ("DistributedDev", "DistributedPM"),
                    
                    ("DistributedTester", "DistributedPM"),
                    ("DistributedTester", "DistributedDev"),
                    
                    ("DistributedDoc", "DistributedPM"),
                    ("DistributedDoc", "TopPM"),
                ],
                "args": [
                    ("TopPM", 1),
                    ("DistributedPM", 1),
                    ("DistributedDev", 3),
                    ("DistributedTester", 3),
                    ("DistributedDoc", 2),
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
        
        mas.config_db(distribut_config)
        # mas.load_data()
        # mas.load("59223d30-7f3a-4b7f-acb8-5873914ba228")
        
        # mas.role_intro("RepoSketcher")
        
        actors = mas.find_with_role("DistributedPM")
        mas.send(str(actors[0].uid), readme_content, after=240)
        import time
        time.sleep(600)
        logger.debug(mas.actors)
        # Open the file in append mode
        with open('./output.txt', 'a', encoding='utf-8') as file:
            for actor in mas.actors:
                logs = mas.get_log(str(actor.uid))
                # Format the data as needed
                formatted_data = {
                    'actor': actor.to_dict(),
                    'logs': logs
                }
                
                # Write the formatted data to the file as a JSON string
                file.write(json.dumps(formatted_data, ensure_ascii=False, indent=4))
                file.write('\n')  # Add a newline for separation between entries
        
except Exception as e:
    print(e)