import requests
import sys
import json 
# import pandas as pd
import logging 
import time

from utils.reading_config import reading_config_credentials, reading_config_database
from utils.logging import logging_crawler, custom_exception_hook
from utils.mongodb_writer import initialize_mongodb, write_data

from modules.tiktok_api import get_access_token, get_videos

if __name__ == "__main__":
    
    # Initiate logging, set the custom exception hook to print errors
    logging_crawler()
    sys.excepthook = custom_exception_hook

    # Read credentials
    path_to_credentials = 'config/api-credentials.ini'
    client_id, client_secret, client_key, grant_type = reading_config_credentials(path_to_credentials)
    
    # Create token to access API 
    #TODO check this part ffs, can you check somewhere in the response how many second are left so to know if you should create a new one 
    access_token = get_access_token()
    # Retrieve token
    
    # Read config db
    path_to_db = "config/database.ini"
    server_path, database, collection1 = reading_config_database(path_to_db)
    
    # # Initialize database
    videos_col = initialize_mongodb(server_path,
    database,
    collection1)

    get_videos(access_token, videos_col)
            




# Add logging
# Mongodb cannot write an empty list?! check that out?!