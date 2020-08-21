import os
import sys
import re
import tweepy
import preprocessor as p
import pandas as pd
#for vader we have to download vader_lexicon for the first time
import nltk
nltk.download('vader_lexicon')
hiddenimports = ["nltk.chunk.named_entity"]
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from googletrans import Translator
from twitter_sentiment_handler import twitter_credential
from datetime import datetime

auth = tweepy.OAuthHandler(twitter_credential.CONSUMER_KEY, twitter_credential.CONSUMER_SECRET)
auth.set_access_token(twitter_credential.ACCESS_TOKEN, twitter_credential.ACCESS_TOKEN_SECRET)
api = tweepy.API(auth,wait_on_rate_limit=True)

if not api:
    print("Error in Authenticate")
    sys.exit(-1)

def tweet_data():
    try:
        # Open/Create a file to append data
        # If the file exists, then read the existing data from the CSV file.
        file_name = "tourism_"+datetime.now().strftime("%d-%b-%Y")+"_data.csv"

        COLS = ['created_at','id','send_by','tweet_url','original_text','trans','process', 'priority','type']

        if os.path.exists(file_name):
            df = pd.read_csv(file_name, header=0)
            pre_id = max(df["id"])
            print(pre_id)
        else:
            pre_id = 0
            df = pd.DataFrame(columns=COLS)
            print(pre_id)
        hndlr_lst = twitter_credential.handler_list
        # new_entry = []
        for name in hndlr_lst:
            for tweet in tweepy.Cursor(api.search, q=name, count=100,
                                       # lang="en",
                                       since=datetime.now().strftime("%Y-%m-%d"),
                                       since_id=pre_id,
                                       # max_id = pre_id
                                       # until= datetime.now().strftime("%Y-%m-%d")
                                       ).items():

                # # tweet URL
                tweet_url = f"https://twitter.com/" + tweet.user.screen_name + "/status/" + str(tweet.id)

                # google tranglater
                translator = Translator()
                trans = translator.translate(tweet.text).text

                # cleaning data
                process = p.clean(trans)
                process = re.sub(r':', '', process)
                process = re.sub(r'‚Ä¶', '', process)

                # vader
                sen_analyser = SentimentIntensityAnalyzer()
                polarity_scores = sen_analyser.polarity_scores(process)
                print(tweet.id)
                compnd = polarity_scores['compound']
                if compnd >= 0.05:
                    polarity = polarity_scores['pos']
                    polarity_type = "positive"
                elif compnd <= -0.05:
                    polarity = polarity_scores['neg']
                    polarity_type = "negative"
                else:
                    polarity = polarity_scores['neu']
                    polarity_type = "neutral"

                new_entry = [tweet.created_at, tweet.id, tweet.user.screen_name,
                             tweet_url, tweet.text, trans, process, polarity, polarity_type]
                # print(new_entry)

                single_tweet_df = pd.DataFrame([new_entry], columns=COLS)
                df_final = df.append(single_tweet_df, ignore_index=True)
                df = pd.DataFrame(data=df_final, columns=COLS)
                df.to_csv(file_name)

        # print("Got all the tweet.")
    except tweepy.TweepError as e:
        print(str(e))
        print("Something went wrong.")

if __name__ == "__main__":
    #call the function
    tweet_data()