# -*- coding: utf-8 -*-
import os
import re
import json
from datetime import datetime
from typing import List, Dict, Optional
from pathlib import Path

import markdown
import yaml
from flask import current_app, abort


META_SPLIT = "---"
ARTICLE_ID_PATTERN = re.compile(r"^[a-z0-9][a-z0-9-]*$")
THEME_ID_PATTERN = re.compile(r"^[a-z0-9][a-z0-9-]*$")
DEFAULT_THEME_ID = "default"

# Match inline/block math like $...$ or $$...$$ (ignore escaped $)
MATH_PATTERN = re.compile(r"(?<!\\)(\${1,2})(.*?)(?<!\\)\1", re.DOTALL)


def _parse_metadata_block(metadata_str: str) -> Dict[str, str]:
    loaded = yaml.safe_load(metadata_str) or {}
    if not isinstance(loaded, dict):
        return {}
    return {str(k).strip().lower(): v for k, v in loaded.items()}


def _parse_article_date(value) -> datetime:
    if isinstance(value, datetime):
        return value
    if hasattr(value, "year") and hasattr(value, "month") and hasattr(value, "day"):
        return datetime(value.year, value.month, value.day)
    if isinstance(value, str) and value:
        try:
            return datetime.strptime(value, "%Y-%m-%d")
        except ValueError:
            pass
    return datetime.now()


def _normalize_tags(value) -> List[str]:
    if isinstance(value, list):
        raw = [str(t).strip() for t in value]
    elif isinstance(value, str) and value.strip():
        raw = [t.strip() for t in value.split(",")]
    else:
        return []
    return sorted(set(t for t in raw if t))


def slugify_tag(tag: str) -> str:
    """
    Convert a tag string into a URL-safe slug suitable for ``/tags/<tag>`` routes.

    Lowercases the input, replaces any run of non-alphanumeric characters
    (including whitespace and ``/``) with a single ``-``, and trims leading /
    trailing dashes.
    """
    slug = tag.strip().lower()
    slug = re.sub(r"[^a-z0-9]+", "-", slug)
    return slug.strip("-")


def _normalize_link_items(value) -> List[dict]:
    if not isinstance(value, list):
        return []

    normalized = []
    for item in value:
        if not isinstance(item, dict):
            continue
        url = str(item.get("url") or "").strip()
        if not url:
            continue
        normalized.append(
            {
                "name": str(item.get("name") or item.get("platform") or "Link").strip(),
                "url": url,
                "label": str(item.get("label") or "").strip(),
            }
        )
    return normalized


def _extract_cover(metadata: dict) -> dict:
    """Normalize optional cover image metadata for list/index previews."""
    raw_cover = metadata.get("cover") or metadata.get("cover_image") or metadata.get("featured_image")

    src = ""
    alt = ""

    if isinstance(raw_cover, str):
        src = raw_cover.strip()
    elif isinstance(raw_cover, dict):
        src = str(raw_cover.get("src") or raw_cover.get("url") or "").strip()
        alt = str(raw_cover.get("alt") or "").strip()

    if not src:
        return {}

    return {
        "src": src,
        "alt": alt,
    }


def _extract_article_promo(metadata: dict) -> dict:
    mirror = metadata.get("mirror") if isinstance(metadata.get("mirror"), dict) else {}
    cta = metadata.get("call_to_action") if isinstance(metadata.get("call_to_action"), dict) else {}

    mirror_url = str(mirror.get("url") or metadata.get("external_url") or "").strip()
    mirror_label = str(mirror.get("label") or metadata.get("external_label") or "").strip()
    mirror_platform = str(mirror.get("platform") or metadata.get("external_platform") or "").strip()

    cta_url = str(cta.get("url") or "").strip()
    cta_data = {
        "title": str(cta.get("title") or "").strip(),
        "text": str(cta.get("text") or "").strip(),
        "label": str(cta.get("label") or "").strip(),
        "url": cta_url,
    }

    socials = _normalize_link_items(metadata.get("social_links"))

    return {
        "mirror": {
            "platform": mirror_platform,
            "url": mirror_url,
            "label": mirror_label,
        },
        "cta": cta_data,
        "social_links": socials,
    }


def _extract_article_mirror(metadata: dict) -> dict:
    promo = _extract_article_promo(metadata)
    return promo.get("mirror", {})


def _normalize_article_id(value: str) -> str:
    article_id = (value or "").strip().lower()
    if not ARTICLE_ID_PATTERN.match(article_id):
        raise ValueError(
            f"Invalid article id '{value}'. Use lowercase letters, numbers, and dashes only."
        )
    return article_id


