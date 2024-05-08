import unittest
import uuid

from .test_base import PingMessage


class TestMessage(unittest.TestCase):
    def test_message_generate(self):
        message_id = uuid.uuid4()
        task_id = uuid.uuid4()
        from_agent = "test_agent_addr"
        content = "test content"
        specific_ping_message = PingMessage(
            message_id=message_id,
            task_id=task_id,
            from_agent=from_agent,
            content=content,
        )
        self.assertEqual(specific_ping_message.message_name, "PingMessage")
        self.assertEqual(specific_ping_message.message_id, message_id)
        self.assertEqual(specific_ping_message.task_id, task_id)
        self.assertEqual(specific_ping_message.content, content)
        self.assertEqual(specific_ping_message.from_agent, from_agent)


if __name__ == "__main__":
    unittest.main()
