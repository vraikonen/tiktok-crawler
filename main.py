import sys

from utils.reading_config import reading_config_credentials, reading_config_database
from utils.logging import logging_crawler, custom_exception_hook
from utils.mongodb_writer import initialize_mongodb

from modules.tiktok_api import get_access_token, get_videos

if __name__ == "__main__":

    # Initiate logging, set the custom exception hook to print errors
    logging_crawler()
    sys.excepthook = custom_exception_hook

    # Create token to access API
    access_token = get_access_token()

    # Read config db
    path_to_db = "config/database.ini"
    server_path, database, collection1 = reading_config_database(path_to_db)

    # # Initialize database
    videos_col = initialize_mongodb(server_path, database, collection1)

    get_videos(access_token, videos_col)
