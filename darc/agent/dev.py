from typing import List

from loguru import logger

from darc.llm.proxy import get_answer_sync
from darc.message import Message
from darc.node import Node


class PM(Node):
    def __init__(self, node_addr=None, node_name="") -> None:
        super().__init__(node_addr=node_addr, node_name=node_name)

    @Node.process(["Task:PM"])
    def transport(self, message: List[Message]) -> [Message]:
        valid_message = message[0]
        message_to_FeatureDev = Message(
            message_name="PM:FeatureDev", content=valid_message.content
        )
        msgs = []
        msgs.append(message_to_FeatureDev)
        return msgs


class QADev(Node):
    def __init__(self, node_addr=None, node_name="") -> [Message]:
        super().__init__(node_addr=node_addr, node_name=node_name)

    @Node.process(["PM:QADev"])
    def act(self, message: List[Message]) -> [Message]:
        demand = message[0].content
        return [self.work_test(demand)]

    def work_test(self, demand: str) -> Message:
        return Message(
            message_name="QADev:FeatureDev",
            content=demand,
        )


class FeatureDev(Node):
    def __init__(self, node_addr=None, node_name="") -> [Message]:
        super().__init__(node_addr=node_addr, node_name=node_name)

    @Node.process(["PM:FeatureDev"])
    def act(self, message: List[Message]) -> [Message]:
        logger.debug("act")
        demand = message[0].content
        return [self.work_feature(demand)]

    def work_feature(self, demand: str):
        prompt = f"请仅输出代码，不需要任何解释或额外文字, 特别是'```python', '```' 类似的文字。以下是我需要的功能描述：\
[{demand}]\
请直接给出代码："
        # prompt = "what do you want to do"
        file_path = "/Users/mac/Documents/pjlab/repo/LLMSafetyChallenge/darc/llm/proxy/snake.py"

        # 生成代码
        code = get_answer_sync(prompt)

        # 将代码保存到指定文件
        # self.save_code_to_file(code, file_path)

        message = Message(
            message_name="FeatureDev:END",
            content=code,
        )

        return message

    def save_code_to_file(self, code, file_path):
        with open(file_path, "w", encoding="utf-8") as file:
            file.write(code)
