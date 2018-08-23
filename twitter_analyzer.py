from twitter import Twitter, OAuth
from keys import *
from watson_data import ContentItem
from typing import List, Dict, Tuple
from datetime import datetime
import time
from watson_developer_cloud.personality_insights_v3 import PersonalityInsightsV3
import argparse
import numpy as np
import matplotlib
matplotlib.use("TkAgg")
import matplotlib.pyplot as plt


def analyze_user(screen_name: str):
    json_dictionary = create_watson_json_from_twitter(screen_name)
    profile = get_personality_insights_from_tweets(json_dictionary)
    display_results(screen_name, profile)


def create_watson_json_from_twitter(screen_name: str) -> Dict:
    tweet_objects = get_tweets_string(screen_name)
    items = tweets_to_content_items(tweet_objects)
    watson_dictionary = {"contentItems": [item.__dict__ for item in items]}
    return watson_dictionary


def get_tweets_string(screen_name: str) -> List[Dict]:
    oauth = OAuth(TWITTER_ACCESS_TOKEN, TWITTER_ACCESS_SECRET, TWITTER_CONSUMER_KEY, TWITTER_CONSUMER_SECRET)
    twitter = Twitter(auth=oauth)
    tweets = twitter.statuses.user_timeline(screen_name=screen_name, count=200)
    get_all_tweets(twitter, tweets, screen_name)
    return tweets


def get_all_tweets(twitter: Twitter, tweets: List, screen_name: str):
    for i in range(15):
        last_id = tweets[-1]["id"]
        new_tweets = twitter.statuses.user_timeline(screen_name, count=200)
        tweets.extend(new_tweets)


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


def display_results(screen_name: str, profile: Dict):
    plt.suptitle("@{}".format(screen_name), fontsize=14)
    create_plot("personality", profile, 311)
    create_plot("values", profile, 312)
    create_plot("needs", profile, 313)
    figure_manager = plt.get_current_fig_manager()
    figure_manager.window.state('zoomed')
    plt.show()


def create_plot(key: str, profile: Dict, axes_num: int):
    personality_type = profile[key]
    bar_width = .35
    index = np.arange(len(personality_type))
    names_percents = sort_by_percent(personality_type)
    axis = plt.subplot(axes_num)
    axis.bar(index, [percent * 100 for _, percent in names_percents], bar_width, alpha=.4, color='r')
    axis.set_ylabel("Percent (%)")
    axis.set_title("{} metrics".format(key.capitalize()))
    axis.set_xticks(index)
    axis.set_xticklabels([name for name, _ in names_percents])
    plt.tight_layout()


def sort_by_percent(personality_type) -> List[Tuple[str, float]]:
    names_percents = [(trait["name"], trait["percentile"]) for trait in personality_type]
    names_percents = sorted(names_percents, key=lambda x: x[1])
    return names_percents


if __name__ == "__main__":
    PARSER = argparse.ArgumentParser(description="Screen name of twitter user.")
    PARSER.add_argument('screen_name', metavar="ScreenName", type=str,
                        help="Screen name of the twitter user to analyze.")
    ARGS = PARSER.parse_args()
    analyze_user(ARGS.screen_name)
