#!/usr/bin/python3

import tweepy
import mastodon
import pymysql
import time
from bs4 import BeautifulSoup
import re

# Connect to the database
connection = pymysql.connect(
    host='[DB-Host]',
    user='[DB-User]',
    password='[DB-Password]',
    db='[DB-Name]'
)

# Initialize the Mastodon API wrapper
mastodon = mastodon.Mastodon(
    client_id='your-client-id',
    client_secret='your-client-secret',
    api_base_url='https://your-base.url',
    access_token='your-access-token'
)

# Connect to the Twitter API
bearerToken = 'your-bearer-token'
oauth2ClientID = 'your-client-id'
oauth2ClientSecret = 'your-client-secret'

consumerKey = 'your-consumer-key'
consumerSecret = 'your-consumer-secret'
accessToken = 'your-access-token'
accessTokenSecret = 'your-access-token-secret'
returnType = 'Response'
waitOnRateLimit = True

with open('/root/twootsyncer/oauth_access_token.txt') as f:
    access_token = f.read()
with open('/root/twootsyncer/oauth_access_token_secret.txt') as f:
    access_token_secret = f.read()

oauth1_user_handler = tweepy.OAuth1UserHandler(consumerKey, consumerSecret, callback="oob")
oauth1_user_handler.secure = True

api = tweepy.API(oauth1_user_handler)

if access_token == '' or access_token_secret == '':
    auth_url = oauth1_user_handler.get_authorization_url()
    print("Please authorize: " + auth_url)
    
    oauth_verifier = input("Please input oauth_verifier here: ")
    
    access_token, access_token_secret = oauth1_user_handler.get_access_token(oauth_verifier)
    f = open('/root/twootsyncer/oauth_access_token.txt', "w")
    f.write(access_token)
    f.close()
    f = open('/root/twootsyncer/oauth_access_token_secret.txt', "w")
    f.write(access_token_secret)
    f.close()

client = tweepy.Client(consumer_key=consumerKey, consumer_secret=consumerSecret, access_token=access_token, access_token_secret=access_token_secret, return_type=returnType, wait_on_rate_limit=waitOnRateLimit)

while True:
    
    # Get notifications from Mastodon
    
    with connection.cursor() as cursor:
        cursor.execute("SELECT toot_id from notifications ORDER BY toot_id DESC LIMIT 0,1")
        lastID = cursor.fetchone()
    
    notifications = mastodon.notifications(exclude_types=['follow','follow_request','poll','update'],since_id=lastID)
    
    print(notifications)
    
    for notification in notifications:
        if 'status' in notification:
            # Get the tweet_id corresponding to the toot_id in the notification
            
            if notification['type'] == 'favourite':
                with connection.cursor() as cursor:
                    cursor.execute("SELECT tweet_id FROM twoot_ids WHERE toot_id = %s", (notification['status']['id'],))
                    tweet_id = cursor.fetchone()[0]
                client.like(tweet_id, user_auth=True)
                with connection.cursor() as cursor:
                    sql_insert = "INSERT INTO notifications (toot_id, notification_type) VALUES (%s, %s)"
                    data_insert = (notification['id'], "favourite")
                    cursor.execute(sql_insert, data_insert)
            
            elif notification['type'] == 'reblog':
                with connection.cursor() as cursor:
                    cursor.execute("SELECT tweet_id FROM twoot_ids WHERE toot_id = %s", (notification['status']['id'],))
                    tweet_id = cursor.fetchone()[0]
                client.retweet(tweet_id, user_auth=True)
                with connection.cursor() as cursor:
                    sql_insert = "INSERT INTO notifications (toot_id, notification_type) VALUES (%s, %s)"
                    data_insert = (notification['id'], "reblog")
                    cursor.execute(sql_insert, data_insert)
            
            elif notification['type'] == 'mention':
                inReplyToID = notification['status']['in_reply_to_id']
                repliedID = notification['status']['id']
                with connection.cursor() as cursor:
                    cursor.execute("SELECT tweet_id FROM twoot_ids WHERE toot_id = %s", inReplyToID)
                    tweet_id = cursor.fetchone()[0]
                tootText = notification['status']['content']
                soup = BeautifulSoup(tootText, 'html.parser')
                tootText = soup.get_text()
                print(tootText)
                tootText = tootText.replace('@tootbot ','')
                tootText = tootText.replace('@twitter.com','')
    #            print(tootText)
    #            with connection.cursor() as cursor:
    #                cursor.execute("SELECT tweet_text, author_username FROM tweets WHERE tweet_id = %s", tweet_id)
    #                tweet_text, author_username = cursor.fetchone()
    #                print(tweet_text)
    #            print(tweet_text)
    #            tweet_text = author_username + " " + tweet_text
    #            tweet_text = tweet_text.replace('@twitter.com','')
    #            print(tweet_text)
    #            mentions = []
    #            for match in re.finditer("@\w+", tweet_text):
    #                mention = match.group(0).lower()
    #                if mention not in mentions:
    #                    mention = mention
    #                    mentions.append(mention + " ")
    #            for mention in reversed(mentions):
    #                tootText = mention + tootText
                client.create_tweet(text=tootText, in_reply_to_tweet_id=tweet_id, user_auth=True)
                with connection.cursor() as cursor:
                    sql_insert = "INSERT INTO notifications (toot_id, notification_type, replied_id) VALUES (%s, %s, %s)"
                    data_insert = (notification['id'], "mention", repliedID)
                    cursor.execute(sql_insert, data_insert)
    connection.commit()
            
    print("Sleeping…")
    time.sleep(10)