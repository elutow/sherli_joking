# -*- coding: utf-8 -*-
"""Logic for finding articles in PICK_ARTICLE state"""

from typing import List, Tuple

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

    keyphrases: Tuple[str] = _extract_topics_from_utterance(user_utterance)
    query: str = ' AND '.join("'{}'".format(x) for x in keyphrases)
    session_attributes.queried_articles = _NEWSAPI_CLIENT.get_top_headlines(
        q=query)
    # TODO: Confirmation of going into article
    chosen_article = session_attributes.queried_articles['articles'][0]
    article_parser = Article(
        session_attributes.queried_articles['articles'][0]['url'])
    article_parser.download()
    article_parser.parse()
    article_parser.nlp()
    session_attributes.current_article = {
        'title': chosen_article['title'],
        'text': article_parser.text,
        'keywords': article_parser.keywords,
        'summary': article_parser.summary,
    }
    bot_message.response_ssml = 'I have found an article: {}.'.format(
        chosen_article['title'])

    return DialogueStates.QNA
