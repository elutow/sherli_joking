##### Import ####

from allennlp.predictors.predictor import Predictor
import aylien_news_api
from aylien_news_api.rest import ApiException
import json


#### Input variables ######

#usersentence = "Tell me something about Trump's meeting from yesterday excluding his visit to Korea but including his visit to Japan"

#inputcatvar = 'Politics'
#excatvar = 'None'

##### Functions


def querygenerator(usersentence):


    predictor = Predictor.from_path("https://s3-us-west-2.amazonaws.com/allennlp/models/biaffine-dependency-parser-ptb-2018.08.23.tar.gz")
    predresponse = predictor.predict(usersentence)

    wordlist = predresponse['words']
    taglist = predresponse['pos']

    excludewords = ['exclude', 'omit', 'excluded','omitted', 'skipped', 'without', 'but', 'shouldn\'t', 'not',  'skip','excluding','omitting','skipping','except','excepting']
    includewords = ['include','including','included']

    includetags = ['CD','NNS','NN','NNP','NNPS']

    mainwordlist = []
    excludewordlist = []

    excludeflag=0
    for ivar in range(len(wordlist)):
        if excludeflag==0:
            for elvar in excludewords:
                if elvar==wordlist[ivar]:
                    excludeflag=1
                    break
        if excludeflag==1:
            for elvar in includewords:
                if elvar==wordlist[ivar]:
                    excludeflag=0
                    break
        if excludeflag==0:
            for elvar2 in includetags:
                if taglist[ivar]==elvar2:
                    mainwordlist.append(wordlist[ivar])
                    break
        else:
            for elvar3 in includetags:
                if taglist[ivar]==elvar3:
                    excludewordlist.append(wordlist[ivar])
                    break
    
    
    mainwordstr = " OR ".join(mainwordlist)

#    print(mainwordlist)
#    print(excludewordlist)

    return(mainwordstr,mainwordlist,excludewordlist)


def extractnews(usersentence,inputcatvar,excatvar):
    
    mainwordstr,mainwordlist,excludewordlist =  querygenerator(usersentence)


    #############
    '''
        CATEGORIES - there are 5 categories for this project
        
        Sports, Business, Politics, Technology, Others
        
        User can include one category, currently
        User can exclude one category, currently
        
        '''
    ###


    inputcatvar = inputcatvar.lower()
    excatvar = excatvar.lower()
    #excatvar = 'Politics'
    #excatvar = excatvar.lower()

    if inputcatvar == 'sports':
        incatidvar = ['15000000']
    elif inputcatvar == 'business':
        incatidvar = ['04000000']
    elif inputcatvar == 'politics':
        incatidvar = ['11000000']
    elif inputcatvar == 'technology':
        incatidvar = ['13000000']
    else :
        incatidvar = ['01000000','02000000','03000000','04000000','05000000','06000000','07000000','08000000','09000000','10000000','11000000','12000000','13000000','14000000','15000000','16000000','17000000']

    if excatvar == 'sports':
        excatidvar = ['15000000']
    elif excatvar == 'business':
        excatidvar = ['04000000']
    elif excatvar == 'politics':
        excatidvar = ['11000000']
    elif excatvar == 'technology':
        excatidvar = ['13000000']
    else :
        excatidvar = []


    # Configure API key authorization: app_id
    aylien_news_api.configuration.api_key['X-AYLIEN-NewsAPI-Application-ID'] = '8402043d'
    # Configure API key authorization: app_key
    aylien_news_api.configuration.api_key['X-AYLIEN-NewsAPI-Application-Key'] = '10ebc45e35c0c1b6cc32391f5ba5f20d'

    # create an instance of the API class
    api_instance = aylien_news_api.DefaultApi()

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
        '_return': ['title','summary','source']
    }


    # List stories
    api_response = api_instance.list_stories(**opts)
    print("API called successfully. Returned data: ")
    print("========================================")

    titlelist = []
    summarylist = []
    sourcelist = []
    ctrvar = 1
    ctrlimit = 5

    for lvar in range(len(api_response.stories)):
        story = api_response.stories[lvar]
        title = story.title
        summary = story.summary
        source = story.source.name
        if ctrvar>ctrlimit:
            break
        if not len(story.summary.sentences)==0:
            ctrvar = ctrvar+1
            #print(story.title + " / " + story.source.name)
            #print(story.summary)
            titlelist.append(title)
            summarylist.append(summary.sentences)
            sourcelist.append(source)

    return(titlelist,summarylist,sourcelist)



def readingcomprefn( summarylist, userquestion, summaryindex):


    #summarytext = "The Matrix is a 1999 science fiction action film written and directed by The Wachowskis, starring Keanu Reeves, Laurence Fishburne, Carrie-Anne Moss, Hugo Weaving, and Joe Pantoliano."

    #userquestion="Who stars in The Matrix?"
    
    summarytext = ' '.join(summarylist[summaryindex])

    predictor = Predictor.from_path("https://s3-us-west-2.amazonaws.com/allennlp/models/bidaf-model-2017.09.15-charpad.tar.gz")
    answer = predictor.predict(
                      passage= summarytext,
                      question= userquestion
                      )

    return(answer['best_span_str'])




#### USE TITLELIST and read out the titles. the chosen title's index is summary index
#### User question is the input from the user

#summaryindex = 0
#userquestion = "Who is the crown prince?"

#titlelist, summarylist, sourcelist = extractnews(usersentence,inputcatvar,excatvar)
#answer = readingcomprefn(summarylist, userquestion, summaryindex)

