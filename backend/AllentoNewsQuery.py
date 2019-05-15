from allennlp.predictors.predictor import Predictor

sentence = "Tell me something about Trump's meeting from yesterday excluding his visit to Korea but including his visit to Japan"

predictor = Predictor.from_path("https://s3-us-west-2.amazonaws.com/allennlp/models/biaffine-dependency-parser-ptb-2018.08.23.tar.gz")
predresponse = predictor.predict(sentence)

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

print(mainwordlist)
print(excludewordlist)

