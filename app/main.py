from __future__ import annotations

import utils.transport
import utils.session
from app.crew.workflow import run_workflow


def main() -> None:
    run_workflow()


if __name__ == "__main__":
    main()

