# -*- coding: utf-8 -*-
import json
from pathlib import Path
from datetime import datetime

from flask import Flask
from babel.dates import format_date

from app.config import get_config
from app.i18n import load_translations, make_translator
from app.routes import register_routes
from app.services.content import get_site_config

BASE_DIR = Path(__file__).resolve().parent.parent
TEMPLATES_DIR = BASE_DIR / "templates"
STATIC_DIR=str(BASE_DIR / "static")

def create_app():
    cfg = get_config()
    app = Flask(__name__, template_folder=str(TEMPLATES_DIR), static_folder=str(BASE_DIR / "static"))
    app.config.from_object(cfg)

    @app.context_processor
    def inject_site_config():
        site_cfg = get_site_config()
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

        return dict(
            site=site,
            profile=profile,
            footer=footer,
            footer_extra_html=footer_extra_html,
            site_year_text=year_text,
        )


    @app.context_processor
    def inject_translations():
        site_cfg = get_site_config()
        i18n_file = site_cfg.get("i18n_file", "i18n/en.json")
        translations = load_translations(i18n_file)
        t = make_translator(translations)
        lang = site_cfg.get("lang", 'en')
        return dict(t=t, lang=lang)

    @app.template_filter()
    def date_i18n(value, fmt="long"):
        site_cfg = get_site_config()

        return format_date(value, format=fmt, locale=site_cfg.get("date_locale", "en"))

    register_routes(app)

    return app
