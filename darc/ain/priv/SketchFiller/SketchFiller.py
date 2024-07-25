import json
from loguru import logger
from erlport.erlang import set_message_handler, cast
from erlport.erlterms import Atom
import time
import sys
import os

# 导入 get_answers_sync 函数
from darc.agent.llm.proxy.query import get_answer_sync
from darc.agent.llm.prompt.system_prompt_template import tester_system_prompt
from darc.agent.codes.prompt_construction_utils import get_repo_sketch_prompt
from darc.agent.codes.utils import parse_reponse, parse_repo_sketch, RepoSketchNode
from darc.agent.codes.from_scratch_gpt35_eval import TEMPLATE_DICT

# Reference to the Elixir process to send result to
message_handler = None

def cast_message(pid, message):
    cast(pid, message)

def register_handler(pid):
    # Save message handler pid
    global message_handler
    message_handler = pid

def handle_message(input):
    try:
        result = compute(input)
        cast_message(message_handler, message)

        logger.info(f"Message Handler PID: {message_handler}")

        if message_handler:
            # Serialize result to JSON and encode to bytes
            serialized_result = json.dumps(result).encode('utf-8')
            message = (Atom('python'), serialized_result)
            cast_message(message_handler, message)
    except Exception as e:
        logger.error(f"handle_message, {type(e).__name__}, {str(e)}")
        if message_handler:
            # Encode error message to bytes
            error_message = str(e).encode('utf-8')
            cast_message(message_handler, (Atom('error'), error_message))
    
def compute(input: bytes) -> str:
    decoded_string = input.decode('utf-8', errors='ignore')
    data = json.loads(decoded_string)
    data = data["parameters"]
    prompt = data.get("instruction")
    file_path = data.get("file_path")
    response = get_answer_sync(prompt)
    message = [
        {
                "parameters": {
                    "repo_response": response,
                    "readme_content": "",
                    "file_path": file_path,
                    "function_header": "",
                    "function_body": response,
                }
            }
    ]

    with open("sketchfiller.txt", "a", encoding="utf-8") as f:
        content = f"1\n"
        f.write(content)

    return json.dumps(data, message, ensure_ascii=False)

def save_sketch_filler(data, messages, readme, generated, parsed):
    for message in messages:
        message = message["parameters"]
        file_content =  {
            "readme_summary": data["readme_summary"],
            "repo_sketch": data["repo_sketch"],
            "relevant_file_paths": [],
            "relevant_file_sketches": {},
            "current_file_path": data["current_file_path"],
            # TODO: call def get_current_file_sketch_content(idx, path, current_python_content):
            "current_file_sketch": {},
            "function_header": ,
            "instruction": ,
            "generated": ,
            "parsed": ,
        }
        with open('./filesketch.jsonl', 'w') as json_file:
            json.dump(file_content, json_file, indent=4)
    

set_message_handler(handle_message)

