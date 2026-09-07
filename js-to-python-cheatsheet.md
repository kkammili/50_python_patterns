# JS → Python Cheat Sheet (for DSA)

A quick-reference for developers moving from JavaScript to Python, focused on the mechanics that matter most for DSA problem-solving.

---

## 1. Mutability: List vs Tuple

| | List | Tuple |
|---|---|---|
| Mutable? | Yes | No |
| Hashable (usable as dict key / set item)? | No | Yes |
| Syntax | `[1, 2, 3]` | `(1, 2, 3)` |

```python
seen = set()
seen.add((row, col))   # tuple works as a set element
seen.add([row, col])   # TypeError: list is unhashable
```

**Use tuples** for fixed coordinate pairs, dict keys, or anything you don't want changed accidentally.

---

## 2. The Mutable Default Argument Trap

Default arguments are evaluated **once**, at function definition time — not on every call.

```python
# BAD — my_list is shared across every call
def add_item(item, my_list=[]):
    my_list.append(item)
    return my_list

# GOOD
def add_item(item, my_list=None):
    if my_list is None:
        my_list = []
    my_list.append(item)
    return my_list
```

Same root bug shows up in `[[0]*3] * 2` — see section 9.

---

## 3. `==` vs `is`

- `==` → compares **value** (use this ~95% of the time)
- `is` → compares **identity** (same object in memory)

```python
if node.next is None:   # idiomatic — None is a singleton
if node.next == None:   # works, but not the Python convention
```

Reach for `is` only for: `is None`, `is True`/`is False`, or checking if two variables literally reference the same mutable object.

---

## 4. Slicing (JS `.slice()` equivalent, but more powerful)

```python
nums = [10, 20, 30, 40, 50]

nums[1:4]    # [20, 30, 40]   start:stop
nums[:3]     # [10, 20, 30]   from beginning
nums[::-1]   # [50, 40, 30, 20, 10]   reversed
nums[::2]    # [10, 30, 50]   every 2nd element
```

Syntax: `list[start:stop:step]` — any part is optional.

---

## 5. Dict `.get()` — avoiding `KeyError`

Python dicts raise `KeyError` on a missing key (unlike JS, where `obj.missingKey` just gives `undefined`).

```python
counts = {}
for ch in word:
    counts[ch] = counts.get(ch, 0) + 1   # defaults to 0 if ch not seen yet
```

---

## 6. `enumerate()` (JS `.entries()` / `.forEach((val, i) => ...)`)

```python
for i, val in enumerate(nums):
    print(i, val)
```

Better than `for i in range(len(nums))` — gives you index **and** value directly, no extra `nums[i]` lookup, fewer off-by-one risks.

---

## 7. Unpacking / Multiple Assignment

```python
a, b = 5, 10
a, b = b, a          # swap, no temp variable needed
print(a, b)           # 10 5

x = [1, 2, 3]
first, *rest = x
print(first, rest)    # 1 [2, 3]   <-- first is a plain value, NOT wrapped in a list
```

---

## 8. Stack & Queue

| | Structure | Why |
|---|---|---|
| Stack | plain `list` | `.append()` / `.pop()` — both O(1) from the end |
| Queue | `collections.deque` | `.append()` / `.popleft()` — both O(1) |

```python
from collections import deque

stack = []
stack.append(1); stack.append(2)
stack.pop()          # 2

queue = deque()
queue.append(1); queue.append(2)
queue.popleft()       # 1
```

**Never** use `list.pop(0)` for a queue — it's O(n) because every remaining element has to shift left.

---

## 9. List Multiplication — and Its Trap

```python
[1, 2, 3] * 3        # [1, 2, 3, 1, 2, 3, 1, 2, 3]  -- repeats the list
3 * [1, 2, 3]         # same result, order doesn't matter
[1, 2, 3] * [1, 2, 3] # TypeError -- can't multiply list by list
```

**Danger zone — 2D grids:**

```python
grid = [[0]*3] * 2      # BAD: repeats the SAME inner list reference twice
grid[0][1] = 9
print(grid)              # [[0, 9, 0], [0, 9, 0]]  <-- both rows changed!

grid = [[0]*3 for _ in range(2)]   # GOOD: fresh list created each iteration
```

Same underlying bug as the mutable default argument: **`*` repeats a reference, it doesn't copy.**

---

## 10. Element-wise Multiplication (no built-in `*` for lists)

