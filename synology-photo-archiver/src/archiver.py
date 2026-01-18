"""
DEPRECATED: This file is kept for backward compatibility only.
Please update your cron jobs and scripts to use 'src/main.py' instead.

This wrapper will be removed in a future version.
"""
import warnings

warnings.warn(
    "archiver.py is deprecated. Please update your scripts to use 'src/main.py' instead.",
    DeprecationWarning,
    stacklevel=2
)

from .main import main

if __name__ == "__main__":
    main()

