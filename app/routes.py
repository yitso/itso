# -*- coding: utf-8 -*-
from flask import Blueprint, render_template
from app.services.content import load_article_metadata, load_article_content

def register_routes(app):
    @app.route("/")
    def index():
        articles = load_article_metadata()[:5]
        return render_template("index.html", articles=articles)

    @app.route("/posts")
    def article_list():
        articles = load_article_metadata()
        return render_template("list.html", articles=articles)

    @app.route("/posts/<path:slug>")
    def article_detail(slug):
        article = load_article_content(slug)
        return render_template("detail.html", article=article)
