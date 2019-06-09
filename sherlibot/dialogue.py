# -*- coding: utf-8 -*-
"""Dialogue management module"""

from typing import Dict, Any, Optional
import enum

from slowbro.core.bot_message import BotMessage

from .utils import AutoName


@enum.unique
class DialogueStates(AutoName):
    """Overall states for dialogue control"""
    INIT = enum.auto()
    FIND_ARTICLE = enum.auto()
    LIST_ARTICLES = enum.auto()
    QNA = enum.auto()


class DialogueStateResult:  #pylint: disable=too-few-public-methods
    """
    Returned whenever a dialogue state exits
    """

    def __init__(self,
                 next_state: DialogueStates,
                 bot_message: Optional[BotMessage] = None,
                 memory_dict: Optional[Dict[str, Any]] = None):
        self.next_state = next_state
        self.bot_message = bot_message
        self.memory_dict = memory_dict
