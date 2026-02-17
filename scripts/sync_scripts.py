"""Sync expstash scripts into expaper templates.

Run after updating the expstash submodule:
  python3 scripts/sync_scripts.py
"""
import shutil
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent
UPSTREAM = REPO_ROOT / "vendor" / "expstash" / "scripts"
VENDOR = REPO_ROOT / "expaper" / "templates" / "scripts"

SCRIPTS = ["add_tool", "run_experiment", "snapshot_experiment"]


def main():
    if not UPSTREAM.exists():
        print("[ERROR] vendor/expstash not found. Run: git submodule update --init")
        return 1

    for name in SCRIPTS:
        src = UPSTREAM / name
        dst = VENDOR / name
        if not src.exists():
            print(f"[WARNING] {src} not found, skipping")
            continue
        shutil.copy2(src, dst)
        dst.chmod(dst.stat().st_mode | 0o755)
        print(f"  Synced: {name}")

    print("[OK] Scripts synced from vendor/expstash/scripts/")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
