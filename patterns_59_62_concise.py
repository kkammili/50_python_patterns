"""Patterns 59–62: Concise, comment-rich code. No essays."""

import asyncio
import queue
import random
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from contextlib import contextmanager
from functools import wraps

# ─── Pattern 59: Retry + Backoff + Rate Limit ───────────────────────────────

def backoff(attempt, base=0.5, cap=8):
    """Exponential backoff with jitter: 0-base, 0-base*2, 0-base*4, ..., capped."""
    return random.uniform(0, min(cap, base * 2**attempt))

def with_retry(max_tries=3):
    """Retry transient errors with exponential backoff."""
    def decorator(fn):
        @wraps(fn)
        def wrapper(*a, **kw):
            for attempt in range(max_tries):
                try:
                    return fn(*a, **kw)
                except Exception as e:
                    if attempt == max_tries - 1 or (hasattr(e, 'status') and e.status == 404):
                        raise
                    time.sleep(backoff(attempt))
        return wrapper
    return decorator

class RateLimiter:
    """Block if called too soon (2 calls/sec max)."""
    def __init__(self, rate):
        self.rate, self.last = rate, 0
    def wait(self):
        elapsed = time.time() - self.last
        wait_time = 1/self.rate - elapsed
        if wait_time > 0:
            time.sleep(wait_time)
        self.last = time.time()

# ─── Pattern 60: Validation + Error Hierarchy + Cleanup ──────────────────────

class AppError(Exception): pass
class ValidationError(AppError): pass
class InsufficientFundsError(AppError): pass

class Account:
    def __init__(self, name, balance):
        self.name, self.balance = name, balance

    def transfer(self, other, amount):
        # Validate before mutating
        if not isinstance(amount, (int, float)):
            raise ValidationError(f"amount must be number, got {type(amount)}")
        if amount <= 0:
            raise ValidationError("amount must be positive")
        if self.balance < amount:
            raise InsufficientFundsError(f"need {amount}, have {self.balance}")
        # Only mutate if all checks passed
        self.balance -= amount
        other.balance += amount

@contextmanager
def safe_file(name):
    """Open file; guarantee cleanup with try/finally."""
    f = open(name, "w")
    try:
        yield f
    finally:
        f.close()

# ─── Pattern 61: Locks + Thread Pool + Queue ──────────────────────────────────

class Counter:
    def __init__(self):
        self.value, self.lock = 0, threading.Lock()

    def unsafe_inc(self):
        v = self.value
        time.sleep(0)  # yield → race condition
        self.value = v + 1

    def safe_inc(self):
        with self.lock:  # only one thread at a time
            v = self.value
            time.sleep(0)
            self.value = v + 1

def download(url):
    time.sleep(0.1)
    return f"Downloaded {url}"

def producer(q):
    for i in range(1, 4):
        q.put(i)
    q.put(None)  # sentinel

def consumer(q):
    while True:
        item = q.get()
        if item is None:
            break
        print(f"  Consumed: {item}")

# ─── Pattern 62: async/await ──────────────────────────────────────────────────

async def fetch(url, delay=0.05):
    await asyncio.sleep(delay)  # yield control; other tasks run
    return f"Page: {url}"

async def demo_async():
    urls = [f"site{i}.com" for i in range(4)]
    # Sequential
    start = time.perf_counter()
    for url in urls:
        await fetch(url)
    t1 = time.perf_counter() - start
    # Concurrent
    start = time.perf_counter()
    await asyncio.gather(*[fetch(url) for url in urls])
    t2 = time.perf_counter() - start
    print(f"Seq: {t1:.2f}s | Parallel: {t2:.2f}s ({t1/t2:.1f}x faster)")

# Quick demo
if __name__ == "__main__":
    print("= Pattern 60: Error handling & validation =")
    alice, bob = Account("alice", 100), Account("bob", 0)
    try:
        alice.transfer(bob, 50)
        print(f"✓ alice={alice.balance}, bob={bob.balance}")
    except AppError as e:
        print(f"✗ {e}")

    print("\n= Pattern 61: Thread pool =")
    urls = [f"site{i}.com" for i in range(3)]
    with ThreadPoolExecutor(max_workers=3) as pool:
        for result in pool.map(download, urls):
            print(f"✓ {result}")

    print("\n= Pattern 62: Async/await =")
    asyncio.run(demo_async())
