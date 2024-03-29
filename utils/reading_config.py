import configparser
import os
from datetime import datetime, timezone
import ast


def reading_video_config(config_path):
    # Load the configuration file
    config = configparser.ConfigParser()
    config.read(config_path)

    # Initialize dictionaries to store query clauses for each logical operator
    query_and_clauses = []
    query_or_clauses = []
    query_not_clauses = []

    # Iterate over options in the configuration file
    for section in config.sections():
        if section.startswith("date"):
            start_date = config["date"]["start_date"]
            end_date = config["date"]["end_date"]
            print(start_date, end_date)
        else:
            logical_operator = section.split('_')[0].lower()
            operation_value = config.get(section, 'operation')
            field_name_value = config.get(section, 'field_name')
            field_values_value = config.get(section, 'field_values').split(',')
            
            # Construct query clause dictionary
            query_clause = {
                "operation": operation_value,
                "field_name": field_name_value,
                "field_values": field_values_value
            }
            
            # Append query clause to the appropriate list based on logical operator
            if logical_operator == 'and':
                query_and_clauses.append(query_clause)
            elif logical_operator == 'or':
                query_or_clauses.append(query_clause)
            elif logical_operator == 'not':
                query_not_clauses.append(query_clause)

    # Construct the final query dictionary
    query = {}
    if query_and_clauses:
        query["and"] = query_and_clauses
    if query_or_clauses:
        query["or"] = query_or_clauses
    if query_not_clauses:
        query["not"] = query_not_clauses

    return query, start_date, end_date

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

    
    return (
        server_path,
        database,
        collection1
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