# -*- coding: utf-8 -*-
"""Logic for finding articles in PICK_ARTICLE state"""

from typing import List, Tuple, Dict, Any, Optional
import logging
import string

import pke
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


def _extract_topics_from_utterance(utterance: str) -> Tuple[str]:
    """Extract keyphrases from utterance"""
    filtered_utterance = ''.join(x for x in utterance if x in string.printable)
    extractor = pke.unsupervised.TopicRank()
    extractor.load_document(input=filtered_utterance, language='en')
    extractor.candidate_selection()
    if not extractor.candidates:
        # No candidates found during selection; abort
        return (filtered_utterance, )
    extractor.candidate_weighting()
    keyphrases: List[Tuple[str, float]] = extractor.get_n_best()
    return tuple(x for x, _ in keyphrases)


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
    bot_message.reprompt_ssml = "What would you like to search?"

    # TODO: Ability to query based on top headlines?

    # Extract keyphrases (i.e. search topics) from utterance
    user_utterance: str = user_message.get_utterance()
    if not user_utterance:
        bot_message.response_ssml = "Sorry, I didn't catch that. Please try again"
        return DialogueStateResult(DialogueStates.FIND_ARTICLE,
                                   bot_message=bot_message)

    # Ensure keyphrases are detected
    keyphrases: Tuple[str] = _extract_topics_from_utterance(user_utterance)
    if not keyphrases:
        bot_message.response_ssml = (
            "Sorry, I couldn't figure out what you wanted to search. Please try again"
        )
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
            "Hmm, I couldn't find any articles on {}. "
            "Please try again").format(' and '.join(keyphrases))
        return DialogueStateResult(DialogueStates.FIND_ARTICLE,
                                   bot_message=bot_message)

    # Successfully found articles; store search topics and list of articles
    # Then, let user pick article in LIST_ARTICLES
    session_attributes.update_search(keyphrases, queried_articles)
    return DialogueStateResult(DialogueStates.LIST_ARTICLES)
