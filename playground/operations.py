import asyncio
import time

async def fake_fetch(url, delay=0.1):
    await asyncio.sleep(delay)
    print(url)

    if "bad" in url:
        raise ConnectionError(f"failed: {url}")
    return f"<{url}>"


urls = [f"https://www.kkammili{i}.com" for i in range(100)]

async def sequential():
    return [await fake_fetch(u, 1) for u in urls]

async def concurrent():
    return await asyncio.gather(*[fake_fetch(u, 1) for u in urls])


# start = time.perf_counter();
# seq = asyncio.run(sequential())
# t_seq = time.perf_counter() - start
# print(t_seq)

parallel_timer_start = time.perf_counter()
parallel = asyncio.run(concurrent())
print(time.perf_counter()-parallel_timer_start)



