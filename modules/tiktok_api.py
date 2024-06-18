import requests
import logging
import json
import time
import os
import pandas as pd

from utils.mongodb_writer import write_data

from utils.reading_config import reading_config_credentials, reading_video_config

from utils.file_io import read_pickle, write_pickle


def get_access_token():

    # Read credentials
    path_to_credentials = "config/api-credentials.ini"
    client_id, client_secret, client_key, grant_type = reading_config_credentials(
        path_to_credentials
    )
    # Endpoint URL
    endpoint_url = "https://open.tiktokapis.com/v2/oauth/token/"

    # Request headers
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
    }

    # Request body parameters
    data = {
        "client_key": client_key,
        "client_secret": client_secret,
        "grant_type": grant_type,
    }

    # Make the POST request
    response = requests.post(endpoint_url, headers=headers, data=data)

    # Check if the request was successful (status code 200)
    if response.status_code == 200:
        # Parse and print the response JSON
        response_json = response.json()
        logging.info(f"Token is successfully obtained, response: {response_json}")
        with open("token.json", "w") as outfile:
            json.dump(response_json, outfile)
    else:
        # If the request was not successful, print the error response JSON
        logging.info(f"Obtaining token promted an error: {response.json()}")

    return response_json["access_token"]


def get_videos(access_token, video_col):

    logging.info(f"{50 * '='} Retrieving videos: {50 * '='}")

    # Get values from config
    video_config_path = "config/query-video.ini"
    query, start_date, end_date = reading_video_config(video_config_path)

    # TikTok API endpoint
    endpoint = "https://open.tiktokapis.com/v2/research/video/query/"
    # Set video attributes you want to retrieve
    query_params = {
        "fields": "id,video_description,create_time,region_code,share_count,view_count,like_count,comment_count,music_id,hashtag_names,username,effect_ids,playlist_id,voice_to_text",
    }

    # Create the folder for the files important for the script restart
    temp_path = f"temp_{video_col.database.name}"
    os.makedirs(temp_path, exist_ok=True)
    # Check if we run the script before
    if os.path.exists(f"{temp_path}/cursor.pickle") and os.path.exists(
        f"{temp_path}/search_id.pickle"
    ):
        cursor = read_pickle(f"{temp_path}/cursor.pickle")
        search_id = read_pickle(f"{temp_path}/search_id.pickle")
    else:
        cursor = 0
        search_id = None
    # This is the query
    query_body = {
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
        "Authorization": f"Bearer {access_token}",
    }

    # Attempts to generate new token
    attempts = 0
    responses = 0
    num_videos = 0
    random_response = 0
    has_more = True
    while has_more:
        try:
            response = requests.post(
                endpoint, json=query_body, params=query_params, headers=headers
            )
            if response.status_code == 200:
                random_response = 0
                # Get data and write it
                data = response.json().get("data", {})
                videos = data.get("videos", [])
                write_data(videos, video_col)

                # Track and log responses
                num_videos += len(videos)
                responses += 1
                if responses % 10 == 0:
                    logging.info(
                        f"Number of successful responses {responses}; Number of retrieved_videos: {num_videos}"
                    )
                    print(
                        f"Number of successful responses {responses}; Number of retrieved_videos: {num_videos}"
                    )

                # Update for pagination and save the values for the next time the script is run
                has_more = data.get("has_more")
                query_body["search_id"] = data["search_id"]
                write_pickle(data["search_id"], f"{temp_path}/search_id.pickle")
                query_body["cursor"] = data["cursor"]
                write_pickle(data["cursor"], f"{temp_path}/cursor.pickle")

                # Write cursor and search_id values for the restart of the script

            # 401 status code says we are not authorized
            elif response.status_code == 401:
                random_response = 0
                time.sleep(60)
                attempts += 1
                access_token = get_access_token()
                # Set headers with new access token
                headers = {
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {access_token}",
                }
                # Break it after having the same error 5 times
                if attempts == 5:
                    logging.info(
                        f"Script is terminated after 5 unsuccessfull authorization attempts. Number of valid responses: {responses}. Number of retrieved videos: {num_videos}"
                    )
                    print("Script is terminated. Check the log file and find out why.")
                    break
            # 429 says we hit rate limits
            elif response.status_code == 429:
                random_response = 0
                logging.info(
                    f"We have hit rate limits. Number of valid responses: {responses}. Number of retrieved videos: {num_videos}. {response.json()}"
                )
                print("Script is terminated. Check the log file and find out why.")
                break
            else:
                # Sleep a bit if the status_code is 501, 500 or something random and try again
                random_response += 1
                time.sleep(60)
                logging.info(
                    f"Response not 200, but: {response.status_code}, with an info: {response.text}. Sleeping for one minute, and retrying 20 times."
                )
                if random_response == 20:
                    logging.info(
                        f"Terminating the script after 20 attempts without valid response"
                    )
                    print("Script is terminated. Check the log file and find out why.")
                    break
        except Exception as e:
            logging.info(f"Could not send the request, error:  {str(e)}")
            break

    # TODO Check this logic I cannot figure out right why I put this
    # if has_more == False:
    #     logging.info(
    #         f"1. No more videos can be found for the current query. Number of valid responses: {responses}. Number of retrieved videos: {num_videos}"
    #     )


