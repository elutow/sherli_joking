"""Test sherlibot.dialogue_states.find_article"""

import logging

from hypothesis import given, strategies, settings
import pytest

from slowbro.core.user_message import UserMessage

from sherlibot.dialogue_states import find_article
from sherlibot.dialogue import DialogueStates, DialogueStateResult
from sherlibot.session_attributes import TESTING_URL, SessionAttributes, ProcessedArticle

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

UserMessageStrategy = strategies.builds(UserMessage,
                                        channel=strategies.text(),
                                        request_id=strategies.text(),
                                        session_id=strategies.text(),
                                        user_id=strategies.text(),
                                        text=strategies.text())


class _PseudoNewsAPIClient:  #pylint: disable=too-few-public-methods
    """Pseudo News API client"""

    def __init__(self, data_strategy):
        self._data_strategy = data_strategy

    def get_everything(self, q):  #pylint: disable=unused-argument
        return dict(articles=self._data_strategy.draw(
            strategies.lists(article_candidate_strategy)))


class _PseudoNewsAPIClientContext:
    #pylint: disable=protected-access

    def __init__(self, data_strategy):
        self._data_strategy = data_strategy

    def __enter__(self):
        find_article._NEWSAPI_CLIENT = _PseudoNewsAPIClient(
            self._data_strategy)

    def __exit__(self, *_):
        find_article._NEWSAPI_CLIENT = None


@pytest.fixture(scope='module', autouse=True)
def _pseudo_init_list_articles():
    """Initializes dialogue state with pseudo outputs"""
    #pylint: disable=protected-access
    find_article._LOGGER = logging.getLogger(__file__)
    find_article._INITIALIZED = True


class _PseudoExtractTopicsFromUtterance:
    #pylint: disable=protected-access

    def __init__(self, data_strategy):
        self._orig_func = find_article._extract_topics_from_utterance
        self._data_strategy = data_strategy

    def _pseudo_extract_topics(self, _):
        return self._data_strategy.draw(strategies.lists(strategies.text()))

    def __enter__(self):
        find_article._extract_topics_from_utterance = self._pseudo_extract_topics

    def __exit__(self, *_):
        find_article._extract_topics_from_utterance = self._orig_func


# Disable deadline due to variability in keyphrase extraction
@settings(deadline=None, max_examples=10)
@given(
    strategies.one_of(strategies.just('what is sherlibot'), strategies.text()))
def test_keyprhase_extraction(utterance):
    """Tests keyphrase extraction in _extract_topics_from_utterance"""
    result = find_article._extract_topics_from_utterance(utterance)  #pylint: disable=protected-access
    assert isinstance(result, tuple)


@given(data_strategy=strategies.data(),
       user_message=UserMessageStrategy,
       session_attributes=SessionAttributesStrategy,
       memory_dict=strategies.just(None))
def test_entrypoint(data_strategy, user_message, session_attributes,
                    memory_dict):
    """Test FIND_ARTICLE state"""
    result: DialogueStateResult = DialogueStateResult(
        DialogueStates.FIND_ARTICLE)
    with _PseudoExtractTopicsFromUtterance(
            data_strategy), _PseudoNewsAPIClientContext(data_strategy):
        while result.next_state == DialogueStates.FIND_ARTICLE and not result.bot_message:
            result: DialogueStateResult = find_article.entrypoint(
                user_message=user_message,
                session_attributes=session_attributes,
                memory_dict=memory_dict)
            memory_dict = result.memory_dict
