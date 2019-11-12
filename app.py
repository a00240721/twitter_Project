import re

# import self as self
import tweepy
import private_key as pk
from matplotlib import pyplot as plt

from tweepy import OAuthHandler
from textblob import TextBlob
from flask import Flask, render_template, jsonify, request

app = Flask(__name__)

fig = ''


# @app.route('/')
def hello_world():
    return 'Hello World!'


@app.route('/templates')
def hello_template():
    myList = []
    myList.append('Apple')
    myList.append('Orange')
    myList.append('Lemon')
    return render_template('index.html', hello="My new Flask Hello World", list=myList, len=len(myList))


class TwitterClient(object):
    '''
	Generic Twitter Class for sentiment analysis.
	'''

    def __init__(self):
        '''
		Class constructor or initialization method.
		'''
        # keys and tokens from the Twitter Dev Console
        consumer_key = pk.consumer_key
        consumer_secret = pk.consumer_secret
        access_token = pk.access_token
        access_token_secret = pk.access_token_secret

        # attempt authentication
        try:
            # create OAuthHandler object
            self.auth = OAuthHandler(consumer_key, consumer_secret)
            # set access token and secret
            self.auth.set_access_token(access_token, access_token_secret)
            # create tweepy API object to fetch tweets
            self.api = tweepy.API(self.auth)
        except:
            print("Error: Authentication Failed")

    def clean_tweet(self, tweet):
        '''
		Utility function to clean tweet text by removing links, special characters
		using simple regex statements.
		'''
        return ' '.join(re.sub("(@[A-Za-z0-9]+)|([^0-9A-Za-z \t])|(\w+:\/\/\S+)", " ", tweet).split())

    def get_tweet_sentiment(self, tweet):
        '''
		Utility function to classify sentiment of passed tweet
		using textblob's sentiment method
		'''
        # create TextBlob object of passed tweet text
        analysis = TextBlob(self.clean_tweet(tweet))
        # set sentiment
        if analysis.sentiment.polarity > 0:
            return 'positive'
        elif analysis.sentiment.polarity == 0:
            return 'neutral'
        else:
            return 'negative'

    def get_tweets(self, query, count=10):
        '''
		Main function to fetch tweets and parse them.
		'''
        # empty list to store parsed tweets
        tweets = []

        try:
            # call twitter api to fetch tweets
            fetched_tweets = self.api.search(q=query, count=count)

            # parsing tweets one by one
            for tweet in fetched_tweets:
                # empty dictionary to store required params of a tweet
                parsed_tweet = {}
                parsed_tweet['profile_pic'] = tweet.user.profile_image_url
                parsed_tweet['location'] = tweet.user.location
                parsed_tweet['screen_name'] = tweet.user.screen_name
                # saving text of tweet
                parsed_tweet['text'] = tweet.text
                # saving sentiment of tweet
                parsed_tweet['sentiment'] = self.get_tweet_sentiment(tweet.text)

                # appending parsed tweet to tweets list
                if tweet.retweet_count > 0:
                    # if tweet has retweets, ensure that it is appended only once
                    if parsed_tweet not in tweets:
                        tweets.append(parsed_tweet)
                else:
                    tweets.append(parsed_tweet)

            # return parsed tweets
            return tweets

        except tweepy.TweepError as e:
            # print error (if any)
            print("Error : " + str(e))


