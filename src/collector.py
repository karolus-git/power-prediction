# Libraries
import requests
import json
import pandas as pd
import os
import wget
from pprint import pprint
import logging

logger = logging.getLogger("journal")

def from_web(url, path, folder):
    """Download a file from an url

    Args:
        url (str): url of the file
        path (path): path of the file
        folder (path): folder containing the file
    """

    # If the path already exists, it is removed
    if path.exists():
        os.remove(path)

    logger.info(f"downloading from {url}...")
    #Wget is used to download the file to the folder
    wget.download(url, folder) 

    logger.debug(f"file downloaded")


def from_api(url_request):
    pass
    # TODO
    # response_API = requests.get(url_request)
    
    # json_response = response_API.json()

    # df = pd.json_normalize(json_response)
    # df.columns = df.columns.str.replace("record.fields.", "")

    # return df


def from_csv(csv_path):
    """Import a csv file as pd.DataFrame

    Args:
        csv_path (Path): path of the csv file to read

    Returns:
        pd.DataFrame: build dataframe
    """
    return pd.read_csv(csv_path, delimiter=";")

