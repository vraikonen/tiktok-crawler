import sys
import os
import pandas as pd

from utils.reading_config import (
    reading_config_credentials,
    reading_config_database,
    reading_config_comments,
)
from utils.logging import logging_crawler, custom_exception_hook
from utils.mongodb_writer import initialize_mongodb

from modules.tiktok_api import get_access_token, get_videos, get_video_ids, get_comments

if __name__ == "__main__":

    # Initiate logging, set the custom exception hook to print errors
    logging_crawler()
    sys.excepthook = custom_exception_hook

    # Create token to access API
    access_token = get_access_token()

    # Read config db
    path_to_db = "config/database.ini"
    server_path, database, collection1, collection2, collection3 = (
        reading_config_database(path_to_db)
    )

    # Initialize database
    videos_col, comments_col, invalid_videos_col = initialize_mongodb(
        server_path, database, collection1, collection2, collection3
    )

    # Prompt the user for input
    choice = (
        input("What would you like to crawl? Enter 'comments' or 'videos': ")
        .strip()
        .lower()
    )

    # Perform the appropriate action based on user input
    if choice == "comments":
        # Read df with video_ids
        path_to_comments = "config/fetch-comments.ini"
        path_to_video_df, video_id_column = reading_config_comments(path_to_comments)
        df = pd.read_csv(path_to_video_df)

        # Get ids of the videos
        video_ids = get_video_ids(df, video_id_column, comments_col, invalid_videos_col)

        # Fetch comments
        get_comments(access_token, video_ids, comments_col, invalid_videos_col)
    elif choice == "videos":
        get_videos(access_token, videos_col)
    else:
        print("Invalid choice. Please enter 'comments' or 'videos'.")
