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
    
def intro() -> str:
    return """
        文件树生成机器人
功能说明：

这个机器人能够自动解析项目的 README 文件，并将其中的目录结构转换为文件树。它可以帮助开发者快速了解项目的整体结构，节省时间。

主要特点：

自动化解析：无需手动输入，机器人会自动读取并解析 README 文件。
直观展示：通过可视化的文件树结构，清晰展示项目的目录和文件层级。
易于集成：可以轻松集成到现有的工作流中，支持多种编程语言的项目。
使用方法：

将 README 文件上传至机器人平台。
机器人自动生成文件树。
下载或查看生成的文件树结构。
应用场景：

开发者快速熟悉新项目。
团队协作时统一对项目结构的理解。
文档生成和项目展示需求。
    """

def compute(input: bytes) -> str:
    decoded_string = input.decode('utf-8', errors='ignore')
    data = json.loads(decoded_string)
    response = get_answer_sync(TEMPLATE_DICT["repo_sketch.json"].format_map(
                            {"readme": data["content"]}
                        ))
    
    parsed_response = parse_reponse(response)

    # 解析为文件树
    repo_sketch_tree: RepoSketchNode = parse_repo_sketch(parsed_response)
    # 路径list
    repo_sketch_paths = repo_sketch_tree.get_paths()
    
    instruction = TEMPLATE_DICT["repo_sketch.json"].format_map(
                                {"readme": data["content"]}
                            )
    file_content =  {
            "readme": decoded_string,
            "instruction": instruction,
            "generated": parsed_response,
            "parsed": parsed_response,
        }
    # 确保目录存在
    directory_path = f"./eval_data/jsonl/{REPO_NAME}"
    os.makedirs(directory_path, exist_ok=True)

    file_path = os.path.join(directory_path, "repo_sketch.json.jsonl")
    with open(file_path, 'a') as json_file:
            json_data = json.dumps(file_content)
            json_file.write(json_data + '\n')
    
    messages = []
    for path in repo_sketch_paths:
        if path.endswith(".py"):
            message = {
                "parameters": {
                    "to_role": "FileSketcher",
                    "repo_response": response,
                    "readme_content": data["content"],
                    "repository_sketch": parsed_response,
                    "file_path": path,
                    "repo_sketch_paths": repo_sketch_paths,
                }
            }
            messages.append(message)
    return json.dumps(messages, ensure_ascii=False)

set_message_handler(handle_message)
