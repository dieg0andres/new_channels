from helpers.utils import convert_time_to_iso
from helpers.setup_logging import setup_logging

logger = setup_logging('dict_creation')


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
        'published_parsed': convert_time_to_iso(entry['published_parsed']),
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