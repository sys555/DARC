from darc.darc.node import Node


class LLM_with_PPL(Node):
    def __init__(self, id, llm):
        super().__init__(id)
        self.llm_name = llm

    @Node.process("generate")
    def generate_text(self, prompt):
        return f"Generated text by {self.llm_name} for prompt: {prompt}"
