# -*- coding: utf-8 -*-
"""Common utilities for dialogue states"""

from slowbro.core.bot_message import BotMessage

from ..session_attributes import SessionAttributes


def get_echo_query_message(session_attributes: SessionAttributes
                           ) -> BotMessage:
    bot_message = BotMessage()
    if not session_attributes.query_include_words and not session_attributes.query_exclude_words:
        bot_message.response_ssml = "You haven't searched for anything yet."
        return bot_message
    response = "You're searching for "
    if session_attributes.query_include_words:
        response += ' and '.join(session_attributes.query_include_words)
    if session_attributes.query_exclude_words:
        response += ', excluding '
        response += ' and '.join(session_attributes.query_exclude_words)
    bot_message.response_ssml = response
    return bot_message
