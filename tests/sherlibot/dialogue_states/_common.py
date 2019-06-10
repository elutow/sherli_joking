# -*- coding: utf-8 -*-
"""Common test logic code for dialogue states"""

from typing import Optional

from hypothesis import strategies

from sherlibot import intents
from sherlibot.dialogue_states import list_articles


class PseudoPredictIntent:
    def __init__(self, data_strategy):
        self._data = data_strategy
        self._orig_predict = list_articles.predict_intent

    def _pseudo_predict_intent(
            self,
            utterance: str,  #pylint: disable=unused-argument
            dataset_enum: intents.IntentDataset,
            classifier_name: str = intents.DEFAULT_CLASSIFIER  #pylint: disable=unused-argument
    ) -> Optional[str]:
        if dataset_enum == intents.IntentDataset.NAVIGATE:
            return self._data.draw(
                strategies.sampled_from(
                    ('search', 'elaborate', 'echo_query', None)))
        return None

    def __enter__(self):
        list_articles.predict_intent = self._pseudo_predict_intent

    def __exit__(self, *_):
        list_articles.predict_intent = self._orig_predict
