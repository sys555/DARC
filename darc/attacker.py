from darc.darc.node import Node


class Attacker(Node):
    @Node.process("attack")
    def perform_attack(self, message: str) -> str:
        print("Performing an attack using:", message)
        return f"Attack on {message} completed"
