import json
from loguru import logger
from erlport.erlang import set_message_handler, cast
from erlport.erlterms import Atom
import time
import sys
import os

# 导入 get_answers_sync 函数
from darc.agent.llm.proxy.query import get_answer_sync
from darc.agent.llm.prompt.system_prompt_template import SYS_PROMPT_DICT, abstract_system_prompt
from darc.agent.codes.prompt_construction_utils import get_repo_sketch_prompt
from darc.agent.codes.from_scratch_gpt35_eval import TEMPLATE_DICT
from darc.agent.codes.utils import parse_reponse, parse_repo_sketch, RepoSketchNode
from darc.ain.priv.env import REPO_NAME

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
    # from_role = data["parameters"]["from_role"]
    prompt = data["content"]
    response = get_answer_sync(prompt, SYS_PROMPT_DICT["Tester"])
    abstract = get_answer_sync(prompt, abstract_system_prompt)
    messages = [{
            "content": f"abstract:{abstract}; Tester response: {response}",
            "parameters": {
                "from_role": "DistributedTester",
                "to_role": "random",
            }
        }
    ]

    return json.dumps(messages, ensure_ascii=False)


set_message_handler(handle_message)
