# -*- coding: utf-8 -*-
import argparse
import json
import os
import shutil
import subprocess
from datetime import datetime
from functools import lru_cache
from pathlib import Path

from flask import render_template

from app.config import get_config


def _vite_manifest_path(dist_path):
    return dist_path / ".vite" / "manifest.json"

@lru_cache
def vite_manifest(out_dir: str):
    path = _vite_manifest_path(Path(out_dir))
    with open(path, "r") as fd:
        return json.load(fd)

def maybe_build_assets(_out_dir: str):
    """
    Build Vite assets on startup.
    Reads `root` and `outDir` from the provided Vite config file.
    """
    root_dir = Path(".").resolve()
    out_dir = Path(_out_dir)
    manifest = _vite_manifest_path(out_dir)
    package_json = root_dir / "package.json"

    if not package_json.exists():
        print("[vite] package.json not found; skipping build.")
        return

    force = os.getenv("FORCE_BUILD", "1") == "1"
    if manifest.exists() and not force:
        print("[vite] manifest exists; skipping build.")
        return

    print("[vite] building assets...")
    env = os.environ.copy()
    if out_dir.exists():
        print(f"[vite] rm -r {out_dir}")
        subprocess.run(["rm", "-r", out_dir])
    # Ensure dependencies are installed
    if not (root_dir / "node_modules").exists():
        if (root_dir / "package-lock.json").exists():
            subprocess.run(["npm", "ci"], cwd=str(root_dir), check=True, env=env)
        else:
            subprocess.run(
                ["npm", "install", "--no-audit", "--no-fund"],
                cwd=str(root_dir),
                check=True,
                env=env
            )

    # Run build
    subprocess.run(["npm", "run", "build:assets"], cwd=str(root_dir), check=True, env=env)
    print("[vite] build complete.")


def _write_html(site_dir: Path, rel_path: str, html: str):
    target_path = site_dir / rel_path
    target_path.parent.mkdir(parents=True, exist_ok=True)
    target_path.write_text(html, encoding="utf-8")


def _resolve_content_path(content_root: str, path_value: str) -> Path:
    path = Path(path_value)
    if path.is_absolute():
        return path
    return Path(content_root) / path


def _validate_build_inputs(cfg):
    content_root = Path(cfg.CONTENT_ROOT)
    if not content_root.exists() or not content_root.is_dir():
        raise ValueError(f"CONTENT_ROOT does not exist or is not a directory: {content_root}")

    site_config_path = _resolve_content_path(cfg.CONTENT_ROOT, cfg.SITE_CONFIG_PATH)
    if not site_config_path.exists():
        raise ValueError(f"SITE_CONFIG_PATH does not exist: {site_config_path}")

    with open(site_config_path, "r", encoding="utf-8") as fd:
        site_cfg = json.load(fd)

    posts = site_cfg.get("posts")
    if not posts:
        raise ValueError("Site config must define `posts` directory")

    posts_path = _resolve_content_path(cfg.CONTENT_ROOT, posts)
    if not posts_path.exists() or not posts_path.is_dir():
        raise ValueError(f"Posts directory does not exist: {posts_path}")


def _write_build_manifest(site_dir: Path, cfg, article_count: int):
    html_files = sorted([str(path.relative_to(site_dir)) for path in site_dir.rglob("*.html")])
    manifest = {
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "site_base": cfg.SITE_BASE,
        "content_root": str(Path(cfg.CONTENT_ROOT).resolve()),
        "site_config_path": cfg.SITE_CONFIG_PATH,
        "output_dir": str(site_dir),
        "article_count": article_count,
        "html_count": len(html_files),
        "html_files": html_files,
        "warnings": [],
    }
    (site_dir / "build-manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def build_static_site(cfg, skip_assets: bool = False):
    from app import create_app
    from app.services.content import (
        load_article_content,
        load_article_metadata,
        get_all_tags,
        get_articles_by_tag,
        get_site_config,
    )

    if not skip_assets:
        maybe_build_assets(cfg.VITE_DIST_PATH)

    _validate_build_inputs(cfg)

    project_root = Path(".").resolve()
    site_dir = project_root / cfg.STATIC_SITE_DIR
    static_src = project_root / "static"

    if site_dir.exists():
        shutil.rmtree(site_dir)
    site_dir.mkdir(parents=True, exist_ok=True)

    if static_src.exists():
        shutil.copytree(static_src, site_dir / "static", dirs_exist_ok=True)

    app = create_app()

    with app.app_context():
        articles = load_article_metadata()
        _write_html(
            site_dir,
            "index.html",
            render_template("index.html", articles=articles[:5]),
        )
        _write_html(
            site_dir,
            "posts/index.html",
            render_template("list.html", articles=articles),
        )

        for item in articles:
            article = load_article_content(item["id"])
            _write_html(
                site_dir,
                f"posts/{item['id']}/index.html",
                render_template("detail.html", article=article),
            )

        _write_html(site_dir, "404.html", render_template("404.html"))

        # Build tag pages
        tags = get_all_tags()
        _write_html(site_dir, "tags/index.html", render_template("tags.html", tags=tags))
        for tag_info in tags:
            tag_articles = get_articles_by_tag(tag_info["slug"])
            _write_html(
                site_dir,
                f"tags/{tag_info['slug']}/index.html",
                render_template("tag.html", tag=tag_info["slug"], display_tag=tag_info["tag"], articles=tag_articles),
            )

        # Generate sitemap.xml and robots.txt
        site_cfg_data = get_site_config()
        base_url = (site_cfg_data.get("base_url") or "").rstrip("/")
        if base_url:
            sitemap_xml = render_template("sitemap.xml", articles=articles, tags=tags)
            (site_dir / "sitemap.xml").write_text(sitemap_xml, encoding="utf-8")
            robots_content = f"User-agent: *\nAllow: /\nSitemap: {base_url}/sitemap.xml\n"
            (site_dir / "robots.txt").write_text(robots_content, encoding="utf-8")
            print(f"[site] generated sitemap.xml and robots.txt")

    _write_build_manifest(site_dir, cfg, len(articles))

    (site_dir / ".nojekyll").write_text("", encoding="utf-8")
    print(f"[site] generated static site at {site_dir}")
    print(f"[site] pages: home=1 list=1 details={len(articles)} tags={len(tags)}")


def main(argv=None):
    parser = argparse.ArgumentParser(description="Build frontend assets and static site pages")
    parser.add_argument("--static", action="store_true", help="Build static HTML pages")
    parser.add_argument("--assets-only", action="store_true", help="Build frontend assets only")
    parser.add_argument("--skip-assets", action="store_true", help="Skip frontend asset build")
    args, unknown = parser.parse_known_args(argv)

    cfg = get_config(unknown)

    try:
        if args.assets_only:
            maybe_build_assets(cfg.VITE_DIST_PATH)
            return

        if args.static:
            build_static_site(cfg, skip_assets=args.skip_assets)
            return

        maybe_build_assets(cfg.VITE_DIST_PATH)
    except ValueError as exc:
        print(f"[build:error] {exc}")
        raise SystemExit(1)
    except subprocess.CalledProcessError as exc:
        print(f"[build:error] command failed with exit code {exc.returncode}")
        raise SystemExit(2)


if __name__ == "__main__":
    main()
