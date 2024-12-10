import logging
import json
from datetime import datetime
from web_scraper import ProductScraper

# Create an instance of ProductScraper
product_scraper = ProductScraper(spreadSheetManager=None)

def check_availability(webScrapeManager, dataManager, jsonManager, selectorJson):
    current_datetime = datetime.now()
    logging.info(f"""
------------------------------------------------------------
                 AVAILABILITY CHECK INITIATED
                     {current_datetime}          
------------------------------------------------------------""")

    # User input for the type of check
    print("Select the type of check to perform:")
    print("1. Check only Available items (Default check on available items to see if they have been sold.)")
    print("2. Check only Unavailable items (Double Checking Unavailable items that may have become available again.)")
    print("3. Check both Available and Unavailable items (Checking all products.)")
    choice = input("Enter your choice (1/2/3): ").strip()

    if choice not in {"1", "2", "3"}:
        print("Invalid choice! Please restart and select a valid option.")
        return

    # Determine what to check based on the choice
    check_available_items = choice in {"1", "3"}
    check_unavailable_items = choice in {"2", "3"}

    # Load JSON selectors
    try:
        with open(selectorJson, 'r') as userFile:
            jsonData = json.load(userFile)
    except Exception as e:
        logging.error(f'Error loading JSON selector file: {e}')
        return

    total_urls_checked = 0
    error_count = 0
    update_count = 0
    no_update_count = 0

    # Iterate over each site in JSON
    for militariaSite in jsonData:
        (
            conflict, nation, item_type, grade, source, pageIncrement, currency, products,
            productUrlElement, titleElement, descElement, priceElement, availableElement,
            productsPageUrl, base_url
        ) = jsonManager.jsonSelectors(militariaSite)

        # Combine URLs to be checked based on the choice
        product_urls = []
        if check_available_items:
            query_available = "SELECT url FROM militaria WHERE site = %s AND available = %s"
            try:
                product_urls_available = dataManager.sqlFetch(query_available, (source, True))
                product_urls.extend(product_urls_available)
            except Exception as e:
                logging.error(f"Error executing SQL fetch for available items: {e}")
                return

        if check_unavailable_items:
            query_unavailable = "SELECT url FROM militaria WHERE site = %s AND available = %s"
            try:
                product_urls_unavailable = dataManager.sqlFetch(query_unavailable, (source, False))
                product_urls.extend(product_urls_unavailable)
            except Exception as e:
                logging.error(f"Error executing SQL fetch for unavailable items: {e}")
                return

        total_products = len(product_urls)

        # Log the total number of URLs to be processed for the site
        logging.info(f"Total URLs to be processed for site {source}: {total_products}")

        for index, product_url_record in enumerate(product_urls, start=1):
            total_urls_checked += 1
            product_url = product_url_record[0]  # Extract URL from tuple

            try:
                # Scrape availability using your specified logic
                try:
                    available = eval(availableElement) if product_scraper.productSoup else False
                except AttributeError as e:
                    logging.warning(f"AttributeError while evaluating available element: {e}")
                    available = False
                except Exception as err:
                    logging.warning('Unable to retrieve product AVAILABLE.')
                    logging.warning(f"Error while evaluating available element: {err}")
                    available = False

                # Determine if there is a change in availability
                current_availability_query = "SELECT available FROM militaria WHERE url = %s"
                current_availability = dataManager.sqlFetch(current_availability_query, (product_url,))[0][0]

                if available != current_availability:
                    # Update availability and set date_sold if necessary
                    update_query = """
                        UPDATE militaria
                        SET available = %s,
                            date_sold = %s
                        WHERE url = %s
                    """
                    date_sold = None if available else datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    dataManager.sqlExecute(update_query, (available, date_sold, product_url))
                    update_count += 1
                else:
                    no_update_count += 1

            except Exception as e:
                error_count += 1
                logging.error(f"Error processing URL {product_url}: {e}")

            # Log summary every 100 URLs checked
            if total_urls_checked % 100 == 0:
                logging.info(f"""
------------------------------------------------------------
               SUMMARY AFTER {total_urls_checked} URLS CHECKED
------------------------------------------------------------
Total Products Checked  : {total_urls_checked}
Products Updated        : {update_count}
Products with No Update : {no_update_count}
Errors Encountered      : {error_count}
------------------------------------------------------------
""")

    # Final summary after all URLs are processed
    logging.info(f"""
------------------------------------------------------------
                 FINAL SUMMARY AFTER COMPLETION
------------------------------------------------------------
Total Products Checked  : {total_urls_checked}
Products Updated        : {update_count}
Products with No Update : {no_update_count}
Errors Encountered      : {error_count}
------------------------------------------------------------
""")