def _read_site_config() -> dict:
    path = Path(current_app.config["SITE_CONFIG_PATH"])
    content_root = Path(current_app.config.get("CONTENT_ROOT", "."))
    if not path.is_absolute():
        path = content_root / path
    with open(path, encoding="utf-8") as fd:
        return json.load(fd)


def get_site_config() -> dict:
    # cache in app config to avoid reloading each request
    if "SITE_CONFIG" not in current_app.config:
        current_app.config["SITE_CONFIG"] = _read_site_config()
    return current_app.config["SITE_CONFIG"]


def _normalize_theme_id(value: str) -> str:
    theme_id = (value or "").strip().lower()
    if not THEME_ID_PATTERN.match(theme_id):
        return DEFAULT_THEME_ID
    return theme_id


def _resolve_themes_root() -> Path:
    themes_dir = Path(current_app.config.get("THEMES_DIR", "themes"))
    if themes_dir.is_absolute():
        return themes_dir
    project_root = Path(current_app.root_path).parent
    return project_root / themes_dir


def _read_theme_definition(theme_id: str) -> Optional[dict]:
    path = _resolve_themes_root() / f"{theme_id}.json"
    if not path.exists() or not path.is_file():
        return None
    try:
        with open(path, "r", encoding="utf-8") as fd:
            loaded = json.load(fd)
    except (OSError, json.JSONDecodeError):
        return None
    if not isinstance(loaded, dict):
        return None
    return loaded


def _normalize_theme_tokens(value) -> Dict[str, str]:
    if not isinstance(value, dict):
        return {}

    normalized = {}
    for key, token_value in value.items():
        token_key = str(key).strip()
        if not token_key:
            continue
        normalized[token_key] = str(token_value).strip()
    return normalized


def _normalize_theme_modes(value) -> Dict[str, Dict[str, str]]:
    if not isinstance(value, dict):
        return {}

    normalized = {}
    for mode_name in ("light", "dark"):
        if mode_name not in value:
            continue

        mode_value = value.get(mode_name)
        if not isinstance(mode_value, dict):
            continue

        normalized[mode_name] = _normalize_theme_tokens(mode_value)
    return normalized


def _resolve_theme_css_path(theme_id: str) -> str:
    css_path = Path(current_app.static_folder or "") / "itso" / "themes" / f"{theme_id}.css"
    if css_path.exists() and css_path.is_file():
        return f"/static/itso/themes/{theme_id}.css"
    return ""


def get_theme_config() -> dict:
    # cache because theme is static for process lifecycle in current mode
    if "SITE_THEME" in current_app.config:
        return current_app.config["SITE_THEME"]

    site_cfg = get_site_config()
    raw_theme = site_cfg.get("theme") if isinstance(site_cfg.get("theme"), dict) else {}
    requested_id = _normalize_theme_id(raw_theme.get("id") or DEFAULT_THEME_ID)

    loaded = _read_theme_definition(requested_id)
    resolved_id = requested_id
    fallback_used = False
    if loaded is None:
        loaded = _read_theme_definition(DEFAULT_THEME_ID) or {}
        resolved_id = DEFAULT_THEME_ID
        fallback_used = requested_id != DEFAULT_THEME_ID

    tokens = _normalize_theme_tokens(loaded.get("tokens"))
    modes = _normalize_theme_modes(loaded.get("modes"))

    override_tokens = _normalize_theme_tokens(raw_theme.get("overrides"))
    tokens.update(override_tokens)

    theme = {
        "id": resolved_id,
        "requested_id": requested_id,
        "fallback_used": fallback_used,
        "tokens": tokens,
        "modes": modes,
        "css_path": _resolve_theme_css_path(resolved_id),
    }
    current_app.config["SITE_THEME"] = theme
    return theme


def get_posts_root() -> str:
    site_cfg = get_site_config()
    # Expect the JSON to contain key `posts` with a directory path
    posts_dir = site_cfg.get("posts")
    if not posts_dir:
        raise RuntimeError("`posts` directory missing in site config JSON")

    content_root = Path(current_app.config.get("CONTENT_ROOT", "."))
    posts_path = Path(posts_dir)
    if not posts_path.is_absolute():
        posts_path = content_root / posts_path
    return str(posts_path)


def _get_pinned_post_ids() -> List[str]:
    site_cfg = get_site_config()
    raw = site_cfg.get("pinned_post_ids", [])
    if not isinstance(raw, list):
        return []

    pinned = []
    for value in raw:
        try:
            normalized = _normalize_article_id(str(value))
        except ValueError:
            continue
        if normalized not in pinned:
            pinned.append(normalized)
        if len(pinned) >= 3:
            break
    return pinned


