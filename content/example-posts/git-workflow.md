---
id: git-workflow
title: Git Workflow in Practice
date: 2025-03-01
summary: Feature branches, clean history, and practical commands for team collaboration.
tags:
  - git
  - engineering
---

## Feature Branch Flow

```bash
git checkout -b feature/user-auth
git push -u origin feature/user-auth
git fetch origin
git rebase origin/main
```

## Useful Commands

| Scenario          | Command                        |
|:------------------|:-------------------------------|
| Stage all changes | `git add -A`                   |
| Amend last commit | `git commit --amend --no-edit` |
| Compare branches  | `git diff main..feature/foo`   |

## Commit Types

- `feat`
- `fix`
- `docs`
- `refactor`
- `perf`
- `chore`
