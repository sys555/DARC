import random
import string
import os


class MultiAddr:
    def __init__(self, name="None") -> None:
        self.addr: str = self.random_addr()
        self.name: str = name

    def random_addr(self):
        random.seed(os.urandom(32))
        characters = string.ascii_letters + string.digits
        # 生成随机字符串
        random_string = "".join(random.choice(characters) for _ in range(16))
        return random_string
