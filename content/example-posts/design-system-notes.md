---
id: design-system-notes
title: Design System Notes
date: 2025-05-20
summary: Key decisions for tokens, typography scale, spacing, and component documentation.
tags:
  - design
  - frontend
---

## Design System Scope

A practical design system includes:

- Design tokens
- Reusable components
- Documentation and accessibility rules

## Token Example

```js
const tokens = {
  color: {
    brand: {
      primary: '#0f766e',
      strong: '#115e59'
    }
  }
}
```

## Type Scale

| Level | Size | Usage |
|:------|----:|:------|
| base  | 16px | body |
| lg    | 20px | lead |
| xl    | 25px | section title |
| 2xl   | 31px | card title |

## Documentation Checklist

1. Overview
2. API/props
3. States
4. Accessibility
