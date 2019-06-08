# -*- coding: utf-8 -*-
"""Test sherlibot.session_attributes"""

from hypothesis import given, strategies

from sherlibot.session_attributes import SessionAttributes, ProcessedArticle
from sherlibot.dialogue import DialogueStates

JsonStrategy = strategies.recursive(
    strategies.none() | strategies.booleans() | strategies.floats()
    | strategies.text(),
    lambda children: strategies.lists(children, 1) | strategies.dictionaries(
        strategies.text(), children, min_size=1),
    max_leaves=5)
SessionAttributesStrategy = strategies.builds(
    SessionAttributes,
    search_topics=strategies.one_of(strategies.none(),
                                    strategies.lists(strategies.text())),
    queried_articles=strategies.one_of(strategies.none(),
                                       strategies.lists(JsonStrategy)),
    current_article=strategies.one_of(
        strategies.none(),
        strategies.builds(ProcessedArticle, strategies.text(), JsonStrategy,
                          strategies.text(),
                          strategies.lists(strategies.text()),
                          strategies.text())),
    current_article_index=strategies.integers(),
    next_round_index=strategies.integers(),
    next_dialogue_state=strategies.sampled_from(DialogueStates))


@given(SessionAttributesStrategy)
def test_dict_serialization(session_attributes):
    """Test serialization via {to,from}_dict() methods"""
    new_attributes = SessionAttributes()
    new_attributes.from_dict(session_attributes.to_dict())
    assert session_attributes.to_dict() == new_attributes.to_dict()
