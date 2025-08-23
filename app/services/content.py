# -*- coding: utf-8 -*-
import os
import re
import json
from datetime import datetime
from typing import List, Dict

import markdown
from flask import current_app, abort


META_SPLIT = "---"

# Match inline/block math like $...$ or $$...$$ (ignore escaped $)
MATH_PATTERN = re.compile(r"(?<!\\)(\${1,2})(.*?)(?<!\\)\1", re.DOTALL)


def _parse_metadata_block(metadata_str: str) -> Dict[str, str]:
    metadata = {}
    for line in metadata_str.split("\n"):
        if ":" in line:
            key, value = re.split(r"\s*:\s*", line, 1)
            metadata[key.strip().lower()] = value.strip()
    return metadata


def _read_site_config() -> dict:
    path = current_app.config["SITE_CONFIG_PATH"]
    with open(path, encoding="utf-8") as fd:
        return json.load(fd)


def get_site_config() -> dict:
    # cache in app config to avoid reloading each request
    if "SITE_CONFIG" not in current_app.config:
        current_app.config["SITE_CONFIG"] = _read_site_config()
    return current_app.config["SITE_CONFIG"]


def get_posts_root() -> str:
    site_cfg = get_site_config()
    # Expect the JSON to contain key `posts` with a directory path
    posts_dir = site_cfg.get("posts")
    if not posts_dir:
        raise RuntimeError("`posts` directory missing in site config JSON")
    return posts_dir


def load_article_metadata() -> List[dict]:
    articles = []
    root_dir = get_posts_root()

    for root, dirs, files in os.walk(root_dir):
        for filename in files:
            if not filename.endswith(".md"):
                continue
            filepath = os.path.join(root, filename)
            with open(filepath, "r", encoding="utf-8") as f:
                parts = f.read().split(META_SPLIT, 2)
                if len(parts) < 3:
                    continue
                metadata = _parse_metadata_block(parts[1].strip())
                # date
                try:
                    date = datetime.strptime(metadata.get("date", ""), "%Y-%m-%d")
                except ValueError:
                    date = datetime.now()
                # slug
                rel_root = os.path.relpath(root, root_dir)
                slug = os.path.join(rel_root, filename[:-3]).replace(os.sep, "/")
                articles.append({
                    "title": metadata.get("title", "Untitled"),
                    "date": date,
                    "slug": slug,
                    "summary": metadata.get("summary", ""),
                })

    return sorted(articles, key=lambda x: x["date"], reverse=True)


def load_article_content(slug: str) -> dict:
    if ".." in slug or slug.startswith("/"):
        abort(404)

    root_dir = get_posts_root()
    filepath = os.path.join(root_dir, slug + ".md")

    if not os.path.isfile(filepath):
        abort(404)

    with open(filepath, "r", encoding="utf-8") as f:
        parts = f.read().split(META_SPLIT, 2)
        if len(parts) < 3:
            abort(404)
        metadata = _parse_metadata_block(parts[1].strip())
        raw_body = parts[2].strip()
        processed_body = process_markdown(raw_body)
        return {
            "title": metadata.get("title", "Untitled"),
            "date": datetime.strptime(metadata.get("date", ""), "%Y-%m-%d"),
            "slug": slug,
            "content": processed_body,
            "summary": metadata.get("summary", ""),
        }


def process_markdown(text: str) -> str:
    """Process Markdown content with math escaping while preserving code fences."""
    # Temporarily replace fenced code blocks
    code_block_pattern = re.compile(r"```.*?```", re.DOTALL)
    code_blocks = []

    def code_replacer(match):
        code_blocks.append(match.group(0))
        return f"@@CODE_BLOCK_{len(code_blocks) - 1}@@"

    text = code_block_pattern.sub(code_replacer, text)

    # Escape math content
    def math_replacer(match):
        delimiter = match.group(1)
        content = match.group(2)
        content = content.replace("\\", "\\\\")  # double the backslashes
        content = content.replace("_", r"\_").replace("*", r"\*")
        return delimiter + content + delimiter

    text = MATH_PATTERN.sub(math_replacer, text)

    # Restore code blocks
    for i, code in enumerate(code_blocks):
        text = text.replace(f"@@CODE_BLOCK_{i}@@", code)

    return markdown.markdown(
        text,
        escape=True,
        extensions=["fenced_code", "tables", "sane_lists"],
        output_format="html5",
    )