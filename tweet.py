#!/usr/bin/python3
#from twython import Twython, TwythonError
import tweepy
import mysql.connector
from random import randint
import re
import requests
import time

print("=======================================================================================================================================================================================================================================================================================")

debug = False

def replace_usernames(tweet):
    return re.sub(r'@(\w+)', r'@\1@twitter.com', tweet)

def quoteTweet(quoteID,iam):
    isRetweet = False
    isReply = False
    isQuote = False
    quote = client.get_tweet(quoteID,expansions='author_id,referenced_tweets.id,referenced_tweets.id.author_id,entities.mentions.username,attachments.poll_ids,attachments.media_keys,in_reply_to_user_id,geo.place_id', media_fields="media_key", place_fields="name", poll_fields="id", tweet_fields='author_id,created_at,entities', user_fields=None, user_auth=True).data
    referencedTweets = quote.referenced_tweets
#    print("ReferencedTweets:")
#    print(referencedTweets)
    if referencedTweets != None:
        referenced_tweets_strings = [str(tweet) for tweet in referencedTweets]
        for tweet_string in referenced_tweets_strings:
            tweet_id = re.search(r"id=(\d+)", tweet_string).group(1)
            tweet_type = re.search(r"type=(\w+)", tweet_string).group(1)
#            print("Tweet ID:", tweet_id)
#            print("Tweet Type:", tweet_type)
            if tweet_type == "retweeted":
                isRetweet = True
#                print("isRetweet")
                retweetID = tweet_id
                retweetText = retweet(retweetID,"quote")
    if isRetweet == True:
        tweetText == retweetText
    else:
        originalAuthor = quote.author_id
        originalAuthorName = "@" + client.get_user(id=originalAuthor,user_fields="username",user_auth=True).data.username
        tweetText = "[RT " + originalAuthorName + "]\n" + quote.text
    return tweetText

def retweet(retweetID,iam):
    isRetweet = False
    isReply = False
    isQuote = False
    retweet = client.get_tweet(retweetID,expansions='author_id,referenced_tweets.id,referenced_tweets.id.author_id,entities.mentions.username,attachments.poll_ids,attachments.media_keys,in_reply_to_user_id,geo.place_id', media_fields="media_key", place_fields="name", poll_fields="id", tweet_fields='author_id,created_at,entities', user_fields=None, user_auth=True).data
    originalAuthor = retweet.author_id
    originalAuthorName = "@" + client.get_user(id=originalAuthor,user_fields="username",user_auth=True).data.username
    tweetText = "RT " + originalAuthorName + "\n" + retweet.text
    referencedTweets = retweet.referenced_tweets
#    print("ReferencedTweets:")
#    print(referencedTweets)
    if referencedTweets != None:
        referenced_tweets_strings = [str(tweet) for tweet in referencedTweets]
        for tweet_string in referenced_tweets_strings:
            tweet_id = re.search(r"id=(\d+)", tweet_string).group(1)
            tweet_type = re.search(r"type=(\w+)", tweet_string).group(1)
#            print("Tweet ID:", tweet_id)
#            print("Tweet Type:", tweet_type)
            if tweet_type == "quoted" and iam == "quote":
                isQuote = True
#                print("isQuote")
                quoteID = tweet_id
            else:
                isQuote = True
#                print("isQuote")
                quoteID = tweet_id
                quoteTweetText = quoteTweet(quoteID,"retweet")
                tweetText = tweetText + "\n" + quoteTweetText
    return tweetText
    
def get_attachment_url(tweetID):
    headers = {'Authorization': 'Bearer your-bearer-token'} # <- Your Bearer token needs to go here as well!
    expansions = "attachments.media_keys"
    fields = "duration_ms,height,media_key,preview_image_url,public_metrics,type,url,width,alt_text,variants"
    url = f"https://api.twitter.com/2/tweets?ids={tweetID}&expansions={expansions}&media.fields={fields}"
    response = requests.get(url, headers=headers)
    urls = []
    if response.status_code == 200:
        data = response.json()
        #print(data)
        if 'includes' not in data or 'media' not in data['includes']:
            return None
        media_list = data['includes']['media']
        for media in media_list:
            #try:
            if media['type'] == 'animated_gif' or media['type'] == 'video':
                if 'variants' in media:
                    variants = media['variants']
                    sorted_variants = sorted(variants, key=lambda x: x.get('bit_rate', 0), reverse=True)
                    urls.append(sorted_variants[0]['url'])
                    #print(video_url)
                else:
                    print("no variants key")
            elif media['type'] == 'photo':
                #print(media['url'])
                urls.append(media['url'])
            #except:
            #    print("no url key")
        return urls
    else:
        print(response.status_code)


