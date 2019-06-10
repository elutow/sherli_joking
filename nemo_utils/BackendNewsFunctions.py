# -*- coding: utf-8 -*-
"""Modules for search query extraction and Aylien"""

import json

from allennlp.predictors.predictor import Predictor
import aylien_news_api
from aylien_news_api.rest import ApiException

from sherlibot.utils import get_config_dir

#### Input variables ######

#user_sentence = "Tell me something about Trump's meeting from yesterday excluding his visit to Korea but including his visit to Japan"

#include_category = 'Politics'
#exclude_category = 'None'

##### Functions

# Runtime utilities
_DEPENDENCY_PARSER = None
_AYLIEN_API = None
_INITIALIZED = False


def initialize():
    """Initializes utilities"""
    global _INITIALIZED, _DEPENDENCY_PARSER, _AYLIEN_API
    if _INITIALIZED:
        return

    _DEPENDENCY_PARSER = Predictor.from_path(
        "https://s3-us-west-2.amazonaws.com/allennlp/models/biaffine-dependency-parser-ptb-2018.08.23.tar.gz"
    )

    # Configure API key authorization: app_id
    aylien_news_api.configuration.api_key[
        'X-AYLIEN-NewsAPI-Application-ID'] = (
            get_config_dir() / 'aylien_app_id').read_text().strip()
    # Configure API key authorization: app_key
    aylien_news_api.configuration.api_key[
        'X-AYLIEN-NewsAPI-Application-Key'] = (
            get_config_dir() / 'aylien_app_key').read_text().strip()
    # Instantiate API
    _AYLIEN_API = aylien_news_api.DefaultApi()

    _INITIALIZED = True


def generate_query(user_sentence):

    assert _INITIALIZED

    predresponse = _DEPENDENCY_PARSER.predict(user_sentence)

    wordlist = predresponse['words']
    taglist = predresponse['pos']

    excludewords = [
        'exclude', 'omit', 'excluded', 'omitted', 'skipped', 'without', 'but',
        'shouldn\'t', 'not', 'skip', 'excluding', 'omitting', 'skipping',
        'except', 'excepting'
    ]
    includewords = ['include', 'including', 'included']

    includetags = ['CD', 'NNS', 'NN', 'NNP', 'NNPS']

    mainwordlist = []
    excludewordlist = []

    excludeflag = 0
    for ivar in range(len(wordlist)):
        if excludeflag == 0:
            for elvar in excludewords:
                if elvar == wordlist[ivar]:
                    excludeflag = 1
                    break
        if excludeflag == 1:
            for elvar in includewords:
                if elvar == wordlist[ivar]:
                    excludeflag = 0
                    break
        if excludeflag == 0:
            for elvar2 in includetags:
                if taglist[ivar] == elvar2:
                    mainwordlist.append(wordlist[ivar])
                    break
        else:
            for elvar3 in includetags:
                if taglist[ivar] == elvar3:
                    excludewordlist.append(wordlist[ivar])
                    break

    mainwordstr = " OR ".join(mainwordlist)

    return mainwordstr, mainwordlist, excludewordlist


def extract_news(user_sentence, include_category='', exclude_category=''):

    assert _INITIALIZED

    mainwordstr, mainwordlist, excludewordlist = generate_query(user_sentence)

    #############
    '''
        CATEGORIES - there are 5 categories for this project
        
        Sports, Business, Politics, Technology, Others
        
        User can include one category, currently
        User can exclude one category, currently
        
        '''
    ###

    include_category = include_category.lower()
    exclude_category = exclude_category.lower()

    if include_category == 'sports':
        incatidvar = ['15000000']
    elif include_category == 'business':
        incatidvar = ['04000000']
    elif include_category == 'politics':
        incatidvar = ['11000000']
    elif include_category == 'technology':
        incatidvar = ['13000000']
    else:
        incatidvar = [
            '01000000', '02000000', '03000000', '04000000', '05000000',
            '06000000', '07000000', '08000000', '09000000', '10000000',
            '11000000', '12000000', '13000000', '14000000', '15000000',
            '16000000', '17000000'
        ]

    if exclude_category == 'sports':
        excatidvar = ['15000000']
    elif exclude_category == 'business':
        excatidvar = ['04000000']
    elif exclude_category == 'politics':
        excatidvar = ['11000000']
    elif exclude_category == 'technology':
        excatidvar = ['13000000']
    else:
        excatidvar = []

    opts = {
        'title': mainwordstr,
        'text': mainwordstr,
        'categories_taxonomy': 'iptc-subjectcode',
        'categories_id': incatidvar,
        'not_categories_id': excatidvar,
        'entities_body_text': mainwordlist,
        'not_entities_body_text': excludewordlist,
        'sort_by': 'relevance',
        'language': ['en'],
        'not_language': ['es', 'it'],
        'published_at_start': 'NOW-6MONTHS',
        'published_at_end': 'NOW',
        '_return': ['title', 'summary', 'source']
    }

    api_response = _AYLIEN_API.list_stories(**opts)

    return tuple(api_response.stories)


#### USE TITLELIST and read out the titles. the chosen title's index is summary index
#### User question is the input from the user

#summaryindex = 0
#userquestion = "Who is the crown prince?"

#titlelist, summarylist, sourcelist = extract_news(user_sentence,include_category,exclude_category)
#answer = readingcomprefn(summarylist, userquestion, summaryindex)
