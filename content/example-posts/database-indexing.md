---
id: database-indexing
title: Database Indexing Fundamentals
date: 2023-11-08
summary: Understand B+ tree indexing, composite index rules, and common anti-patterns.
tags:
  - database
  - engineering
---

## B+ Tree Basics

Most relational databases rely on B+ trees for efficient lookup.

- Internal nodes route by key
- Leaf nodes store pointers to data
- Depth remains low at large scale

```mermaid
graph TD
    Root["[30 | 60]"]
    Root --> L1["[10 | 20]"]
    Root --> L2["[40 | 50]"]
    Root --> L3["[70 | 80]"]
```

## Index Types

| Type      | Description |
|:----------|:------------|
| Primary   | Clustered key index |
| Unique    | Enforces uniqueness |
| Composite | Multi-column optimization |

## Leftmost Prefix Rule

```sql
-- index (a, b, c)
SELECT * FROM t WHERE a = 1;
SELECT * FROM t WHERE a = 1 AND b = 2;
SELECT * FROM t WHERE b = 2; -- usually misses index
```
