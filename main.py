import sys
import os

from utils.reading_config import reading_config_credentials, reading_config_database
from utils.logging import logging_crawler, custom_exception_hook
from utils.mongodb_writer import initialize_mongodb

from modules.tiktok_api import get_access_token, get_videos, get_video_ids, get_comments

# TODO check reponses from the log file, response 504 is tricky! do the same id once again? why does that happend, how to do that?
# write every invalid video id, and then try later to run the script on them,
# write response code as separate key, and whole response as separate key, maybe also add timestamp?

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
        video_ids = get_video_ids(comments_col, videos_col, invalid_videos_col)
        get_comments(access_token, video_ids, comments_col, invalid_videos_col)
    elif choice == "videos":
        get_videos(access_token, videos_col)
    else:
        print("Invalid choice. Please enter 'comments' or 'videos'.")
