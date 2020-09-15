import csv
import tweepy
import ssl
import os
import time
import json

ssl._create_default_https_context = ssl._create_unverified_context

# Oauth keys
consumer_key = os.environ.get('consumer_key')
consumer_secret = os.environ.get('consumer_secret')
access_token = os.environ.get('access_token')
access_token_secret = os.environ.get('access_token_secret')

# Authentication with Twitter
auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
api = tweepy.API(auth)

def obj_to_dict(obj):
    tweet_dict = {}
    for attr in vars(obj):
        if not attr.startswith('_'):
            if attr == 'user':
                tweet_dict[attr] = json.dumps(getattr(obj.user, "_json"))
            else:
                tweet_dict[attr] = getattr(obj, attr)
                  
    return tweet_dict


def get_tweets(name):
    replies=[]
    try:
        count = 0
        for tweet in tweepy.Cursor(api.search, q='to:'+name, result_type='recent', auto_populate_reply_metadata=True, wait_on_rate_limit=True, wait_on_rate_limit_notify=True, timeout=99000000).items(5):
            count += 1
            replies.append(tweet)
            
        write_to_csv(replies)
    except Exception as e:
        print(count, e)


def write_to_csv(replies):
    #dict_keys = obj_to_dict(replies[0]).keys()
    dict_keys = ['created_at', 'id', 'id_str', 'text', 'truncated', 'entities', 'metadata', 'source', 'source_url', 'in_reply_to_status_id', 
    'in_reply_to_status_id_str', 'in_reply_to_user_id', 'in_reply_to_user_id_str', 'in_reply_to_screen_name', 'author', 'user', 'geo', 
    'coordinates', 'place', 'contributors', 'is_quote_status', 'quoted_status_id_str', 'quoted_status', 'quoted_status_id', 'possibly_sensitive', 
    'retweeted_status', 'retweet_count', 'favorite_count', 'favorited', 'retweeted', 'lang', 'extended_entities', 'withheld_in_countries']

    with open('replies_clean.csv', 'w', encoding='utf-8', newline='') as f:
        csv_writer = csv.DictWriter(f, fieldnames=dict_keys)

        csv_writer.writeheader()
        for tweet in replies:
            row = obj_to_dict(tweet)
            try:
                csv_writer.writerow(row)
            except Exception as e:
                print(e)


if __name__ == "__main__":
    name = 'realDonaldTrump'
    
    get_tweets(name)