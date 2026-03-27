# -*- coding: utf-8 -*-
import os
import sys
import argparse
from dataclasses import dataclass

@dataclass
class BaseConfig:
    VITE_DIST_PATH: str = "static/itso/dist"
    SITE_CONFIG_PATH: str = "configs/example.json"
    THEMES_DIR: str = "themes"
    CONTENT_ROOT: str = "."
    SITE_BASE: str = "/"
    STATIC_SITE_DIR: str = "dist"
    HOST: str = "127.0.0.1"
    PORT: int = 8000
    DEBUG: bool = False

class DevConfig(BaseConfig):
    DEBUG: bool = True

class ProdConfig(BaseConfig):
    DEBUG: bool = False

CONFIG_MAP = {
    "development": DevConfig,
    "production": ProdConfig,
}

def _parse_cli_args(argv=None) -> dict:
    if argv is None:
        argv = sys.argv[1:]

    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("--lang", dest="LANG")
    parser.add_argument("--site-config", dest="SITE_CONFIG_PATH")
    parser.add_argument("--themes-dir", dest="THEMES_DIR")
    parser.add_argument("--content-root", dest="CONTENT_ROOT")
    parser.add_argument("--site-base", dest="SITE_BASE")
    parser.add_argument("--static-site-dir", dest="STATIC_SITE_DIR")
    parser.add_argument("--host", dest="HOST")
    parser.add_argument("--port", dest="PORT", type=int)

    args, _ = parser.parse_known_args(argv)
    return {k: v for k, v in vars(args).items() if v is not None}

def get_config(argv=None):
    env = os.getenv("FLASK_ENV", "production").lower()

    cfg = CONFIG_MAP.get(env, ProdConfig)()

    env_site_base = os.getenv("SITE_BASE")
    env_static_site_dir = os.getenv("STATIC_SITE_DIR")
    env_content_root = os.getenv("CONTENT_ROOT")
    env_themes_dir = os.getenv("THEMES_DIR")
    if env_site_base:
        cfg.SITE_BASE = env_site_base
    if env_static_site_dir:
        cfg.STATIC_SITE_DIR = env_static_site_dir
    if env_content_root:
        cfg.CONTENT_ROOT = env_content_root
    if env_themes_dir:
        cfg.THEMES_DIR = env_themes_dir

    overrides = _parse_cli_args(argv)

    for k, v in overrides.items():
        setattr(cfg, k, v)

    return cfg
