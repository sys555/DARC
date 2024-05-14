from dataclasses import dataclass
import random
import string


def random_addr():
    characters = string.ascii_letters + string.digits
    # 生成随机字符串
    random_string = "".join(random.choice(characters) for _ in range(16))
    return random_string


@dataclass
class MultiAddr:
    addr: str = random_addr()
    name: str = "None"
