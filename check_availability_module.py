from datetime import datetime
import logging
import json
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

# This gets the main part started and looping
def run_availability_check_loop(webScrapeManager, dataManager, jsonManager, selectorJson):
    """
    Run the availability check in a loop with a user-defined sleep interval.
    """
    # Prompt the user for sleep duration
    try:
        sleep_minutes = int(input("Enter the number of minutes to sleep between checks: "))
    except ValueError:
        print("Invalid input. Defaulting to 480 minutes (8 hours).")
        sleep_minutes = 480

    # Convert minutes to seconds
    sleep_seconds = sleep_minutes * 60

    # Run the availability check in a loop
    while True:
        try:
            check_availability(webScrapeManager, dataManager, jsonManager, selectorJson)
            print(f"Availability check completed. Sleeping for {sleep_minutes} minutes...")
            time.sleep(sleep_seconds)
        except KeyboardInterrupt:
            print("Availability check loop interrupted by user. Exiting...")
            break
        except Exception as e:
            logging.error(f"Error during availability check loop: {e}")
            break

# This is the main part of this program
def check_availability(webScrapeManager, dataManager, jsonManager, selectorJson):
    """Main availability check function."""
    current_datetime = datetime.now()
    logging.info(f"""
------------------------------------------------------------
                 AVAILABILITY CHECK INITIATED
                     {current_datetime}          
------------------------------------------------------------""")

    # Load JSON selectors
    jsonData = jsonManager.load_json_selectors(selectorJson)

    # This sets up workers to do the code in parallel and not serial
    with ThreadPoolExecutor(max_workers=6) as executor:
        future_to_site = {}

        for militariaSite in jsonData:
            source = militariaSite.get("source", "Unknown")

            # Log the JSON for debugging
            logging.debug(f"Processing site '{source}' JSON data: {militariaSite}")

            # Validate JSON profile
            try:
                jsonManager.validate_json_profile(militariaSite)
            except ValueError as e:
                logging.error(f"Validation error for site '{source}': {e}")
                continue

            availableElement = militariaSite.get("available_element")

            if availableElement in ["True", "False"]:
                # Skip sites with hardcoded availableElement
                logging.info(f"Skipping site '{source}' as availableElement is set to '{availableElement}'")
                continue

            try:
                # Determine whether to use full scraping or availableElement logic
                if availableElement:
                    future = executor.submit(process_site_with_available_element, webScrapeManager, dataManager, militariaSite)
                else:
                    future = executor.submit(process_site_full_scrape, webScrapeManager, dataManager, militariaSite)
                future_to_site[future] = source
            except Exception as e:
                logging.error(f"Error submitting task for site '{source}': {e}")

        # Collect results
        for future in as_completed(future_to_site):
            site = future_to_site[future]
            try:
                future.result()
                logging.info(f"Finished processing site: {site}")
            except Exception as e:
                logging.error(f"Error processing site {site}: {e}")

def process_site_with_available_element(webScrapeManager, dataManager, militariaSite):
    """Check product availability using the availableElement."""
    source = militariaSite["source"]
    availableElement = militariaSite["available_element"]

    logging.info(f"Processing site '{source}' using availableElement logic...")

    # Fetch products from database
    query = "SELECT url, available FROM militaria WHERE site = %s"
    products = dataManager.sqlFetch(query, (source,))

    for url, db_available in products:
        try:
            productSoup = webScrapeManager.fetch_page(url)
            if not productSoup:
                logging.warning(f"Failed to fetch product: {url}")
                continue

            # Evaluate availableElement
            scraped_available = bool(eval(availableElement))
            if scraped_available != db_available:
                update_query = "UPDATE militaria SET available = %s, date_modified = %s WHERE url = %s"
                dataManager.sqlExecute(update_query, (scraped_available, datetime.now(), url))
                logging.info(f"Product {url} availability updated to {scraped_available}")
        except Exception as e:
            logging.error(f"Error processing product {url}: {e}")

def process_site_full_scrape(webScrapeManager, dataManager, militariaSite):
    """Perform full-site scraping and compare product URLs with the database."""
    source = militariaSite["source"]
    logging.info(f"Processing site '{source}' using full-site scraping...")

    try:
        productUrlElement = militariaSite["product_url_element"]
        productsPageUrl = militariaSite["productsPageUrl"]
        base_url = militariaSite["base_url"]
    except KeyError as e:
        logging.error(f"Missing required JSON key {e} for site '{source}'")
        return

    scraped_urls = set()
    page = 0  # Start scraping from page 0
    while True:
        try:
            page_url = productsPageUrl.format(page=page)
            productSoup = webScrapeManager.fetch_page(page_url)
            if not productSoup:
                break

            products_on_page = productSoup.select(productUrlElement)
            if not products_on_page:
                break

            for product in products_on_page:
                scraped_urls.add(base_url + product["href"])

            page += 1
        except Exception as e:
            logging.error(f"Error scraping page {page} for site '{source}': {e}")
            break

    # Fetch product URLs from the database
    query = "SELECT url FROM militaria WHERE site = %s"
    db_products = dataManager.sqlFetch(query, (source,))
    db_urls = {row[0] for row in db_products}

    # Compare scraped URLs with database URLs
    unavailable_urls = db_urls - scraped_urls
    for url in unavailable_urls:
        try:
            update_query = "UPDATE militaria SET available = FALSE, date_modified = %s WHERE url = %s"
            dataManager.sqlExecute(update_query, (datetime.now(), url))
            logging.info(f"Marked product as unavailable: {url}")
        except Exception as e:
            logging.error(f"Error marking product {url} as unavailable: {e}")
