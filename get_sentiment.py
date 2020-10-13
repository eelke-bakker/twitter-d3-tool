import numpy as np
import pandas as pd

#from nltk
import nltk
#from nltk.tokenize import word_tokenize
from nltk.tokenize import RegexpTokenizer
from nltk.corpus import stopwords
from nltk.tokenize import TweetTokenizer
from textblob import TextBlob
from nltk.stem.wordnet import WordNetLemmatizer
from prettytable import PrettyTable
from collections import Counter

sw            = stopwords.words('english')
lemma         = WordNetLemmatizer()

import re
import string
import os
import pickle

pd.options.display.max_colwidth = 400
pd.options.display.max_rows = 100

#This cleans and tokenizes an individual tweet
def clean_text_and_tokenize(line):
    line   = re.sub(r'\$\w*', '', line)  # Remove tickers
    line   = re.sub(r'http?:.*$', '', line)
    line   = re.sub(r'https?:.*$', '', line)
    line   = re.sub(r'pic?.*\/\w*', '', line)
    line   = re.sub(r'[' + string.punctuation + ']+', ' ', line)  # Remove puncutations like 's
    
    tokens = TweetTokenizer(strip_handles=True, reduce_len=True).tokenize(line)
    tokens = [w.lower() for w in tokens if w not in sw and len(w) > 2 and w.isalpha()]
    tokens = [lemma.lemmatize(word) for word in tokens]
    
    return tokens

def clean_tweet(tweet):
    return " ".join(clean_text_and_tokenize(tweet))

# This gets a list of words (cleaned) from different lines
def getCleanedWords(lines):
    words = []
    
    for line in lines:
        words += clean_text_and_tokenize(line)
    return words

#this performs a basic sentiment analysis on list of tweets (Series)
def sentiment_analysis_basic(tweets):
    positive_tweets = 0
    neutral_tweets  = 0
    negative_tweets = 0

    for tweet in tweets:
        analysis  = TextBlob(tweet)
        sentiment = analysis.sentiment.polarity

        if sentiment > 0:
            positive_tweets += 1
        elif sentiment == 0:
            neutral_tweets += 1
        else:
            negative_tweets += 1
    total_tweets_analysed      = positive_tweets + neutral_tweets + negative_tweets
    positive_tweets_percentage = positive_tweets / total_tweets_analysed * 100
    neutral_tweets_percentage  = neutral_tweets  / total_tweets_analysed * 100

    #print("No. of positive tweets = {} Percentage = {}".format(positive_tweets, positive_tweets_percentage))
    #print("No. of neutral tweets  = {} Percentage = {}".format(neutral_tweets, neutral_tweets_percentage))
    #print("No. of negative tweets = {} Percentage = {}".format(negative_tweets, 100 - (positive_tweets_percentage neutral_tweets_percentage)))

def sentiment_calc(text):
    try:
        return TextBlob(text).sentiment
    except:
        return None

def get_word_statistics(filepath):
    #This reads the data
    data = pd.read_csv(filepath)
    data['tomatch'] = data.index
    
    #This uses textBlob to get the sentiment
    sent_obj = data['text'].apply(sentiment_calc)
    data['polarity'], data['subjectivity'] = zip(*sent_obj)
    conditions = [
        data['polarity'] > 0,
        data['polarity'] < 0,
        data['polarity'] == 0
        ]

    outputs = ['positive', 'negative','no value']

    data['sentiment'] = np.select(conditions, outputs)
    
    #Get clean version of the tweets
    cleaned_comment_text = []
    for row in data['text']:
        cleaned_comment_text.append(clean_tweet(row))
     
    data['cleaned_comment_text'] = cleaned_comment_text
    # Make dataset long
    s = data['cleaned_comment_text'].str.split(' ').apply(pd.Series, 1).stack()
    s.index = s.index.droplevel(-1)
    words_data = pd.DataFrame(s)
    words_data['tomatch'] = words_data.index
    words_data.columns = ['word','tomatch']
    
    print(words_data)
    #del data['cleaned_comment_text']
    data = pd.merge(words_data, data, on='tomatch', how='left')
    
    grouped = data.groupby('word', as_index=False).agg({'polarity':['mean','count'], 'subjectivity':'mean'})
    grouped.columns = ['word','polarity','count','subjectivity']
    
    return grouped