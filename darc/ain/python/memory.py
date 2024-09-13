from mem0 import Memory

class Mem:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(Mem, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not hasattr(self, '_memory'):
            self._memory = Memory()
    
    def add(self, *args, **kwargs):
        return self._memory.add(*args, **kwargs)

    def update(self, *args, **kwargs):
        return self._memory.update(*args, **kwargs)

    def search(self, *args, **kwargs):
        return self._memory.search(*args, **kwargs)

    def get_all(self):
        return self._memory.get_all()