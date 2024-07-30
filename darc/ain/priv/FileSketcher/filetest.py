import json
from loguru import logger
import time
import sys
import os

# 导入 get_answers_sync 函数
from darc.agent.llm.proxy.query import get_answer_sync
from darc.agent.llm.prompt.system_prompt_template import tester_system_prompt
from darc.agent.codes.prompt_construction_utils import get_repo_sketch_prompt
from darc.agent.codes.utils import parse_reponse, parse_repo_sketch, RepoSketchNode, generate_function_body_input_openai
from darc.agent.codes.from_scratch_gpt35_eval import TEMPLATE_DICT


data = {
    "parameters": {
    "file_path": "utils.py",
    "readme_content": "# CVE-2023-44487\nBasic vulnerability scanning to see if web servers may be vulnerable to CVE-2023-44487\n\nThis tool checks to see if a website is vulnerable to CVE-2023-44487 completely non-invasively.\n\n1. The tool checks if a web server accepts HTTP/2 requests without downgrading them\n2. If the web server accepts and does not downgrade HTTP/2 requests the tool attempts to open a connection stream and subsequently reset it\n3. If the web server accepts the creation and resetting of a connection stream then the server is definitely vulnerable, if it only accepts HTTP/2 requests but the stream connection fails it may be vulnerable if the server-side capabilities are enabled.\n\nTo run,\n\n    $ python3 -m pip install -r requirements.txt\n\n    $ python3 cve202344487.py -i input_urls.txt -o output_results.csv\n\nYou can also specify an HTTP proxy to proxy all the requests through with the `--proxy` flag\n\n    $ python3 cve202344487.py -i input_urls.txt -o output_results.csv --proxy http://proxysite.com:1234\n\nThe script outputs a CSV file with the following columns\n\n- Timestamp: a timestamp of the request\n- Source Internal IP: The internal IP address of the host sending the HTTP requests\n- Source External IP: The external IP address of the host sending the HTTP requests\n- URL: The URL being scanned\n- Vulnerability Status: \"VULNERABLE\"/\"LIKELY\"/\"POSSIBLE\"/\"SAFE\"/\"ERROR\"\n- Error/Downgrade Version: The error or the version the HTTP server downgrades the request to\n\n*Note: \"Vulnerable\" in this context means that it is confirmed that an attacker can reset the a stream connection without issue, it does not take into account implementation-specific or volume-based detections*",
    "repo_response": "Based on the provided README, here's a sketch of the repository structure, including the relationship between files through import statements:\n\n```\n.\n├── cve202344487.py # import scanner; import utils; import csv; import argparse\n├── scanner.py # import http_client; import stream_handler\n├── http_client.py # import requests\n├── stream_handler.py # import logging\n├── utils.py # import datetime; import csv\n├── requirements.txt\n├── input_urls.txt\n├── output_results.csv\n└── README.md\n```\n\n### Explanation of the Structure:\n- **cve202344487.py**: This is the main script that orchestrates the vulnerability scanning process. It imports various modules for handling HTTP requests, managing streams, and utility functions.\n- **scanner.py**: This module is responsible for the scanning logic, utilizing the HTTP client and stream handler.\n- **http_client.py**: This module manages HTTP requests, leveraging the `requests` library for sending requests.\n- **stream_handler.py**: This module handles stream connections and resets, and it might also include logging functionality.\n- **utils.py**: This module contains utility functions, such as timestamp generation and CSV handling.\n- **requirements.txt**: This file lists the dependencies required to run the project.\n- **input_urls.txt**: This file is expected to contain the URLs to be scanned.\n- **output_results.csv**: This file will store the results of the scans in CSV format.\n- **README.md**: This file provides documentation about the repository, including usage instructions and details about the vulnerability being checked.",
    "repo_sketch_paths": [
        "cve202344487.py",
        "scanner.py",
        "http_client.py",
        "stream_handler.py",
        "utils.py",
        "requirements.txt",
        "input_urls.txt",
        "output_results.csv",
        "README.md"
    ],
    "repository_sketch": ".\n├── cve202344487.py # import scanner; import utils; import csv; import argparse\n├── scanner.py # import http_client; import stream_handler\n├── http_client.py # import requests\n├── stream_handler.py # import logging\n├── utils.py # import datetime; import csv\n├── requirements.txt\n├── input_urls.txt\n├── output_results.csv\n└── README.md\n",
    "to_role": "FileSketcher"
    },
    "content": ""
}
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

# print(response)

insts = {path: {"parsed": "not impl yet."} for path in repo_sketch_paths}
insts[file_path]["parsed"] = response

messages = []
each = {
    "parsed": parse_reponse(response),
    "repo_sketch": repository_sketch,
    "file_path": file_path,
}

function_requests = generate_function_body_input_openai(
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
                }
        }
    messages.append(message)