def get_video_ids(videos_df, video_id_column, comments_col, invalid_videos_col):
    logging.info(f"{50 * '='} Retrieving comments: {50 * '='}")

    video_ids = []

    # cursor = videos_col.find({"comment_count": {"$ne": 0}}, {"_id": 0, "id": 1})
    # cursor_list = list(cursor)
    # ids = [item["id"] for item in cursor_list]
    # video_ids.extend(ids)

    if "comment_count" in videos_df.columns:
        try:
            videos_df["comment_count"] = videos_df["comment_count"].astype(int)
        except Exception as e:
            logging.info(
                f"Check your comment_count column - probably you have some alphabetic characters. This is the error: {str(e)}"
            )
        videos_df = videos_df[videos_df["comment_count"] != 0]
    try:
        videos_df[video_id_column] = videos_df[video_id_column].astype(int)
    except Exception as e:
        logging.info(
            f"Check your 'video_id' column - probably you have some alphabetic characters. Error: {str(e)}"
        )
    ids = videos_df[video_id_column].to_list()
    video_ids.extend(ids)

    processed_ids = []
    cols = [invalid_videos_col, comments_col]
    try:
        for col in cols:
            if col == invalid_videos_col:
                cursor = col.find({}, {"_id": 0, "id": 1})
                cursor_list = list(cursor)
                ids = [item["id"] for item in cursor_list]
            else:
                cursor = col.find({}, {"_id": 0, "video_id": 1})
                cursor_list = list(cursor)
                ids = [item["video_id"] for item in cursor_list]
            processed_ids.extend(ids)
    except Exception as e:
        logging.info(f"Error for accessing video IDs from collection: {e}")

    # Filter processed videos
    video_ids = list(set(video_ids))
    processed_ids = list(set(processed_ids))
    filtered_list = [item for item in video_ids if item not in processed_ids]
    logging.info(
        f"Total, initial videos that will eventually be fetched: {len(video_ids)}"
    )
    logging.info(
        f"Number of videos processed in previous iterations: {len(processed_ids)}"
    )
    return filtered_list


