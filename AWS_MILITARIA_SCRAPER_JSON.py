# This is the AWS Cloud version of this program designed to be used with EC2 and RDS

# Making a more universal scraper which just takes a json library as input

import os
import json
import logging
import sys
from datetime import datetime
from time import sleep
from tqdm import trange
from aws_postgresql_manager import PostgreSQLProcessor  # Imported unchanged
from web_scraper import ProductScraper  # Imported unchanged
from militaria_json_manager import JsonManager  # Imported unchanged
from log_print_manager import log_print  # Imported unchanged
from settings_manager import get_user_settings  # Modified: Added for settings management
from site_product_processor import process_site  # Modified: Added to handle site processing
from check_availability_module import check_availability  # Importing check_availability

# Modified: Moved logging configuration into a reusable function
def initialize_logging():
    # Define the log directory
    log_dir = "logs"
    
    # Ensure the log directory exists
    os.makedirs(log_dir, exist_ok=True)
    
    # Get the current date for the log file name
    current_date = datetime.now().strftime("%Y-%m-%d")
    
    # Count existing log files for the current date to determine instance number
    existing_logs = [f for f in os.listdir(log_dir) if f.startswith(current_date)]
    instance_number = len(existing_logs) + 1
    
    # Define the log file name
    log_file_name = f"{current_date}_instance_{instance_number}.log"
    log_file_path = os.path.join(log_dir, log_file_name)
    
    # Configure logging with utf-8 encoding
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file_path, encoding='utf-8'),  # File logging with utf-8 encoding
            logging.StreamHandler(sys.stdout)  # Console logging explicitly set to stdout
        ]
    )
    logging.info(f"Logging initialized. Log file: {log_file_path}")

def main():
    print('INITIALIZING. PLEASE WAIT...')
    initialize_logging()

    # Get user settings
    try:
        targetMatch, user_settings, run_availability_check = get_user_settings()
        infoLocation = user_settings["infoLocation"]
        pgAdminCred = user_settings["pgAdminCred"]
        selectorJson = user_settings["selectorJson"]
    except KeyError as e:
        logging.error(f"Error accessing user settings: {e}")
        return

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
    try:
        dataManager = PostgreSQLProcessor(credFile=pgAdminCred)
        webScrapeManager = ProductScraper(dataManager)
        jsonManager = JsonManager()
        prints = log_print()
    except Exception as e:
        logging.error(f"Error initializing components: {e}")
        return

    # Load JSON selectors
    try:
        with open(selectorJson, 'r') as userFile:
            jsonData = json.load(userFile)
    except FileNotFoundError:
        logging.error(f'JSON selector file not found: {selectorJson}')
        return
    except json.JSONDecodeError as e:
        logging.error(f'Error decoding JSON selector file: {e}')
        return

    # Run availability check if selected by user
    if run_availability_check:
        try:
            check_availability(webScrapeManager, dataManager, jsonManager, selectorJson)
        except Exception as e:
            logging.error(f"Error running availability check: {e}")

    # Main loop for processing sites
    runCycle = 0
    productsProcessed = 0

    while True:
        for militariaSite in jsonData:
            try:
                process_site(
                    webScrapeManager, dataManager, jsonManager, prints, militariaSite,
                    targetMatch, runCycle, productsProcessed
                )
            except Exception as e:
                logging.error(f"Error processing site {militariaSite.get('source', 'Unknown')}: {e}")

        # Pause between cycles
        sleepTime = int(os.getenv('CYCLE_PAUSE_SECONDS', 300))  # Default: 300 seconds
        runCycle += 1
        prints.standby()

        for _ in trange(sleepTime, desc="Waiting for the next cycle", unit="seconds"):
            sleep(1)

if __name__ == "__main__":
    main()