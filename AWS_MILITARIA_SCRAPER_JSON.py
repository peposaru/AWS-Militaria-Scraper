from concurrent.futures import ThreadPoolExecutor, as_completed
import os
import json
import logging
import time
from datetime import datetime
from time import sleep
from aws_postgresql_manager import PostgreSQLProcessor
from web_scraper import ProductScraper
from militaria_json_manager import JsonManager
from log_print_manager import log_print
from settings_manager import get_user_settings, site_choice
from site_product_processor import process_site
from aws_s3_manager import S3Manager
from check_availability_module import run_availability_check_loop

# Sets up logging for the rest of the program
def initialize_logging():
    log_dir = "logs"
    os.makedirs(log_dir, exist_ok=True)
    current_date = datetime.now().strftime("%Y-%m-%d")
    existing_logs = [f for f in os.listdir(log_dir) if f.startswith(current_date)]
    instance_number = len(existing_logs) + 1
    log_file_name = f"{current_date}_instance_{instance_number}.log"
    log_file_path = os.path.join(log_dir, log_file_name)
    logging.basicConfig(
        level=logging.DEBUG, # Levels are NOTSET , DEBUG , INFO , WARN , ERROR , CRITICAL
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file_path, encoding='utf-8'),
            logging.StreamHandler()
        ]
    )
    logging.info(f"Logging initialized. Log file: {log_file_path}")


def main():
    print('INITIALIZING. PLEASE WAIT...')
    initialize_logging()

    # Setting up the enviroment in which this program is running.
    try:
        targetMatch, sleeptime, user_settings, run_availability_check = get_user_settings()
        infoLocation = user_settings["infoLocation"]
        pgAdminCred  = user_settings["pgAdminCred"]
        selectorJson = user_settings["selectorJson"]
        s3Cred       = user_settings["s3Cred"]
    except KeyError as e:
        logging.error(f"Error accessing user settings: {e}")
        return

    # Switching to designated info / credentials location.
    try:
        os.chdir(infoLocation)
    except Exception as e:
        logging.error(f"Error changing directory to {infoLocation}: {e}")
        return

    # Logging when the program initialized
    logging.warning(f"\n{'-'*60}\nPROGRAM INITIALIZED {datetime.now()}\n{'-'*60}")

    # Setting up the object managers
    try:
        dataManager      = PostgreSQLProcessor(credFile=pgAdminCred)
        s3_manager       = S3Manager(s3Cred)
        webScrapeManager = ProductScraper(dataManager)
        jsonManager      = JsonManager()
        prints           = log_print()
    except KeyError as e:
        logging.error(f"Error accessing user settings: {e}")
        return
    except RuntimeError as e:
        logging.error(f"Error loading S3 credentials: {e}")
        return

    # Run Availability Check if selected
    if run_availability_check:
        run_availability_check_loop(webScrapeManager, dataManager, jsonManager, selectorJson)

    # Load JSON selectors
    try: 
        jsonData = jsonManager.load_json_selectors(selectorJson)
    except Exception as e:
        logging.error(f"Error retrieving jsonData: {e}")

    # Which sites to process
    selected_sites = site_choice(jsonData)

    # How many times has the program gone through all the sites?
    runCycle          = 0
    # How many products total has the program gone through?
    productsProcessed = 0

    # This is the main loop which keeps everything going.
    while True:  
        for site in selected_sites:
            try:
                # From this point it is pretty much all site_product_processor.py
                process_site(
                webScrapeManager, dataManager, jsonManager, prints, site,
                targetMatch, runCycle, productsProcessed, s3_manager
                )
                logging.info(f"Successfully processed site: {site['source']}")
            except Exception as e:
                logging.error(f"Error processing site {site['source']}: {e}")

        # Use the user-defined sleeptime between cycles
        if sleeptime > 0:
            logging.info(f"Pausing for {sleeptime} seconds before starting the next cycle...")
            try:
                for _ in range(sleeptime):
                    sleep(1)
            except Exception as e:
                logging.error(f"Error during sleep: {e}")
        else:
            logging.info("No pause configured (sleeptime = 0). Starting the next cycle immediately.")


if __name__ == "__main__":
    main()