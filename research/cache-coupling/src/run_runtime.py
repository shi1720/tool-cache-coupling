"""Compatibility entry point for provenance-preserving runtime reproduction."""
import sys

sys.dont_write_bytecode = True
from reproduce import main


if __name__ == "__main__":
    main(["runtime"])
