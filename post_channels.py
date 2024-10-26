from decouple import config
from helpers.setup_logging import setup_logging
from helpers.pickle_helpers import load_from_pickle, save_to_pickle
from helpers.http_request_helper import post_request
from helpers.utils import get_channel_dict_for_post
from helpers.json_helpers import convert_to_json_and_save



logger = setup_logging('post_channels')



NEW_ENTRIES_WITH_SUMMARIES_PICKLE = config("NEW_ENTRIES_WITH_SUMMARIES_PICKLE")
NEW_ENTRIES_WITH_SUMMARIES_JSON = config("NEW_ENTRIES_WITH_SUMMARIES_JSON")

ENV = config('ENV')

# Set the BASE_URL based on the environment
if ENV == 'DEV':
    BASE_URL = config('BASE_DEV_URL')
elif ENV == 'PROD':
    BASE_URL = config('BASE_PROD_URL')
else:
    logger.error("Invalid environment specified")
    raise ValueError("Invalid environment specified")

API_URL_SECRET_STRING = config('API_URL_SECRET_STRING')

if API_URL_SECRET_STRING == "None":
    API_URL_SECRET_STRING = None



def build_url(api_base_url, table, secret_string=None):
    """
    Constructs a URL for API requests based on the provided parameters.

    This function builds a URL by combining the base API URL, an optional secret string,
    and the table name. It's designed to create URLs for different API endpoints.

    Args:
        api_base_url (str): The base URL of the API.
        table (str): The name of the table or endpoint to be accessed: 'channels', 'entries', 'summaries', or 'transcripts'.
        secret_string (str, optional): A secret string to be included in the URL for authentication purposes.
            Defaults to None.

    Returns:
        str: The constructed URL.
    """
  
    if secret_string is None:
        url = f"{api_base_url}{table}/"
    else:
        url = f"{api_base_url}{secret_string}/{table}/"

    return url




def post_data_for_channel(channel):
    """
    Posts data for a single entry to the server, including the entry itself, its summary, and transcript.

    Args:
        entry (dict): A dictionary containing the entry data.
        channel_id (int): The ID of the channel this entry belongs to.

    Returns:
        None

    This function performs three main tasks:
    1. Posts the entry data to the server.
    2. Posts the summary data for the entry.
    3. Posts the transcript data for the entry.

    If any of these operations fail, it logs an error and returns early.
    """

    channel_dict = get_channel_dict_for_post(channel)
    url = build_url(BASE_URL, 'channels', API_URL_SECRET_STRING)
    new_channel = post_request(channel_dict, url)

    if new_channel.status_code != 201:
        logger.error(f"FAILED to create channel in the database. Status code: {new_channel.status_code}.  at {url}, for channel: {channel_dict}")
        return

    channel_id = new_channel.json()['id']

    channel['id'] = channel_id
   
    logger.info(f"Successfully created channel in the database for channel: {channel.get('title', 'No title')}")




def post_channels_to_server(pods):
    """
    Posts data for all entries in all channels to the server.

    Args:
        pods (list): A list of tuples, where each tuple contains a channel dictionary
                     and a list of entry dictionaries for that channel.

    Returns:
        None

    This function iterates through all channels and their entries, posting each entry's
    data to the server. It logs the progress and any errors encountered during the process.
    """


    for index, (channel, entries) in enumerate(pods):
        logger.info(f"Posting channel {channel['title']}")

        new_channel = post_data_for_channel(channel)

        channel_id = channel.get('id', None)

        if channel_id is None:
            logger.error(f"Channel ID not found for channel {channel.get('title', 'No title')}")
            return



def save_results(pods_with_summaries, pickle_filename, json_filename):
    """
    Save the podcast entries with transcripts to both pickle and JSON files.

    Args:
        pods_with_summaries (list): List of channels and entries with summaries attached.
        pickle_filename (str): Filename for the pickle file.
        json_filename (str): Filename for the JSON file.
    """
    save_to_pickle(pods_with_summaries, pickle_filename)
    convert_to_json_and_save(pods_with_summaries, json_filename)



def post_channels():
    
     # Load the new entries with summaries from the pickle file
    pods = load_from_pickle(NEW_ENTRIES_WITH_SUMMARIES_PICKLE)

    # Post the loaded data to the server
    post_channels_to_server(pods)


    save_results(pods, NEW_ENTRIES_WITH_SUMMARIES_PICKLE, NEW_ENTRIES_WITH_SUMMARIES_JSON)

    # Log a success message
    logger.info("post_channels.py ran successfully")
