import json
from loguru import logger
from erlport.erlang import set_message_handler, cast
from erlport.erlterms import Atom
import time
import sys
import os
import subprocess

# 导入 get_answers_sync 函数
from darc.agent.llm.proxy.query import get_answer_sync
from darc.agent.llm.prompt.system_prompt_template import tester_system_prompt
from darc.agent.codes.prompt_construction_utils import get_repo_sketch_prompt, get_current_file_sketch_content
from darc.agent.codes.utils import parse_reponse, parse_repo_sketch, RepoSketchNode
from darc.agent.codes.from_scratch_gpt35_eval import TEMPLATE_DICT
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
    repo_name = data["content"]

    command = [
        "python",
        "/Users/mac/Documents/pjlab/repo/CodeS/validation/evaluation_scripts/batch_eval/get_metric.py",
        "--pred", "/Users/mac/Documents/pjlab/repo/LLMSafetyChallenge/darc/ain/eval_data/repo/" + repo_name,
        "--ref", "/Users/mac/Documents/pjlab/repo/CodeS/validation/cleaned_repos/" + repo_name,
        "--metric_file", "/Users/mac/Documents/pjlab/repo/LLMSafetyChallenge/darc/ain/eval_data/repo",
    ]

    # 执行命令
    result = subprocess.run(command, capture_output=True, text=True)

    # 输出结果
    print("stdout:", result.stdout)
    print("stderr:", result.stderr)

    # 检查返回码
    if result.returncode == 0:
        print("命令执行成功")
    else:
        print("命令执行失败")
    
    message = [
        {}
    ]
    return json.dumps(message, ensure_ascii=False)

set_message_handler(handle_message)

