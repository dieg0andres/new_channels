from decouple import config
from helpers.setup_logging import setup_logging
from helpers.utils import parse_rss
from helpers.pickle_helpers import save_to_pickle
from helpers.json_helpers import convert_to_json_and_save


logger = setup_logging('get_new_channels_and_entries')



NEW_ENTRIES_PICKLE = config('NEW_ENTRIES_PICKLE')
NEW_ENTRIES_JSON = config('NEW_ENTRIES_JSON')



def get_new_channels_and_entries(urls):
    
    pods = []

    for count, url in enumerate(urls):
        logger.info(f"Parcing url {count+1} of {len(urls)} total")

        channel, entries = parse_rss(url)

        if channel is not None and entries is not None:
            pods.append((channel, entries))    
        else:
            logger.error(f"Failed to parse url {url}")

    if len(pods) > 0:

        convert_to_json_and_save(pods, NEW_ENTRIES_JSON)
        save_to_pickle(pods, NEW_ENTRIES_PICKLE)

        return True
    else:
        logger.warning("No new channels and entries were successfully parsed")
        return False

    
