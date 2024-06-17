from typing import List

from loguru import logger

from darc.llm.prompt.system_prompt_template import (
    dev_system_prompt,
    project_manager_prompt,
    pytest_system_prompt,
    tester_system_prompt,
)
from darc.llm.proxy import get_answer_sync
from darc.message import Message
from darc.mock.mock_llm_query import (
    mock_FeatureDev_query,
    mock_PM_query,
    mock_QADev_query,
)
from darc.node import Node


def save_code_to_file(self, code, file_path):
    with open(file_path, "w", encoding="utf-8") as file:
        file.write(code)


class PM(Node):
    def __init__(self, node_addr=None, node_name=""):
        super().__init__(node_addr=node_addr, node_name=node_name)

    @Node.process(["Task:PM"])
    def transport(self, message: List[Message]) -> List[Message]:
        valid_message = message[0]
        demand = valid_message.content
        # result = get_answer_sync(valid_message.content, \
        # project_manager_prompt)
        result = "mock_PM_query"
        message_to_FeatureDev = Message(
            message_name="PM:FeatureDev", content=f"需求：{demand}. {result}"
        )
        msgs = []
        msgs.append(message_to_FeatureDev)
        return msgs


class QADev(Node):
    def __init__(self, node_addr=None, node_name=""):
        super().__init__(node_addr=node_addr, node_name=node_name)

    @Node.process(["FeatureDev:QADev"])
    def act(self, message: List[Message]) -> List[Message]:
        demand = message[0].content
        return [self.work_test(demand)]

    def work_test(self, demand: str) -> Message:
        #         prompt = f"请仅输出代码，不需要任何解释或额外文字, \
        # 特别是'```python', '```' 类似的文字。以下是我需要的功能描述：\
        # [{demand}]\
        # 请直接给出代码："
        # result = get_answer_sync(prompt, pytest_system_prompt)
        result = "mock_QADev_query"
        return Message(
            message_name="QADev:END",
            content=result,
        )


class FeatureDev(Node):
    def __init__(self, node_addr=None, node_name=""):
        super().__init__(node_addr=node_addr, node_name=node_name)

    @Node.process(["PM:FeatureDev"])
    def act(self, message: List[Message]) -> List[Message]:
        logger.debug("act")
        demand = message[0].content
        return [self.work_feature(demand)]

    def work_feature(self, demand: str):
        #         prompt = f"请仅输出代码，不需要任何解释或额外文字, \
        # 特别是'```python', '```' 类似的文字。以下是我需要的功能描述：\
        # [{demand}]\
        # 请直接给出代码："
        # 生成代码
        # code = get_answer_sync(prompt, dev_system_prompt)
        code = "mock_FeatureDev_query"
        message = Message(
            message_name="FeatureDev:QADev",
            content=code,
        )

        return message
