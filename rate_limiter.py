import time

class TokenBucketRateLimiter:
    """
    Mock global rate limiter that blocks bursts of traffic to simulate spam protection.
    Limits global throughput to ~10 requests per second.
    """
    def __init__(self, *args, **kwargs):
        self.global_requests = 0
        self.last_reset = time.time()
        
    async def is_allowed(self, user_id: str) -> bool:
        now = time.time()
        # Reset bucket every 1 second
        if now - self.last_reset > 1.0:
            self.global_requests = 0
            self.last_reset = now
            
        self.global_requests += 1
        
        # Block if more than 10 requests per second globally
        if self.global_requests > 10:
            return False
            
        return True
