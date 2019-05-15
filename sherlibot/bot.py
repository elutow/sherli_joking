from typing import Dict, Any, Tuple
import os
import logging

import pke

from slowbro.core.bot_base import BotBase
from slowbro.core.round_saver import DynamoDbRoundSaverAdapter
from slowbro.core.user_message import UserMessage
from slowbro.core.bot_message import BotMessage

from .rasa_nlu_annotate import rasa_nlu_annotate
from .session_attributes import SessionAttributes
from .round_attributes import RoundAttributes
from .dialogue import DialogueStates

logger = logging.getLogger(__file__)


def _update_session_attributes(round_attributes: RoundAttributes
                               ) -> SessionAttributes:
    """Updates the session attributes.

    Because the session attributes are created from the round attributes, we do
    NOT need to save the session attributes separately to DynamoDB.
    """
    session_attributes = SessionAttributes(
        dialogue_state=next_state, round_index=round_attributes.round_index)

    return session_attributes


def _extract_topics_from_utterance(utterance: str) -> Tuple[str]:
    """Extract keyphrases from utterance"""
    extractor = pke.unsupervised.TopicRank()
    extractor.load_document(input=utterance, language='en')
    extractor.candidate_selection()
    extractor.candidate_weighting()
    keyphrases: List[Tuple[str, float]] = extractor.get_n_best()
    return tuple(x for x, _ in keyphrases)


class Bot(BotBase):
    """Sherli Joking bot implementation.
    """

    def __init__(self, dynamodb_table_name: str,
                 dynamodb_endpoint_url: str) -> None:
        """Constructor."""

        round_saver_adapter = DynamoDbRoundSaverAdapter(
            table_name=dynamodb_table_name, endpoint_url=dynamodb_endpoint_url)
        super().__init__(round_saver_adapter=round_saver_adapter, )

    def _handle_message_impl(
            self, user_message: UserMessage,
            ser_session_attributes: Dict[str, Any]
    ) -> Tuple[int, Dict[str, Any], BotMessage, Dict[str, Any]]:
        """Implementation of the message handling logic.

        Incrementally populates the round_attributes.
        """

        session_attributes = SessionAttributes()
        if ser_session_attributes:
            session_attributes.from_dict(ser_session_attributes)

        # =====================
        # Step 1: Initialization
        # =====================
        if session_attributes.round_index is None:
            raise Exception('undefined round_index in session_attributes')

        # restores the session data
        # if session_attributes.round_index > 0:

        bot_message = BotMessage()
        current_state: DialogueStates = session_attributes.dialogue_state

        # =====================
        # Step 2: Generates the bot response
        # =====================
        next_state: DialogueStates
        bot_message.should_end_session = False
        if current_state == DialogueStates.INIT:
            bot_message.response_ssml = 'Hi, this is Sherli. What news would you like?'
            bot_message.reprompt_ssml = 'What topics are you interested in?'
            next_state = DialogueStates.FIND_ARTICLE
        else:
            user_utterance = user_message.get_utterance()
            if user_utterance == 'stop':
                bot_message.should_end_session = True
                # Choice of state is arbitrary
                next_state = DialogueStates.INIT
            elif current_state == DialogueStates.FIND_ARTICLE:
                keyphrases: Tuple[str] = _extract_topics_from_utterance(
                    user_utterance)
                # TODO: Query news API
            elif current_state == DialogueStates.PICK_ARTICLE:
                # TODO
                pass
            elif current_state == DialogueStates.QA:
                # TODO
                pass
            else:
                raise NotImplementedError(f'Unknown state: {current_state}')
            # queries the RASA-NLU server
            #rasa_nlu_response = rasa_nlu_annotate(
            #    text=user_utterance,
            #    rasa_nlu_url='http://localhost:5000',
            #    project='current',
            #    model=None
            #)
            #bot_message.response_ssml = 'The recognized intent is {} with confidence score {}.'.format(
            #    rasa_nlu_response.intent.name,
            #    rasa_nlu_response.intent.confidence
            #)
            #bot_message.reprompt_ssml = 'There are {} recognized entities.'.format(
            #    len(rasa_nlu_response.entities)
            #)
            #bot_message.should_end_session = False

        # =====================
        # Step 3: Stores round attributes
        # =====================
        round_attributes = RoundAttributes(
            # increment the round index
            round_index=session_attributes.round_index + 1,
            dialogue_state=next_state,
            user_message=user_message,
            bot_message=bot_message)
        ser_round_attributes = round_attributes.to_dict()
        del ser_round_attributes['round_index']

        # =====================
        # Step 6: Finalizes session attributes
        # =====================
        session_attributes = _update_session_attributes(round_attributes)
        ser_session_attributes = session_attributes.to_dict()

        return (round_attributes.round_index, ser_round_attributes,
                round_attributes.bot_message, ser_session_attributes)
