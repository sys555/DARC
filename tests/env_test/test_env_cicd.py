import os
from pathlib import Path
import shutil

from darc.environment.cicd import run_pytest
from loguru import logger

def test_pytest():
    # demand_dir = "/tmp/demand/pytest_demo"
    demand_dir = "/Users/mac/Documents/pjlab/repo/LLMSafetyChallenge/tests/env_test/tmp/demand/pytest_demo"
    if os.path.exists(demand_dir):
        shutil.rmtree(demand_dir)
    os.makedirs(demand_dir)
    tests_dir = os.path.join(demand_dir, "tests")
    os.makedirs(tests_dir)
    test_main_path = os.path.join(tests_dir, "test_main.py")
    with open(test_main_path, "w") as f:
        f.write(
            """
def test_add():
    assert 1+ 1 == 2
"""
        )
    pytest_result = run_pytest(demand_dir)
    assert "coverage_report" in pytest_result
    assert "pytest_report" in pytest_result
    assert pytest_result["pytest_report"] == {"collected": 1, "passed": 1, "total": 1}
    assert pytest_result["coverage_report"][f"{demand_dir}/tests/test_main.py"][
        "summary"
    ] == {
        "covered_lines": 2,
        "num_statements": 2,
        "percent_covered": 100.0,
        "percent_covered_display": "100",
        "missing_lines": 0,
        "excluded_lines": 0,
    }