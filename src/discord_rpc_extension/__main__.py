from __future__ import annotations

import logging
import sys

from .config import load_config
from .rpc import run_presence_loop


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    config = load_config()
    ok = run_presence_loop(config)
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
