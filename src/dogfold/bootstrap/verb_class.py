#!/usr/bin/env python3
"""
VerbClass - base interface for all verbs
"""

from typing import List


class VerbClass:
    """Base class for all org verbs.

    Verbs must implement execute(args) and return an int exit code.
    """

    def execute(self, args: List[str]) -> int:
        raise NotImplementedError("Verbs must implement execute(args)")
