"""

IDE: PyCharm
Project: social-media-bot
Author: Robin
Filename: analyze_tweets.py
Date: 25.01.2020

"""
import json
import os
from collections import defaultdict
from datetime import datetime

import dotenv
import numpy as np
import pandas as pd
import spacy
from matplotlib import pyplot

from term_document_matrix import TermDocumentMatrix, filter_top_phrases

nlp = spacy.load('en_core_web_sm')


def text_analysis(tweets_filepath):
    matrix = TermDocumentMatrix(nlp)

    with open(tweets_filepath, 'r', encoding='utf8') as json_file:
        tweet_set = json.load(json_file)

        for tweet in tweet_set["tweets"]:
            text = tweet["text"].strip()
            id = tweet["tweet_id"]
            matrix.add_doc(id, text)

    phrases = matrix.get_most_frequent_phrases(2, 3)
    top_phrases = filter_top_phrases(phrases, 20)

    objects = [x[0] for x in top_phrases]
    y_pos = np.arange(len(objects))
    performance = [x[1] for x in top_phrases]

    pyplot.bar(y_pos, performance, align='center', alpha=0.5)
    pyplot.xticks(y_pos, objects, rotation=45)
    pyplot.ylabel('Document Frequency')
    pyplot.title('Terms')

    pyplot.show()


def general_stats(tweets_filepath):
    with open(tweets_filepath, 'r', encoding='utf8') as json_file:
        tweets = json.load(json_file)["tweets"]

        # preprocessing (categorize top5 mentions, timestamps to dates
        mention_count = defaultdict(int)
        for tweet in tweets:
            tweet["date"] = datetime.strptime(datetime.strptime(tweet["date"], "%c").strftime('%d.%m.%y'), '%d.%m.%y')

            for mention in tweet['mentions']:
                mention_count[mention] += 1

        # only top 5 tags
        topx = 5
        mention_items = list([k, mention_count[k]] for k in mention_count.keys())
        mention_items.sort(key=lambda x: x[1], reverse=True)
        mention_items = mention_items[:topx]
        mention_tags = [k for (k, v) in mention_items]

        # create mention columns
        for tweet in tweets:
            for tag in mention_tags:
                if tag in tweet['mentions']:
                    tweet[tag] = 1
                else:
                    tweet[tag] = 0

    series = pd.DataFrame.from_records(tweets, index="tweet_id", exclude=['hashtags', 'url', 'text', 'mentions'])

    grouped = series.groupby('date').sum()
    grouped.plot()
    pyplot.show()

    for mention_tag in mention_tags:
        grouped = series.query(mention_tag + ">0").groupby('date').count()
        grouped.plot(y=[mention_tag])
        pyplot.show()


if __name__ == '__main__':
    dotenv.load_dotenv()
    tweets_file = os.getenv('TWITTER_DATA')

    general_stats(tweets_file)
    text_analysis(tweets_file)
