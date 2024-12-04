from datetime import datetime, date
import logging


# Process a single product
def process_product(
    webScrapeManager, dataManager, prints, product, source, base_url, currency,
    conflict, nation, item_type, page, urlCount, consecutiveMatches, targetMatch,
    productUrlElement, titleElement, descElement, priceElement, availableElement
):
    """
    Process a single product by constructing its URL, scraping details, and updating/inserting into the database.
    """
    try:
        # Dynamically evaluate the product URL element
        productUrl = construct_product_url(productUrlElement, base_url, product)
        if not productUrl:
            logging.warning("Product URL is invalid. Skipping this product.")
            return urlCount, consecutiveMatches

        # Fetch and scrape the product details
        title, description, price, available = fetch_and_scrape_product(
            webScrapeManager, productUrl, titleElement, descElement, priceElement, availableElement, currency, source
        )
        if not title:
            logging.warning(f"Failed to fetch or scrape product details for {productUrl}. Skipping.")
            return urlCount, consecutiveMatches

        # Update or insert product in the database
        urlCount, consecutiveMatches, updated = update_or_insert_product(
            dataManager, prints, productUrl, title, description, price, available,
            source, currency, conflict, nation, item_type, page, urlCount, consecutiveMatches, targetMatch
        )

        # Log based on whether the product was updated or not
        if updated:
            logging.info(f"Product '{productUrl}' was updated or inserted successfully.")
        else:
            logging.info(f"No changes made for product '{productUrl}'.")
    except Exception as e:
        logging.error(f"Error processing product: {e}")
    return urlCount, consecutiveMatches


def fetch_products_from_page(webScrapeManager, productsPage, productsSelector):
    """Fetch the product list from a site page using the provided selector."""
    soup = webScrapeManager.readProductPage(productsPage)
    if soup is None:
        logging.warning(f"Failed to load products page: {productsPage}")
        return None

    try:
        product_list = eval(productsSelector)
        return product_list
    except Exception as e:
        logging.error(f"Error parsing products on page {productsPage}: {e}")
        return None

# Construct product URL
def construct_product_url(productUrlElement, base_url, product):
    """Construct the product URL using the provided product selector and base URL."""
    try:
        productUrl = eval(productUrlElement)
        if not productUrl.startswith("http"):
            productUrl = base_url + productUrl
        logging.debug(f"Product URL constructed: {productUrl}")
        return productUrl
    except Exception as e:
        logging.error(f"Error constructing product URL: {e}")
        return None


# Fetch and scrape product details
def fetch_and_scrape_product(webScrapeManager, productUrl, titleElement, descElement, priceElement, availableElement, currency, source):
    """Fetch the product page and scrape its details."""
    try:
        productSoup = webScrapeManager.fetch_with_retries(
            webScrapeManager.scrapePage, productUrl, max_retries=3, backoff_factor=2
        )
        if not productSoup:
            logging.warning(f"Failed to fetch product page: {productUrl}")
            return None, None, None, None

        title, description, price, available = webScrapeManager.scrapeData(
            productSoup, titleElement, descElement, priceElement, availableElement, currency, source
        )
        logging.debug(f"Scraped data - Title: {title}, Price: {price}, Available: {available}")
        return title, description, price, available
    except Exception as e:
        logging.error(f"Error fetching or scraping product: {e}")
        return None, None, None, None


