# Python 3 compatibility
from __future__ import unicode_literals
from __future__ import division
from __future__ import absolute_import
from __future__ import print_function
from __future__ import with_statement
from __future__ import unicode_literals

import codecs
import nltk
import csv

import tokenizer
import PreProcess
from nltk import ConfusionMatrix




class LexiconClassifier(object):

    
    def __init__(self):
        self.dictionary = self.read_opinionlex()
        self.negation_words = self.read_negation_words()
        self.sentiment_hashtags = self.read_sentiment_hashtags()
        
        self.window = 4

    
    def read_opinionlex(self):

        # read positive words
        with codecs.open('/home/aman/Desktop/TwitterHybridClassifier/Data/Lexicon/opinion-lexicon-English/positive-words.txt', 'r', encoding='utf8') as f:
            words = f.read().splitlines()
        pos_words = [w for w in words if not w.startswith(';')]
        pos_words.remove('')
        positive_words = {k:1 for k in pos_words}

        # read negative words
        with codecs.open('/home/aman/Desktop/TwitterHybridClassifier/Data/Lexicon/opinion-lexicon-English/negative-words.txt', 'r', encoding='utf8') as f:
            words = f.read().splitlines()
        neg_words = [w for w in words if not w.startswith(';')]
        neg_words.remove('')
        negative_words = {k:-1 for k in neg_words}

        # Dict in the format: {word:polarity, ...}
        dictionary = dict()
        dictionary.update(positive_words)
        dictionary.update(negative_words)

        return dictionary

    def read_negation_words(self):
        with codecs.open('/home/aman/Desktop/TwitterHybridClassifier/Data/Lexicon/negating_word_list.txt', 'r',encoding='utf8') as f:
            negation_words = f.read().splitlines()
        return negation_words

    def read_sentiment_hashtags(self):
        with codecs.open('/home/aman/Desktop/TwitterHybridClassifier/Data/Lexicon/NRC-Hashtag-Sentiment-Lexicon-v0.1/sentimenthashtags.txt', 'r', encoding='utf8') as f:
            hashtags = f.read().splitlines()
        sentiment_hashs = dict()
        for hashtag in hashtags:
            l = hashtag.split('\t')
            sentiment_hashs[l[0]] = l[1]
        return sentiment_hashs

    
    # Returns a tuple with (num_of_positive_words, num_of_negative_words)
    def classify(self, tweet_tokens):
        pos_so = 0
        neg_so = 0
        # the index of the negation word in tweet_message
        neg_word = -1
        # get only the words
        tweet_tokens = [w.lower() for w,tag in tweet_tokens]

        # look for sentiment words in tweet
        for i,w in enumerate(tweet_tokens):
            # search for hashtags
            # it is a better signal for polarity than common sentiment words in tweet
            if w[0] == '#':
                if w[1:] in self.sentiment_hashtags:
                    if self.sentiment_hashtags[w[1:]] == 'positive':
                        pos_so += 2
                    elif self.sentiment_hashtags[w[1:]] == 'negative':
                        neg_so += -2
                    continue
            # found negation context
            if w in self.negation_words:
                neg_word = i
            # found a sentiment word
            elif w in self.dictionary:
                # get polarity
                so_w = self.dictionary[w]
                # flip polarity if there is a previous negation word
                if neg_word != -1 and i - neg_word  <= self.window:
                    neg_word = -1
                    so_w *= -1
                # add SO calculated to compound tweet polarity
                if so_w == 1:
                    pos_so += 1
                else:
                    neg_so += -1

            
        
        return (pos_so,neg_so)