mydb = mysql.connector.connect(
    host="DB-Host",
    user="DB-User",
    passwd="DB-Password",
    database="DB-Name"
)

bearerToken = 'your-bearer-token'
oauth2ClientID = 'your-client-id'
oauth2ClientSecret = 'your-client-secret'

consumerKey = 'your-consumer-key'
consumerSecret = 'your-consumer-secret'
accessToken = 'your-access-token'
accessTokenSecret = 'your-access-token-secret'
returnType = 'Response'
waitOnRateLimit = True

with open('/path/to/script/oauth_access_token.txt') as f: # <- your path here
    access_token = f.read()
with open('/path/to/script/oauth_access_token_secret.txt') as f: # <- your path here
    access_token_secret = f.read()

oauth1_user_handler = tweepy.OAuth1UserHandler(consumerKey, consumerSecret, callback="oob")
oauth1_user_handler.secure = True

api = tweepy.API(oauth1_user_handler)

if access_token == '' or access_token_secret == '':
    auth_url = oauth1_user_handler.get_authorization_url()
    print("Please authorize: " + auth_url)
    
    oauth_verifier = input("Please input oauth_verifier here: ")
    
    access_token, access_token_secret = oauth1_user_handler.get_access_token(oauth_verifier)
    f = open('/path/to/script/oauth_access_token.txt', "w") # <- your path here
    f.write(access_token)
    f.close()
    f = open('/path/to/script/oauth_access_token_secret.txt', "w") # <- your path here
    f.write(access_token_secret)
    f.close()

client = tweepy.Client(consumer_key=consumerKey, consumer_secret=consumerSecret, access_token=access_token, access_token_secret=access_token_secret, return_type=returnType, wait_on_rate_limit=waitOnRateLimit)

while True:
    cursor = mydb.cursor()
    cursor.execute("SELECT tweet_id FROM tweets ORDER BY tweet_id DESC LIMIT 0, 1")
    result = cursor.fetchone()
    try:
        for y in result:
            lastID = y
    except:
        print("ID not fetched")
        lastID = None
    
    #data = []
