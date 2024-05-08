from darc.darc.node import Node


class Attacker(Node):
    @Node.process("attack")
    def perform_attack(self, message):
        print("Performing an attack using:", message["data"])
