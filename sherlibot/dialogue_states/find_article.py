# -*- coding: utf-8 -*-
"""Logic for finding articles in PICK_ARTICLE state"""

from typing import List, Tuple, Dict, Any, Optional
import logging
import string
import random

from newsapi import NewsApiClient

from slowbro.core.bot_message import BotMessage
from slowbro.core.user_message import UserMessage

from ..dialogue import DialogueStates, DialogueStateResult
from ..session_attributes import SessionAttributes
from ..utils import get_config_dir

# Modular services and utilities
_INITIALIZED = False
_NEWSAPI_CLIENT = None
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


def _extract_topics_from_utterance(utterance: str) -> Tuple[str]:
    """Extract keyphrases from utterance"""
    filtered_utterance = ''.join(x for x in utterance if x in string.printable)
    # TODO: Use depeendency parser-based keyphrase extraction from aylien branch
    # Previous pke-based implementation has been removed due to license incompatibility
    keyphrases: List[Tuple[str, float]] = extractor.get_n_best()
    return tuple(filtered_utterance.split(' '))


def initialize() -> None:  #pragma: no cover
    """Initialize one-time modular services and utilities"""
    global _INITIALIZED, _NEWSAPI_CLIENT, _LOGGER  #pylint: disable=global-statement
    if _INITIALIZED:
        return
    _NEWSAPI_CLIENT = NewsApiClient(
        api_key=(get_config_dir() / 'newsapi_key').read_text().strip())
    _LOGGER = logging.getLogger(__file__)
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
    keyphrases: Tuple[str] = _extract_topics_from_utterance(user_utterance)
    if not keyphrases:
        bot_message.response_ssml = "{} {}".format(
            random.choice(_NO_KEYWORD_QUERY_RESPONSE),
            random.choice(_REPEAT_QUERY_RESPONSE))

        return DialogueStateResult(DialogueStates.FIND_ARTICLE,
                                   bot_message=bot_message)

    # Query NewsAPI based on keyphrases
    query: str = ' AND '.join("'{}'".format(x) for x in keyphrases)
    _LOGGER.debug(f'Query: {query}')
    queried_articles: List[Dict[str, Any]] = _NEWSAPI_CLIENT.get_everything(
        q=query)['articles']
    _LOGGER.debug(f'Number of articles: {len(queried_articles)}')
    if not queried_articles:
        bot_message.response_ssml = (
            "Hmm, I couldn't find any articles on {}. " +
            random.choice(_REPEAT_QUERY_RESPONSE)).format(
                ' and '.join(keyphrases))
        return DialogueStateResult(DialogueStates.FIND_ARTICLE,
                                   bot_message=bot_message)

    # Successfully found articles; store search topics and list of articles
    # Then, let user pick article in LIST_ARTICLES
    session_attributes.update_search(keyphrases, queried_articles)
    return DialogueStateResult(DialogueStates.LIST_ARTICLES)