# Update or insert product in database
def update_or_insert_product(dataManager, prints, productUrl, title, description, price, available, source, currency, conflict, nation, item_type, page, urlCount, consecutiveMatches, targetMatch):
    """Update or insert product details into the database."""
    try:
        searchQuery = f"SELECT url, available, date_sold FROM militaria WHERE url LIKE '{productUrl}'"
        existingProducts = dataManager.sqlFetch(searchQuery)

        updated = False  # Track if any update is performed

        if productUrl in [product[0] for product in existingProducts]:
            # Fetch the existing product details
            existingProduct = next(product for product in existingProducts if product[0] == productUrl)
            original_available, original_date_sold = existingProduct[1:]

            # Update 'available' if it changes
            if available != original_available:
                updateAvailabilityQuery = f"UPDATE militaria SET available = {available} WHERE url = '{productUrl}';"
                dataManager.sqlExecute(updateAvailabilityQuery)
                logging.info(f"Product '{productUrl}' availability updated: {original_available} → {available}")
                updated = True

            # Update 'date_sold' if applicable and 'available' is False
            if not available:
                todayDate = datetime.now().strftime('%Y-%m-%d %H:%M:%S')  # Format for timestamp
                if original_date_sold is None or original_date_sold != todayDate:
                    updateSoldDateQuery = f"UPDATE militaria SET date_sold = '{todayDate}' WHERE url = '{productUrl}';"
                    dataManager.sqlExecute(updateSoldDateQuery)
                    logging.info(f"Product '{productUrl}' sold date updated: {original_date_sold} → {todayDate}")
                    updated = True

            if updated:
                logging.info(f"Product '{productUrl}' updated successfully.")
            else:
                logging.info(f"No updates required for product '{productUrl}'.")

            consecutiveMatches += 1
            prints.sysUpdate(page, urlCount, consecutiveMatches, productUrl, updated)
        else:
            # Insert the product if it doesn't exist
            todayDate = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            insertQuery = f"""
                INSERT INTO militaria (url, title, description, price, available, date, site, currency, conflict, nation, item_type)
                VALUES ('{productUrl}', '{title}', '{description}', {price}, {available}, '{todayDate}', '{source}', '{currency}', '{conflict}', '{nation}', '{item_type}')
            """
            dataManager.sqlExecute(insertQuery)
            logging.info(f"New product inserted: URL='{productUrl}', Title='{title}', Price={price}, Available={available}")
            prints.newProduct(page, urlCount, title, productUrl, description, price, available)
            consecutiveMatches = 0

        # Log only if an update or new insert occurred
        if updated:
            logging.info("------------------------------------------------------------")
            logging.info("                      PRODUCT UPDATED")
            logging.info("------------------------------------------------------------")

    except Exception as e:
        logging.error(f"Error updating or inserting product: {e}")

    return urlCount + 1, consecutiveMatches, updated





# Process a site
def process_site(webScrapeManager, dataManager, jsonManager, prints, militariaSite, targetMatch, runCycle, productsProcessed):
    """
    Processes a single site based on the JSON selector configuration, scraping and updating/inserting products.
    """
    (
        conflict, nation, item_type, grade, source, pageIncrement, currency, products,
        productUrlElement, titleElement, descElement, priceElement, availableElement,
        productsPageUrl, base_url
    ) = jsonManager.jsonSelectors(militariaSite)

    urlCount = 0
    consecutiveMatches = 0
    page = 0

    while consecutiveMatches != targetMatch:
        productsPage = base_url + productsPageUrl.format(page=page)
        logging.debug(f"Navigating to products page: {productsPage}")

        product_list = fetch_products_from_page(webScrapeManager, productsPage, products)
        if not product_list:
            logging.warning(f"No products found on page: {productsPage}")
            break

        prints.newInstance(source, productsPage, runCycle, productsProcessed)

        for product in product_list:
            if not product:
                logging.info("Empty product element found, skipping.")
                continue

            # Process each product and track updates
            urlCount, consecutiveMatches = process_product(
                webScrapeManager, dataManager, prints, product, source, base_url, currency,
                conflict, nation, item_type, page, urlCount, consecutiveMatches, targetMatch,
                productUrlElement, titleElement, descElement, priceElement, availableElement
            )

            # Stop if the target match count is reached
            if consecutiveMatches == targetMatch:
                logging.info(f"Target match count ({targetMatch}) reached. Terminating site processing.")
                prints.terminating(source, consecutiveMatches, runCycle, productsProcessed)
                return

        # Increment to the next page
        page += int(pageIncrement)

    logging.info(f"Finished processing site: {source}")
