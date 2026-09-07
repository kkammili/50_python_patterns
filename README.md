# 50 Python Coding Patterns

A comprehensive, interactive Jupyter notebook covering 50 essential coding algorithm patterns with vivid explanations, detailed pseudocode, and fully executable Python examples.

## 📚 Overview

This repository is a **deep dive into algorithm design patterns** used in competitive programming, technical interviews, and real-world software engineering. Each pattern includes:

- **Vivid Story**: Intuitive metaphor explaining the core concept
- **When to Use**: Real-world scenarios and problem recognition clues
- **Core Idea**: Pseudocode template with step-by-step logic
- **Pitfalls**: Common mistakes and how to avoid them
- **Executable Examples**: Multiple runnable Python code cells with test cases and verification

## 🎯 What's Included

The notebook covers **50 patterns** across these categories:

### Fundamentals (1-5)
1. **Sliding Window** — Fixed/dynamic window over arrays
2. **Two Pointers** — Meeting pointers from opposite ends
3. **Prefix Sum** — Precompute cumulative sums for range queries
4. **Difference Array** — Efficient range updates
5. **Greedy + Sorting** — Sort then optimize

### Searching & Sorting (6-10)
6. **Binary Search** — Logarithmic search in sorted arrays
7. **Merge Sort** — Divide-and-conquer sorting with inversion counting
8. **Quick Sort** — Average O(n log n) with randomization
9. **Counting Sort** — Linear sorting for bounded integers
10. **Heap & Priority Queue** — Efficient min/max extraction

### Hash & Frequency (11-15)
11. **Hash Map** — Count frequencies, detect duplicates
12. **Anagrams & Patterns** — Group and match similar strings
13. **LRU Cache** — Implement cache with eviction policy
14. **Union-Find (Disjoint Set)** — Detect cycles, connected components
15. **Graph Representation** — Adjacency list/matrix trade-offs

### Graphs: Search & Traversal (16-20)
16. **DFS (Depth-First Search)** — Recursive graph exploration
17. **BFS (Breadth-First Search)** — Level-by-level exploration
18. **Backtracking** — Explore all possibilities with undo
19. **0/1 BFS** — Shortest path with 0/1 edge weights
20. **Topological Sort** — Order dependencies using Kahn's algorithm

### Arrays & Matrix (21-25)
21. **Array Rotation** — Reverse algorithm for efficient rotation
22. **Kadane's Algorithm** — Maximum subarray sum in O(n)
23. **Matrix Traversal** — Spiral order, rotation, zero-setting
24. **Bit Manipulation** — XOR tricks, set operations, count bits
25. **Modular Arithmetic** — Handle large numbers with mod operations

### Linked Lists (26-30)
26. **Linked List Basics** — Insert, delete, reverse
27. **Slow & Fast Pointers** — Detect cycles, find midpoint
28. **Merge Sorted Lists** — Combine multiple sorted lists
29. **Reorder List** — Rearrange linked list in-place
30. **Copy List with Random Pointer** — Clone complex structures

### Strings (31-35)
31. **String Matching** — Find substring (KMP, Rabin-Karp approaches)
32. **Palindrome** — Check and generate palindromes
33. **Edit Distance** — Minimum edits to transform strings
34. **Longest Common Subsequence** — LCS DP approach
35. **Regular Expression Matching** — Pattern matching with wildcards

### Dynamic Programming: 1D (36-40)
36. **Fibonacci Variants** — Classic DP examples
37. **Climbing Stairs** — Combinations, permutations
38. **House Robber** — Max sum with constraints
39. **Coin Change** — Minimum coins for target sum
40. **Longest Increasing Subsequence (LIS)** — O(n log n) with binary search

### Dynamic Programming: Advanced (41-45)
41. **2D DP** — Grid paths, matrix DP
42. **Partition DP** — Interval problems (burst balloons, palindrome)
43. **Knapsack** — 0/1 knapsack, unbounded variations
44. **Game Theory DP** — Minimax, optimal play
45. **Matrix Traversal** — Spiral order, rotation, set zeroes

### Recursion & Optimization (46-50)
46. **Recursion Template** — Linear, tree, backtracking patterns
47. **Memoization / Top-Down DP** — Cache recursive results
48. **String Parsing / Simulation** — Character-by-character processing
49. **Graph Cycle Detection** — Directed vs undirected cycles
50. **State Compression DP (Bitmask)** — Optimal subset selection with small n

## 🚀 Quick Start

