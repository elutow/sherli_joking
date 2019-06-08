# -*- coding: utf-8 -*-
"""Logic for finding articles in LIST_ARTICLES state"""

from typing import Dict, Any, Optional
import enum
import logging

from slowbro.core.bot_message import BotMessage
from slowbro.core.user_message import UserMessage

from ..dialogue import DialogueStates, DialogueStateResult
from ..session_attributes import SessionAttributes
from ..utils import AutoName

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


def initialize() -> None:
    """Initialize one-time modular services and utilities"""
    global _INITIALIZED, _LOGGER  #pylint: disable=global-statement
    if _INITIALIZED:
        return
    _LOGGER = logging.getLogger(__file__)
    _INITIALIZED = True


def entrypoint(user_message: UserMessage,
               session_attributes: SessionAttributes,
               memory_dict: Optional[Dict[str, Any]]) -> DialogueStateResult:
    """
    Entrypoint for state LIST_ARTICLES

    It can mutate session_attributes or round_attributes
    """
    assert _INITIALIZED
    assert session_attributes.search_topics
    assert session_attributes.queried_articles

    memory = ListArticleMemory()
    if memory_dict:
        memory.from_dict(memory_dict)

    if memory.sub_state == ListArticleStates.GET_ARTICLE:
        # Ask if user wants to hear current article
        bot_message = BotMessage()
        bot_message.response_ssml = (
            "Here's an article from {}: {}. Do you want to hear more?").format(
                session_attributes.article_candidate['source']['name'],
                session_attributes.article_candidate['title'])
        _LOGGER.debug("Article title: %s",
                      session_attributes.article_candidate['title'])
        memory.sub_state = ListArticleStates.CONFIRM_ARTICLE
        return DialogueStateResult(DialogueStates.LIST_ARTICLES,
                                   bot_message=bot_message,
                                   memory_dict=memory.to_dict())
    if memory.sub_state == ListArticleStates.CONFIRM_ARTICLE:
        user_utterance = user_message.get_utterance()
        if False:  # TODO: Check if intent is detected
            raise NotImplementedError()
        elif user_utterance == 'yes':
            # User wants to hear about article; process it and goto QnA for summary
            session_attributes.update_current_article()
            return DialogueStateResult(DialogueStates.QNA)
        elif user_utterance == 'no':
            try:
                session_attributes.current_article_index += 1
            except IndexError:
                bot_message = BotMessage()
                # TODO: Suggest a new query?
                bot_message.response_ssml = (
                    "I couldn't find any more articles about {}. "
                    "Could you try something else?").format(' and '.join(
                        session_attributes.search_topics))
                bot_message.reprompt_ssml = "What would you like to search for?"
                return DialogueStateResult(DialogueStates.FIND_ARTICLE,
                                           bot_message=bot_message)
            memory.sub_state = ListArticleStates.GET_ARTICLE
            return DialogueStateResult(DialogueStates.FIND_ARTICLE,
                                       memory_dict=memory.to_dict())
        else:
            bot_message = BotMessage()
            bot_message.response_ssml = (
                "Sorry, I didn't quite catch that. Do you want to hear more?")
            bot_message.reprompt_ssml = (
                "I have an article from {}: {}. Do you want to hear more?"
            ).format(session_attributes.article_candidate['source']['name'],
                     session_attributes.article_candidate['title'])
            return DialogueStateResult(DialogueStates.LIST_ARTICLES,
                                       bot_message=bot_message,
                                       memory_dict=memory.to_dict())
