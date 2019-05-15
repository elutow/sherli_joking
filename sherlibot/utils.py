# -*- coding: utf-8 -*-
"""Miscellaneous collection of utilities"""

import enum


class AutoName(enum.Enum):
    def _generate_next_value_(name: str, start, count, last_values) -> str:
        return name.lower()
