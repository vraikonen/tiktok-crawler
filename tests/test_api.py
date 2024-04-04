import requests
import subprocess
import time
import os
from utils.reading_config import reading_video_config
from modules.tiktok_api import get_access_token

from utils.file_io import read_pickle

# Get the absolute path of the current file
current_file_path = os.path.abspath(__file__)
tests_dir = os.path.dirname(current_file_path)
parent_dir = os.path.dirname(tests_dir)


# Run both tests from the root directory of the project
def test_response():

    # Create token to access API
    access_token = get_access_token()

    # Get values from config
    video_config_path = os.path.join(parent_dir, "config/query-video.ini")
    query, start_date, end_date = reading_video_config(video_config_path)

    # TikTok API endpoint
    endpoint = "https://open.tiktokapis.com/v2/research/video/query/"
    # Set video attributes you want to retrieve
    query_params = {
        "fields": "id,video_description,create_time,region_code,share_count,view_count,like_count,comment_count,music_id,hashtag_names,username,effect_ids,playlist_id,voice_to_text",
    }
    # Query
    query_body = {
        "query": query,
        "max_count": 100,
        "cursor": 0,
        "start_date": start_date,
        "end_date": end_date,
        "search_id": None,
    }
    # Set headers
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {access_token}",
    }

    response = requests.post(
        endpoint, json=query_body, params=query_params, headers=headers
    )
    if response.status_code == 200:
        # Get data and write it
        data = response.json().get("data", {})
        videos1 = data.get("videos", [])

    # Use the same query second time
    response = requests.post(
        endpoint, json=query_body, params=query_params, headers=headers
    )
    if response.status_code == 200:
        # Get data and write it
        data = response.json().get("data", {})
        videos2 = data.get("videos", [])

    assert videos1 == videos2


temp_dir = os.path.join(parent_dir, "temp_videos")
cursor1 = read_pickle(os.path.join(temp_dir, "cursor.pickle"))
search_id1 = read_pickle(os.path.join(temp_dir, "search_id.pickle"))


# Run the main code once, check the pickles, run it again, check the pickles
def test_pagination():

    # Run the main script
    process = subprocess.Popen(["python", os.path.join(parent_dir, "main.py")])
    time.sleep(30)
    process.terminate()
    # assert process.returncode == 0

    # Read pagination variables
    cursor1 = read_pickle(os.path.join(temp_dir, "cursor.pickle"))
    search_id1 = read_pickle(os.path.join(temp_dir, "search_id.pickle"))

    # Run the main scriot again
    process = subprocess.Popen(["python", os.path.join(parent_dir, "main.py")])
    time.sleep(30)
    process.terminate()
    # assert process.returncode == 0

    # Read pagination variables
    cursor2 = read_pickle(os.path.join(temp_dir, "cursor.pickle"))
    search_id2 = read_pickle(os.path.join(temp_dir, "search_id.pickle"))

    assert cursor1 < cursor2
    assert search_id1 == search_id2
