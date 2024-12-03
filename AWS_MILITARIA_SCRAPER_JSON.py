# This is the AWS Cloud version of this program designed to be used with EC2 and RDS

# Making a more universal scraper which just takes a json library as input

import os
import json
import logging
from datetime import datetime, date
from time import sleep
from tqdm import trange
from aws_postgresql_manager import PostgreSQLProcessor  # Imported unchanged
from web_scraper import ProductScraper  # Imported unchanged
from militaria_json_manager import JsonManager  # Imported unchanged
from log_print_manager import log_print  # Imported unchanged
from settings_manager import get_user_settings  # Modified: Added for settings management
from site_product_processor import process_site  # Modified: Added to handle site processing

# Modified: Moved logging configuration into a reusable function
def initialize_logging():
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler("AWS_militaria_scraper.log"),  # File logging unchanged
            logging.StreamHandler()  # Console logging unchanged
        ]
    )

def main():
    print('INITIALIZING. PLEASE WAIT...')
    initialize_logging()

    # Get user settings
    targetMatch, user_settings = get_user_settings()
    infoLocation = user_settings["infoLocation"]
    pgAdminCred = user_settings["pgAdminCred"]
    selectorJson = user_settings["selectorJson"]

    # Change to the directory containing settings and credentials
    try:
        os.chdir(infoLocation)
    except Exception as e:
        logging.error(f"Error changing directory to {infoLocation}: {e}")
        return

    current_datetime = datetime.now()
    logging.info(f"""
------------------------------------------------------------
                     PROGRAM INITIALIZED
                     {current_datetime}          
------------------------------------------------------------""")

    # Initialize PostgreSQL manager and other components
    dataManager = PostgreSQLProcessor(credFile=pgAdminCred)
    webScrapeManager = ProductScraper(dataManager)
    jsonManager = JsonManager()
    prints = log_print()

    # Load JSON selectors
    try:
        with open(selectorJson, 'r') as userFile:
            jsonData = json.load(userFile)
    except Exception as e:
        logging.error(f'Error loading JSON selector file: {e}')
        return

    # Main loop for processing sites
    runCycle = 0
    productsProcessed = 0

    while True:
        for militariaSite in jsonData:
            process_site(
                webScrapeManager, dataManager, jsonManager, prints, militariaSite,
                targetMatch, runCycle, productsProcessed
            )

        # Pause between cycles
        sleepTime = int(os.getenv('CYCLE_PAUSE_SECONDS', 300))  # Default: 300 seconds
        runCycle += 1
        prints.standby()

        for _ in trange(sleepTime, desc="Waiting for the next cycle", unit="seconds"):
            sleep(1)

if __name__ == "__main__":
    main()
