from typing import Dict
import os
import sys
import subprocess
import json
import pstats
import shutil

from darc.models.interface import SourceCode

venv_path = os.path.dirname(os.path.dirname(sys.executable))


def run_pytest(source_code_path):
    # 载入预先创建好的虚拟环境
    pytest_report_path = os.path.join(source_code_path, "pytest_report.json")
    coverage_report_path = os.path.join(source_code_path, "coverage_report.json")
    pytest_command = [
        os.path.join(venv_path, "bin", "pytest"),
        "--cov",
        f"--cov-report=json:{coverage_report_path}",
        "--json-report",
        f"--json-report-file={pytest_report_path}",
        source_code_path,
    ]
    subprocess.run(pytest_command)
    report = {}
    # 读取json报告
    with open(pytest_report_path, "r") as file:
        report_data = json.load(file)
        report["pytest_report"] = report_data["summary"]
    with open(coverage_report_path, "r") as file:
        report_data = json.load(file)
        report["coverage_report"] = report_data["files"]
    # {'passed': 3, 'total': 3, 'collected': 3}
    return report


def run_cprofile(source_code_path):
    # 编辑run.sh文件，追加虚拟环境进去
    run_script_path = os.path.join(source_code_path, "run.sh")
    activate_command = f"source activate {venv_path}\n"
    change_folder_command = f"cd {source_code_path} \n"
    # 读取脚本的原始内容
    with open(run_script_path, "r") as file:
        original_content = file.readlines()
    # 插入激活命令
    new_content = [activate_command] + [change_folder_command] + original_content
    # 重新写回文件
    with open(run_script_path, "w") as file:
        file.writelines(new_content)

    # 此处为了使用cprofile监控函数的运行，则需要修改shell脚本的
    command = ["/bin/bash", run_script_path]
    subprocess.run(command)
    # 初始化pstats对象并加载.prof文件
    profile_file_path = os.path.join(source_code_path, "output.prof")
    pstats_obj = pstats.Stats(profile_file_path)
    pstats_obj.strip_dirs().sort_stats("cumulative")  # 根据需要调整排序方式

    # 构建字典数据
    profile_data = {}
    for func_name, stats in pstats_obj.stats.items():
        # 将stats对象转化为更易处理的形式，这里简化处理，只提取几个关键指标
        func_stats = {
            "ncalls": stats[0],  # 调用次数
            "tottime": stats[1],  # 总时间（不包括子调用）
            "cumtime": stats[3],  # 累积时间（包括子调用）
            # 可以根据需要添加更多字段，例如 'filename', 'lineno' 等
        }
        profile_data[f"{func_name[0]}:{func_name[1]}:({func_name[2]})"] = func_stats
    return profile_data


def generate_code_project(source_code: SourceCode):
    code_tree = source_code.tree
    code_str = source_code.content

    project_name = code_tree.split("├──")[0].strip()
    project_path = f"/tmp/{project_name}"
    if os.path.exists(project_path):
        shutil.rmtree(project_path)
        os.makedirs(project_path, exist_ok=True)

    # 创建文件并写入内容
    for file_path, file_content in code_str.items():
        file_dir = os.path.join("/tmp", os.path.dirname(file_path))
        file_name = os.path.basename(file_path)
        os.makedirs(file_dir, exist_ok=True)
        with open(os.path.join(file_dir, file_name), "w") as f:
            f.write(file_content)
    return project_path


def run_ci(source_code: SourceCode):
    source_code_path = generate_code_project(source_code)
    pytest_result = run_pytest(source_code_path)
    performance_result = run_cprofile(source_code_path)
    return pytest_result, performance_result
