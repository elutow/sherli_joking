from collections import namedtuple
from typing import Dict, Any, List, Optional

from .dialogue import DialogueStates

TESTING_URL = '_testing'

SubstateMemory = namedtuple('SubstateMemory', ('state', 'memory'),
                            defaults=(None, None))
ProcessedArticle = namedtuple('ProcessedArticle',
                              ('title', 'source', 'text', 'summary'))


class SessionAttributes():
    """Session attributes.
    """

    def __init__(self,
                 query_include_words: Optional[List[str]] = None,
                 query_exclude_words: Optional[List[str]] = None,
                 queried_articles: Optional[List[Any]] = None,
                 current_article: Optional[ProcessedArticle] = None,
                 current_article_index: int = 0,
                 substate_memory: SubstateMemory = SubstateMemory(),
                 next_round_index: int = 0,
                 next_dialogue_state: DialogueStates = DialogueStates.INIT
                 ) -> None:
        """Constructor."""
        if query_include_words:
            self.query_include_words = query_include_words
        else:
            self.query_include_words = list()
        if query_exclude_words:
            self.query_exclude_words = query_exclude_words
        else:
            self.query_exclude_words = list()
        if queried_articles:
            self.queried_articles = queried_articles
        else:
            self.queried_articles = list()
        self.current_article = current_article
        self._current_article_index = current_article_index
        self.substate_memory = substate_memory
        # Stores the next state for dialogue management
        self.next_dialogue_state = next_dialogue_state
        self.next_round_index = next_round_index

    @property
    def article_candidate(self) -> Dict[str, Any]:
        """Returns the current article candidate"""
        return self.queried_articles[self._current_article_index]

    @property
    def current_article_index(self) -> int:
        return self._current_article_index

    @current_article_index.setter
    def current_article_index(self, value: int) -> None:
        if value >= len(self.queried_articles) or value < 0:
            raise IndexError(
                'New article index {} is out of bounds. Total articles: {}'.
                format(value, len(self.queried_articles)))
        self._current_article_index = value
        self.current_article = None

    def update_search(self, include_words, exclude_words,
                      queried_articles) -> None:
        """Updates the search query, clearing out old state info"""
        self.query_include_words = include_words
        self.query_exclude_words = exclude_words
        self.queried_articles = queried_articles
        self.current_article_index = 0
        self.current_article = None

    def update_current_article(self) -> None:
        """Updates current_article with article details"""
        chosen_article = self.queried_articles[self.current_article_index]

        # Store article details
        self.current_article = ProcessedArticle(
            title=chosen_article.title,
            source=chosen_article.source,
            text=' '.join(tuple(chosen_article.summary.sentences)[:3]),
            summary=' '.join(chosen_article.summary.sentences),
        )

    def to_dict(self) -> Dict[str, Any]:
        if self.current_article:
            current_article = self.current_article._asdict()
        else:
            current_article = None
        json_obj: Dict[str, Any] = {
            'queried_articles': self.queried_articles,
            'current_article': current_article,
            '_current_article_index': self._current_article_index,
            'substate_memory': self.substate_memory._asdict(),
            'next_dialogue_state': self.next_dialogue_state.value,
            'next_round_index': self.next_round_index,
        }

        return json_obj

    def from_dict(self, json_obj: Dict[str, Any]) -> None:
        self.queried_articles = json_obj.get('queried_articles', None)
        if json_obj.get('current_article'):
            self.current_article = ProcessedArticle(
                **json_obj['current_article'])
        else:
            self.current_article = None
        self._current_article_index = json_obj.get('_current_article_index', 0)
        self.substate_memory = SubstateMemory(
            **json_obj.get('substate_memory', dict()))
        self.next_dialogue_state = DialogueStates(
            json_obj.get('next_dialogue_state', DialogueStates.INIT.value))
        self.next_round_index = json_obj.get('next_round_index', 0)
