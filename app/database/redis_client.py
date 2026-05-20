# MOCKED REDIS CLIENT FOR LOCAL TESTING

class MockRedis:
    def __init__(self):
        self.store = {}

    async def get(self, *args, **kwargs): return None
    async def set(self, *args, **kwargs): return True
    async def eval(self, *args, **kwargs): return 1
    async def close(self): pass
    async def aclose(self): pass

    # Mock pipeline for rate limiters
    def pipeline(self, *args, **kwargs): return self
    async def execute(self, *args, **kwargs): return [1, 1]
    
    # Allow missing methods to be called without crashing
    def __getattr__(self, name):
        async def mock_method(*args, **kwargs):
            return 1
        return mock_method

class MockPool:
    async def disconnect(self): pass

pool = MockPool()
redis_client = MockRedis()
