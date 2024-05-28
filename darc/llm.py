import json
from typing import List

from darc.message import Message
from darc.node import Node


class LLM_with_PPL(Node):
    def __init__(self, llm="GPT-4"):
        super().__init__()
        self.llm = llm
        self.num_llm_batch = 32
        self.llm_batch_msg = []

    @Node.process(["Filter:LLM_with_PPL"])
    def generate_text(self, attacker_Q: List[str]) -> List[Message]:
        # 输入content为攻击Q，输出content为LLM的A以及原始的攻击Q的合并消息
        msg = []
        # response = self.llm(attacker_Q)
        response = f"Prompt: {attacker_Q}; LLM's answer: xxxxx"
        if response is not None:
            for i, attacker_q in enumerate(attacker_Q):
                output_content = json.dumps([attacker_q, response[i]])
                # 将Q和对应的A以某种用户定义的形式进行拼接
                msg.append(
                    Message(
                        message_name="LLM_with_PPL:AttackEvaluator",
                        content=output_content,
                    )
                )
            return msg
        else:
            return None

    # LLM函数内部支持batch操作
    def llm(self, inp: str):
        responces = None
        self.llm_batch_msg.append(inp)
        if len(self.llm_batch_msg) >= self.num_llm_batch:
            responces = self.batch_llm(self.llm_batch_msg)
        return responces

    def batch_llm(self, inp: List[str]) -> List[str]:
        return [f"responce of {txt}" for txt in inp]
