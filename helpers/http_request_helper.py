import requests
from helpers.setup_logging import setup_logging

logger = setup_logging("http_request_helper")


def get_channels(api_base_url, secret_string=None):
    """
    Sends a GET request to retrieve the channels.

    :param api_base_url: The base URL of the API (e.g., 'http://localhost:8000/api/' or 'https://podsum.ai/api/')
    :return: A list of dicts (limited fields) of the channels data if available, None if not
    """

    if secret_string is None:
        url = f"{api_base_url}channels/limited-fields/"
    else:
        url = f"{api_base_url}{secret_string}/channels/limited-fields/"

    try:
        # Send GET request to the API
        response = requests.get(url)

        # Check if the request was successful
        if response.status_code == 200:
            logger.info(f"Successfully retrieved the channels from the PODSUM API")
            return response.json() 
        
        else:
            logger.error(f"Failed to retrieve channels. Status code: {response.status_code}, Response: {response.text}")
            return None
    except requests.exceptions.RequestException as e:
        logger.error(f"Error occurred while sending GET request: {e}")
        return None
    

def post_request(data_dict, url):
    """
    Sends a POST request with JSON data to the specified URL.

    Parameters:
    - data_dict (dict): The data dictionary to send as JSON.
    - url (str): The target URL for the POST request.

    Returns:
    - response (requests.Response): The response object from the POST request.
    """
    try:
        # Log the start of the request
        logger.info(f"Sending POST request to {url}")

        # Send POST request with JSON data
        response = requests.post(url, json=data_dict)
        
        # Log the successful request
        logger.info(f"POST request to {url} succeeded with status code {response.status_code}")

        # Raise an exception if the request was unsuccessful
        response.raise_for_status()

        # Return the response object if successful
        return response
    except requests.exceptions.RequestException as e:
        # Log the exception
        logger.error(f"An error occurred during POST request to {url}: {e}")
        return response