from datetime import datetime
import logging
import json
from concurrent.futures import ThreadPoolExecutor, as_completed
from threading import Semaphore


def check_availability(webScrapeManager, dataManager, jsonManager, selectorJson):
    current_datetime = datetime.now()
    logging.info(f"""
------------------------------------------------------------
                 AVAILABILITY CHECK INITIATED
                     {current_datetime}          
------------------------------------------------------------""")

    # Load JSON selectors
    try:
        with open(selectorJson, 'r') as userFile:
            jsonData = json.load(userFile)
    except Exception as e:
        logging.error(f"Error loading JSON selector file: {e}")
        return

    # Semaphore for per-site limits
    site_semaphores = {}

    # Thread pool with 6 total workers
    with ThreadPoolExecutor(max_workers=6) as executor:
        future_to_url = {}

        for militariaSite in jsonData:
            (
                conflict, nation, item_type, grade, source, pageIncrement, currency, products,
                productUrlElement, titleElement, descElement, priceElement, availableElement,
                productsPageUrl, base_url
            ) = jsonManager.jsonSelectors(militariaSite)

            if source not in site_semaphores:
                site_semaphores[source] = Semaphore(3)  # Max 3 workers per site

            # Fetch all products for the site
            query = "SELECT url, title, description, price, available FROM militaria WHERE site = %s"
            try:
                all_products = dataManager.sqlFetch(query, (source,))
            except Exception as e:
                logging.error(f"Error fetching data for site {source}: {e}")
                continue

            # Submit tasks
            for product_record in all_products:
                product_url, db_title, db_desc, db_price, db_available = product_record
                future = executor.submit(
                    process_product, webScrapeManager, dataManager, product_url, db_title, db_desc, db_price,
                    db_available, titleElement, descElement, priceElement, availableElement, site_semaphores[source]
                )
                future_to_url[future] = product_url

        # Process results
        for future in as_completed(future_to_url):
            url = future_to_url[future]
            try:
                future.result()
            except Exception as e:
                logging.error(f"Error processing URL {url}: {e}")


def process_product(webScrapeManager, dataManager, product_url, db_title, db_desc, db_price, db_available,
                    titleElement, descElement, priceElement, availableElement, semaphore):
    with semaphore:
        try:
            productSoup = webScrapeManager.fetch_page(product_url)
            if not productSoup:
                logging.warning(f"Failed to fetch product: {product_url}")
                return

            # Use eval() safely with fallbacks
            try:
                scraped_title = eval(titleElement) if titleElement else "N/A"
            except Exception:
                scraped_title = "N/A"
                logging.warning(f"Failed to extract title for {product_url}")

            try:
                scraped_desc = eval(descElement) if descElement else "N/A"
            except Exception:
                scraped_desc = "N/A"
                logging.warning(f"Failed to extract description for {product_url}")

            try:
                price_text = eval(priceElement) if priceElement else "0"
                scraped_price = float(price_text.replace("GBP", "").replace(",", "").strip())
            except Exception:
                scraped_price = 0
                logging.warning(f"Failed to extract price for {product_url}")

            try:
                scraped_available = eval(availableElement) if availableElement else False
                scraped_available = bool(scraped_available)  # Ensure boolean result
            except Exception:
                scraped_available = False
                logging.warning(f"Failed to extract availability for {product_url}")

            # Compare values and prepare updates
            updates = {}
            if scraped_title != db_title:
                updates['new_title'] = scraped_title
            if scraped_desc != db_desc:
                updates['new_description'] = scraped_desc
            if scraped_price != db_price:
                updates['new_price'] = scraped_price
            if scraped_available != db_available:
                updates['available'] = scraped_available
                updates['date_sold'] = None if scraped_available else datetime.now().strftime('%Y-%m-%d %H:%M:%S')

            # If there are updates, execute the query
            if updates:
                updates['date_modified'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                set_clause = ", ".join([f"{key} = %s" for key in updates.keys()])
                update_query = f"UPDATE militaria SET {set_clause} WHERE url = %s"
                dataManager.sqlExecute(update_query, (*updates.values(), product_url))
                logging.info(f"Updated product: {product_url}")
            else:
                logging.info(f"No changes for product: {product_url}")

        except Exception as e:
            logging.error(f"Error processing product {product_url}: {e}")
