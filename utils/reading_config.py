import configparser
import os
from datetime import datetime, timezone
import ast


def reading_query_config(config_path):
    """
    Reads configuration values from a Telegram config file.

    Parameters:
    - path(str) to Config file

    Returns:
    tuple: A tuple containing the following configuration values:
        - keywords (list).
        - author (str).
        - subreddit (str).
        - start_date (datetime object).
        - end_date (datetime object)
    """
    # Reading Configs
    config = configparser.ConfigParser()
    config.read(config_path)
    keywords = config["Query"]["keywords"]
    author = config["Query"]["author"]
    subreddit = config["Query"]["subreddit"]
    start_date = config["Query"]["start_date"]
    end_date = config["Query"]["end_date"]
    file_path_sub = config["Query"]["file_path_sub"]
    file_path_com = config["Query"]["file_path_com"]
    # Make them all None if None
    if keywords == "None":
        keywords = None
    else: 
        keywords = ast.literal_eval(keywords)
        
    if author == "None":
        author = None
    
    if subreddit == "None":
        subreddit = None
    
    if keywords == "None":
        keywords = None
    
    if start_date == "None":
        start_date = None
    else:
        start_date_naive = datetime.strptime(start_date, "%Y, %m, %d, %H, %M, %S")
        start_date = start_date_naive.replace(tzinfo=timezone.utc)
    
    if end_date == "None": 
        end_date = None
    else:
        end_date_naive = datetime.strptime(end_date, "%Y, %m, %d, %H, %M, %S")
        end_date = end_date_naive.replace(tzinfo=timezone.utc)

    return keywords, author, subreddit, start_date, end_date, file_path_sub, file_path_com

def reading_config_database(config_file):
    """
    Reads database configuration values from a database config
    file and two scrpt related variables.

    Parameters:
    - config_file (str): The path to the database config file.

    Returns:
    tuple: A tuple containing the following configuration values:
        - server_path (str): The server path for the database.
        - database (str): The name of the database.
        - collection (str): Name of the submission collection.
    """
    # Reading Configs
    config = configparser.ConfigParser()
    config.read(config_file)

    # Setting configuration values
    server_path = config["Database"]["server_path"]

    database = config["Database"]["database"]

    collection1 = config["Database"]["collection1"]
    collection2 = config["Database"]["collection2"]
    collection3 = config["Database"]["collection3"]
    collection4 = config["Database"]["collection4"]
    collection5 = config["Database"]["collection5"]
    
    return (
        server_path,
        database,
        collection1,
        collection2,
        collection3,
        collection4,
        collection5,
    )


def reading_config_credentials(config_file):
    """
    Initializes Telegram client objects based on configuration files.

    Parameters:
    - folder_path (str, optional): The path to the folder containing configuration files.
                                   Defaults to "config".

    Returns:
    tuple: A tuple containing:
        - list: A list of initialized Telegram clients.
        - dict: A dictionary mapping each client to a list containing:
                - str: The phone number associated with the client.
                - str: The username associated with the client.
                - str: The initial connection status of the client.
    """
    # Reading Configs
    config = configparser.ConfigParser()
    config.read(config_file)
    
    # Read config
    client_id = config["Tiktok"]["CLIENT_ID"]
    client_secret = config["Tiktok"]["CLIENT_SECRET"]
    client_key = config["Tiktok"]["CLIENT_KEY"]
    grant_type = config["Tiktok"]["GRANT_TYPE"]
    
    # submission_attributes = config["Reddit"]["submission_attributes"]    
    # submission_attributes = ast.literal_eval(submission_attributes)


    return client_id, client_secret, client_key, grant_type