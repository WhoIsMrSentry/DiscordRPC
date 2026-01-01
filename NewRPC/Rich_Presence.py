"""Backwards-compatible entrypoint.

Yeni yapı: src/discord_rpc_extension paketine taşındı.
Bu dosya eski çalıştırma alışkanlıklarını bozmamak için sadece yönlendirici.
"""

from __future__ import annotations

import sys
from pathlib import Path


def _ensure_src_on_path() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    src_path = repo_root / "src"
    if src_path.exists():
        sys.path.insert(0, str(src_path))


_ensure_src_on_path()

from discord_rpc_extension.__main__ import main  # noqa: E402


if __name__ == "__main__":
    main()