#    lastID = 
    
    if debug == False:
        
        homeTimeline = client.get_home_timeline(end_time=None, exclude=None, expansions='author_id,referenced_tweets.id,referenced_tweets.id.author_id,entities.mentions.username,attachments.poll_ids,attachments.media_keys,in_reply_to_user_id,geo.place_id', max_results=100, media_fields="media_key,preview_image_url", pagination_token=None, place_fields="name", poll_fields="id", since_id=lastID, start_time=None, tweet_fields='author_id,created_at,entities', until_id=None, user_fields=None, user_auth=True)
        
        if homeTimeline.data is not None:
            
            for tweet in homeTimeline.data:
                tweetID = tweet.id
                print("TweetID:")
                print(tweetID)
                tweetAuthor = tweet.author_id
        #        print("AuthorID:")
        #        print(tweetAuthor)
                tweetAuthorName = "@" + client.get_user(id=tweetAuthor,user_fields="username",user_auth=True).data.username + "@twitter.com"
                print("AuthorName:")
                print(tweetAuthorName)
                isRetweet = False
                isReply = False
                isQuote = False
                retweetID = None
                replyID = None
                quoteID = None
                attachment_urls = [None, None, None, None]
                referencedTweets = tweet.referenced_tweets
            #    print("ReferencedTweets:")
            #    print(referencedTweets)
                if referencedTweets != None:
                    referenced_tweets_strings = [str(tweet) for tweet in referencedTweets]
                    for tweet_string in referenced_tweets_strings:
                        referenced_tweet_id = re.search(r"id=(\d+)", tweet_string).group(1)
                        tweet_type = re.search(r"type=(\w+)", tweet_string).group(1)
        #                print("Tweet ID:", tweet_id)
        #                print("Tweet Type:", tweet_type)
                        if tweet_type == "retweeted":
                            isRetweet = True
        #                    print("isRetweet")
                            retweetID = referenced_tweet_id
                        elif tweet_type == "replied_to":
                            isReply = True
        #                    print("isReply")
                            replyID = referenced_tweet_id
                        elif tweet_type == "quoted":
                            isQuote = True
        #                    print("isQuote")
                            quoteID = referenced_tweet_id
        #                    print(quoteID)
                if isRetweet == True:
                    tweetText = retweet(retweetID,"tweet")
                    isQuote = False
                else:
                    tweetText = tweet.text
                if isQuote == True:
                    quoteTweetText = quoteTweet(quoteID,"tweet")
                    tweetText = tweetText + "\n" + quoteTweetText
                tweetText = replace_usernames(tweetText)
                print("TweetText:")
                print(tweetText)
                createdAt = tweet.created_at
                print("Created at:")
                print(createdAt)
                attachmentURL = get_attachment_url(tweetID)
                print("AttachmentURL:")
                print(attachmentURL)
        
                attachment_variables = ['attachment1', 'attachment2', 'attachment3', 'attachment4']
        
                attachment_values = [None] * 4
                
                if attachmentURL is None:
                    print("No attachmentURL")
                else:
                    for i, attachment in enumerate(attachmentURL):
                        if i < 4:
                            attachment_values[i] = attachment
                
                add_tweet = "INSERT INTO tweets (tweet_id, author_id, author_username, tweet_text, retweet_id, reply_id, quote_id, timestamp, {}) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, {})".format(', '.join(attachment_variables), ', '.join(['%s'] * len(attachment_variables)))
                
                data_tweet = (tweetID, tweetAuthor, tweetAuthorName, tweetText, retweetID, replyID, quoteID, createdAt) + tuple(attachment_values)
                cursor.execute(add_tweet, data_tweet)
                print("===================================================================================================================================")
        mydb.commit()


        cursor.execute("SELECT tweet_id FROM mentions ORDER BY timestamp DESC LIMIT 0, 1")
        result = cursor.fetchone()
        try:
            for y in result:
                lastMentionID = y
        except:
            print("ID not fetched")
            lastMentionID = None

        
        mentions = client.get_users_mentions(id="3043198296",end_time=None, expansions='author_id,referenced_tweets.id,referenced_tweets.id.author_id,entities.mentions.username,attachments.poll_ids,attachments.media_keys,in_reply_to_user_id,geo.place_id', max_results=100, media_fields="media_key,preview_image_url", pagination_token=None, place_fields="name", poll_fields="id", since_id=lastMentionID, start_time=None, tweet_fields='author_id,created_at,entities', until_id=None, user_fields=None, user_auth=True)

        if mentions.data is not None:
            
            for tweet in mentions.data:
                tweetID = tweet.id
                print("TweetID:")
                print(tweetID)
                tweetAuthor = tweet.author_id
        #        print("AuthorID:")
        #        print(tweetAuthor)
                tweetAuthorName = "@" + client.get_user(id=tweetAuthor,user_fields="username",user_auth=True).data.username + "@twitter.com"
                print("AuthorName:")
                print(tweetAuthorName)
                isRetweet = False
                isReply = False
                isQuote = False
                retweetID = None
                replyID = None
                quoteID = None
                attachment_urls = [None, None, None, None]
                referencedTweets = tweet.referenced_tweets
            #    print("ReferencedTweets:")
            #    print(referencedTweets)
                if referencedTweets != None:
                    referenced_tweets_strings = [str(tweet) for tweet in referencedTweets]
                    for tweet_string in referenced_tweets_strings:
                        tweet_id = re.search(r"id=(\d+)", tweet_string).group(1)
                        tweet_type = re.search(r"type=(\w+)", tweet_string).group(1)
        #                print("Tweet ID:", tweet_id)
        #                print("Tweet Type:", tweet_type)
                        if tweet_type == "retweeted":
                            isRetweet = True
        #                    print("isRetweet")
                            retweetID = tweet_id
                        elif tweet_type == "replied_to":
                            isReply = True
        #                    print("isReply")
                            replyID = tweet_id
                        elif tweet_type == "quoted":
                            isQuote = True
        #                    print("isQuote")
                            quoteID = tweet_id
                if isRetweet == True:
                    tweetText = retweet(retweetID,"tweet")
                    isQuote = False
                else:
                    tweetText = tweet.text
                if isQuote == True:
                    quoteTweetText = quoteTweet(quoteID,"tweet")
                    tweetText = tweetText + "\n" + quoteTweetText
                tweetText = replace_usernames(tweetText)
                print("TweetText:")
                print(tweetText)
                createdAt = tweet.created_at
                print("Created at:")
                print(createdAt)
                attachmentURL = get_attachment_url(tweetID)
                print("AttachmentURL:")
                print(attachmentURL)
        
                attachment_variables = ['attachment1', 'attachment2', 'attachment3', 'attachment4']
        
                attachment_values = [None] * 4
                
                if attachmentURL is None:
                    print("No attachmentURL")
                else:
                    for i, attachment in enumerate(attachmentURL):
                        if i < 4:
                            attachment_values[i] = attachment
                
                add_tweet = "INSERT INTO mentions (tweet_id, author_id, author_username, tweet_text, retweet_id, reply_id, quote_id, timestamp, {}) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, {})".format(', '.join(attachment_variables), ', '.join(['%s'] * len(attachment_variables)))
                
                data_tweet = (tweetID, tweetAuthor, tweetAuthorName, tweetText, retweetID, replyID, quoteID, createdAt) + tuple(attachment_values)
                cursor.execute(add_tweet, data_tweet)
                print("===================================================================================================================================")
        mydb.commit()
        
    else:
        
        
        tweet = client.get_tweet("1",expansions='author_id,referenced_tweets.id,referenced_tweets.id.author_id,entities.mentions.username,attachments.poll_ids,attachments.media_keys,in_reply_to_user_id,geo.place_id', media_fields="media_key,preview_image_url,url,variants", place_fields="name", poll_fields="id", tweet_fields='author_id,created_at,entities,attachments', user_fields=None, user_auth=True)
        
        tweetID = tweet.data.id
        print("TweetID:")
        print(tweetID)
        tweetAuthor = tweet.data.author_id
        print("AuthorID:")
        print(tweetAuthor)
        tweetAuthorName = "@" + client.get_user(id=tweetAuthor,user_fields="username",user_auth=True).data.username + "@twitter.com"
        print("AuthorName:")
        print(tweetAuthorName)
        isRetweet = False
        isReply = False
        isQuote = False
        retweetID = None
        replyID = None
        quoteID = None
        referencedTweets = tweet.data.referenced_tweets
        #    print("ReferencedTweets:")
        #    print(referencedTweets)
        if referencedTweets != None:
            referenced_tweets_strings = [str(tweet) for tweet in referencedTweets]
            for tweet_string in referenced_tweets_strings:
                tweet_id = re.search(r"id=(\d+)", tweet_string).group(1)
                tweet_type = re.search(r"type=(\w+)", tweet_string).group(1)
                print("Tweet ID:", tweet_id)
                print("Tweet Type:", tweet_type)
                if tweet_type == "retweeted":
                    isRetweet = True
                    print("isRetweet")
                    retweetID = tweet_id
                elif tweet_type == "replied_to":
                    isReply = True
                    print("isReply")
                    replyID = tweet_id
                elif tweet_type == "quoted":
                    isQuote = True
                    print("isQuote")
                    quoteID = tweet_id
        if isRetweet == True:
            tweetText = retweet(retweetID,"tweet")
            isQuote = False
        else:
            tweetText = tweet.data.text
        if isQuote == True:
            quoteTweetText = quoteTweet(quoteID,"tweet")
            tweetText = tweetText + "\n" + quoteTweetText
        print("TweetText:")
        print(tweetText)
        createdAt = tweet.data.created_at
        print("Created at:")
        print(createdAt)
        
    #    print(tweet.data.data)
    #    print(tweet.includes)
    #    entities = tweet.data.get("entities", {})
    #    if entities:
    #        urls = entities.get("urls", [])
    #        if urls:
    #            for url in urls:
    #                images = url.get("images", [])
    #                if images:
    #                    print("Original Image URL:", images[0]["url"])
                        
    #    media = tweet.get("media", {})
    #    if media:
        attachmentURL = get_attachment_url(tweetID)
        print(attachmentURL)
        
        
    print("Sleeping…")
    time.sleep(10)
