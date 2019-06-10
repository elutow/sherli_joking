"""Test sherlibot.dialogue_states.list_articles"""

import logging

from hypothesis import given, strategies
import pytest

from slowbro.core.user_message import UserMessage

from sherlibot.dialogue import DialogueStates, DialogueStateResult
from sherlibot.dialogue_states import list_articles
from sherlibot.session_attributes import TESTING_URL, SessionAttributes, ProcessedArticle

from ._common import PseudoPredictIntent

article_candidate_strategy = strategies.fixed_dictionaries(
    dict(source=strategies.fixed_dictionaries(
        dict(id=strategies.text(), name=strategies.text())),
         author=strategies.text(),
         title=strategies.text(),
         description=strategies.text(),
         url=strategies.just(TESTING_URL)))


@strategies.composite
def _SessionAttributesStrategy(draw):
    queried_articles = draw(
        strategies.lists(article_candidate_strategy, min_size=1))
    current_article_index = draw(
        strategies.integers(min_value=0, max_value=len(queried_articles) - 1))
    session_attributes = draw(
        strategies.builds(
            SessionAttributes,
            search_topics=strategies.lists(strategies.text(), min_size=1),
            queried_articles=strategies.just(queried_articles),
            current_article=strategies.builds(
                ProcessedArticle, strategies.text(), strategies.none(),
                strategies.text(), strategies.lists(strategies.text()),
                strategies.text()),
            current_article_index=strategies.just(current_article_index),
            #next_round_index=strategies.integers(),
            next_dialogue_state=strategies.sampled_from(DialogueStates)))
    return session_attributes


SessionAttributesStrategy = _SessionAttributesStrategy()  #pylint: disable=no-value-for-parameter

UserMessageStrategy = strategies.builds(
    UserMessage,
    channel=strategies.text(),
    request_id=strategies.text(),
    session_id=strategies.text(),
    user_id=strategies.text(),
    text=strategies.one_of(strategies.just('yes'), strategies.just('no'),
                           strategies.just('what did i search'),
                           strategies.just('get news about python'),
                           strategies.text()))
ListArticleMemoryStrategy = strategies.builds(
    list_articles.ListArticleMemory,
    sub_state=strategies.sampled_from(list_articles.ListArticleStates))
memory_dict_strategy = strategies.one_of(
    strategies.none(), ListArticleMemoryStrategy.map(lambda x: x.to_dict()))


@pytest.fixture(scope='module', autouse=True)
def _pseudo_init_list_articles():
    """Initializes dialogue state with pseudo outputs"""
    #pylint: disable=protected-access
    list_articles._LOGGER = logging.getLogger(__file__)
    list_articles._INITIALIZED = True


@given(ListArticleMemoryStrategy)
def test_list_articles_memory_dict_serialization(memory):
    """Test QnaMemory serialization via {to,from}_dict() methods"""
    new_memory = list_articles.ListArticleMemory()
    new_memory.from_dict(memory.to_dict())
    assert memory.to_dict() == new_memory.to_dict()


@given(data_strategy=strategies.data(),
       user_message=UserMessageStrategy,
       session_attributes=SessionAttributesStrategy,
       memory_dict=memory_dict_strategy)
def test_entrypoint(data_strategy, user_message, session_attributes,
                    memory_dict):
    """Test LIST_ARTICLES state"""
    result: DialogueStateResult = DialogueStateResult(
        DialogueStates.LIST_ARTICLES)
    with PseudoPredictIntent(data_strategy):
        while result.next_state == DialogueStates.LIST_ARTICLES and not result.bot_message:
            result: DialogueStateResult = list_articles.entrypoint(
                user_message=user_message,
                session_attributes=session_attributes,
                memory_dict=memory_dict)
            memory_dict = result.memory_dict
