# -*- coding: utf-8 -*-
"""
Downloads the necessary NLTK models and corpora required for all modules

Modification of https://raw.githubusercontent.com/codelucas/newspaper/76956d28dcc005c0a9e5bef4be1a2a55e2159698/download_corpora.py
"""
import nltk
import spacy


NLTK_REQUIRED_CORPORA = [
    'brown',  # Required for FastNPExtractor in newspaper3k
    'punkt',  # Required for WordTokenizer in newspaper3k
    'maxent_treebank_pos_tagger',  # Required for NLTKTagger in newspaper3k
    'movie_reviews',  # Required for NaiveBayesAnalyzer in newspaper3k
    'wordnet',  # Required for lemmatization and Wordnet in newspaper3k
    'universal_target', # Required by pke
    'stopwords' # Required by newspaper3k and pke
]

def main():
    print("Downloading nltk corpora...")
    for corpus in NLTK_REQUIRED_CORPORA:
        print(('Downloading "{0}"'.format(corpus)))
        nltk.download(corpus)

    print("Downloading spacy en corpus...")
    spacy.cli.download("en")

    print("Finished.")

if __name__ == '__main__':
    main()
