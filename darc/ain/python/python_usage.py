import subprocess
import json
import os

def call_elixir_function(command, *args):
    elixir_project_path = os.path.join(os.path.dirname(__file__), '..')
    elixir_command = ['mix', 'invoke'] + list(command) + list(args)
    process = subprocess.Popen(
        elixir_command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        cwd=elixir_project_path  # 指定工作目录为 Elixir 项目目录
    )

    stdout, stderr = process.communicate()

    if process.returncode != 0:
        raise Exception(f"Error occurred: {stderr}")

    return stdout.strip()

def start_function(str_arg):
    output = call_elixir_function(['start', str_arg])
    for line in output.splitlines():
        if line.startswith("UUID:"):
            return line.split(": ")[1]
    raise Exception("UUID not found in output")

def send_function(uuid, message):
    message_json = json.dumps(message)
    call_elixir_function(['send', uuid, message_json])

# 示例调用
try:
    uuid = start_function("Hello Elixir")
    print("Received UUID:", uuid)

    send_function(uuid, {"key": "value"})
    print("Message sent successfully")
except Exception as e:
    print(e)