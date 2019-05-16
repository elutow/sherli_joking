from typing import Dict, Any, List, Optional

from .dialogue import DialogueStates


class SessionAttributes():
    """Session attributes.
    """

    def __init__(self,
                 topics: Optional[List[str]] = None,
                 queried_articles: Optional[Dict[str, Any]] = None,
                 current_article: Optional[Dict[str, Any]] = None,
                 next_round_index: int = 0,
                 next_dialogue_state: DialogueStates = DialogueStates.INIT
                 ) -> None:
        """Constructor."""
        if topics:
            self.topics = topics
        else:
            self.topics = list()
        if queried_articles:
            self.queried_articles = queried_articles
        else:
            self.queried_articles = dict()
        if current_article:
            self.current_article = current_article
        else:
            self.current_article = current_article
        # Stores the next state for dialogue management
        self.next_dialogue_state = next_dialogue_state
        self.next_round_index = next_round_index

    def to_dict(self) -> Dict[str, Any]:
        json_obj: Dict[str, Any] = {
            'topics': self.topics,
            'queried_articles': self.queried_articles,
            'current_article': self.current_article,
            'next_dialogue_state': self.next_dialogue_state.value,
            'next_round_index': self.next_round_index,
        }

        return json_obj

    def from_dict(self, json_obj: Dict[str, Any]) -> None:
        self.topics = json_obj.get('topics', list())
        self.queried_articles = json_obj.get('queried_articles', None)
        self.current_article = json_obj.get('current_article', None)
        self.next_dialogue_state = DialogueStates(
            json_obj.get('next_dialogue_state', DialogueStates.INIT.value))
        self.next_round_index = json_obj.get('next_round_index', 0)
