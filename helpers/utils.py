import datetime
import feedparser
import time

from decouple import config
from helpers.setup_logging import setup_logging
from helpers.http_request_helper import get_channels, post_request


logger = setup_logging("utils")


ENV = config('ENV')
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



def count_total_entries(pods):
    """
    Counts the total number of entries across all tuples in the pods list.
    
    Args:
        pods (list): A list of tuples where the second element in each tuple is a list of entries (dictionaries).

    Returns:
        int: The total number of entries across all tuples.
    """
    total_entries = 0

    # Iterate over each tuple in pods
    for _, entries in pods:
        total_entries += len(entries)  # Add the number of entries in the current tuple

    return total_entries



def convert_time_to_iso(time_struct):
    if isinstance(time_struct, time.struct_time):
        updated_parsed_dt = datetime.datetime(*time_struct[:6])  # Convert to datetime
        updated_parsed_iso = updated_parsed_dt.isoformat()  # Convert to ISO 8601 string
    else:
        updated_parsed_iso = None  # Handle missing or invalid date

    return updated_parsed_iso



def parse_rss(rss_url):
    """
    Parses an RSS feed and extracts channel information and entries to match the format of the PODSUM API (model)
    Returns a tuple of channel and entry dictionaries.
    """
    # Parse the RSS feed
    try:
        d = feedparser.parse(rss_url)
        if not d or d.bozo:  # bozo indicates parsing errors
            logger.error(f"Failed to parse RSS feed from {rss_url}")
            raise ValueError(f"Failed to parse RSS feed from {rss_url}")
    except Exception as e:
        logger.error(f"Error parsing RSS feed: {e}")
        return None, None

    # Extract channel information with defaulting to None if not present
    channel = {
        "author": d.feed.get("author", None),
        "category": d.feed.get("category", None),
        "description": d.feed.get("description", None),
        "image": d.feed.get("image", {}).get("href", None) if "image" in d.feed else None,
        "subtitle": d.feed.get("subtitle", None),
        "summary": d.feed.get("summary", None),
        "title": d.feed.get("title", None),
        "updated_parsed": convert_time_to_iso(d.feed.get("updated_parsed", None)),
        "rss_url": rss_url
    }

    # Initialize for processing entries
    newest_entry = d.entries[0]
    
    entry = {
        "author": newest_entry.get("author", None),
        "id": newest_entry.get("id", None),
        "itunes_duration": newest_entry.get("itunes_duration", None),
        "links": newest_entry.get("links", None),
        "published_parsed": convert_time_to_iso(newest_entry.get("published_parsed", None)),
        "summary": newest_entry.get("summary", None),
        "title": newest_entry.get("title", None)
    }

    # Check for None values in channel dictionary
    for key, value in channel.items():
        if value is None:
            logger.warning(f"Channel '{channel.get('title', 'Unknown')}' has None value for '{key}'")

    # Check for None values in entry dictionary
    for key, value in entry.items():
        if value is None:
            logger.warning(f"Entry '{entry.get('title', 'Unknown')}' in channel '{channel.get('title', 'Unknown')}' has None value for '{key}'")

    return channel, [entry]





def process_url(url):
    """
    Steps to process a single RSS URL:
    """

    channel, entry = parse_rss(url)

    channel_response = post_request(channel, BASE_URL+'channels/')

    if channel_response.status_code == 201:
        channel = channel_response.json()

        entry['channel'] = channel['id']

        entry_response = post_request(entry, BASE_URL+'entries/')

        print('entry_response: ', entry_response.json())


    else:
        logger.error(f"Failed to create channel for URL {url}")
        return


    
def get_channel_dict_for_post(channel):
    return {
    'author': channel['author'],
    'category': channel['category'],
    'description': channel['description'],
    'image': channel['image'],
    'subtitle': channel['subtitle'],
    'summary': channel['summary'],
    'title': channel['title'],
    'updated_parsed': convert_time_to_iso(channel['updated_parsed']),
    'rss_url': channel['rss_url'],
    }


def get_entry_dict_for_post(entry, channel_id):
    return {
        'channel': channel_id,
        'author': entry['author'],
        '_id': entry['id'], #_id is the id of the RSS feed entry, not the PODSUM entry id
        'itunes_duration': entry['itunes_duration'],
        'links': entry['links'],
        'published_parsed': entry['published_parsed'],
        # 'published_parsed': convert_time_to_iso(entry['published_parsed']),
        '_summary': entry['summary'],
        'title': entry['title'],
    }



def get_summary_dict_for_post(entry, entry_id):

    summaries = {
        'entry': entry_id,
        'paragraph_summary': entry.get('paragraph_summary', ''),
        'bullet_summary': entry.get('bullet_summary', ''),
    }

    if summaries['paragraph_summary'] == '' or summaries['bullet_summary'] == '':
        return None

    return summaries

def get_transcript_dict_for_post(entry, entry_id):
    return {
        'entry': entry_id,
        'transcript': entry.get('transcript', ''),
    }