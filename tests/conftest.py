from __future__ import annotations

import sys
from pathlib import Path


# Ensure `import app...` works when tests are run via the `pytest` entrypoint
# (which may not include the repo root on `sys.path`).
REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

