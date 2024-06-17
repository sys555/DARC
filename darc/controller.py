from typing import Any, Dict, List, Optional

import networkx as nx

from darc.agent.dev import PM, FeatureDev, QADev
from darc.logger import MASLog, MASLogger
from darc.message import Message
from darc.multi_addr import MultiAddr
from darc.node import Node
from darc.node_gate import NodeGate
from darc.router import Router


def show(self):
    return self.nodes


class Task:
    def __init__(self, graph, task_id):
        self.graph = graph
        self.entry_node = None
        self.exit_node = None
        self.initial_input = None
        self.result = None
        self.task_id = task_id

    def set_entry_node(self, node_id):
        self.entry_node = node_id

    def set_exit_node(self, node_id):
        self.exit_node = node_id

    def set_initial_input(self, input_data):
        self.initial_input = input_data

    def run(self):
        # 假设这里有一个处理逻辑
        message = Message(
            message_name=f"Task:{self.entry_node.proxy().class_name.get()}",
            content=self.initial_input,
            task_id=self.task_id,
        )
        # TODO:use tell
        self.entry_node.proxy().on_receive(message)


class Graph:
    def __init__(self):
        self.nodes = {}
        self.edges = []
        self._router_dict: Dict[str, Any] = {}
        self._node_type = {}
        self._edge_list = {}
        self._instance = {}
        self.logger = MASLogger()

    @classmethod
    def init(cls, config):
        graph = cls()
        node_instances = {}
        instantiated_classes = set()
        # edge_list = []

        # 生成 router
        for left_cls, right_cls in config.get("edge", []):
            # 构造边名
            edge = left_cls.__name__ + ":" + right_cls.__name__
            graph._spawn_new_actor(Router, edge)

        # 根据 args 生成 node
        for node_cls, count, args_list in config.get("args", []):
            instantiated_classes.add(node_cls)
            for args in args_list:
                instance = graph._spawn_new_instance(node_cls, args)
                node_instances.setdefault(node_cls, []).append(instance)
                graph.add_node(instance)

        # 检查config["node"]中提到的所有类，为未实例化的类创建默认实例
        for node_cls in config.get("node", []):
            if node_cls not in instantiated_classes:
                instance = graph._spawn_new_instance(
                    node_cls, args=None
                )  # 无参构造
                node_instances.setdefault(node_cls, []).append(instance)
                graph.add_node(instance)

        return graph

    def _spawn_new_actor(self, cls, router_name: str):
        if router_name not in self._router_dict:
            router_addr = MultiAddr(router_name)
            router_instance = cls.start(router_addr)
            self._instance[router_addr] = router_instance
            self._router_dict[router_name] = router_instance

    def _spawn_new_instance(self, cls, args) -> Any:
        nodegate_type = cls.__name__
        for router_name in self._router_dict:
            if nodegate_type in router_name:
                instance = (
                    self._router_dict[router_name]
                    .proxy()
                    .spawn_real_instance(cls, args)
                    .get()
                )
                return instance
        return None

    def add_edge(self, edge_name):
        if edge_name not in self._router_dict:
            self._spawn_new_actor(Router, edge_name)

    def add_node(self, node: Any):
        self.nodes[node.proxy().id.get()] = node

    def find_type(self, cls_name) -> Any:
        for router_name in self._router_dict:
            if cls_name in router_name:
                node_type_instance = (
                    self._router_dict[router_name]
                    .proxy()
                    .get_all_node_instance(cls_name)
                    .get()
                )
                return node_type_instance
        return []

    def find_node_with_name(self, node_name, cls_name) -> Any:
        for router_name in self._router_dict:
            if cls_name in router_name:
                node_type_instance = (
                    self._router_dict[router_name]
                    .proxy()
                    .get_all_node_instance(cls_name)
                    .get()
                )
                for item in node_type_instance:
                    if item.proxy().node_name.get() == node_name:
                        return item
        return None

    def run(self, task: Task):
        task.run()

    def get_result(self, task_id) -> Any:
        return self.logger.get_result(task_id)

    def get_log(self, task_id) -> Any:
        return self.logger.get_logs(task_id)


def config_to_networkx(config):
    G = nx.MultiDiGraph()  # 创建多重有向图

    # 添加节点
    for node in config["node"]:
        G.add_node(node.__name__)  # 使用类名作为节点标识

    # 添加边
    for edge in config["edge"]:
        G.add_edge(
            edge[0].__name__, edge[1].__name__
        )  # 使用类名作为节点标识，多条边也被允许

    # 添加节点的参数，使用节点属性来存储
    for args in config["args"]:
        node, count, attributes = args
        # 更新节点属性
        G.nodes[node.__name__]["count"] = count
        G.nodes[node.__name__]["attributes"] = attributes

    return G


def networkx_to_config(G):
    config = {"node": [], "edge": [], "args": []}

    # 处理节点和节点参数
    for node in G.nodes:
        node_class = eval(node)  # 通过名字恢复类对象,注意这里的安全风险
        config["node"].append(node_class)
        # 将节点属性信息转换回配置格式
        node_attrs = G.nodes[node]
        config["args"].append(
            (
                node_class,
                node_attrs.get("count", 0),
                node_attrs.get("attributes", []),
            )
        )

    # 处理边，适配MultiGraph或MultiDiGraph
    for from_node, to_node, key in G.edges(
        keys=True
    ):  # 添加keys=True来获取边的键
        from_class = eval(from_node)
        to_class = eval(to_node)
        config["edge"].append(
            (from_class, to_class)
        )  # 如果需要，也可以包含 key

    return config
