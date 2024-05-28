import uuid

from .message import Message

# import pykka


class Graph:
    def __init__(self):
        self.nodes = {}
        self.edges = []

    @classmethod
    def init(cls, config):
        graph = cls()
        node_instances = {}
        instantiated_classes = set()

        # 创建节点实例，并记录已实例化的类
        for node_cls, count, args in config.get("args", []):
            instantiated_classes.add(node_cls)
            for _ in range(count):
                instance = node_cls.start(**args)
                node_instances.setdefault(node_cls, []).append(instance)
                graph.add_node(instance)

        # 检查config["node"]中提到的所有类，为未实例化的类创建默认实例
        for node_cls in config.get("node", []):
            if node_cls not in instantiated_classes:
                instance = (
                    node_cls.start()
                )  # 假设所有类都有一个无参数的构造函数
                node_instances.setdefault(node_cls, []).append(instance)
                graph.add_node(instance)

        # 设置边
        for src_cls, dst_cls in config.get("edge", []):
            for src in node_instances.get(src_cls, []):
                for dst in node_instances.get(dst_cls, []):
                    graph.add_edge(src, dst)

        return graph

    def add_node(self, node):
        self.nodes[node.proxy().node_name.get()] = node

    def add_edge(self, src, dst):
        self.edges.append((src.proxy().id.get(), dst.proxy().id.get()))
        src.proxy().link_node(dst, dst.proxy().address.get())

    def find_type(self, cls_name):
        return [
            node
            for node in self.nodes.values()
            if node.proxy().class_name.get() == cls_name
        ]

    def show(self):
        return self.nodes


class Task:
    def __init__(self, graph):
        self.graph = graph
        self.entry_node = None
        self.exit_node = None
        self.initial_input = None
        self.result = None
        self.task_id = str(uuid.uuid4())

    def set_entry_node(self, node_id):
        self.entry_node = node_id

    def set_exit_node(self, node_id):
        self.exit_node = node_id

    def set_initial_input(self, input_data):
        self.initial_input = input_data

    def run(self):
        # 假设这里有一个处理逻辑
        # current_node = self.graph.nodes[self.entry_node]
        initial_message = Message(
            message_name="Task:Attacker",
            from_agent="",
            to_agent="",
            content=self.initial_input,
            task_id=self.task_id,
        )
        self.entry_node.tell(initial_message)
