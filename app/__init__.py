# -*- coding: utf-8 -*-
from pathlib import Path
from datetime import datetime

from flask import Flask
from babel.dates import format_date

from app.config import get_config
from app.i18n import load_translations, make_translator
from app.routes import register_routes
from app.services.content import get_site_config, get_theme_config, slugify_tag
from app.build import vite_manifest

BASE_DIR = Path(__file__).resolve().parent.parent
TEMPLATES_DIR = BASE_DIR / "templates"
STATIC_DIR=str(BASE_DIR / "static")


def _normalize_site_base(base: str) -> str:
    base = (base or "/").strip()
    if not base:
        return "/"
    if not base.startswith("/"):
        base = "/" + base
    if not base.endswith("/"):
        base += "/"
    return base


def _is_external_url(value: str) -> bool:
    return value.startswith(("http://", "https://", "mailto:", "tel:", "#"))

def create_app():
    cfg = get_config()
    app = Flask(__name__, template_folder=str(TEMPLATES_DIR), static_folder=str(BASE_DIR / "static"))
    app.config.from_object(cfg)
    app.config["SITE_BASE"] = _normalize_site_base(getattr(cfg, "SITE_BASE", "/"))

    def site_url(path: str = "") -> str:
        site_base = app.config["SITE_BASE"]
        if not path:
            return site_base
        if _is_external_url(path):
            return path

        normalized = path if path.startswith("/") else "/" + path
        if site_base == "/":
            return normalized
        return site_base[:-1] + normalized

    def asset_url(path: str) -> str:
        if not path:
            return site_url("/static")
        if _is_external_url(path):
            return path
        if path.startswith("/"):
            return site_url(path)
        return site_url("/static/" + path.lstrip("/"))

    def page_url(path: str) -> str:
        if not path:
            return site_url("/")
        if _is_external_url(path):
            return path
        return site_url(path if path.startswith("/") else "/" + path)

    def article_url(article_id: str) -> str:
        cleaned = (article_id or "").strip("/")
        return page_url(f"/posts/{cleaned}/")

    @app.context_processor
    def inject_site_config():
        site_cfg = get_site_config()
        theme = get_theme_config()
        site = site_cfg.get("site", {}) or {}
        profile = site_cfg.get("profile", {}) or {}
        footer = site_cfg.get("footer", {}) or {}

        # Footer extra (handled in template: pass already-processed html if you want)
        extra_cfg = footer.get("extra", {}) or {}
        extra_type = extra_cfg.get("type", "none")
        footer_extra_html = ""
        if extra_type == "markdown":
            from app.services import process_markdown
            footer_extra_html = process_markdown(extra_cfg.get("markdown_path", ""))
        elif extra_type == "inline":
            footer_extra_html = extra_cfg.get("inline_html", "")

        # year range
        now_year = datetime.now().year
        since_year = int(footer.get("since_year", now_year))
        year_text = f"{since_year}–{now_year}" if since_year < now_year else str(now_year)

        _canonical_base = (site_cfg.get("base_url") or "").rstrip("/")

        def canonical_url(path: str = "") -> str:
            if not _canonical_base:
                return ""
            # Absolute URLs are returned as-is (no site_url prefix needed).
            if path.startswith(("http://", "https://")):
                return path
            # Avoid double-applying SITE_BASE when path is already site-relative.
            site_base = app.config["SITE_BASE"]
            if site_base and site_base != "/" and path.startswith(site_base):
                return _canonical_base + path
            return _canonical_base + site_url(path)

        def tag_url(tag: str) -> str:
            return page_url(f"/tags/{slugify_tag(tag)}/")

        return dict(
            site=site,
            theme=theme,
            profile=profile,
            footer=footer,
            footer_extra_html=footer_extra_html,
            site_year_text=year_text,
            site_url=site_url,
            asset_url=asset_url,
            page_url=page_url,
            home_url=page_url("/"),
            posts_url=page_url("/posts/"),
            article_url=article_url,
            canonical_url=canonical_url,
            tag_url=tag_url,
        )

    @app.context_processor
    def inject_translations():
        site_cfg = get_site_config()
        i18n_file = site_cfg.get("i18n_file", "i18n/en.json")
        translations = load_translations(i18n_file)
        t = make_translator(translations)
        lang = site_cfg.get("lang", 'en')
        return dict(t=t, lang=lang)

    @app.context_processor
    def inject_vite_assets():
        return dict(vite_dist_path=cfg.VITE_DIST_PATH, vite_manifest= vite_manifest(cfg.VITE_DIST_PATH))

    @app.template_filter()
    def date_i18n(value, fmt="long"):
        site_cfg = get_site_config()
        return format_date(value, format=fmt, locale=site_cfg.get("date_locale", "en"))

    register_routes(app)

    return app
