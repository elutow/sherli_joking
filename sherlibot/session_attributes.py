from collections import namedtuple
from typing import Dict, Any, List, Optional

from newspaper import Article

from .dialogue import DialogueStates

SubstateMemory = namedtuple('SubstateMemory', ('state', 'memory'),
                            defaults=(None, None))
ProcessedArticle = namedtuple(
    'ProcessedArticle', ('title', 'source', 'text', 'keywords', 'summary'))


class SessionAttributes():
    """Session attributes.
    """

    def __init__(self,
                 search_topics: Optional[List[str]] = None,
                 queried_articles: Optional[List[Dict[str, Any]]] = None,
                 current_article: Optional[Dict[str, Any]] = None,
                 current_article_index: int = 0,
                 substate_memory: SubstateMemory = SubstateMemory(state=None,
                                                                  memory=None),
                 next_round_index: int = 0,
                 next_dialogue_state: DialogueStates = DialogueStates.INIT
                 ) -> None:
        """Constructor."""
        if search_topics:
            self.search_topics = search_topics
        else:
            self.search_topics = list()
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
    def current_article_index(self):
        return self._current_article_index

    @current_article_index.setter
    def current_article_index(self, value):
        if value >= len(self.queried_articles) or value < 0:
            raise IndexError(
                'New article index {} is out of bounds. Total articles: {}'.
                format(value, len(self.queried_articles)))
        self._current_article_index = value
        self.current_article = None

    def update_search(self, search_topics, queried_articles) -> None:
        """Updates the search query, clearing out old state info"""
        self.search_topics = search_topics
        self.queried_articles = queried_articles
        self.current_article_index = 0
        self.current_article = None

    def update_current_article(self) -> None:
        """Updates current_article with article details"""
        chosen_article = self.queried_articles[self.current_article_index]
        article_parser = Article(chosen_article['url'])
        article_parser.download()
        article_parser.parse()
        article_parser.nlp()

        # Store article details
        self.current_article = ProcessedArticle(
            title=chosen_article['title'],
            source=chosen_article['source'],
            text=article_parser.text,
            keywords=article_parser.keywords,
            summary=article_parser.summary,
        )

    def to_dict(self) -> Dict[str, Any]:
        json_obj: Dict[str, Any] = {
            'search_topics': self.search_topics,
            'queried_articles': self.queried_articles,
            'current_article': self.current_article._asdict(),
            '_current_article_index': self._current_article_index,
            'substate_memory': self.substate_memory._asdict(),
            'next_dialogue_state': self.next_dialogue_state.value,
            'next_round_index': self.next_round_index,
        }

        return json_obj

    def from_dict(self, json_obj: Dict[str, Any]) -> None:
        self.search_topics = json_obj.get('search_topics', list())
        self.queried_articles = json_obj.get('queried_articles', None)
        if 'current_article' in json_obj:
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
