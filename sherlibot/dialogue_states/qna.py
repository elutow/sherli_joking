# -*- coding: utf-8 -*-
"""Logic for QNA state"""

from allennlp.predictors.predictor import Predictor

from slowbro.core.user_message import UserMessage
from slowbro.core.bot_message import BotMessage

from ..round_attributes import RoundAttributes
from ..session_attributes import SessionAttributes
from ..dialogue import DialogueStates

_PREDICTOR = Predictor.from_path(
    'https://s3-us-west-2.amazonaws.com/allennlp/models/bidaf-model-2017.09.15-charpad.tar.gz'
)


def entrypoint(session_attributes: SessionAttributes,
               round_attributes: RoundAttributes) -> DialogueStates:
    """
    Entrypoint for state

    It can mutate session_attributes or round_attributes
    """
    bot_message: BotMessage = round_attributes.bot_message
    user_message: UserMessage = round_attributes.user_message

    answer = _PREDICTOR.predict(
        passage=session_attributes.current_article['text'],
        question=user_message.get_utterance())
    bot_message.response_ssml = 'I think it is: {}.'.format(
        answer['best_span_str'])
    bot_message.reprompt_ssml = 'What other questions do you have?'

    return DialogueStates.QNA
