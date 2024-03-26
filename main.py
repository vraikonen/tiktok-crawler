import requests
import sys
import json 
import pandas as pd
import logging 

from utils.reading_config import reading_config_credentials 
from utils.logging import logging_crawler, custom_exception_hook


def get_access_token(client_secret, client_key, grant_type):
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
        print(response_json)
        print("Access Token:", response_json['access_token'])
        print("Expires In:", response_json['expires_in'])
        print("Token Type:", response_json['token_type'])
        with open("token", "w") as outfile:
            json.dump(response_json, outfile)
    else:
        # If the request was not successful, print the error response JSON
        print("Error:", response.json())



if __name__ == "__main__":
    
    # Initiate logging, set the custom exception hook to print errors
    logging_crawler()
    sys.excepthook = custom_exception_hook

    # Read credentials
    path_to_credentials = 'config/api-credentials.ini'
    client_id, client_secret, client_key, grant_type = reading_config_credentials(path_to_credentials)
    
    # Create token to access API 
    #TODO check this part ffs, can you check somewhere in the response how many second are left so to know if you should create a new one 
    #get_access_token(client_secret, client_key, grant_type)

    # Get token
    with open('token') as file:
        token = json.load(file)
    access_token = token['access_token']
    # TikTok API endpoint
    endpoint = "https://open.tiktokapis.com/v2/research/video/query/"
    start_date = "20230101"
    end_date = "20230131"
        
    # Set the query parameters
    query_params = {
        "fields": "id,video_description,create_time,region_code,share_count,view_count,like_count,comment_count,music_id,hashtag_names,username,effect_ids,playlist_id,voice_to_text",
    }
    
    query_body= {
        "query": {
            "and": [
                {
                    "operation": "EQ",
                    "field_name": "region_code",
                    "field_values": ["US"]
                },
                # {
                #     "operation":"IN",
                #     "field_name":"hashtag_name",
                #     "field_values":["losangeles"]
                # }
            ],
            # "not": [
            # {
            #         "operation": "EQ",
            #         "field_name": "video_length",
            #         "field_values": ["SHORT"]
            # }
            # ]
        },
        "max_count": 10,
        "cursor": 0,
        "start_date": start_date,
        "end_date": end_date,
        # "search_id" : None,
    }
    # Set headers
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {access_token}"
    }
    
    try:
        # Send request
        response = requests.post(endpoint, json=query_body, params=query_params, headers=headers)
        
        # Check if the request was successful
        if response.status_code == 200:
            # Parse and extract information from the response
            data = response.json().get("data", {})
            #print(data)
            search_id = data.get("search_id")
            videos = data.get("videos", [])
            #print(type(data.get('has_more')))
            
            # Pagination
            while True:
                # Update to continue crawling
                query_body['search_id'] = data['search_id']
                query_body['cursor'] = data['cursor']

                #print(query_body)
                response = requests.post(endpoint, json=query_body, params=query_params, headers=headers)
                data = response.json().get("data", {})
                videos = data.get("videos", [])
                #print(data)

        else:
            logging.info(f"Response not 200, but: {response.status_code}, with an info: {response.text}")
    except Exception as e: 
        logging.info(f"No response, an error: {str(e)}")


# potential_error
'''
{'error': {'code': 'internal_error', 'message': 'Something went wrong. Please try again later.', 'log_id': '20240326115713B2A9EF517343BA0802E1'}}'''