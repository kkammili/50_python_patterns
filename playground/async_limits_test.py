import asyncio
import time
import sys

async def fake_fetch(url, delay=1):
    await asyncio.sleep(delay)
    return f"<{url}>"

async def test_concurrent(num_urls):
    """Test concurrent execution"""
    urls = [f"https://example.com/{i}" for i in range(num_urls)]

    start = time.perf_counter()
    try:
        results = await asyncio.gather(*(fake_fetch(u) for u in urls), return_exceptions=True)
        elapsed = time.perf_counter() - start
        errors = sum(1 for r in results if isinstance(r, Exception))
        print(f"✓ Concurrent ({num_urls:,} URLs): {elapsed:.2f}s | Errors: {errors}")
        return True
    except Exception as e:
        print(f"✗ Concurrent ({num_urls:,} URLs): {type(e).__name__}: {e}")
        return False

async def test_sequential(num_urls):
    """Test sequential execution"""
    urls = [f"https://example.com/{i}" for i in range(num_urls)]

    start = time.perf_counter()
    try:
        results = [await fake_fetch(u) for u in urls]
        elapsed = time.perf_counter() - start
        print(f"✓ Sequential ({num_urls:,} URLs): {elapsed:.2f}s")
        return True
    except Exception as e:
        print(f"✗ Sequential ({num_urls:,} URLs): {type(e).__name__}: {e}")
        return False

async def main():
    print("=" * 60)
    print("SEQUENTIAL vs CONCURRENT - Limits Test (1sec delay)")
    print("=" * 60)

    # Sequential tests
    print("\n📊 SEQUENTIAL EXECUTION:")
    for count in [10, 100, 1000, 5000]:
        success = await test_sequential(count)
        if not success:
            break

    # Concurrent tests
    print("\n📊 CONCURRENT EXECUTION:")
    for count in [100, 1000, 5000, 10000]:
        success = await test_concurrent(count)
        if not success:
            print(f"⚠️  Max concurrent limit reached at ~{count:,} URLs")
            break

if __name__ == "__main__":
    asyncio.run(main())
