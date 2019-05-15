# -*- coding: utf-8 -*-
"""Test sherlibot.round_attributes"""

from hypothesis import given, strategies

from sherlibot.round_attributes import RoundAttributes
from sherlibot.dialogue import DialogueStates

# TODO: Random values for user_message, bot_message
DialogueStatesStrategy = strategies.from_type(DialogueStates)
RoundAttributesStrategy = strategies.builds(
    RoundAttributes,
    dialogue_state=DialogueStatesStrategy,
    round_index=strategies.integers())


@given(RoundAttributesStrategy)
def test_dict_serialization(round_attributes):
    """Test serialization via {to,from}_dict() methods"""
    new_attributes = RoundAttributes()
    new_attributes.from_dict(round_attributes.to_dict())
    assert round_attributes.to_dict() == new_attributes.to_dict()
