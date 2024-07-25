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
import darc.agent.codes.utils as utils

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
    readme_content = data.get("readme_content")
    repository_sketch = data.get("repository_sketch")
    file_path = data.get("file_path")
    repo_response = data.get("repo_response")
    repo_sketch_paths = data.get("repo_sketch_paths")
    response = get_answer_sync(TEMPLATE_DICT["file_sketch.json"].format_map(
                            {
                                "readme": readme_content,
                                "repo_sketch": repository_sketch,
                                "file_path": file_path
                            }
                        ))

    insts = {path: {"parsed": "not impl yet."} for path in repo_sketch_paths}
    insts[file_path]["parsed"] = response

    messages = []
    each = {
        "parsed": parse_reponse(response),
        "repo_sketch": repository_sketch,
        "file_path": file_path,
    }

    function_requests = utils.generate_function_body_input_openai(
        each,
        readme_content,
        insts,
        "",
        TEMPLATE_DICT["function_body.json"],
    )

    for function_request in function_requests:
        readme_summary = function_request["readme_summary"]
        repo_sketch = function_request["repo_sketch"]
        relevant_file_list = function_request["relevant_file_paths"]
        relevant_file_sketch_content = function_request["relevant_file_sketches"]
        current_file_path = function_request["current_file_path"]
        function_header = function_request["function_header"]
        prompt = function_request["instruction"]
        message = {
                "parameters": {
                    "readme_summary": readme_summary,
                    "repo_sketch": repo_sketch,
                    "relevant_file_paths": relevant_file_list,
                    "relevant_file_sketches": relevant_file_sketch_content,
                    "current_file_path": current_file_path,
                    "function_header": function_header,
                    "instruction": prompt,
                    "file_path": file_path,
                    "to_role": "SketchFiller",
                    }
            }
        messages.append(message)
    
    with open("filesketch.txt", "a", encoding="utf-8") as f:
        content = f"{len(messages)}\n"
        f.write(content)
        
    save_file_sketch(messages, readme_content, response, parse_reponse(response))
    
    return json.dumps(messages, ensure_ascii=False)

set_message_handler(handle_message)

def save_file_sketch(messages, readme, generated, parsed):
    for message in messages:
        message = message["parameters"]
        file_content =  {
            "readme": readme,
            "repo_sketch": message["repo_sketch"],
            "file_path": message["file_path"],
            "instruction": message["instruction"],
            "generated": generated,
            "parsed": parsed,
        }
        with open('./filesketch.jsonl', 'w') as json_file:
            json.dump(file_content, json_file, indent=4)
    