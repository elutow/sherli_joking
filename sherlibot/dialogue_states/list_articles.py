# -*- coding: utf-8 -*-
"""Logic for finding articles in LIST_ARTICLES state"""

from typing import Dict, Any, Optional
import enum
import logging
import random

from slowbro.core.bot_message import BotMessage
from slowbro.core.user_message import UserMessage

from ..dialogue import DialogueStates, DialogueStateResult
from ..intents import IntentDataset, predict_intent
from ..session_attributes import SessionAttributes
from ..utils import AutoName

from ._common import get_echo_query_message

# Modular services and utilities
_INITIALIZED = False
_LOGGER = None


class ListArticleStates(AutoName):
    """Sub-states for the LIST_ARTICLES dialogue state"""
    # Retrieve and ask the user if they want to hear about the article
    GET_ARTICLE = enum.auto()
    # Confirm whether the user wants to hear the article
    CONFIRM_ARTICLE = enum.auto()


class ListArticleMemory:
    """Memory for LIST_ARTICLES state"""

    def __init__(self,
                 sub_state: ListArticleStates = ListArticleStates.GET_ARTICLE):
        self.sub_state: ListArticleStates = sub_state

    def from_dict(self, json_obj: Dict[str, any]) -> None:
        self.sub_state = ListArticleStates(
            json_obj.get('sub_state', ListArticleStates.GET_ARTICLE.value))

    def to_dict(self) -> Dict[str, Any]:
        return {
            'sub_state': self.sub_state.value,
        }


def initialize() -> None:  #pragma: no cover
    """Initialize one-time modular services and utilities"""
    global _INITIALIZED, _LOGGER  #pylint: disable=global-statement
    if _INITIALIZED:
        return
    _LOGGER = logging.getLogger(__file__)
    _INITIALIZED = True


_FOUND_ARTICLE_RESPONSE_1 = [
    "Here's an article from", "I found an article from"
]
_FOUND_ARTICLE_RESPONSE_2 = [
    "Do you want to hear more?", "Would you like to hear more?"
]
_MISSED_QUERY_RESPONSE = ["I didn't catch that.", "I didn't quite get that."]
_OTHER_SEARCH_RESPONSE = [
    "What else would you like to search for?",
    "What other topics would you like to search?",
    "What other news would you like to hear about?"
]


def entrypoint(user_message: UserMessage,
               session_attributes: SessionAttributes,
               memory_dict: Optional[Dict[str, Any]]) -> DialogueStateResult:
    """
    Entrypoint for state LIST_ARTICLES

    It can mutate session_attributes or round_attributes
    """
    assert _INITIALIZED
    assert session_attributes.query_include_words or session_attributes.query_exclude_words
    assert session_attributes.queried_articles

    memory = ListArticleMemory()
    if memory_dict:
        memory.from_dict(memory_dict)

    if memory.sub_state == ListArticleStates.GET_ARTICLE:
        # Ask if user wants to hear current article
        bot_message = BotMessage()
        bot_message.response_ssml = ("{} {}: {}. {}").format(
            random.choice(_FOUND_ARTICLE_RESPONSE_1),
            session_attributes.article_candidate.source.name,
            session_attributes.article_candidate.title,
            random.choice(_FOUND_ARTICLE_RESPONSE_2))
        _LOGGER.debug("Article title: %s",
                      session_attributes.article_candidate.title)
        memory.sub_state = ListArticleStates.CONFIRM_ARTICLE
        return DialogueStateResult(DialogueStates.LIST_ARTICLES,
                                   bot_message=bot_message,
                                   memory_dict=memory.to_dict())
    elif memory.sub_state == ListArticleStates.CONFIRM_ARTICLE:
        user_utterance = user_message.get_utterance()
        intent = predict_intent(user_utterance, IntentDataset.NAVIGATE)
        if user_utterance in ('no', 'nope'):
            try:
                session_attributes.current_article_index += 1
                _LOGGER.debug('New article index: %s. Total articles: %s',
                              session_attributes.current_article_index,
                              len(session_attributes.queried_articles))
            except IndexError:
                bot_message = BotMessage()
                # TODO: Suggest a new query?
                bot_message.response_ssml = (
                    "I couldn't find any more articles about {}. " +
                    random.choice(_OTHER_SEARCH_RESPONSE)).format(' and '.join(
                        session_attributes.query_include_words))
                if session_attributes.query_exclude_words:
                    bot_message.response_ssml += ', excluding ' + ' and '.join(
                        session_attributes.query_exclude_words)
                bot_message.reprompt_ssml = "What would you like to search for?"
                return DialogueStateResult(DialogueStates.FIND_ARTICLE,
                                           bot_message=bot_message)
            memory.sub_state = ListArticleStates.GET_ARTICLE
            return DialogueStateResult(DialogueStates.LIST_ARTICLES,
                                       memory_dict=memory.to_dict())
        elif intent == 'search':
            return DialogueStateResult(DialogueStates.FIND_ARTICLE)
        elif intent == 'yes':
            # User wants to hear about article; process it and goto QnA for summary
            session_attributes.update_current_article()
            return DialogueStateResult(DialogueStates.QNA)
        elif intent == 'echo_query':
            bot_message: BotMessage = get_echo_query_message(
                session_attributes)
            bot_message.reprompt_ssml = (
                "Do you still want to hear more about the article from {}?"
            ).format(session_attributes.article_candidate.source.name)
            return DialogueStateResult(DialogueStates.LIST_ARTICLES,
                                       bot_message=bot_message,
                                       memory_dict=memory.to_dict())
        else:
            bot_message = BotMessage()
            bot_message.response_ssml = (
                "{}. Do you want to hear more?".format(
                    random.choice(_MISSED_QUERY_RESPONSE)))
            bot_message.reprompt_ssml = ("{} {}: {}. {}").format(
                random.choice(_FOUND_ARTICLE_RESPONSE_1),
                session_attributes.article_candidate.source.name,
                session_attributes.article_candidate.source.name,
                random.choice(_FOUND_ARTICLE_RESPONSE_2))
            return DialogueStateResult(DialogueStates.LIST_ARTICLES,
                                       bot_message=bot_message,
                                       memory_dict=memory.to_dict())
    else:  #pragma: no cover
        raise NotImplementedError('Unknown LIST_ARTICLES sub-state: {}'.format(
            repr(memory.sub_state)))
