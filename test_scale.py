import asyncio
import httpx
import time
import random

# Configuration
API_URL = "http://127.0.0.1:8000"
PRODUCT_ID = "flash_ps5_001"
TOTAL_REQUESTS = 1000
INITIAL_STOCK = 10

async def setup_stock():
    """Initialize the stock in the database before the test."""
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                f"{API_URL}/set_stock/{PRODUCT_ID}",
                json={"quantity": INITIAL_STOCK}
            )
            print(f"Stock initialization: {response.status_code} - {response.json()}")
        except Exception as e:
            print(f"Failed to setup stock. Is the server running? Error: {e}")
            exit(1)

async def make_purchase_request(client: httpx.AsyncClient, req_id: int):
    """Simulates a single user attempting to buy the product."""
    # We use random user IDs to simulate distributed traffic and occasionally hit rate limits
    user_id = f"user_{random.randint(1, 500)}" 
    
    start_time = time.time()
    try:
        response = await client.post(
            f"{API_URL}/purchase/{PRODUCT_ID}",
            json={"user_id": user_id, "quantity": 1},
            timeout=15.0 # Higher timeout since 1000 requests will queue up
        )
        latency = time.time() - start_time
        return response.status_code, response.text, latency
    except Exception as e:
        latency = time.time() - start_time
        return 500, str(e), latency

async def main():
    print("=====================================================")
    print(f"🚀 Starting Flash Sale Load Test")
    print(f"🎯 Target: {TOTAL_REQUESTS} concurrent requests")
    print(f"📦 Initial Stock: {INITIAL_STOCK}")
    print("=====================================================")
    
    # 1. Setup the initial stock
    await setup_stock()
    
    print("\n[Fire!] Sending all requests concurrently at the exact same time...\n")
    
    start_time = time.time()
    
    # 2. We use custom Limits to allow a massive burst of concurrent connections
    limits = httpx.Limits(max_connections=2000, max_keepalive_connections=2000)
    async with httpx.AsyncClient(limits=limits) as client:
        # Create all tasks without awaiting them immediately
        tasks = [make_purchase_request(client, i) for i in range(TOTAL_REQUESTS)]
        
        # Execute them all concurrently using asyncio.gather
        results = await asyncio.gather(*tasks)
        
    total_time = time.time() - start_time
    
    # 3. Analyze Results
    status_counts = {}
    successes = 0
    oversold_errors = 0
    rate_limit_lock_errors = 0
    server_errors = 0
    
    for status, body, latency in results:
        status_counts[status] = status_counts.get(status, 0) + 1
        
        if status == 200:
            successes += 1
        elif status == 400 and "Out of stock" in str(body):
            oversold_errors += 1
        elif status == 429:
            rate_limit_lock_errors += 1
        elif status >= 500:
            server_errors += 1
            
    print("=====================================================")
    print("📊 Test Results")
    print("=====================================================")
    print(f"Total Time Taken     : {total_time:.2f} seconds")
    print(f"Requests per second  : {TOTAL_REQUESTS / total_time:.2f} req/s")
    print(f"Successful Purchases : {successes} (Status 200)")
    print(f"Rate Limit/Lock Busy : {rate_limit_lock_errors} (Status 429)")
    print(f"Out of Stock Rejects : {oversold_errors} (Status 400)")
    print(f"Server Errors        : {server_errors} (Status 500+)")
    print(f"\nRaw Status Codes     : {status_counts}")
    
    print("\n=====================================================")
    print("📝 Conclusion")
    print("=====================================================")
    if successes <= INITIAL_STOCK:
        print(f"✅ SUCCESS: System safely prevented overselling!")
        print(f"   Sold exactly {successes} items out of {INITIAL_STOCK} available.")
    else:
        print(f"❌ FAILURE: System oversold!")
        print(f"   Sold {successes} items, but only {INITIAL_STOCK} were available.")
        print("   Check your Redis Distributed Lock implementation.")

if __name__ == "__main__":
    asyncio.run(main())
