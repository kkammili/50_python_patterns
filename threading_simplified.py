"""
Python Threading & Concurrency Patterns - Simplified
======================================================
Core patterns explained with minimal code.
"""

import threading
import time
import queue
from concurrent.futures import ThreadPoolExecutor, as_completed


# ═══════════════════════════════════════════════════════════════
# 1. RACE CONDITION vs LOCK
# ═══════════════════════════════════════════════════════════════

class Counter:
    def __init__(self):
        self.value = 0
        self.lock = threading.Lock()

    def unsafe_add(self):
        """Without lock: reads and writes can interleave → data corruption"""
        current = self.value
        time.sleep(0)  # yield, simulating the race condition
        self.value = current + 1

    def safe_add(self):
        """With lock: only one thread at a time"""
        with self.lock:
            current = self.value
            time.sleep(0)
            self.value = current + 1

# Test
c_bad = Counter()
c_good = Counter()

def add_1000_times(counter, method):
    for _ in range(1000):
        getattr(counter, method)()

threads_bad = [threading.Thread(target=add_1000_times, args=(c_bad, 'unsafe_add')) for _ in range(4)]
threads_good = [threading.Thread(target=add_1000_times, args=(c_good, 'safe_add')) for _ in range(4)]

for t in threads_bad: t.start()
for t in threads_bad: t.join()

for t in threads_good: t.start()
for t in threads_good: t.join()

print(f"Unsafe: {c_bad.value} (should be 4000) | Safe: {c_good.value}")
assert c_good.value == 4000 and c_bad.value < 4000


# ═══════════════════════════════════════════════════════════════
# 2. THREAD POOL for I/O-bound work
# ═══════════════════════════════════════════════════════════════

def download(url):
    """Simulate a slow network request"""
    time.sleep(0.1)
    return f"Downloaded {url}"

urls = [f"https://site{i}.com" for i in range(5)]

# Sequential (slow)
start = time.perf_counter()
results_seq = [download(url) for url in urls]
time_seq = time.perf_counter() - start

# Parallel with threads (fast)
start = time.perf_counter()
with ThreadPoolExecutor(max_workers=5) as pool:
    results_par = list(pool.map(download, urls))
time_par = time.perf_counter() - start

print(f"Sequential: {time_seq:.2f}s | Parallel: {time_par:.2f}s")
print(f"Speedup: {time_seq/time_par:.1f}x faster")


# ═══════════════════════════════════════════════════════════════
# 3. PRODUCER-CONSUMER with queue.Queue
# ═══════════════════════════════════════════════════════════════

STOP = object()  # Sentinel to tell consumers to stop

def producer(q):
    """Put numbers 1-5 into queue"""
    for i in range(1, 6):
        q.put(i)
        print(f"  Produced: {i}")
    q.put(STOP)  # Signal to stop

def consumer(q, consumer_id):
    """Take numbers and square them"""
    while True:
        item = q.get()
        if item is STOP:
            break
        squared = item ** 2
        print(f"  Consumer {consumer_id} got {item} → {squared}")

q = queue.Queue()
prod = threading.Thread(target=producer, args=(q,))
cons = threading.Thread(target=consumer, args=(q, 1))

prod.start()
cons.start()
prod.join()
cons.join()


# ═══════════════════════════════════════════════════════════════
# 4. EVENT: Stop a background worker gracefully
# ═══════════════════════════════════════════════════════════════

def worker(stop_event):
    """Run until stop_event is set"""
    count = 0
    while not stop_event.wait(timeout=0.1):  # Check every 100ms
        count += 1
        print(f"  Working... ({count})")
    print(f"  Stopped after {count} iterations")

stop = threading.Event()
thread = threading.Thread(target=worker, args=(stop,))
thread.start()
time.sleep(0.35)
stop.set()  # Signal the worker to stop
thread.join()


# ═══════════════════════════════════════════════════════════════
# 5. SEMAPHORE: Limit concurrent access (e.g., connection pool)
# ═══════════════════════════════════════════════════════════════

semaphore = threading.Semaphore(2)  # Only 2 threads at a time
results = []

def query_database(query_id):
    """Simulate DB query with max 2 concurrent"""
    with semaphore:
        results.append(f"Query {query_id} started")
        time.sleep(0.05)  # Simulate work
        results.append(f"Query {query_id} done")

with ThreadPoolExecutor(max_workers=5) as pool:
    pool.map(query_database, range(1, 6))

print("Database queries (max 2 concurrent):")
for r in results:
    print(f"  {r}")


# ═══════════════════════════════════════════════════════════════
# 6. ALTERNATING THREADS with Semaphores
# ═══════════════════════════════════════════════════════════════

class PrintAlternate:
    """Print 'foo' and 'bar' alternately"""
    def __init__(self):
        self.foo_sem = threading.Semaphore(1)    # foo goes first
        self.bar_sem = threading.Semaphore(0)    # bar waits

    def print_foo(self):
        for _ in range(3):
            self.foo_sem.acquire()
            print("foo", end="")
            self.bar_sem.release()

    def print_bar(self):
        for _ in range(3):
            self.bar_sem.acquire()
            print("bar", end="")
            self.foo_sem.release()

printer = PrintAlternate()
t1 = threading.Thread(target=printer.print_foo)
t2 = threading.Thread(target=printer.print_bar)
t1.start()
t2.start()
t1.join()
t2.join()
print()  # newline


# ═══════════════════════════════════════════════════════════════
# 7. ORDERED EXECUTION with Events
# ═══════════════════════════════════════════════════════════════

class PrintInOrder:
    """Guarantee: first() → second() → third() always"""
    def __init__(self):
        self.first_done = threading.Event()
        self.second_done = threading.Event()

    def first(self):
        print("first", end=" ")
        self.first_done.set()

    def second(self):
        self.first_done.wait()
        print("second", end=" ")
        self.second_done.set()

    def third(self):
        self.second_done.wait()
        print("third")

printer = PrintInOrder()
# Start in random order!
t1 = threading.Thread(target=printer.third)
t2 = threading.Thread(target=printer.first)
t3 = threading.Thread(target=printer.second)

t1.start()
t2.start()
t3.start()
t1.join()
t2.join()
t3.join()


# ═══════════════════════════════════════════════════════════════
# 8. DEADLOCK AVOIDANCE: Always acquire locks in the same order
# ═══════════════════════════════════════════════════════════════

class Account:
    counter = 0
    def __init__(self, balance):
        self.id = Account.counter
        self.balance = balance
        self.lock = threading.Lock()
        Account.counter += 1

def transfer(from_acc, to_acc, amount):
    """Transfer money safely (no deadlock)"""
    # Always acquire in the same order (by ID)
    first, second = (from_acc, to_acc) if from_acc.id < to_acc.id else (to_acc, from_acc)

    with first.lock:
        with second.lock:
            from_acc.balance -= amount
            to_acc.balance += amount

# Test: many transfers both directions
alice = Account(1000)
bob = Account(1000)

def do_transfers():
    for i in range(100):
        if i % 2 == 0:
            transfer(alice, bob, 1)
        else:
            transfer(bob, alice, 1)

with ThreadPoolExecutor(max_workers=4) as pool:
    pool.map(lambda _: do_transfers(), range(2))

print(f"Alice: {alice.balance} | Bob: {bob.balance} | Total: {alice.balance + bob.balance}")
assert alice.balance + bob.balance == 2000