@app.route('/')
def results():
    # creating object of TwitterClient Class
    api = TwitterClient()
    # calling function to get tweets
    topic = 'Donald Trump'
    tweets = api.get_tweets(query=topic, count=20000)

    # picking positive tweets from tweets
    ptweets = [tweet for tweet in tweets if tweet['sentiment'] == 'positive']
    # percentage of positive tweets
    print("Positive tweets percentage: {} %".format(100 * len(ptweets) / len(tweets)))
    posPer = 100 * len(ptweets) / len(tweets)
    # picking negative tweets from tweets
    ntweets = [tweet for tweet in tweets if tweet['sentiment'] == 'negative']
    # percentage of negative tweets
    print("Negative tweets percentage: {} %".format(100 * len(ntweets) / len(tweets)))
    negPer = 100 * len(ntweets) / len(tweets)
    # percentage of neutral tweets
    print("Neutral tweets percentage: {} %".format(100 * (len(tweets) - (len(ntweets) + len(ptweets))) / len(tweets)))
    nutPer = 100 * (len(tweets) - (len(ntweets) + len(ptweets))) / len(tweets)
    # printing first 5 positive tweets
    print("\n\nPositive tweets:")
    ptweetsList = []
    pListProfile = []
    for tweet in ptweets:
        # print(tweet['text'])
        pListProfile.append(tweet['profile_pic'])
        tweetText = tweet['screen_name'] + " : " + tweet['text']
        ptweetsList.append(tweetText)

    # printing first 5 negative tweets
    print("\n\nNegative tweets:")
    ntweetList = []
    for tweet in ntweets:
        ntweetList.append(tweet['screen_name'] + " : " + tweet['text'])

    nutTweetList = [tweet for tweet in tweets if tweet['sentiment'] == 'neutral']
    tweetList = []
    for tweet in nutTweetList:
        tweetList.append(tweet['screen_name'] + " : " + tweet['text'])
    # print(topic)

    labels = 'Positive', 'Negative', 'Neutral'
    sizes = [len(ptweets), len(ntweets), len(tweetList)]
    explode = (0.1, 0.1, 0.1)  # only "explode" the 2nd slice (i.e. 'Hogs')

    fig1, ax1 = plt.subplots()
    ax1.pie(sizes, explode=explode, labels=labels, autopct='%1.1f%%',
            shadow=True, startangle=90)
    ax1.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
    plt.savefig('./static/images/new_plot.png')
    # plt.show()
    return render_template('tweet.html', pPer=posPer, negP=negPer, nuP=nutPer,
                           tweetslen=len(tweetList), nTweetlen=len(ntweets),
                           pTweetLen=len(ptweets), nList=ntweetList, pList=ptweetsList,
                           pListProfile=pListProfile,
                           List=tweetList, name='new_plot', url='./static/images/new_plot.png',
                           title=topic)


@app.route('/update', methods=['GET'])
def updateResults():
    # creating object of TwitterClient Class
    api = TwitterClient()
    # calling function to get tweets
    topic = 'Donald Trump'
    tweets = api.get_tweets(query=topic, count=20000)

    # picking positive tweets from tweets
    ptweets = [tweet for tweet in tweets if tweet['sentiment'] == 'positive']
    # percentage of positive tweets
    print("Positive tweets percentage: {} %".format(100 * len(ptweets) / len(tweets)))
    pPer = 100 * len(ptweets) / len(tweets)
    # picking negative tweets from tweets
    ntweets = [tweet for tweet in tweets if tweet['sentiment'] == 'negative']
    # percentage of negative tweets
    print("Negative tweets percentage: {} %".format(100 * len(ntweets) / len(tweets)))
    negP = 100 * len(ntweets) / len(tweets)
    # percentage of neutral tweets
    print("Neutral tweets percentage: {} %".format(100 * (len(tweets) - (len(ntweets) + len(ptweets))) / len(tweets)))
    nuP = 100 * (len(tweets) - (len(ntweets) + len(ptweets))) / len(tweets)
    # printing first 5 positive tweets
    ptweetsList = []
    pListProfile = []
    for tweet in ptweets:
        # print(tweet['text'])
        # pListProfile.append(tweet['profile_pic'])
        tweetText = tweet['screen_name'] + " : " + tweet['text']
        ptweetsList.append(tweetText)

    # printing first 5 negative tweets
    ntweetList = []
    for tweet in ntweets:
        ntweetList.append(tweet['screen_name'] + " : " + tweet['text'])

    nutTweetList = [tweet for tweet in tweets if tweet['sentiment'] == 'neutral']
    tweetList = []
    for tweet in nutTweetList:
        tweetList.append(tweet['screen_name'] + " : " + tweet['text'])
    # print(topic)

    labels = 'Positive', 'Negative', 'Neutral'
    sizes = [len(ptweets), len(ntweets), len(tweetList)]
    explode = (0.1, 0.1, 0.1)  # only "explode" the 2nd slice (i.e. 'Hogs')

    fig1, ax1 = plt.subplots()
    ax1.pie(sizes, explode=explode, labels=labels, autopct='%1.1f%%',
            shadow=True, startangle=90)
    ax1.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
    plt.savefig('./static/images/new_plot.png')
    # plt.show()
    tweetslen = len(tweetList)
    nTweetlen = len(ntweets)
    pTweetLen = len(ptweets)
    name = 'new_plot'
    url = './static/images/new_plot.png',
    title = topic
    res = {"pPer": pPer, "negP": negP, "nuP": nuP,
           "tweetslen": tweetslen, "nTweetlen": nTweetlen,
           "pTweetLen": pTweetLen, "name": name, "url": url,
           "title": title}
    print(jsonify(res))
    return jsonify(res)


if __name__ == '__main__':
    app.run()
