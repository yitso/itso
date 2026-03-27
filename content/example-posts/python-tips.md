---
id: python-tips
title: Practical Python Tips
date: 2024-09-22
summary: Useful Python patterns for everyday development, including comprehensions and dataclasses.
tags:
  - python
  - programming
---

## Comprehensions

```python
squares = [x ** 2 for x in range(10)]
evens = [x for x in range(20) if x % 2 == 0]
```

## Dataclass

```python
from dataclasses import dataclass, field

@dataclass
class Article:
    title: str
    tags: list[str] = field(default_factory=list)
```

## Handy Built-ins

| Function      | Purpose |
|:--------------|:--------|
| `zip()`       | Iterate multiple sequences |
| `enumerate()` | Iterate with index |
| `sorted()`    | Return sorted values |
