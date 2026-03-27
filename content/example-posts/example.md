---
id: welcome-itso
title: Hello World
date: 2017-01-24
summary: Welcome to the Itso example site. This post validates the default rendering pipeline.
cover:
  src: /static/itso/img/IMG_3233.jpg
  alt: Example post cover image
tags:
  - intro
  - example
mirror:
  platform: Medium
  url: https://medium.com/@your-name/your-post
  label: Read on Medium
social_links:
  - name: X
    url: https://x.com/your-handle
    label: Follow on X
  - name: Facebook
    url: https://facebook.com/your-page
    label: Join on Facebook
call_to_action:
  title: More Thoughts and Discussion
  text: If you enjoy this topic, follow and message me on social platforms.
  label: Follow My Medium
  url: https://medium.com/@your-name
---

> Welcome to my blog.

## Test Content

### Image

![City](/static/itso/img/IMG_3233.jpg)

### Code Block

```python
if __name__ == "__main__":
    print("Hello World")
```

### Formula

$$
f(x) = \frac{1}{\sqrt{2\pi\sigma^2}} \exp\left(-\frac{(x - \mu)^2}{2\sigma^2}\right)
$$

Where:

- $\mu$ is the mean
- $\sigma$ is the standard deviation
- $\sigma^2$ is the variance

### Table

| X | Y | Z  |
|:--|--:|:--:|
| 0 | 0 | -1 |
| 0 | 1 | +1 |
| 1 | 0 | +1 |
| 1 | 1 | -1 |

### Mermaid

```mermaid
graph TD
    A("Fever?") -->|Yes| B("Cough?")
    A -->|No| C("Diagnosed as Healthy")
    B -->|Yes| D("Diagnosed as Cold")
    B -->|No| E("Diagnosed as Flu")
```