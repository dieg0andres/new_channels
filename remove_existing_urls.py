from decouple import config
from helpers.setup_logging import setup_logging
from helpers.http_request_helper import get_channels



logger = setup_logging('remove_existing_urls')



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




def _remove_urls_of_existing_channels(rss_urls):
    """
    Remove URLs of existing channels from the provided list of RSS URLs.

    This function filters out URLs that correspond to channels already present in the PODSUM API.

    :param rss_urls: A list of RSS URLs to process.  Each URL is a string.
    :type rss_urls: list of str

    :return: A filtered list of RSS URLs, excluding those that match existing channels.
    :rtype: list of str

    The function performs the following steps:
    1. Retrieves all existing channels from the PODSUM API using the get_channels function. For each channel, we get the 'id', 'rss_url', and 'title'.
    2. Iterates through each URL in the provided rss_urls list.
    3. For each URL, checks if it matches the RSS URL of any existing channel.
    4. If a match is found, removes that URL from the rss_urls list.
    5. Returns the filtered list of RSS URLs.

    This process ensures that only new, unique RSS feeds are retained for further processing,
    preventing the addition of duplicate channels to the PODSUM API.
    """

    # Retrieve all existing channels from the API
    channels = get_channels(BASE_URL, API_URL_SECRET_STRING)
    
    # Create a set of existing RSS URLs for efficient lookup
    existing_urls = {channel['rss_url'] for channel in channels}

    # Use a list comprehension to filter out existing URLs
    filtered_urls = [url for url in rss_urls if url not in existing_urls]

    # Log the number of URLs removed
    removed_count = len(rss_urls) - len(filtered_urls)
    logger.info(f"Removed {removed_count} existing URLs from the input list.")

    # Update the original list with the filtered results
    rss_urls[:] = filtered_urls

    return rss_urls


def remove_existing_urls(rss_urls):
    return _remove_urls_of_existing_channels(rss_urls)
