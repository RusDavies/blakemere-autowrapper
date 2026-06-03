"""Lowercase import path for AutoWrapper.

The original project exposed ``AutoWrapper`` from ``AutoWrapper.py``. This
module provides the conventional lowercase import path while preserving the
existing import for compatibility.
"""

from AutoWrapper import AutoWrapper

__all__ = ["AutoWrapper"]
