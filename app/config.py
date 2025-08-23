# -*- coding: utf-8 -*-
import os
import sys
import argparse
from dataclasses import dataclass

@dataclass
class BaseConfig:
    SITE_CONFIG_PATH: str = "configs/example.json"
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
    parser.add_argument("--host", dest="HOST")
    parser.add_argument("--port", dest="PORT", type=int)

    args, _ = parser.parse_known_args(argv)
    return {k: v for k, v in vars(args).items() if v is not None}

def get_config(argv=None):
    env = os.getenv("FLASK_ENV", "production").lower()

    cfg = CONFIG_MAP.get(env, ProdConfig)()
    overrides = _parse_cli_args(argv)

    for k, v in overrides.items():
        setattr(cfg, k, v)

    return cfg
