# -*- coding: utf-8 -*-
"""Logic for finding articles in PICK_ARTICLE state"""

from typing import List, Tuple, Dict, Any
import logging

import pke
from newspaper import Article
from newsapi import NewsApiClient

from slowbro.core.bot_message import BotMessage

from ..dialogue import DialogueStates
from ..round_attributes import RoundAttributes
from ..session_attributes import SessionAttributes
from ..utils import get_config_dir

_NEWSAPI_CLIENT = NewsApiClient(api_key=(get_config_dir() /
                                         'newsapi_key').read_text().strip())
_LOGGER = logging.getLogger(__file__)


def _extract_topics_from_utterance(utterance: str) -> Tuple[str]:
    """Extract keyphrases from utterance"""
    extractor = pke.unsupervised.TopicRank()
    extractor.load_document(input=utterance, language='en')
    extractor.candidate_selection()
    extractor.candidate_weighting()
    keyphrases: List[Tuple[str, float]] = extractor.get_n_best()
    return tuple(x for x, _ in keyphrases)


def entrypoint(session_attributes: SessionAttributes,
               round_attributes: RoundAttributes) -> DialogueStates:
    """
    Entrypoint for state

    It can mutate session_attributes or round_attributes
    """
    bot_message: BotMessage = round_attributes.bot_message
    user_utterance: str = round_attributes.user_message.get_utterance()
    if not user_utterance:
        bot_message.response_ssml = "Sorry, I didn't catc that. Please try again"
        bot_message.reprompt_ssml = "What would you like to search?"
        return DialogueStates.FIND_ARTICLE

    keyphrases: Tuple[str] = _extract_topics_from_utterance(user_utterance)
    if not keyphrases:
        bot_message.response_ssml = "Sorry, I couldn't figure out what you wanted to search. Please try again"
        bot_message.reprompt_ssml = "What would you like to search?"
        return DialogueStates.FIND_ARTICLE
    query: str = ' AND '.join("'{}'".format(x) for x in keyphrases)
    _LOGGER.debug(f'Query: {query}')
    queried_articles: Dict[str, Any] = _NEWSAPI_CLIENT.get_everything(q=query)
    _LOGGER.debug(f'Number of articles: {len(queried_articles["articles"])}')
    # TODO: Confirmation of going into article
    if not queried_articles['articles']:
        bot_message.response_ssml = (
            "Hmm, I couldn't find any articles on {}. "
            "Please try again").format(' and '.join(keyphrases))
        return DialogueStates.FIND_ARTICLE
    chosen_article = queried_articles['articles'][0]
    article_parser = Article(chosen_article['url'])
    article_parser.download()
    article_parser.parse()
    article_parser.nlp()
    session_attributes.current_article = {
        'title': chosen_article['title'],
        'text': article_parser.text,
        'keywords': article_parser.keywords,
        'summary': article_parser.summary,
    }
    session_attributes.queried_articles = queried_articles
    bot_message.response_ssml = 'I have found an article: {}.'.format(
        chosen_article['title'])
    _LOGGER.debug("Article title: {}".format(chosen_article['title']))

    return DialogueStates.QNA
