import subprocess
import json
import os

def call_elixir_function(command, *args):
    elixir_project_path = os.path.join(os.path.dirname(__file__), '..')
    elixir_command = ['mix', 'invoke']
    if command:
        elixir_command.extend(command)
    if args:
        elixir_command.extend(args)
    timeout = 8
    try:
        # 使用 subprocess.run 执行子进程
        result = subprocess.run(
            elixir_command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            cwd=elixir_project_path,  # 指定工作目录为 Elixir 项目目录
            timeout=timeout,
            check=True  # 自动检查返回码，如果非零则抛出 CalledProcessError
        )

        return result.stdout.strip()

    except subprocess.TimeoutExpired:
        raise Exception("Process timed out.")

    except subprocess.CalledProcessError as e:
        raise Exception(f"Error occurred: {e.stderr}")

    except Exception as e:
        raise e

def execute_function(func_name, *args):
    if func_name == 'load':
        return load_function(*args)
    elif func_name == 'send':
        return send_function(*args)
    elif func_name == 'test':
        return test_function(*args)
    else:
        raise ValueError(f"Unknown function name: {func_name}")

def load_function(str_arg):
    output = call_elixir_function(['load', str_arg])
    for line in output.splitlines():
        print(line)

def send_function(uuid, message):
    try:
        message_json = json.dumps(message)
        output = call_elixir_function(['send', uuid, message_json])
        for line in output.splitlines():
            print(line)
    except BaseException as e:
        print(e)
        
def test_function(arg1, arg2):
    output = call_elixir_function(['test'], arg1, arg2)
    return output