```python
a = [1, 2, 3]
b = [1, 2, 3]

# Element-wise multiply:
[x * y for x, y in zip(a, b)]   # [1, 4, 9]

# Or with NumPy (supports * directly):
import numpy as np
np.array(a) * np.array(b)        # array([1, 4, 9])
```

---

## 11. Higher-Order Functions: JS → Python

| JS | Python (functional) | Python (idiomatic) |
|---|---|---|
| `nums.map(n => n*2)` | `list(map(lambda n: n*2, nums))` | `[n*2 for n in nums]` |
| `nums.filter(n => n>2)` | `list(filter(lambda n: n>2, nums))` | `[n for n in nums if n>2]` |
| `nums.reduce((a,n)=>a+n, 0)` | `reduce(lambda a,n: a+n, nums, 0)` (needs `from functools import reduce`) | `sum(nums)` |
| `nums.forEach(n => ...)` | — | `for n in nums: ...` |
| `nums.find(n => n>2)` | — | `next((n for n in nums if n>2), None)` |
| `nums.every(n => n>0)` | — | `all(n > 0 for n in nums)` |
| `nums.some(n => n>0)` | — | `any(n > 0 for n in nums)` |

**Note:** `map()` and `filter()` return lazy iterators in Python — wrap with `list(...)` to materialize them.

**Culture note:** idiomatic Python favors comprehensions and built-ins (`sum`, `all`, `any`) over chained `map`/`filter`/`reduce`. `reduce` in particular is considered unpythonic for anything beyond a trivial one-liner.

---

## 12. Lambda Functions

```python
# JS: (a, b) => a + b
add = lambda a, b: a + b
```

Shape: `lambda args: expression` — single expression only, implicit return, no multi-line body.

---

## 13. `key=` in `sorted()` / `max()` / `min()` — THE BIG TRAP

**`key=` is a lens, not a filter or transformer.** It tells Python *what to compare by* — the function always returns the **full original items**, never the key value itself.

```python
students = [("Alice", 85), ("Bob", 72), ("Cara", 91)]

max(students, key=lambda s: s[1])
# ('Cara', 91)  -- the whole tuple, not just 91

sorted(students, key=lambda s: s[1], reverse=True)
# [('Cara', 91), ('Alice', 85), ('Bob', 72)]  -- full tuples, sorted by score
```

**Multi-key sort (like sorting by multiple Excel columns):**

```python
words = ["pear", "fig", "kiwi", "date", "plum"]
sorted(words, key=lambda w: (len(w), w))
# ['fig', 'date', 'kiwi', 'pear', 'plum']
# sorts by length first, alphabetically as tiebreaker
```

---

## 14. `Counter` and `set`

```python
from collections import Counter

c = Counter([1, 2, 2, 3, 3, 3])
# Counter({3: 3, 2: 2, 1: 1})

c.most_common(1)
# [(3, 3)]  <-- ALWAYS a list of (element, count) tuples, even for n=1
# grab just the element: c.most_common(1)[0][0]

s = {1, 2, 3}
2 in s          # True — O(1) membership check, backbone of "seen" patterns
```

---

## 15. String Methods

```python
s = "Hello World"
s.lower()        # "hello world"
s.split()         # ["Hello", "World"]
"".join(["a","b","c"])   # "abc"
s[::-1]           # "dlroW olleH"
```

`.split()` breaks a string into a list; `"".join(...)` glues a list back into a string. This pair is the standard toolkit for anagram/palindrome/parsing problems.

---

## 16. Dict of Lists (Graph Adjacency List)

```python
graph = {
    "A": ["B", "C"],
    "B": ["D"],
    "C": ["D"],
    "D": []
}

"B" in graph              # True — key existence check
graph.get("Z", [])         # [] — safe default for missing key

for node in graph:         # iterates KEYS only
    print(node, graph[node])   # manually access value
```

---

## Quick Mental Checklist for DSA Coding

- [ ] Am I creating a **fresh** object each time, or accidentally sharing one reference? (`*` on lists, mutable default args)
- [ ] Does this built-in return a **list of tuples**, a **generator**, or a **plain value**? Check before indexing into it.
- [ ] Is `key=` here to **transform** the output, or just to **decide comparison order**? (It's always the latter.)
- [ ] Do I need O(1) lookup? → **set** or **dict**. Do I need O(1) from both ends? → **deque**.
