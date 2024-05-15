import unittest
from darc.darc.router import Router
from darc.darc.multi_addr import MultiAddr

from tests.darc_test.test_base import TestPingMessage

import copy


class TestRouter(unittest.TestCase):
    def setUp(self):
        self.test_multi_addr = MultiAddr("PingPonger--PingPonger")
        self.test_router = Router(self.test_multi_addr)

    def test_addr(self):
        # spawn的node gate实例
        node_gate_instance_addr = self.test_router._node_gate_type_address_dict[
            "PingPonger"
        ]
        node_gate_instance = self.test_router._instance[node_gate_instance_addr]
        # 对比node gate实例的address book
        self.assertEqual(
            id(node_gate_instance._instance[self.test_router._node_addr]),
            id(self.test_router),
        )

    def test_receieve(self):
        test_router_message = copy.deepcopy(TestPingMessage)
        test_router_message.from_agent_type = "PingPonger"
        self.test_router.on_receive(test_router_message)

    def tearDown(self) -> None:
        del self.test_router
        return super().tearDown()


if __name__ == "__main__":
    unittest.main()
