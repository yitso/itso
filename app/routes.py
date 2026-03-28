# -*- coding: utf-8 -*-
from flask import render_template, abort, Response, redirect, url_for
from werkzeug.exceptions import NotFound
from app.services.content import (
    load_article_metadata,
    load_article_content,
    load_article_content_by_slug,
    get_all_tags,
    get_articles_by_tag,
    get_site_config,
    slugify_tag,
)

def register_routes(app):
    @app.route("/", strict_slashes=False)
    def index():
        articles = load_article_metadata()[:5]
        return render_template("index.html", articles=articles)

    @app.route("/posts", strict_slashes=False)
    @app.route("/posts/", strict_slashes=False)
    def article_list():
        articles = load_article_metadata()
        return render_template("list.html", articles=articles)

    @app.route("/posts/<path:article_ref>/", strict_slashes=False)
    def article_detail(article_ref):
        try:
            article = load_article_content(article_ref)
            return render_template("detail.html", article=article)
        except NotFound:
            article = load_article_content_by_slug(article_ref)
            if not article:
                abort(404)
            return redirect(url_for("article_detail", article_ref=article["id"]), code=301)

    @app.route("/tags/", strict_slashes=False)
    def tag_list():
        tags = get_all_tags()
        return render_template("tags.html", tags=tags)

    @app.route("/tags/<tag>", strict_slashes=False)
    @app.route("/tags/<tag>/", strict_slashes=False)
    def tag_detail(tag):
        articles = get_articles_by_tag(tag)
        if not articles:
            abort(404)
        display_tag = next(
            (t for a in articles for t in a.get("tags", []) if slugify_tag(t) == tag),
            tag,
        )
        return render_template("tag.html", tag=tag, display_tag=display_tag, articles=articles)

    @app.route("/sitemap.xml")
    def sitemap():
        site_cfg = get_site_config()
        if not (site_cfg.get("base_url") or "").strip():
            abort(404)
        articles = load_article_metadata()
        tags = get_all_tags()
        xml = render_template("sitemap.xml", articles=articles, tags=tags)
        return Response(xml, mimetype="application/xml")

    @app.route("/robots.txt")
    def robots_txt():
        site_cfg = get_site_config()
        base_url = (site_cfg.get("base_url") or "").strip()
        if not base_url:
            abort(404)
        base_url = base_url.rstrip("/")
        content = "User-agent: *\nAllow: /\n"
        content += f"Sitemap: {base_url}/sitemap.xml\n"
        return Response(content, mimetype="text/plain")
