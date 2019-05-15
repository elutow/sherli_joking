import aylien_news_api
from aylien_news_api.rest import ApiException
import json

#############
'''
CATEGORIES - there are 5 categories for this project

Sports, Business, Politics, Technology, Others

User can include one category, currently
User can exclude one category, currently

'''
###

inputcatvar = 'Technology'
inputcatvar = inputcatvar.lower()
excatvar = 'Politics'
excatvar = excatvar.lower()

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
aylien_news_api.configuration.api_key['X-AYLIEN-NewsAPI-Application-ID'] = 'c67c6aac'
# Configure API key authorization: app_key
aylien_news_api.configuration.api_key['X-AYLIEN-NewsAPI-Application-Key'] = '0223546f7c5d669df103843cbec1833f'

# create an instance of the API class
api_instance = aylien_news_api.DefaultApi()

opts = {
  'title': 'trump',
  'text': 'trump',
  'categories_taxonomy': 'iptc-subjectcode',
  'categories_id': incatidvar,
  'not_categories_id': excatidvar,
  'entities_body_text': ['trump'],
  'not_entities_body_text': ['china','usa','obama'],
  'sort_by': 'relevance',
  'language': ['en'],
  'not_language': ['es', 'it'],
  'published_at_start': 'NOW-6MONTHS',
  'published_at_end': 'NOW',
  '_return': ['title','summary','source']
}

try:
    # List stories
    api_response = api_instance.list_stories(**opts)
    print("API called successfully. Returned data: ")
    print("========================================")
    
    numberstories = 50
    written = 0

    for lvar in range(numberstories):
      story = api_response.stories[lvar]
      title = story.title
      summary = story.summary
      source = story.source.name
      if not len(story.summary.sentences)==0:
        written = 1
        print(story.title + " / " + story.source.name)
        print(story.summary)
        break

          #with open('topnewsoutput.json', 'w') as outf:
    #   outf.write(api_response.content)
#  json.dump(api_response.stories,outf)

except ApiException as e:
    print("Exception when calling DefaultApi->list_stories: %sn" % e)

