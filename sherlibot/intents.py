# -*- coding: utf-8 -*-
"""Intent detection helper code"""

from typing import Tuple, Any, List, Optional, Dict
from pathlib import Path
import enum
import logging

import know_your_intent

from .utils import AutoName

# Constants
_MODELS_DIR = Path(__file__).resolve().parent.parent / 'intent_models'

# Runtime module state
_MODELS = dict()
# Model params: tuple(classifier_name, threshold)
_MODEL_PARAMS: Dict[Any, Tuple[str, float]] = None
_LOGGER = None
_INITIALIZED = False


class IntentDataset(AutoName):
    """Available intent models"""
    NAVIGATE = enum.auto()


def initialize():
    """
    Initializes services needed by this module
    """
    know_your_intent.initialize()
    global _INITIALIZED, _MODEL_PARAMS, _LOGGER  #pylint: disable=global-statement
    _LOGGER = logging.getLogger(__file__)
    _MODEL_PARAMS = {
        IntentDataset.NAVIGATE: ('LogisticRegression', 0.75),
    }
    _INITIALIZED = True


def get_model(dataset_name: str
              ) -> Tuple[List[Tuple[Any, str]], Any, List[str]]:
    """
    Loads and returns pre-trained models for the given dataset
    """
    assert _INITIALIZED
    if dataset_name not in _MODELS:
        _MODELS[dataset_name] = know_your_intent.load_models(
            dataset_name, models_prefix=_MODELS_DIR)
    return _MODELS[dataset_name]


def clf_by_name(classifiers: List[Tuple[Any, str]],
                classifier_name: str) -> Any:
    """Return classifier object with the associated name"""
    assert _INITIALIZED
    for clf, name in classifiers:
        if name == classifier_name:
            return clf
    raise ValueError(f'Cannot find classifier with name: {classifier_name}')


def predict_intent(utterance: str,
                   dataset_enum: IntentDataset) -> Optional[str]:
    """
    Predict the intent of an utterance. Uses pre-trained models traiend on dataset
        dataset_name

    Returns the most likely intent, and a dictionary of intent probabilities
    """
    assert _INITIALIZED
    dataset_name = dataset_enum.value
    classifiers, vectorizer, target_names = get_model(dataset_name)
    vectorized_utterance = know_your_intent.get_vectorized_utterance(
        utterance, vectorizer)
    classifier_name, prob_threshold = _MODEL_PARAMS[dataset_enum]
    clf = clf_by_name(classifiers, classifier_name)
    intent, intent_probs = know_your_intent.predict_intent(
        vectorized_utterance, clf, target_names)
    if intent_probs[intent] >= prob_threshold:
        _LOGGER.debug('Predicted intent "%s" for utterance "%s"', intent,
                      utterance)
        return intent
    _LOGGER.debug('No intents matching threshold for utterance "%s"',
                  utterance)
    return None
