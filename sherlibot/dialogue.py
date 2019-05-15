# -*- coding: utf-8 -*-
"""Dialogue management module"""

import enum

from .utils import AutoName


@enum.unique
class DialogueStates(AutoName):
    """States for dialogue control"""
    # NOTE: See https://github.com/elutow/sherli_joking/projects/1
    INIT = enum.auto()
    FIND_ARTICLE = enum.auto()
    PICK_ARTICLE = enum.auto()
    QA = enum.auto()
