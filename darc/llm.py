from darc.darc.node import Node


class LLM_with_PPL(Node):
    def __init__(self, llm="GPT-4"):
        super().__init__()
        self.llm = llm

    @Node.process("generate")
    def generate_text(self, message):
        # Example logic for generating text with a language model
        print(
            f"Generating text with {self.llm} using prompt: {message['data']}"
        )

    @Node.process("evaluate_ppl")
    def evaluate_ppl(self, message):
        # Example logic for evaluating perplexity
        print(f"Evaluating PPL for text: {message['data']} using {self.llm}")
