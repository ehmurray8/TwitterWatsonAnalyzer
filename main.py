from twitter import Twitter, OAuth
from collections import namedtuple
from keys import *
from watson_data import ContentItem
from typing import List, Dict
from datetime import datetime
import time
import json


def get_tweets_string(screen_name: str) -> namedtuple:
    oauth = OAuth(TWITTER_ACCESS_TOKEN, TWITTER_ACCESS_SECRET, TWITTER_CONSUMER_KEY, TWITTER_CONSUMER_SECRET)
    twitter = Twitter(auth=oauth)
    tweets = twitter.statuses.user_timeline(screen_name=screen_name)
    return tweets


def tweets_to_content_items(tweets: List[Dict]) -> List[ContentItem]:
    content_items = []
    for tweet in tweets:
        date_time = datetime.strptime(tweet["created_at"], "%a %b %d %H:%M:%S +0000 %Y")
        timestamp = int(time.mktime(date_time.timetuple()) * 1000)
        content_item = ContentItem(content=tweet["text"], created=timestamp, id_str=tweet["id_str"])
        content_items.append(content_item)
    return content_items

if __name__ == "__main__":
    tweet_objects = get_tweets_string("realDonaldTrump")
    items = tweets_to_content_items(tweet_objects)
    watson_json_string = '{"contentItems": ['
    watson_json_string += ",".join([json.dumps(item.__dict__) for item in items])
    print(watson_json_string)
