from typing import Dict, Any, List

from .dialogue import DialogueStates


class SessionAttributes():
    """Session attributes.
    """

    def __init__(self,
                 topics: List[str] = list(),
                 dialogue_state: DialogueStates = DialogueStates.INIT,
                 round_index: int = 0) -> None:
        """Constructor."""
        self.topics = topics
        self.round_index = round_index
        # Stores the next state for dialogue management
        self.dialogue_state = dialogue_state

    def to_dict(self) -> Dict[str, Any]:
        json_obj: Dict[str, Any] = {
            'round_index': self.round_index,
            'topics': self.topics,
            'dialogue_state': self.dialogue_state.value,
        }

        return json_obj

    def from_dict(self, json_obj: Dict[str, Any]) -> None:
        self.round_index = json_obj.get('round_index', 0)
        self.topics = json_obj.get('topics', list())
        self.dialogue_state = DialogueStates(
            json_obj.get('dialogue_state', DialogueStates.INIT.value))
