class Graph:
    def __init__(self):
        self.nodes = {}
        self.edges = []

    @classmethod
    def init(cls, config):
        graph = cls()
        node_instances = {}

        # 创建节点实例
        for node_cls, count, args in config["args"]:
            for _ in range(count):
                instance = node_cls(**args)
                node_instances.setdefault(node_cls, []).append(instance)
                graph.add_node(instance)

        # 设置边
        for src_cls, dst_cls in config["edge"]:
            for src in node_instances[src_cls]:
                for dst in node_instances[dst_cls]:
                    graph.add_edge(src, dst)

        return graph

    def add_node(self, node):
        self.nodes[node.id] = node

    def add_edge(self, src, dst):
        self.edges.append((src.id, dst.id))

    def find_type(self, cls_name):
        return [
            node
            for node in self.nodes.values()
            if node.__class__.__name__ == cls_name
        ]


class Task:
    def __init__(self, graph):
        self.graph = graph
        self.entry_node = None
        self.exit_node = None
        self.initial_input = None
        self.result = None

    def set_entry_node(self, node_id):
        self.entry_node = node_id

    def set_exit_node(self, node_id):
        self.exit_node = node_id

    def set_initial_input(self, input_data):
        self.initial_input = input_data

    def run(self):
        # 假设这里有一个处理逻辑
        # current_node = self.graph.nodes[self.entry_node]
        self.result = "Process complete"
