# -*- coding: utf-8 -*-
"""Logic for QNA state"""

from typing import Dict, Any, Optional
import enum
import logging
import random

from allennlp.predictors.predictor import Predictor

from slowbro.core.bot_message import BotMessage
from slowbro.core.user_message import UserMessage

from ..session_attributes import SessionAttributes
from ..intents import IntentDataset, predict_intent
from ..dialogue import DialogueStates, DialogueStateResult
from ..utils import AutoName

from ._common import get_echo_query_message

# Modular services and utilities
_INITIALIZED = False
_PREDICTOR = None
_LOGGER = None


class QnaStates(AutoName):
    """Sub-states for the QNA dialogue state"""
    SUMMARIZE = enum.auto()
    QNA = enum.auto()


class QnaMemory:
    """Memory for QNA state"""

    def __init__(self, sub_state: QnaStates = QnaStates.SUMMARIZE):
        self.sub_state: QnaStates = sub_state

    def from_dict(self, json_obj: Dict[str, any]) -> None:
        self.sub_state = QnaStates(
            json_obj.get('sub_state', QnaStates.SUMMARIZE.value))

    def to_dict(self) -> Dict[str, Any]:
        return {
            'sub_state': self.sub_state.value,
        }


def initialize() -> None:  #pragma: no cover
    """Initialize one-time modular services and utilities"""
    global _INITIALIZED, _PREDICTOR, _LOGGER  #pylint: disable=global-statement
    if _INITIALIZED:
        return
    _PREDICTOR = Predictor.from_path(
        'https://s3-us-west-2.amazonaws.com/allennlp/models/bidaf-model-2017.09.15-charpad.tar.gz'
    )
    _LOGGER = logging.getLogger(__file__)
    _INITIALIZED = True


_ARTICLE_CONTENT_RESPONSE = [
    'I think the answer is', 'I found this in the article',
    'I think this may answer your question', 'This may answer your question'
]

_ARTICLE_CONTENT_CONFIRMATION = [
    'Did that answer your question?', 'Was that able to answer your question?',
    'Was that answer helpful?'
]

_ARTICLE_CONTENT_QUERY_OTHER = [
    'What other questions do you have?',
    'What additional questions do you have?',
    'What else would you like to know?'
]

_ARTICLE_CONTENT_QUERY = [
    'What questions do you have regarding this article?',
    "What would you like to know about this article?"
]


def entrypoint(user_message: UserMessage,
               session_attributes: SessionAttributes,
               memory_dict: Optional[Dict[str, Any]]) -> DialogueStateResult:
    """
    Entrypoint for state QNA

    It can mutate session_attributes or round_attributes
    """
    assert _INITIALIZED

    memory = QnaMemory()
    if memory_dict:
        memory.from_dict(memory_dict)

    bot_message: BotMessage = BotMessage()

    if memory.sub_state == QnaStates.SUMMARIZE:
        bot_message.response_ssml = session_attributes.current_article.summary.replace(
            '\n', ' ')
        bot_message.reprompt_ssml = bot_message.reprompt_ssml = random.choice(
            _ARTICLE_CONTENT_QUERY)
        memory.sub_state = QnaStates.QNA
        return DialogueStateResult(DialogueStates.QNA,
                                   bot_message=bot_message,
                                   memory_dict=memory.to_dict())
    if memory.sub_state == QnaStates.QNA:
        intent = predict_intent(user_message.get_utterance(),
                                IntentDataset.NAVIGATE)
        if intent == 'search':
            return DialogueStateResult(DialogueStates.FIND_ARTICLE)
        elif intent == 'echo_query':
            bot_message = get_echo_query_message(session_attributes)
            bot_message.reprompt_ssml = random.choice(_ARTICLE_CONTENT_QUERY)
            return DialogueStateResult(DialogueStates.QNA,
                                       bot_message=bot_message,
                                       memory_dict=memory.to_dict())
        answer = _PREDICTOR.predict(
            passage=session_attributes.current_article.text,
            question=user_message.get_utterance())
        bot_message.response_ssml = '{}: {}.'.format(
            random.choice(_ARTICLE_CONTENT_RESPONSE), answer['best_span_str'])
        bot_message.reprompt_ssml = random.choice(_ARTICLE_CONTENT_QUERY)
        return DialogueStateResult(DialogueStates.QNA,
                                   bot_message=bot_message,
                                   memory_dict=memory.to_dict())
    raise NotImplementedError(
        'Unknown QNA sub state {}'.format(  #pragma: no cover
            memory.sub_state))
