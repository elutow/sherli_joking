from allennlp.predictors.predictor import Predictor

summarytext = "The Matrix is a 1999 science fiction action film written and directed by The Wachowskis, starring Keanu Reeves, Laurence Fishburne, Carrie-Anne Moss, Hugo Weaving, and Joe Pantoliano."

userquestion="Who stars in The Matrix?"

predictor = Predictor.from_path("https://s3-us-west-2.amazonaws.com/allennlp/models/bidaf-model-2017.09.15-charpad.tar.gz")
answer = predictor.predict(
                  passage= summarytext,
                  question= userquestion
                  )

print(answer['best_span_str'])
