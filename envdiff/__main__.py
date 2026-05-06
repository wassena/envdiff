"""Allow `python -m envdiff` to invoke the diff CLI by default."""

import sys
from envdiff.cli_diff import run

if __name__ == "__main__":
    sys.exit(run())
