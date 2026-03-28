---
id: web-performance
title: Web Performance Basics
date: 2025-01-15
summary: A quick guide to critical rendering path, image strategy, and Core Web Vitals.
tags:
  - performance
  - frontend
  - web
---

## Critical Rendering Path

1. Parse HTML and CSS
2. Build render tree
3. Layout and paint

## Resource Loading

```html
<link rel="preload" href="/fonts/main.woff2" as="font" crossorigin>
<script src="app.js" defer></script>
```

## Image Strategy

| Practice          | Benefit |
|:------------------|:--------|
| Use WebP/AVIF     | Smaller assets |
| Set width/height  | Lower CLS |
| Lazy load images  | Faster initial render |

```mermaid
sequenceDiagram
    Browser->>Server: Request HTML
    Server-->>Browser: Return HTML
    Browser->>Server: Request CSS/JS/Images
    Server-->>Browser: Return assets
```
