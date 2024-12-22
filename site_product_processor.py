from datetime import datetime, date
import logging, json

# Process a single product
def process_product(
    webScrapeManager, dataManager, prints, product, source, base_url, currency,
    conflict, nation, item_type, page, urlCount, consecutiveMatches, targetMatch,
    productUrlElement, titleElement, descElement, priceElement, availableElement,
    imageElement, s3_manager
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
        title, description, price, available, original_image_urls, uploaded_image_urls = fetch_and_scrape_product(
            webScrapeManager, productUrl, titleElement, descElement, priceElement,
            availableElement, imageElement, currency, source, s3_manager, dataManager
        )

        if not title:
            logging.warning(f"Failed to fetch or scrape product details for {productUrl}. Skipping.")
            return urlCount, consecutiveMatches

        # Update or insert product in the database
        urlCount, consecutiveMatches, updated = update_or_insert_product(
            dataManager, prints, productUrl, title, description, price, available,
            source, currency, conflict, nation, item_type, page, urlCount, consecutiveMatches,
            targetMatch, original_image_urls, uploaded_image_urls, s3_manager  ########## Added original and uploaded image URLs for clarity
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
def fetch_and_scrape_product(
    webScrapeManager, productUrl, titleElement, descElement, priceElement,
    availableElement, imageElement, currency, source, s3_manager, dataManager
):
    """
    Fetch the product page and scrape its details, including uploading images to S3.
    """
    try:
        productSoup = webScrapeManager.fetch_with_retries(
            webScrapeManager.scrapePage, productUrl, max_retries=3, backoff_factor=2
        )
        if not productSoup:
            logging.warning(f"Failed to fetch product page: {productUrl}")
            return None, None, None, None, [], []

        # Scrape product details
        title, description, price, available, image_urls = webScrapeManager.scrapeData(
            productSoup, titleElement, descElement, priceElement, availableElement,
            imageElement, currency, source
        )

        # Get product ID
        product_id_query = "SELECT id FROM militaria WHERE url = %s;"
        product_id_result = dataManager.sqlFetch(product_id_query, (productUrl,))
        if not product_id_result:
            logging.warning(f"Product ID not found for URL: {productUrl}")
            return title, description, price, available, image_urls, []

        product_id = product_id_result[0][0]  # Assign valid product_id

        # Upload all images to S3
        logging.debug(f"Extracted image URLs for product {productUrl}: {image_urls}")
        uploaded_image_urls = []
        for idx, url in enumerate(image_urls, start=1):
            object_name = f"{source}/{product_id}/{product_id}-{idx}.jpg"  # Construct object name with product ID and image index
            try:
                s3_manager.upload_image(url, object_name)
                uploaded_image_urls.append(f"s3://{s3_manager.bucket_name}/{object_name}")
            except Exception as e:
                logging.warning(f"Error uploading image {url}: {e}")

        return title, description, price, available, image_urls, uploaded_image_urls
    except Exception as e:
        logging.error(f"Error fetching and scraping product: {e}")
        return None, None, None, None, [], []


# Update or insert product in database
def update_or_insert_product(
    dataManager, prints, productUrl, title, description, price, available, source, 
    currency, conflict, nation, item_type, page, urlCount, consecutiveMatches, 
    targetMatch, original_image_urls, uploaded_image_urls, s3_manager
):
    """
    Update or insert product details into the database, including handling image URLs.
    """
    try:
        searchQuery = "SELECT url, available, date_sold, original_image_urls, s3_image_urls FROM militaria WHERE url = %s"  ########## Adjusted for original and S3 URLs
        existingProducts = dataManager.sqlFetch(searchQuery, (productUrl,))

        updated = False
        s3_image_urls_json = json.dumps(uploaded_image_urls)
        original_image_urls_json = json.dumps(original_image_urls)

        if existingProducts:
            existingProduct = existingProducts[0]
            original_available, original_date_sold, db_original_image_urls, db_s3_image_urls = existingProduct[1:]

            # Update available status
            if available != original_available:
                updateQuery = "UPDATE militaria SET available = %s WHERE url = %s;"
                dataManager.sqlExecute(updateQuery, (available, productUrl))
                updated = True

            # Update sold date
            if not available and original_date_sold is None:
                todayDate = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                updateSoldQuery = "UPDATE militaria SET date_sold = %s WHERE url = %s;"
                dataManager.sqlExecute(updateSoldQuery, (todayDate, productUrl))
                updated = True

            # Update image URLs
            if s3_image_urls_json != db_s3_image_urls or original_image_urls_json != db_original_image_urls:
                updateImageUrlsQuery = """
                    UPDATE militaria SET s3_image_urls = %s, original_image_urls = %s WHERE url = %s;
                """
                dataManager.sqlExecute(updateImageUrlsQuery, (s3_image_urls_json, original_image_urls_json, productUrl))
                updated = True
        else:
            todayDate = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            insertQuery = """
                INSERT INTO militaria (url, title, description, price, available, date, 
                site, currency, conflict, nation, item_type, s3_image_urls, original_image_urls)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """  ########## Insert now handles both original and S3 image URLs
            dataManager.sqlExecute(insertQuery, (
                productUrl, title, description, price, available, todayDate,
                source, currency, conflict, nation, item_type, s3_image_urls_json, original_image_urls_json
            ))
            updated = True

        consecutiveMatches = consecutiveMatches + 1 if updated else consecutiveMatches
    except Exception as e:
        logging.error(f"Error updating or inserting product: {e}")
    return urlCount + 1, consecutiveMatches, updated


def process_site(webScrapeManager, dataManager, jsonManager, prints, site, targetMatch, runCycle, productsProcessed, s3_manager):
    """
    Processes a single site based on the JSON selector configuration, scraping and updating/inserting products.
    """
    (
        conflict, nation, item_type, grade, source, pageIncrement, currency, products,
        productUrlElement, titleElement, descElement, priceElement, availableElement,
        productsPageUrl, base_url, imageElement
    ) = jsonManager.jsonSelectors(site)

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
                productUrlElement, titleElement, descElement, priceElement, availableElement,
                imageElement, s3_manager  # Passes the updated S3 manager handling to process_product
            )

            # Stop if the target match count is reached
            if consecutiveMatches == targetMatch:
                logging.info(f"Target match count ({targetMatch}) reached. Terminating site processing.")
                prints.terminating(source, consecutiveMatches, targetMatch, runCycle, productsProcessed)
                return

        # Increment to the next page
        page += int(pageIncrement)

    logging.info(f"Finished processing site: {source}")
