# -*- coding: utf-8 -*-
import json
import os
import subprocess
from functools import lru_cache
from pathlib import Path

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
    subprocess.run(["npm", "run", "build"], cwd=str(root_dir), check=True, env=env)
    print("[vite] build complete.")
