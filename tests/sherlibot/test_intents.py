from hypothesis import given, strategies
import pytest

from sherlibot import intents


@pytest.fixture(scope='session', autouse=True)
def init_intent_detector():
    """Initializes intent detection"""
    intents.initialize()


@given(strategies.sampled_from(intents.IntentDataset))
def test_predict_intent(dataset_enum):
    intents.predict_intent('news about python', dataset_enum)
