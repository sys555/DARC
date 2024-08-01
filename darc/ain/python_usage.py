import subprocess
import json

def call_elixir_function(command, *args):
    elixir_command = ['mix', 'invoke'] + list(command) + list(args)
    process = subprocess.Popen(
        elixir_command,
        stdout = subprocess.PIPE,
        stderr = subprocess.PIPE,
        text = True,        # 确保输出被解码为字符串
    )
    
    stdout, stderr = process.communicate()
    
    if process.returncode != 0:
        raise Exception(f"Error occurred: {stderr}")
    
    return stdout.strip()

def start_function(str_args):
    return call_elixir_function(['start', str_args])

def send_function(uuid, message):
    message_json = json.dumps(message)
    return call_elixir_function(['send', uuid, message_json])

try:
    uuid = start_function("Hello Elixir")
    print("Received UUID:", uuid)
    
    send_function(uuid, {"key": "value"})
    print("Message sended")
except Exception as e:
    print(e)