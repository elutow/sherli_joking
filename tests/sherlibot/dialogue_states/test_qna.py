# -*- coding: utf-8 -*-
"""Test sherlibot.session_attributes"""

import logging

from hypothesis import given, strategies
import pytest

from slowbro.core.user_message import UserMessage

from sherlibot.dialogue_states import qna
from sherlibot.dialogue import DialogueStates, DialogueStateResult
from sherlibot.session_attributes import SessionAttributes, ProcessedArticle

JsonStrategy = strategies.recursive(
    strategies.none() | strategies.booleans() | strategies.floats()
    | strategies.text(),
    lambda children: strategies.lists(children, 1) | strategies.dictionaries(
        strategies.text(), children, min_size=1),
    max_leaves=5)
SessionAttributesStrategy = strategies.builds(
    SessionAttributes,
    #search_topics=strategies.one_of(strategies.none(),
    #                                strategies.lists(strategies.text())),
    #queried_articles=strategies.one_of(strategies.none(),
    #                                   strategies.lists(JsonStrategy)),
    current_article=strategies.builds(ProcessedArticle, strategies.text(),
                                      JsonStrategy, strategies.text(),
                                      strategies.lists(strategies.text()),
                                      strategies.text()),
    #current_article_index=strategies.integers(),
    #next_round_index=strategies.integers(),
    next_dialogue_state=strategies.sampled_from(DialogueStates))
QnaMemoryStrategy = strategies.builds(qna.QnaMemory,
                                      sub_state=strategies.sampled_from(
                                          qna.QnaStates))
UserMessageStrategy = strategies.builds(UserMessage,
                                        channel=strategies.text(),
                                        request_id=strategies.text(),
                                        session_id=strategies.text(),
                                        user_id=strategies.text(),
                                        text=strategies.text())
memory_dict_strategy = strategies.one_of(
    strategies.none(), QnaMemoryStrategy.map(lambda x: x.to_dict()))


class _PseudoPredictor:  #pylint: disable=too-few-public-methods
    """Dummy allennlp.Predictor"""

    @staticmethod
    def predict(passage: str, question: str) -> str:
        return {
            'best_span_str':
            'DUMMY_PREDICTION({}, {})'.format(len(passage), len(question))
        }


@pytest.fixture(scope='module', autouse=True)
def _pseudo_init_qna():
    """Initializes dialogue state with pseudo outputs"""
    #pylint: disable=protected-access
    qna._LOGGER = logging.getLogger(__file__)
    qna._PREDICTOR = _PseudoPredictor()
    qna._INITIALIZED = True


@given(QnaMemoryStrategy)
def test_qnamemory_dict_serialization(memory):
    """Test QnaMemory serialization via {to,from}_dict() methods"""
    new_memory = qna.QnaMemory()
    new_memory.from_dict(memory.to_dict())
    assert memory.to_dict() == new_memory.to_dict()


@given(user_message=UserMessageStrategy,
       session_attributes=SessionAttributesStrategy,
       memory_dict=memory_dict_strategy)
def test_entrypoint(user_message, session_attributes, memory_dict):
    """Test QNA state"""
    result: DialogueStateResult = DialogueStateResult(DialogueStates.QNA)
    while result.next_state == DialogueStates.QNA and not result.bot_message:
        result: DialogueStateResult = qna.entrypoint(
            user_message=user_message,
            session_attributes=session_attributes,
            memory_dict=memory_dict)
        memory_dict = result.memory_dict
