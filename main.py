import json
from decouple import config

from helpers.setup_logging import setup_logging

from remove_existing_urls import remove_existing_urls
from get_new_channels_and_entries import get_new_channels_and_entries
from generate_transcripts import generate_transcripts
from generate_summaries import generate_summaries
from post_channels import post_channels
from update_db import update_db


logger = setup_logging("main")



def main():
    """
    Main function to run the new_channels script.
    """
    logger.info("Starting the new_channels script")

    rss_urls = json.loads(config('RSS_URLS'))

    # 0. Remove existing channels from the list
    rss_urls = remove_existing_urls(rss_urls)


    # Check if rss_urls is empty
    if len(rss_urls) == 0:
        logger.warning("No new RSS URLs to process. All provided URLs already exist as channels in the database. Exiting the script.")
        return

    # 1. Get new entries
    if get_new_channels_and_entries(rss_urls):
        logger.info("New entries found")

        # 2. Generate transcripts
        generate_transcripts()
        logger.info("Transcripts generated")
        
        # 3. Generate summaries
        generate_summaries()
        logger.info("Summaries generated")

        # 3.1 Post the channels, get the channel ids
        post_channels()

        # 4. Update the db
        update_db()
        logger.info("database updated")


    else:
        logger.info("No new entries found.  Nothing updated to the database.")

    logger.info("new_channels script completed")




if __name__ == "__main__":

    main()