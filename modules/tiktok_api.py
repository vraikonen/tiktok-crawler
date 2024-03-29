import requests
import logging
import json
import time
import os

from utils.mongodb_writer import write_data

from utils.reading_config import reading_config_credentials, reading_video_config

from utils.file_io import read_pickle, write_pickle

def get_access_token():
    
    # Read credentials
    path_to_credentials = 'config/api-credentials.ini'
    client_id, client_secret, client_key, grant_type = reading_config_credentials(path_to_credentials)
    # Endpoint URL
    endpoint_url = "https://open.tiktokapis.com/v2/oauth/token/"

    # Request headers
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
    }

    # Request body parameters
    data = {
        'client_key': client_key,
        'client_secret': client_secret,
        'grant_type': grant_type,
    }

    # Make the POST request
    response = requests.post(endpoint_url, headers=headers, data=data)

    # Check if the request was successful (status code 200)
    if response.status_code == 200:
        # Parse and print the response JSON
        response_json = response.json()
        logging.info(f"Token is successfully obtained, response: {response_json}")
        print(response_json)
        with open("token", "w") as outfile:
            json.dump(response_json, outfile)
    else:
        # If the request was not successful, print the error response JSON
        logging.info("Obtaining token promted an error:", response.json())

    return response_json['access_token']

def get_videos(access_token, video_col):
        
    logging.info(50*"==", " Retrieving comments: ", 50*"==")
    
    # Get values from config
    video_config_path = "config/query-video.ini"
    query, start_date, end_date = reading_video_config(video_config_path)
    print(start_date)

    # TikTok API endpoint
    endpoint = "https://open.tiktokapis.com/v2/research/video/query/"
    # Set video attributes you want to retrieve
    query_params = {
        "fields": "id,video_description,create_time,region_code,share_count,view_count,like_count,comment_count,music_id,hashtag_names,username,effect_ids,playlist_id,voice_to_text",
    }
    
    # Create the folder for the files important for the script restart
    temp_path = f"temp_{video_col.name}"
    os.makedirs(temp_path, exist_ok=True)
    # Check if we run the script before
    if os.path.exists(f"{temp_path}/cursor.pickle") and os.path.exists(f"{temp_path}/search_id.pickle"):
        cursor = read_pickle(f"{temp_path}/cursor.pickle")
        search_id = read_pickle(f"{temp_path}/search_id.pickle")
    else:
        cursor = 0
        search_id = None
    print(cursor, search_id)
    # This is the query
    query_body= {
        "query": query,
        "max_count": 100,
        "cursor": cursor,
        "start_date": start_date,
        "end_date": end_date,
        "search_id": search_id,
    }
    # Set headers
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {access_token}"
    }
    
    # Attempts to generate new token 
    attempts = 0
    responses = 0
    num_videos = 0
    random_error = 0
    has_more = True 
    while has_more:
        try:
            response = requests.post(endpoint, json=query_body, params=query_params, headers=headers)
            if response.status_code == 200:
                # Get data and write it
                data = response.json().get("data", {})
                videos = data.get("videos", [])
                write_data(videos, video_col)
                
                # Track and log responses
                num_videos += len(videos)
                responses +=1
                if responses %10 == 0: 
                    logging.info(f"Number of successful responses {responses}; Number of retrieved_videos: {num_videos}")
                    print(f"Number of successful responses {responses}; Number of retrieved_videos: {num_videos}")
                
                # Update for pagination and save the values for the next time the script is run
                has_more = data.get('has_more')
                query_body['search_id'] = data['search_id']
                write_pickle(data['search_id'], f"{temp_path}/search_id.pickle")
                query_body['cursor'] = data['cursor']
                write_pickle(data['cursor'], f"{temp_path}/cursor.pickle")
                
                
                # Write cursor and search_id values for the restart of the script
                
            # 401 status code says we are not authorized
            elif response.status_code == 401:
                time.sleep(60)
                attempts += 1
                access_token = get_access_token()
                # Set headers with new access token
                headers = {
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {access_token}"
                }
                # Break it after having the same error 5 times
                if attempts == 5:
                    logging.info(f"Script is terminated after 5 unsuccessfull authorization attempts. Number of valid responses: {responses}. Number of retrieved videos: {num_videos}")
                    print("Script is terminated. Check the log file and find out why.")
                    break
            # 429 says we hit rate limits
            elif response.status_code == 429:
                logging.info(f"We have hit rate limits. Number of valid responses: {responses}. Number of retrieved videos: {num_videos}")
                print("Script is terminated. Check the log file and find out why.")
                break
            else:
                # Sleep a bit if the status_code is 501, 500 or something random and try again
                random_error +=1
                time.sleep(60)
                logging.info(f"Response not 200, but: {response.status_code}, with an info: {response.text}. Sleeping for one minute, and retrying 20 times.")
                if random_error == 20:
                    logging.info(f"Terminating the script after 20 attempts without valid response")
                    print("Script is terminated. Check the log file and find out why.")
                    break          
        except Exception as e:
            logging.info("Could not send the request, error: ", str(e))
            break
    if has_more == False:
        logging.info(f"No more videos can be found for the current query. Number of valid responses: {responses}. Number of retrieved videos: {num_videos}")


