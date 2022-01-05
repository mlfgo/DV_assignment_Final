from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from textblob import TextBlob
import pandas as pd
import numpy as np
import logging
import matplotlib.pyplot as plt
import sys
from os import walk,remove
from time import time_ns as time
import re

IMAGE_DIRECT="./static/images"

LEVELS={
    'debug':logging.DEBUG,
    'info':logging.INFO,
    'warning':logging.WARNING,
    'error':logging.ERROR,
    'critical':logging.CRITICAL
}


def getLevel(lvl):
    return LEVELS.get(lvl,logging.DEBUG)


TERRIBLE="TERRIBLE"
BAD="BAD"
NORMAL="NORMAL"
GOOD="GOOD"

'''
This method invoke the library SentimentIntensityAnalyzer to analyze the input natural sentence.
text: It is context of the natural language
'''
def parse_text(text:str):
    analyser = SentimentIntensityAnalyzer()
    blob = TextBlob(text)
    score = analyser.polarity_scores(blob)
    # print('Textblob output', blob.sentiment.polarity,"{:-<40} {blob}", str(score))
    return score

'''
This method converts the input JSON object into a Pandas DataFrame
@:parameter
data: It is the input data in JSON pattern
'''
def parse_data(data):
    column = ["user_text", "followers_counts", "re_followers", "re_text"]
    try:
        df=pd.DataFrame([[data['text'], data["user"]["followers_count"], data["retweeted_status"]["user"]["followers_count"], re.sub(r"[^A-za-z1-9@ ]", "", data["retweeted_status"]["text"])]], columns=column)
        return df
    except:
        df=pd.DataFrame([[data['text'], data["user"]["followers_count"], 0, ""]], columns=column)
        return df


'''
The method to convet the natural language into prediscriptive words
@:parameter
text input context
'''
def convert_to_text(text):
    if text >=0.7:
        return GOOD
    elif  text >0 and text <=0.7:
        return NORMAL
    elif text< 0 and text > -0.7:
        return BAD
    else:
        return TERRIBLE

'''
A logging method to logging the reasonable information to the sys.out
@:parameter
df: It is the input pandas DataFrame
logger: It is the input logger 
outPut: It is position where to display
'''
def logging_data_to(df,logger,outPut):
    ch=logging.StreamHandler(outPut)
    ch.setLevel(logging.CRITICAL)
    logger.addHandler(ch)
    for tweet in df:
        if tweet._json['text'] != '':
            logger.debug(tweet)

'''
This method builds the chart and save the chart to the static folder
@:parameter
data: It is the input array list with columns 'Comment','Level','Person','Retweet_Level'.
'''
def build_chart(data:[],logger):
    arr=np.array(data)
    df=pd.DataFrame(arr, columns=['Comment','Level','Person','Retweet_Level'])
    plt.title(df['Person'][0])
    df['Level'].value_counts().plot.bar(rot=0)
    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(logging.DEBUG)
    logger.addHandler(ch)
    logger.debug(f'static/images/{time()}.png')
    plt.savefig(f'static/images/{time()}.png')

'''
This method fetches the latest charts from the static/images/
@:parameter
direct: The particular fold to save the charts
'''
def fetch_latest_result(direct=IMAGE_DIRECT):

    files=walk(direct)
    files_list=[]
    for (_,_,filenames) in files:
        if isinstance(filenames,list):
            for filename in filenames:
                files_list.append(filename)
    print(files_list)
    files_list.sort(key=lambda f: int(re.sub('\D', '', f)),reverse=True)
    print(files_list)
    if len(files_list)>3:
        files_gt_4=files_list[3:]
        print(files_gt_4)
        for removed_file in files_gt_4:
            removed_tmp= IMAGE_DIRECT+"/"+removed_file
            print(removed_tmp)
            remove(removed_tmp)

    return files_list


if __name__ == '__main__':
    parse_text("I love it")