def _iter_article_files() -> List[dict]:
    root_dir = get_posts_root()
    items = []

    for root, dirs, files in os.walk(root_dir):
        for filename in files:
            if not filename.endswith(".md"):
                continue

            filepath = os.path.join(root, filename)
            rel_root = os.path.relpath(root, root_dir)
            if rel_root == ".":
                slug = filename[:-3]
            else:
                slug = os.path.join(rel_root, filename[:-3]).replace(os.sep, "/")

            items.append({"filepath": filepath, "slug": slug})

    return items


def load_article_metadata() -> List[dict]:
    articles = []
    id_registry = set()

    for item in _iter_article_files():
        with open(item["filepath"], "r", encoding="utf-8") as f:
            parts = f.read().split(META_SPLIT, 2)
            if len(parts) < 3:
                continue
            metadata = _parse_metadata_block(parts[1].strip())

            raw_id = metadata.get("id")
            if not raw_id:
                raise ValueError(f"Missing required front matter field `id` in {item['filepath']}")
            article_id = _normalize_article_id(str(raw_id))
            if article_id in id_registry:
                raise ValueError(f"Duplicate article id '{article_id}' found in {item['filepath']}")
            id_registry.add(article_id)

            date = _parse_article_date(metadata.get("date"))
            mirror = _extract_article_mirror(metadata)
            articles.append({
                "id": article_id,
                "title": metadata.get("title", ""),
                "date": date,
                "slug": item["slug"],
                "summary": metadata.get("summary", ""),
                "tags": _normalize_tags(metadata.get("tags", [])),
                "mirror": mirror,
                "cover": _extract_cover(metadata),
            })

    pinned_ids = _get_pinned_post_ids()
    pinned_rank = {post_id: index for index, post_id in enumerate(pinned_ids)}

    for article in articles:
        article["is_pinned"] = article["id"] in pinned_rank

    def sort_key(article: dict):
        rank = pinned_rank.get(article["id"], 999)
        return (rank, -article["date"].timestamp())

    return sorted(articles, key=sort_key)


def _load_article_content_from_file(filepath: str, slug: str) -> dict:
    with open(filepath, "r", encoding="utf-8") as f:
        parts = f.read().split(META_SPLIT, 2)
        if len(parts) < 3:
            abort(404)
        metadata = _parse_metadata_block(parts[1].strip())
        raw_id = metadata.get("id")
        if not raw_id:
            abort(404)
        article_id = _normalize_article_id(str(raw_id))

        raw_body = parts[2].strip()
        processed_body = process_markdown(raw_body)
        promo = _extract_article_promo(metadata)
        return {
            "id": article_id,
            "title": metadata.get("title", ""),
            "date": _parse_article_date(metadata.get("date")),
            "slug": slug,
            "content": processed_body,
            "summary": metadata.get("summary", ""),
            "tags": _normalize_tags(metadata.get("tags", [])),
            "cover": _extract_cover(metadata),
            "promo": promo,
        }


def load_article_content(article_id: str) -> dict:
    try:
        normalized_id = _normalize_article_id(article_id)
    except ValueError:
        abort(404)

    for item in _iter_article_files():
        with open(item["filepath"], "r", encoding="utf-8") as f:
            parts = f.read().split(META_SPLIT, 2)
            if len(parts) < 3:
                continue
            metadata = _parse_metadata_block(parts[1].strip())
            raw_id = metadata.get("id")
            if not raw_id:
                continue
            try:
                current_id = _normalize_article_id(str(raw_id))
            except ValueError:
                continue

            if current_id == normalized_id:
                return _load_article_content_from_file(item["filepath"], item["slug"])

    abort(404)


def load_article_content_by_slug(slug: str) -> Optional[dict]:
    if ".." in slug or slug.startswith("/"):
        return None

    root_dir = get_posts_root()
    filepath = os.path.join(root_dir, slug + ".md")
    if not os.path.isfile(filepath):
        return None

    return _load_article_content_from_file(filepath, slug)


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


def get_all_tags() -> List[dict]:
    """Return [{tag, slug, count}] sorted by count desc then slug asc."""
    tag_map: Dict[str, dict] = {}
    for article in load_article_metadata():
        for tag in article.get("tags", []):
            slug = slugify_tag(tag)
            if slug not in tag_map:
                tag_map[slug] = {"tag": tag, "slug": slug, "count": 0}
            tag_map[slug]["count"] += 1
    return sorted(tag_map.values(), key=lambda x: (-x["count"], x["slug"]))


def get_articles_by_tag(tag_slug: str) -> List[dict]:
    """Return articles that have the given tag slug."""
    return [
        a for a in load_article_metadata()
        if any(slugify_tag(t) == tag_slug for t in a.get("tags", []))
    ]