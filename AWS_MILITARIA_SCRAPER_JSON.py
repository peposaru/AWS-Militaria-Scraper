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
from settings_manager import get_user_settings
from site_product_processor import process_site


def initialize_logging():
    log_dir = "logs"
    os.makedirs(log_dir, exist_ok=True)
    current_date = datetime.now().strftime("%Y-%m-%d")
    existing_logs = [f for f in os.listdir(log_dir) if f.startswith(current_date)]
    instance_number = len(existing_logs) + 1
    log_file_name = f"{current_date}_instance_{instance_number}.log"
    log_file_path = os.path.join(log_dir, log_file_name)

    logging.basicConfig(
        level=logging.DEBUG,
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

    try:
        targetMatch, sleeptime, user_settings, run_availability_check = get_user_settings()
        infoLocation = user_settings["infoLocation"]
        pgAdminCred = user_settings["pgAdminCred"]
        selectorJson = user_settings["selectorJson"]
    except KeyError as e:
        logging.error(f"Error accessing user settings: {e}")
        return

    try:
        os.chdir(infoLocation)
    except Exception as e:
        logging.error(f"Error changing directory to {infoLocation}: {e}")
        return

    current_datetime = datetime.now()
    logging.info(f"\n{'-'*60}\nPROGRAM INITIALIZED {current_datetime}\n{'-'*60}")

    try:
        dataManager = PostgreSQLProcessor(credFile=pgAdminCred)
        webScrapeManager = ProductScraper(dataManager)
        jsonManager = JsonManager()
        prints = log_print()
    except Exception as e:
        logging.error(f"Error initializing components: {e}")
        return

    # Run Availability Check if selected
    if run_availability_check:
        try:
            sleep_minutes = int(input("Enter the number of minutes to sleep between checks: "))
        except ValueError:
            print("Invalid input. Defaulting to 480 minutes (8 hours).")
            sleep_minutes = 480

        # Convert minutes to seconds
        sleep_seconds = sleep_minutes * 60

        while run_availability_check:
            from check_availability_module import check_availability
            check_availability(webScrapeManager, dataManager, jsonManager, selectorJson)
            print(f"Availability check completed. Sleeping for {sleep_minutes} minutes...")
            time.sleep(sleep_seconds)  # Sleep for user-defined minutes before the next run

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

    print("Available sites:")
    for idx, site in enumerate(jsonData):
        print(f"{idx + 1}. {site['source']}")

    try:
        choice = input("Select sites to scrape (e.g., '1,3-5,7'): ")
        selected_indices = set()
        for part in choice.split(','):
            if '-' in part:
                start, end = map(int, part.split('-'))
                selected_indices.update(range(start - 1, end))
            else:
                selected_indices.add(int(part) - 1)

        selected_indices = sorted(selected_indices)
        if any(idx < 0 or idx >= len(jsonData) for idx in selected_indices):
            raise ValueError("One or more indices are out of range.")

        selected_sites = [jsonData[idx] for idx in selected_indices]
    except ValueError as e:
        logging.error(f"Invalid selection: {e}")
        return

    runCycle = 0
    productsProcessed = 0

    while True:  # Infinite loop to keep cycling through the selected sites
        for site in selected_sites:
            try:
                process_site(
                    webScrapeManager, dataManager, jsonManager, prints, site,
                    targetMatch, runCycle, productsProcessed
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
