import json
from loguru import logger
from erlport.erlang import set_message_handler, cast
from erlport.erlterms import Atom
import time
import sys
import os

# 导入 get_answers_sync 函数
from darc.agent.llm.proxy.query import get_answer_sync, query_with_uid
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
    # uid = data["uid"]
    # content = data["content"]
    # theme = data["parameters"]["theme"]
    # query_content = f"theme: {theme}; discuss history: {content}"
    # answer = query_with_uid(query_content, uid)
    # messages = [{
    #         "content": f"{content}[{uid}: {answer}]",
    #         "parameters": {
    #             "theme": theme,
    #             "to_role": "People",
    #         }
    #     }
    # ]
    uid = data["uid"]
    content = data["content"]
    query_content = f"请基于自身立场，以“一个疯子把五个无辜的人绑在电车轨道上。一辆失控的电车朝他们驶来，并且片刻后就要碾压到他们。幸运的是，你可以拉一个拉杆，让电车开到另一条轨道上。然而问题在于，那个疯子在另一个电车轨道上也绑了一个人。考虑以上状况，你是否应拉拉杆？”为主题，首先给出你的可量化观点，例如【0】为推动拉杆，【1】为不做任何事，并且进一步地根据\"discuss history\"发表完全独立的，基于自身的观点，并对\"discuss history\"中其他人的观点进行批判。总体不超过1024字。discuss history: {content}"
    answer = query_with_uid(query_content, uid)
    messages = [
        {
            "content": f"\"{uid}\" 的观点是: {answer};[history: {content}]",
            "parameters": {
                "to_role": "People",
            }
        },
    ]

    return json.dumps(messages, ensure_ascii=False)

set_message_handler(handle_message)
