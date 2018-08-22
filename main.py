from twitter import Twitter, OAuth
from collections import namedtuple
from keys import *
from watson_data import ContentItem
from typing import List, Dict
from datetime import datetime
import time
from watson_developer_cloud.personality_insights_v3 import PersonalityInsightsV3


def create_watson_json_from_twitter(screen_name: str) -> Dict:
    tweet_objects = get_tweets_string(screen_name)
    items = tweets_to_content_items(tweet_objects)
    watson_dictionary = {"contentItems": [item.__dict__ for item in items]}
    return watson_dictionary


def get_tweets_string(screen_name: str) -> namedtuple:
    oauth = OAuth(TWITTER_ACCESS_TOKEN, TWITTER_ACCESS_SECRET, TWITTER_CONSUMER_KEY, TWITTER_CONSUMER_SECRET)
    twitter = Twitter(auth=oauth)
    tweets = twitter.statuses.user_timeline(screen_name=screen_name, count=3200)
    return tweets


def tweets_to_content_items(tweets: List[Dict]) -> List[ContentItem]:
    content_items = []
    for tweet in tweets:
        date_time = datetime.strptime(tweet["created_at"], "%a %b %d %H:%M:%S +0000 %Y")
        timestamp = int(time.mktime(date_time.timetuple()) * 1000)
        content_item = ContentItem(content=tweet["text"], created=timestamp, id_str=tweet["id_str"])
        content_items.append(content_item)
    return content_items


def get_personality_insights_from_tweets(tweets_dictionary: Dict) -> Dict:
    personality_insights = PersonalityInsightsV3(version="2017-10-16",
                                                 url="https://gateway-wdc.watsonplatform.net/personality-insights/api",
                                                 iam_api_key=WATSON_KEY)
    return personality_insights.profile(tweets_dictionary, raw_scores=True, consumption_preferences=True,
                                        accept_language="en")


if __name__ == "__main__":
    SCREEN_NAME = "realDonaldTrump"
    JSON_DICTIONARY = create_watson_json_from_twitter(SCREEN_NAME)
    PROFILE = get_personality_insights_from_tweets(JSON_DICTIONARY)
