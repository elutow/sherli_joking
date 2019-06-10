# -*- coding: utf-8 -*-
"""Common utilities for dialogue states"""

from slowbro.core.bot_message import BotMessage

from ..session_attributes import SessionAttributes


def get_echo_query_message(session_attributes: SessionAttributes
                           ) -> BotMessage:
    bot_message = BotMessage()
    if not session_attributes.search_topics:
        bot_message.response_ssml = "You haven't searched for anything yet."
        return bot_message
    response = "You're searching for "
    if len(session_attributes.search_topics) >= 3:
        for i in range(len(session_attributes.search_topics) - 1):
            response += session_attributes.search_topics[i] + ', '
        response += 'and ' + session_attributes.search_topics[-1]
    elif len(session_attributes.search_topics) == 2:
        response += ' and '.join(session_attributes.search_topics)
    else:
        response += session_attributes.search_topics[0]
    bot_message.response_ssml = response
    return bot_message
