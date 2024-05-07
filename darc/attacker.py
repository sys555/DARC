from darc.node import Node
class Attacker(Node):
    def __init__(self, id):
        super().__init__(id)

    @Node.process('attack')
    def perform_attack(self, data):
        return f"Attacked data: {data}"