### Prerequisites
- Python 3.7+
- Jupyter Notebook or JupyterLab
- VS Code with Jupyter extension (optional but recommended)

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/kkammili/50_python_patterns.git
   cd 50_python_patterns
   ```

2. **Open in Jupyter:**
   ```bash
   jupyter notebook coding-patterns.ipynb
   ```
   
   Or in VS Code:
   ```bash
   code coding-patterns.ipynb
   ```

3. **Run cells interactively:**
   - Each pattern has markdown cells (explanation) followed by executable code cells
   - Click "Run" (▶) on any cell to execute the examples
   - Modify code and re-run to experiment

## 📖 How to Use

### For Learning
1. Read the **Story** section to build intuition
2. Understand **When to Use** to recognize patterns in problems
3. Study the **Core Idea** pseudocode
4. Review **Pitfalls** to avoid common mistakes
5. Run and modify the **Examples** to see patterns in action

### For Interviews
- Use **Core Idea** as a template when coding solutions
- Reference **When to Use** to identify the right approach
- Check **Pitfalls** during code review

### For Implementation
- Copy the algorithm pseudocode as a starting point
- Adapt the test cases to your specific problem
- Verify with the provided examples

## 🔍 Pattern Lookup

### By Problem Type

**Need to search?**
- Pattern 6: Binary Search

**Need to sort?**
- Pattern 7: Merge Sort
- Pattern 8: Quick Sort
- Pattern 9: Counting Sort
- Pattern 5: Greedy + Sorting

**Need dynamic programming?**
- Pattern 36-40: 1D DP basics
- Pattern 41-44: Advanced DP techniques
- Pattern 47: Memoization
- Pattern 50: Bitmask DP

**Need graph algorithms?**
- Pattern 16: DFS
- Pattern 17: BFS
- Pattern 20: Topological Sort
- Pattern 49: Cycle Detection

**Need string processing?**
- Pattern 31: String Matching
- Pattern 32: Palindrome
- Pattern 48: String Parsing/Simulation

### By Difficulty

**Beginner (Patterns 1-15):**
- Fundamental data structure techniques
- Hash-based problem solving

**Intermediate (Patterns 16-35):**
- Graph traversal
- String algorithms
- Linked list manipulation

**Advanced (Patterns 36-50):**
- Dynamic programming variants
- Optimization under constraints
- Complex state management

## 💡 Example: Using Pattern 6 (Binary Search)

```python
# From the notebook's Pattern 6 code cell:
def binary_search(arr, target):
    left, right = 0, len(arr) - 1
    
    while left <= right:
        mid = (left + right) // 2
        if arr[mid] == target:
            return mid
        elif arr[mid] < target:
            left = mid + 1
        else:
            right = mid - 1
    
    return -1

# Run with example from notebook:
result = binary_search([1, 3, 5, 7, 9], 7)  # Returns 3 ✓
```

## 📊 Complexity Reference

Each pattern includes:
- **Time Complexity**: Worst, average, and best case
- **Space Complexity**: Auxiliary space needed
- **Trade-offs**: When to prefer one approach over another

Common complexities covered:
- O(n), O(log n), O(n log n) — Efficient algorithms
- O(n²), O(n³) — Moderate for small inputs
- O(2^n), O(n!) — Only feasible for small n (with optimization)

## 🛠️ Contributing

Found a bug? Want to add more examples? Contributions welcome!

1. Fork the repository
2. Create a feature branch: `git checkout -b add-pattern-x`
3. Make your changes
4. Commit: `git commit -m "Add comprehensive example for Pattern X"`
5. Push: `git push origin add-pattern-x`
6. Open a Pull Request

## 📝 Structure

```
50_python_patterns/
├── README.md                    # This file
├── coding-patterns.ipynb        # Main Jupyter notebook with all 50 patterns
└── .git/                        # Git history and metadata
```

### Notebook Structure

Each pattern follows this format:

```
## Pattern N — [Name]

**Importance:** [★★★★★ rating]

### Story
[Vivid metaphor and intuitive explanation]

### When to Use
[Real-world scenarios and recognition clues]

### Core Idea
[Pseudocode template with key operations]

### Pitfalls
[Common mistakes and how to avoid them]

### Mini Examples
[Traced examples showing the algorithm step-by-step]

[Executable Python code cells with test cases and output]
```

## 🎓 Learning Path

**Week 1-2:** Patterns 1-10 (Fundamentals + Searching)
- Build solid foundation in array/string basics
- Master binary search

**Week 3-4:** Patterns 11-20 (Hash + Graphs)
- Learn hash-based techniques
- Understand graph traversal

**Week 5-6:** Patterns 21-30 (Arrays + Linked Lists)
- Advanced array manipulation
- Linked list tricks

**Week 7-8:** Patterns 31-40 (Strings + DP Basics)
- String algorithms
- Classic DP problems

**Week 9-10:** Patterns 41-50 (Advanced DP + Optimization)
- Complex DP scenarios
- State compression and bitmask techniques

## 🔗 Resources

- **LeetCode**: Practice problems using these patterns
- **GeeksforGeeks**: Extended explanations for specific algorithms
- **Cracking the Coding Interview**: Interview-focused pattern reference
- **Algorithm Design Manual**: Theoretical background

## 📄 License

This project is open source and available under the [MIT License](LICENSE).

## 👤 Author

Created and maintained by [kkammili](https://github.com/kkammili)

## ⭐ Show Your Support

If this repository helped you prepare for interviews or improve your coding skills, consider giving it a star ⭐!

---

**Happy coding! 🚀**

Questions? Open an issue or start a discussion in the repository.
