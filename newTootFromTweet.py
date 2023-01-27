#!/usr/bin/python3

import requests
import mastodon
import pymysql
import mimetypes
import os
import time

def upload_media(attachment_url, api):
    """Upload media attachment to Mastodon
    attachment_url : string : URL of the media attachment
    api : Mastodon : Mastodon API object
    """
    try:
        # Get the binary data of the attachment
        attachment_data = requests.get(attachment_url).content

        # Get the file type of the attachment
        file_type, encoding = mimetypes.guess_type(attachment_url)
        if file_type is None:
            raise ValueError("Invalid file type")
        # Upload the attachment
        media = api.media_post(attachment_data, mime_type=file_type, synchronous=True)
        return media
    except Exception as e:
        print(f'Error uploading media: {e}')
        
def upload_attachments(attachment1, attachment2, attachment3, attachment4, api):
    media_ids=[]
    if attachment1 is not None:
        media_ids.append(upload_media(attachment1, api))
    if attachment2 is not None:
        media_ids.append(upload_media(attachment2, api))
    if attachment3 is not None:
        media_ids.append(upload_media(attachment3, api))
    if attachment4 is not None:
        media_ids.append(upload_media(attachment4, api))
    return media_ids

# Connect to the database
connection = pymysql.connect(
    host='DB-Host',
    user='DB-User',
    password='DB-Password',
    db='DB-Name'
)

# Initialize the Mastodon API wrapper
mastodon = mastodon.Mastodon(
    client_id='your-client-id',
    client_secret='your-client-secret',
    api_base_url='https://your-base.url',
        access_token='your-access-token'
)

i=1

while i == 1:
    i = 2
    try:
        # Get the highest tweet_id from the twoot_ids table
        with connection.cursor() as cursor:
            cursor.execute("SELECT tweet_id FROM twoot_ids ORDER BY tweet_id DESC")
            highest_tweet_id = cursor.fetchone()[0]

        # If there are no previous tweets, set the highest tweet_id to 0
        if highest_tweet_id is None:
            highest_tweet_id = 0

        # Get all new tweets with a higher tweet_id than the highest tweet_id in the twoot_ids table
        print("Highest tweet id:")
        print(highest_tweet_id)
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT tweet_id, author_id, author_username, tweet_text, retweet_id, reply_id, quote_id, timestamp, attachment1, attachment2, attachment3, attachment4 FROM tweets WHERE tweet_id > %s ORDER BY tweet_id ASC",
                (highest_tweet_id)
            )
            tweets = cursor.fetchall()
    
        # Process each new tweet
        for tweet in tweets:
            tweet_id, author_id, author_username, tweet_text, retweet_id, reply_id, quote_id, timestamp, attachment1, attachment2, attachment3, attachment4 = tweet
            
            toot_text = author_username + ":\n" + tweet_text
            print("Tweet ID:")
            print(tweet_id)
            print("TweetText:")
            print(toot_text)
            # If there is a dataset with the value tweet_id in the twoot_ids corresponding to the reply_id of the tweet, the new toot will be a reply to the corresponding toot from the twoot_ids table
            if reply_id is not None:
                with connection.cursor() as cursor:
                    cursor.execute(
                        "SELECT toot_id FROM twoot_ids WHERE tweet_id = %s",
                        (reply_id,)
                    )
                    reply_toot_id = cursor.fetchone()
                    if reply_toot_id is not None:
                        reply_toot_id = reply_toot_id[0]
            else:
                reply_toot_id = None
                
            print("Reply toot ID:")
            print(reply_toot_id)
    
            # Upload attachments if they exist
            media_ids = []
            if attachment1 or attachment2 or attachment3 or attachment4:
                media_ids = upload_attachments(attachment1, attachment2, attachment3, attachment4, mastodon)
    
            print("Media IDs:")
            print(media_ids)
            # Create the toot with the tweet data
            toot = mastodon.status_post(
                status=toot_text,
                in_reply_to_id=reply_toot_id,
                media_ids=media_ids,
                visibility='public'
            )
            
            print("New toot ID:")
            print(toot['id'])
            #Insert the resulting toot_id and the corresponding tweet_id to the twoot_ids table
            with connection.cursor() as cursor:
                cursor.execute(
                    "INSERT INTO twoot_ids (toot_id, tweet_id) VALUES (%s, %s)",
                    (toot['id'], tweet_id)
                )
                connection.commit()
            
            # Update the highest tweet_id
            #highest_tweet_id = tweet_id
            
            print("===================================================================================================================================")
        
    except Exception as e:
        print(f'Error: {e}')
        
        
    try:
        # Get the highest tweet_id from the twoot_ids table
        with connection.cursor() as cursor:
            cursor.execute("SELECT MAX(tweet_id) FROM twoot_mentions")
            highest_tweet_mention = cursor.fetchone()[0]

        # If there are no previous tweets, set the highest tweet_id to 0
        if highest_tweet_mention is None:
            highest_tweet_mention = 0

        # Get all new tweets with a higher tweet_id than the highest tweet_id in the twoot_ids table
        print("Highest tweet mention:")
        print(highest_tweet_mention)
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT tweet_id, author_id, author_username, tweet_text, retweet_id, reply_id, quote_id, timestamp, attachment1, attachment2, attachment3, attachment4 FROM mentions WHERE tweet_id > %s ORDER BY tweet_id ASC",
                (highest_tweet_mention,)
            )
            mentions = cursor.fetchall()
    
        # Process each new tweet
        for mention in mentions:
            tweet_id, author_id, author_username, tweet_text, retweet_id, reply_id, quote_id, timestamp, attachment1, attachment2, attachment3, attachment4 = mention
            
            toot_text = "@niko\n" + author_username + ":\n" + tweet_text
            print("Tweet ID:")
            print(tweet_id)
            print("TweetText:")
            print(toot_text)
            # If there is a dataset with the value tweet_id in the twoot_ids corresponding to the reply_id of the tweet, the new toot will be a reply to the corresponding toot from the twoot_ids table
            if reply_id is not None:
                with connection.cursor() as cursor:
                    cursor.execute(
                        "SELECT toot_id FROM twoot_ids WHERE tweet_id = %s",
                        (reply_id,)
                    )
                    reply_toot_id = cursor.fetchone()
                    if reply_toot_id is not None:
                        reply_toot_id = reply_toot_id[0]
            else:
                reply_toot_id = None
                
            print("Reply toot ID:")
            print(reply_toot_id)
    
            # Upload attachments if they exist
            media_ids = []
            if attachment1 or attachment2 or attachment3 or attachment4:
                media_ids = upload_attachments(attachment1, attachment2, attachment3, attachment4, mastodon)
    
            print("Media IDs:")
            print(media_ids)
            # Create the toot with the tweet data
            toot = mastodon.status_post(
                status=toot_text,
                in_reply_to_id=reply_toot_id,
                media_ids=media_ids,
                visibility='unlisted'
            )
            
            print("New toot ID:")
            print(toot['id'])
            #Insert the resulting toot_id and the corresponding tweet_id to the twoot_ids table
            with connection.cursor() as cursor:
                cursor.execute(
                    "INSERT INTO twoot_mentions (toot_id, tweet_id) VALUES (%s, %s)",
                    (toot['id'], tweet_id)
                )
                connection.commit()
            
            # Update the highest tweet_id
            #highest_tweet_id = tweet_id
            
            print("===================================================================================================================================")
        
    except Exception as e:
        print(f'Error: {e}')

#    print("Sleeping…")        
#    time.sleep(10) # Sleep for 60 seconds before checking for new tweets