def get_comments(video_ids):
    url = 'https://open.tiktokapis.com/v2/research/video/comment/list/'
    
    
    headers = {
        'Authorization': 'Bearer clt.4nyeJxanUuBpOsu39aB19KcMPHwmY7YSM8QwOodHype5r0EeCDZit7ERtoZ3',
        'Content-Type': 'application/json'
    }
    for video_id in video_ids:
        data = {
            "video_id": video_id,
            "max_count": 100,
            "cursor": 0
        }

        response = requests.post(url, headers=headers, json=data)
        print(response.json())
        


def get_comments(access_token, comment_col):
    
    logging.info(50*"==", " Retrieving comments: ", 50*"==")
    # TikTok API endpoint
    endpoint = "https://open.tiktokapis.com/v2/research/video/comment/list/"
    
    # Set comment attributes you want to retrieve
    query_params = {
        "fields": "id, video_id, text, like_count, reply_count, parent_comment_id, create_time",
    }
    
    # Create the folder for the files important for the script restart
    temp_path = f"temp_{comment_col.name}"
    os.makedirs(temp_path, exist_ok=True)
    # Check if we run the script before
    if os.path.exists(f"{temp_path}/cursor.pickle") and os.path.exists(f"{temp_path}/search_id.pickle"):
        cursor = read_pickle(f"{temp_path}/cursor.pickle")
        search_id = read_pickle(f"{temp_path}/search_id.pickle")
    else:
        cursor = 0
        search_id = None

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {access_token}"
    }
    
    # TODO read video ids
    video_ids = []
    
    # Iterate over every video
    for video_id in video_id:
        # TODO check if the video was already processed
        
        # This is the query
        query_body= {
            {
            "video_id": video_id,
            "max_count": 100,
            "cursor": 0
            }
        }
    
        # TRY
        response = requests.post(endpoint, json=query_body, params=query_params, headers=headers)

    
    # Attempts to generate new token 
    attempts = 0
    responses = 0
    num_videos = 0
    random_error = 0
    has_more = True 
    while has_more:
        try:
            response = requests.post(endpoint, json=query_body, params=query_params, headers=headers)
            if response.status_code == 200:
                # Get data and write it
                data = response.json().get("data", {})
                videos = data.get("videos", [])
                write_data(videos, comment_col)
                
                # Track and log responses
                num_videos += len(videos)
                responses +=1
                if responses %10 == 0: 
                    logging.info(f"Number of successful responses {responses}; Number of retrieved_videos: {num_videos}")
                    print(f"Number of successful responses {responses}; Number of retrieved_videos: {num_videos}")
                
                # Update for pagination and save the values for the next time the script is run
                has_more = data.get('has_more')
                query_body['search_id'] = data['search_id']
                write_pickle(data['search_id'], f"{temp_path}/search_id.pickle")
                query_body['cursor'] = data['cursor']
                write_pickle(data['cursor'], f"{temp_path}/cursor.pickle")
                
                
                # Write cursor and search_id values for the restart of the script
                
            # 401 status code says we are not authorized
            elif response.status_code == 401:
                time.sleep(60)
                attempts += 1
                access_token = get_access_token()
                # Set headers with new access token
                headers = {
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {access_token}"
                }
                # Break it after having the same error 5 times
                if attempts == 5:
                    logging.info(f"Script is terminated after 5 unsuccessfull authorization attempts. Number of valid responses: {responses}. Number of retrieved videos: {num_videos}")
                    print("Script is terminated. Check the log file and find out why.")
                    break
            # 429 says we hit rate limits
            elif response.status_code == 429:
                logging.info(f"We have hit rate limits. Number of valid responses: {responses}. Number of retrieved videos: {num_videos}")
                print("Script is terminated. Check the log file and find out why.")
                break
            else:
                # Sleep a bit if the status_code is 501, 500 or something random and try again
                random_error +=1
                time.sleep(60)
                logging.info(f"Response not 200, but: {response.status_code}, with an info: {response.text}. Sleeping for one minute, and retrying 20 times.")
                if random_error == 20:
                    logging.info(f"Terminating the script after 20 attempts without valid response")
                    print("Script is terminated. Check the log file and find out why.")
                    break          
        except Exception as e:
            logging.info("Could not send the request, error: ", str(e))
            break
    logging.info(f"No more videos can be found for the current query. Number of valid responses: {responses}. Number of retrieved videos: {num_videos}")
