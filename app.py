#System modules
import logging
import pickle as pkl

#Third-part modules
import sys
import tweepy as tp
import pandas as pd
from flask import Flask, render_template, request

#Customer modules
from twitter_auth import *
from common_tools import logging_data_to
from common_tools import build_chart
from common_tools import parse_data
from common_tools import fetch_latest_result
from common_tools import parse_text, convert_to_text
from common_tools import GOOD,NORMAL,BAD,TERRIBLE


logger = logging.getLogger('data_visualization')

auth = tp.OAuthHandler(API_KEY, API_SECRET)
auth.set_access_token(ACCESS_TOKEN, ACCESS_SECRET)
COLUMNS=["user_text", "followers_counts", "re_followers", "re_text"]
api = tp.API(auth)

app = Flask(__name__)

'''
The root directory as the HomePage 
'''
@app.route('/', methods=['GET'])
def homepage():
    files=fetch_latest_result()
    return render_template('index.html',query=files)

'''
Tweets page post the particular query to fetch the related tweets
'''
@app.route('/tweets', methods=['POST'])
def tweetspage():
    arr=[]

    #Handle the behavior from the client
    if request.method == 'POST':
        query = request.form['query']
        search = api.search(query)
        tweets = search

        logging_data_to(tweets,logger,sys.stdout)
        df = pd.DataFrame(columns=COLUMNS)

        for tweet in tweets:
            if tweet._json['text'] != '':
                df=df.append(parse_data(tweet._json))

        for i in range(len(df)):
            text_data = parse_text(df.iloc[i,0])
            re_tweet_text_data = ""
            if df.iloc[i, 3] != "":
                re_tweet_text_data=parse_text(df.iloc[i,3])
                arr.append([df.iloc[i,0], convert_to_text(text_data['compound']), query,convert_to_text(re_tweet_text_data['compound'])])
            else:
                arr.append([df.iloc[i, 0], convert_to_text(text_data['compound']), query,
                            "Null"])

        '''
        This section builds the chart 
        '''
        try:
            if len(arr) !=0:
                build_chart(arr,logger)
            else:
                return render_template('404.html')
            pkl.dump(arr, open('static/temp_files/file.pkl', 'wb'))
            return render_template('results.html', query=arr)
        except:
            return render_template('invalid_search_context.html')

    return render_template('404.html')

'''
Return the fetched information
'''
@app.route('/forms', methods=['GET'])
def request_form():
    return render_template('request_form.html')

'''
Display the data visualization in HighChart
'''
@app.route('/dv', methods=['GET'])
def data_visualization():
    pick_data = []
    #The labels for pandas DataFrame
    labels = ['Context', 'Orient', 'Name', 'Retweet_Orient']
    pick_df = pd.DataFrame(columns=labels)
    try:
        pick_data = pkl.load(open('static/temp_files/file.pkl', 'rb'))
        # pick_df = pick_df.append(pkl.load(open('static/temp_files/df.pkl', 'rb')))
    except:
        error_msg="There is no such a temp file to read the raw data"
        return render_template('data_visualization.html', error=error_msg)

    if pick_data is not None and len(pick_data) != 0 and pick_df is not None:
        df = pd.DataFrame(pick_data, columns=labels)
        result_dict = df['Orient'].value_counts().to_dict()
        retweet_dict_not_worked=df[df.Retweet_Orient == "Null"].Retweet_Orient.count()
        retweet_dict_good = df[df.Retweet_Orient == GOOD].Retweet_Orient.value_counts().to_dict()
        retweet_dict_bad = df[df.Retweet_Orient == BAD].Retweet_Orient.value_counts().to_dict()
        retweet_dict_terrible = df[df.Retweet_Orient == TERRIBLE].Retweet_Orient.value_counts().to_dict()
        retweet_dict_normal = df[df.Retweet_Orient == NORMAL].Retweet_Orient.value_counts().to_dict()

        return render_template('data_visualization.html', result_dict=result_dict,
                               retweet_dict_good=retweet_dict_good,
                               retweet_dict_bad=retweet_dict_bad,
                               retweet_dict_terrible=retweet_dict_terrible,
                               retweet_dict_normal=retweet_dict_normal,
                               retweet_dict_not_worked=retweet_dict_not_worked,
                               title=df['Name'][0])
    else:
        error_msg = 'Reading deserialized data error'
        return render_template('data_visualization.html', error=error_msg)


if __name__ == '__main__':
    app.run()
