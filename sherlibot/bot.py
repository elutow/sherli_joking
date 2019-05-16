from typing import Dict, Any, Tuple
import logging

from slowbro.core.bot_base import BotBase
from slowbro.core.round_saver import DynamoDbRoundSaverAdapter
from slowbro.core.user_message import UserMessage
from slowbro.core.bot_message import BotMessage

from .session_attributes import SessionAttributes
from .round_attributes import RoundAttributes
from .dialogue import DialogueStates
from . import dialogue_states

_LOGGER = logging.getLogger(__file__)


class Bot(BotBase):
    """Sherli Joking bot implementation.
    """

    def __init__(self, dynamodb_table_name: str,
                 dynamodb_endpoint_url: str) -> None:
        """Constructor."""

        # TODO: Move local session data to DynamoDb
        # session_id -> SessionAttributes
        self._local_session_attributes = dict()

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

        # =====================
        # Step 1: Initialization
        # =====================
        bot_message = BotMessage()

        # TODO: Determine what to do with session attributes from ASK
        #session_attributes = SessionAttributes()
        #if ser_session_attributes:
        #    session_attributes.from_dict(ser_session_attributes)
        session_attributes = self._local_session_attributes.setdefault(
            user_message.session_id, SessionAttributes())

        current_state: DialogueStates = session_attributes.next_dialogue_state

        round_attributes = RoundAttributes(
            round_index=session_attributes.next_round_index,
            dialogue_state=current_state,
            user_message=user_message,
            bot_message=bot_message)

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
                next_state = dialogue_states.find_article.entrypoint(
                    session_attributes, round_attributes)
            elif current_state == DialogueStates.QNA:
                next_state = dialogue_states.qna.entrypoint(
                    session_attributes, round_attributes)
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
        ser_round_attributes = round_attributes.to_dict()

        # =====================
        # Step 6: Finalizes session attributes
        # =====================
        session_attributes.next_round_index = round_attributes.round_index + 1
        session_attributes.next_dialogue_state = next_state
        # TODO: Determine what to do with session attributes from ASK
        #ser_session_attributes = session_attributes.to_dict()
        ser_session_attributes = dict()

        return (round_attributes.round_index, ser_round_attributes,
                round_attributes.bot_message, ser_session_attributes)
