class Graph:
    def __init__(self):
        self.nodes = []
        self.edges = []

    @classmethod
    def init(cls, config):
        graph = cls()
        # Create node instances as per config
        id_counter = 0
        node_lookup = {}
        for node_cls in config["node"]:
            if isinstance(node_cls, tuple):
                for _ in range(node_cls[1]):
                    node_instance = node_cls[0](id=id_counter, **node_cls[2])
                    graph.nodes.append(node_instance)
                    node_lookup[
                        node_instance.__class__.__name__, id_counter
                    ] = node_instance
                    id_counter += 1
            else:
                node_instance = node_cls(id=id_counter)
                graph.nodes.append(node_instance)
                node_lookup[node_instance.__class__.__name__, id_counter] = (
                    node_instance
                )
                id_counter += 1

        # Create edges
        for src, dest in config["edge"]:
            graph.edges.append(
                (node_lookup[src.__name__], node_lookup[dest.__name__])
            )

        return graph

    def find_type(self, type_name):
        return [
            node for node in self.nodes if node.__class__.__name__ == type_name
        ]


class Task:
    def __init__(self, graph):
        self.graph = graph
        self.entry_node = None
        self.exit_node = None
        self.result = None

    def set_entry_node(self, node_id):
        self.entry_node = self.graph.nodes[node_id]

    def set_exit_node(self, node_id):
        self.exit_node = self.graph.nodes[node_id]

    def set_initial_input(self, input_data):
        self.input_data = input_data

    def run(self):
        # Simplified example: run the task and update result
        self.result = (
            "expected task result"  # Modify this with actual execution logic
        )
