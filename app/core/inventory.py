import asyncio
import logging
from fastapi import HTTPException, status

logger = logging.getLogger(__name__)

# Global state for mock testing
_mock_store = {}
_mock_locks = {}

class RedisInventoryManager:
    """
    Mocked inventory manager using in-memory dicts and asyncio.Lock.
    Implements Dynamic Surge Pricing and Cart Expiration Mock.
    """
    
    def __init__(self, redis_client=None):
        self.store = _mock_store
        self.locks = _mock_locks
        
    def _get_lock(self, product_id: str) -> asyncio.Lock:
        if product_id not in self.locks:
            self.locks[product_id] = asyncio.Lock()
        return self.locks[product_id]

    async def purchase_item(self, product_id: str, quantity: int = 1, lock_timeout: float = 2.0) -> dict:
        lock = self._get_lock(product_id)
        
        try:
            # 1. Acquire Local Async Lock
            await asyncio.wait_for(lock.acquire(), timeout=lock_timeout)
        except asyncio.TimeoutError:
            logger.warning(f"Could not acquire lock for {product_id}. High contention.")
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="System is experiencing high traffic for this item. Please try again."
            )

        try:
            inventory_key = f"inventory:{product_id}"
            
            # 2. Check Current Inventory
            if inventory_key not in self.store:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Product inventory not found. Please initialize stock first."
                )
            
            current_stock = self.store[inventory_key]['current']
            initial_stock = self.store[inventory_key]['initial']
            base_price = self.store[inventory_key]['base_price']
            
            # 3. Validate Stock
            if current_stock < quantity:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Out of stock. Requested: {quantity}, Available: {current_stock}."
                )

            # 4. Dynamic Surge Pricing Logic
            # If stock drops below 20%, surge the price by 10%
            surge_active = current_stock <= (initial_stock * 0.20)
            final_price = base_price * 1.10 if surge_active else base_price

            # 5. Deduct Inventory safely inside lock
            self.store[inventory_key]['current'] -= quantity
            remaining_stock = self.store[inventory_key]['current']
            
            logger.info(f"Processed purchase for {product_id}. Remaining stock: {remaining_stock}, Final Price: {final_price}")
            
            # 6. Cart Expiration Mock
            # Simulate placing in a cart with a 10-minute TTL.
            asyncio.create_task(self._mock_cart_expiration(product_id, quantity))
            
            return {
                "remaining_stock": remaining_stock,
                "final_price": final_price,
                "surge_active": surge_active
            }

        finally:
            # 7. Release Local Lock
            lock.release()
            
    async def _mock_cart_expiration(self, product_id: str, quantity: int):
        """Simulates holding an item in a cart for 10 minutes, then reverting if payment isn't completed."""
        await asyncio.sleep(600)  # Sleep for 10 minutes (mock TTL)
        
        lock = self._get_lock(product_id)
        async with lock:
            inventory_key = f"inventory:{product_id}"
            if inventory_key in self.store:
                self.store[inventory_key]['current'] += quantity
                logger.info(f"Cart expired for {product_id}. Reverted {quantity} items back to stock.")

    async def set_inventory(self, product_id: str, quantity: int, base_price: float) -> None:
        inventory_key = f"inventory:{product_id}"
        self.store[inventory_key] = {
            'initial': quantity,
            'current': quantity,
            'base_price': base_price
        }

    async def get_status(self, product_id: str) -> dict:
        """Helper to get live stock and pricing data for the Frontend UI."""
        inventory_key = f"inventory:{product_id}"
        if inventory_key not in self.store:
            return None
            
        current = self.store[inventory_key]['current']
        initial = self.store[inventory_key]['initial']
        base = self.store[inventory_key]['base_price']
        
        surge_active = current > 0 and current <= (initial * 0.20)
        current_price = base * 1.10 if surge_active else base
        
        return {
            "stock": current,
            "price": current_price,
            "surge": surge_active
        }
