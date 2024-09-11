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
import time
import os

from darc.ain.python.mas import MAS


db_url = 'postgresql+psycopg2://postgres:123456@localhost:5432/ain_repo'
    
try:
    with MAS(db_url) as mas:
        mas.clear_tables()
            
        chat_config = {
                "role": [
                    "People",
                ],
                "edge": [
                    ("People", "People"),
                ],
                "args": [
                    ("People", 24),
                ]
            }
        
        # theme
        content = "社交媒体是社会的进步还是退步"
        
        # config
        current_path = os.path.abspath(__file__)
        root_path = os.path.abspath(os.path.join(current_path, "../../../"))
        mas.config_db(chat_config)
        
        # actor <->system prompt
        actors = mas.find_with_role("People")
        prompt_path = root_path + "/agent/llm/persona/persona.jsonl"
        output_path = root_path + "/agent/llm/persona/uid_system_prompt.jsonl"
        mas.bind_system_prompt(actors, prompt_path, output_path)
        
        time.sleep(24)
        mas.send(str(actors[0].uid), content)

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