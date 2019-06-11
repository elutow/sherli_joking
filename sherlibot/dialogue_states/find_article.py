# -*- coding: utf-8 -*-
"""Logic for finding articles in PICK_ARTICLE state"""

from typing import List, Dict, Any, Optional
import logging
import random

from slowbro.core.bot_message import BotMessage
from slowbro.core.user_message import UserMessage

from nemo_utils import aylien_wrapper

from ..dialogue import DialogueStates, DialogueStateResult
from ..session_attributes import SessionAttributes

# Modular services and utilities
_INITIALIZED = False
_LOGGER = None

# Language generation variations
_QUERY_LIST_1 = ['news', 'news topics', 'news subject']
_QUERY_LIST_2 = [
    'would you like to hear about?', 'are you interested in?',
    'would you like to know more about?'
]
_MISSED_QUERY_RESPONSE = ["I didn't catch that.", "I didn't quite get that."]
_REPEAT_QUERY_RESPONSE = [
    "Please try again.", "Please repeat what you said.", "Please answer again"
]
_NO_KEYWORD_QUERY_RESPONSE = [
    "Sorry, I couldn't figure out what you wanted to search.",
    "Sorry, I wasn't able to figure out what you wanted to search."
]


def initialize() -> None:  #pragma: no cover
    """Initialize one-time modular services and utilities"""
    global _INITIALIZED, _LOGGER  #pylint: disable=global-statement
    if _INITIALIZED:
        return
    _LOGGER = logging.getLogger(__file__)
    aylien_wrapper.initialize()
    _INITIALIZED = True


def entrypoint(user_message: UserMessage,
               session_attributes: SessionAttributes,
               memory_dict: Optional[Dict[str, Any]]) -> DialogueStateResult:
    """
    Entrypoint for state FIND_ARTICLE

    It can mutate session_attributes or round_attributes
    """
    assert _INITIALIZED

    bot_message: BotMessage = BotMessage()
    bot_message.reprompt_ssml = "What {} {}".format(
        random.choice(_QUERY_LIST_1), random.choice(_QUERY_LIST_2))

    # TODO: Ability to query based on top headlines?

    # Extract keyphrases (i.e. search topics) from utterance
    user_utterance: str = user_message.get_utterance()
    if not user_utterance:
        bot_message.response_ssml = "Sorry, {} {}".format(
            random.choice(_MISSED_QUERY_RESPONSE),
            random.choice(_REPEAT_QUERY_RESPONSE))
        return DialogueStateResult(DialogueStates.FIND_ARTICLE,
                                   bot_message=bot_message)

    # Ensure keyphrases are detected
    main_query, include_words, exclude_words = aylien_wrapper.generate_query(
        user_utterance)
    if not include_words and not exclude_words:
        bot_message.response_ssml = "{} {}".format(
            random.choice(_NO_KEYWORD_QUERY_RESPONSE),
            random.choice(_REPEAT_QUERY_RESPONSE))

        return DialogueStateResult(DialogueStates.FIND_ARTICLE,
                                   bot_message=bot_message)

    # Query Aylien
    queried_articles: List[Any] = aylien_wrapper.extract_news(
        main_query, include_words, exclude_words)
    _LOGGER.debug(f'Number of articles: {len(queried_articles)}')
    if not queried_articles:
        bot_message.response_ssml = (
            "Hmm, I couldn't find any articles on {}, excluding {}. " +
            random.choice(_REPEAT_QUERY_RESPONSE)).format(
                ' or '.join(include_words), ' and '.join(exclude_words))
        return DialogueStateResult(DialogueStates.FIND_ARTICLE,
                                   bot_message=bot_message)

    # Successfully found articles; store search topics and list of articles
    # Then, let user pick article in LIST_ARTICLES
    session_attributes.update_search(include_words, exclude_words,
                                     queried_articles)
    return DialogueStateResult(DialogueStates.LIST_ARTICLES)
