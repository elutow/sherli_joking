from typing import Dict, Any, Tuple, Optional
import logging
import random

from slowbro.core.bot_base import BotBase
from slowbro.core.round_saver import DynamoDbRoundSaverAdapter
from slowbro.core.user_message import UserMessage
from slowbro.core.bot_message import BotMessage

from .session_attributes import SessionAttributes, SubstateMemory
from .round_attributes import RoundAttributes
from .dialogue import DialogueStates, DialogueStateResult
from . import dialogue_states, intents

_LOGGER = logging.getLogger(__file__)

sherli_intro_1 = ['Hi,', 'Hello,', 'Greetings,']
shelri_intro_2 = ["I'm Sherli.", 'Sherli here.', 'this is Sherli.']

query_list_1 = ['news', 'news topics', 'news subject']
query_list_2 = [
    'would you like to hear about?', 'are you interested in?',
    'would you like to know more about?'
]


def _generate_bot_response(user_message: UserMessage, state: DialogueStates,
                           session_attributes: SessionAttributes
                           ) -> Tuple[BotMessage, DialogueStates]:
    """
    Accepts a user's utterance for a new turn and returns a response

    The internal state machine will follow next states until a valid BotMessage
        is returned by a state.

    Returns BotMessage for the response, and a DialogueStates value
        for the dialogue state in the next turn.
    """
    bot_message: Optional[BotMessage] = None
    _LOGGER.debug('Processing user utterance: %s',
                  repr(user_message.get_utterance()))
    while bot_message is None:
        _LOGGER.debug('Entering state: %s', repr(state))
        if state == DialogueStates.INIT:
            bot_message = BotMessage()
            bot_message.response_ssml = "{} {} What {} {}".format(
                random.choice(sherli_intro_1), random.choice(shelri_intro_2),
                random.choice(query_list_1), random.choice(query_list_2))

            bot_message.reprompt_ssml = "What {} {}".format(
                random.choice(query_list_1), random.choice(query_list_2))

            state = DialogueStates.FIND_ARTICLE
        else:
            user_utterance = user_message.get_utterance()
            if user_utterance in ('stop', 'halt', 'quit', 'exit', ''):
                bot_message = BotMessage()
                bot_message.should_end_session = True
            else:
                state_result: DialogueStateResult
                if (session_attributes.substate_memory.state
                        and session_attributes.substate_memory.state != state):
                    session_attributes.substate_memory = SubstateMemory()
                memory_dict: Optional[
                    Dict[str, Any]] = session_attributes.substate_memory.memory
                if state == DialogueStates.FIND_ARTICLE:
                    state_result = dialogue_states.find_article.entrypoint(
                        user_message, session_attributes, memory_dict)
                elif state == DialogueStates.LIST_ARTICLES:
                    state_result = dialogue_states.list_articles.entrypoint(
                        user_message, session_attributes, memory_dict)
                elif state == DialogueStates.QNA:
                    state_result = dialogue_states.qna.entrypoint(
                        user_message, session_attributes, memory_dict)
                else:
                    raise NotImplementedError(f'Unknown state: {state}')
                bot_message = state_result.bot_message
                state = state_result.next_state
                session_attributes.substate_memory = SubstateMemory(
                    state=state, memory=state_result.memory_dict)
        _LOGGER.debug('Exited state. Next state: %s', repr(state))
        if bot_message:
            _LOGGER.debug(
                'Bot response: %s, (Reprompt: %s)',
                repr(getattr(bot_message, 'response_ssml',
                             '(NOT AN ATTRIBUTE')),
                repr(
                    getattr(bot_message, 'reprompt_ssml',
                            '(NOT AN ATTRIBUTE)')))
        else:
            _LOGGER.debug('No bot response returned by state.')
    # Ensure a break statement didn't get us here
    assert bot_message is not None
    _LOGGER.debug('Sending bot message')
    return bot_message, state


class Bot(BotBase):
    """Sherli Joking bot implementation.
    """

    def __init__(self, dynamodb_table_name: str,
                 dynamodb_endpoint_url: str) -> None:
        """Constructor."""

        # Initialize dialogue management utilities if not already initialized
        _LOGGER.info('Initializing modules...')
        dialogue_states.find_article.initialize()
        dialogue_states.list_articles.initialize()
        dialogue_states.qna.initialize()
        intents.initialize()
        _LOGGER.info('Done initializing modules.')

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
        session_attributes = self._local_session_attributes.setdefault(
            user_message.session_id, SessionAttributes())

        current_state: DialogueStates = session_attributes.next_dialogue_state

        # =====================
        # Step 2: Generates the bot response
        # =====================
        next_state: DialogueStates
        bot_message: BotMessage
        bot_message, next_state = _generate_bot_response(
            user_message, current_state, session_attributes)

        # =====================
        # Step 3: Stores round attributes
        # =====================
        round_attributes = RoundAttributes(
            round_index=session_attributes.next_round_index,
            user_message=user_message,
            bot_message=bot_message)

        ser_round_attributes = round_attributes.to_dict()

        # =====================
        # Step 6: Finalizes session attributes
        # =====================
        session_attributes.next_round_index = round_attributes.round_index + 1
        session_attributes.next_dialogue_state = next_state
        # We do not send session attributes to ASK due to its size
        ser_session_attributes = None

        return (round_attributes.round_index, ser_round_attributes,
                round_attributes.bot_message, ser_session_attributes)
