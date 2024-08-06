import subprocess
import json
import os

def run_mix_task(task, args=None, project_path="."):
    command = ["mix", task]
    if args:
        command.extend(args)
    print(command)
    result = subprocess.run(command, capture_output=True, text=True, cwd=project_path)
    
    if result.returncode == 0:
        print(result.stdout)
    else:
        print("Error:", result.stderr)

if __name__ == "__main__":
    project_path = "./"  # 指定 Elixir 项目的路径

    # 示例参数
    arg1 = "example_arg1"
    arg2 = "example_arg2"
    
    # 调用 `mix invoke test <arg1> <arg2>`
    run_mix_task("invoke", ["test", arg1, arg2], project_path=project_path)