# TODO Maybe check if some comments are not retrieved due to error 504 etc
def get_comments(access_token, video_ids, comments_col, invalid_videos_col):

    endpoint = "https://open.tiktokapis.com/v2/research/video/comment/list/"

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }
    query_params = {
        "fields": "id, video_id, text, like_count, reply_count, parent_comment_id, create_time",
    }
    # Variables to track count for logging + max_count
    num_videos = 0
    responses = 0
    num_comments = 0
    attempts = 0
    random_response = 0
    consecutive_bad_requests = 0
    max_count = 100
    break_ = False

    # Iterate over videos
    for video_id in video_ids:
        # TODO add here to query the same video_id for a few times if we couldnt send request or the request is bad?
        # Or keep it like this, and then at the end just run the crawler once again as every time we run the crawler,
        # All unprocessed video_ids will be queried
        num_videos += 1
        has_more = True
        cursor = 0
        while (
            has_more and cursor + max_count <= 1000
        ):  # Check this if it is really needed or the server will solve it on its own
            query_body = {
                "video_id": video_id,
                "max_count": max_count,
                "cursor": cursor,
            }
            try:
                response = requests.post(
                    endpoint, json=query_body, params=query_params, headers=headers
                )
                consecutive_bad_requests = 0
                if response.status_code == 200:
                    random_response = 0
                    # Get data and write it
                    data = response.json().get("data", {})
                    comments = data.get("comments", [])
                    if len(comments) > 0:
                        write_data(comments, comments_col)
                    else:
                        write_data(
                            {
                                "id": video_id,
                                "status": "No comments found in this video.",
                            },
                            invalid_videos_col,
                        )
                    num_comments += len(comments)
                    responses += 1
                    if responses % 100 == 0:
                        logging.info(
                            f"Number of successful responses {responses}; Number of videos queries: {num_videos}; Total comments retrieved: {num_comments}"
                        )
                        print(
                            f"Number of successful responses {responses}; Number of videos queries: {num_videos}; Total comments retrieved: {num_comments}"
                        )
                    # Update for pagination
                    has_more = data.get("has_more")
                    cursor = data["cursor"]
                elif response.status_code == 400:
                    logging.info(
                        f"Invalid video ID {response.status_code}, with an info: {response.text}. Sleeping for one minute, and retrying {20-random_response} more times."
                    )
                    write_data(
                        {"id": video_id, "status": response.text}, invalid_videos_col
                    )
                    break
                # 401 status code says we are not authorized
                elif response.status_code == 401:
                    random_response = 0
                    time.sleep(60)
                    attempts += 1
                    access_token = get_access_token()
                    # Set headers with new access token
                    headers = {
                        "Content-Type": "application/json",
                        "Authorization": f"Bearer {access_token}",
                    }
                    # Break it after having the same error 5 times
                    if attempts == 5:
                        logging.info(
                            f"Script is terminated after 5 unsuccessfull authorization attempts. Number of valid responses: {responses}. Number of retrieved videos: {num_videos}"
                        )
                        print(
                            "Script is terminated. Check the log file and find out why."
                        )
                        break_ = True
                        break
                # 429 says we hit rate limits
                elif response.status_code == 429:
                    logging.info(
                        f"We have hit rate limits. Number of valid responses: {responses}. Number of retrieved comments: {num_comments}. {response.json()}"
                    )
                    print("Script is terminated. Check the log file and find out why.")
                    break_ = True
                    break
                else:
                    # Sleep a bit if the status_code is 501, 500 or something random and try again
                    # We do not save random response because we will eventually retrieve all the comments
                    # As these are server errors and script will be terminate after 20 server errors
                    random_response += 1
                    time.sleep(10 * random_response)
                    logging.info(
                        f"Response not 200, but: {response.status_code}, with an info: {response.text}. Sleeping for 10 seconds*number of 5xx responses. Number of consecutive 5xx responses: {random_response} ."
                    )
                    if random_response == 20:
                        logging.info(
                            f"Terminating the script after 20 attempts without valid response - most likely server errors."
                        )
                        print(
                            "Script is terminated. Check the log file and find out why."
                        )
                        break_ = True
                        break
            except Exception as e:
                logging.info(f"Could not send the request, error:  {str(e)}")
                consecutive_bad_requests += 1
                if consecutive_bad_requests == 5:
                    break_ = True
                    break
        if break_:
            break
    logging.info(f"No more comments? Or we hit rate limits.")
