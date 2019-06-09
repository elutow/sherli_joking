# -*- coding: utf-8 -*-
"""Miscellaneous collection of utilities"""

import enum
from pathlib import Path


class AutoName(enum.Enum):
    """Enum with auto values as lowercase key names"""

    def _generate_next_value_(name: str, start, count, last_values) -> str:  #pylint: disable=no-self-argument,unused-argument
        return name.lower()  #pylint: disable=no-member


def get_config_dir() -> Path:
    """Returns the path to the config dir"""
    return Path(__file__).resolve().parent.parent / 'config'
