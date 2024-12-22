import logging, time
from bs4 import BeautifulSoup

def woo_commerce(product_soup):
    """
    Extracts high-quality images from WooCommerce product pages.

    Args:
        product_soup (BeautifulSoup): Parsed HTML of the product page.

    Returns:
        list: List of URLs for the largest images.
    """
    try:
        # Extract `data-large_image` directly if available
        large_image_urls = [
            tag['data-large_image']
            for tag in product_soup.select("div.woocommerce-product-gallery__image")
            if 'data-large_image' in tag.attrs
        ]
        
        # If `data-large_image` is missing, fallback to the <a href>
        if not large_image_urls:
            large_image_urls = [
                a_tag['href']
                for a_tag in product_soup.select("div.woocommerce-product-gallery__image a")
                if 'href' in a_tag.attrs
            ]

        return large_image_urls
    except Exception as e:
        logging.error(f"Error in woo_commerce: {e}")
        return []

def woo_commerce2(product_soup):
    """
    Extracts high-quality images from WooCommerce-like vertical gallery product pages.

    Args:
        product_soup (BeautifulSoup): Parsed HTML of the product page.

    Returns:
        list: List of URLs for the largest images.
    """
    try:
        # Extract URLs from `data-zoom` attribute
        logging.debug("Attempting to extract URLs from `data-zoom` attributes.")
        large_image_urls = [
            div['data-zoom']
            for div in product_soup.select("div.product.item-image.imgzoom")
            if 'data-zoom' in div.attrs
        ]

        # Log extracted URLs
        logging.debug(f"Extracted URLs from `data-zoom`: {large_image_urls}")

        # Fallback to <a href> if `data-zoom` is not present
        if not large_image_urls:
            logging.debug("Falling back to extracting URLs from `<a href>`.")
            large_image_urls = [
                a_tag['href']
                for a_tag in product_soup.select("div.product.item-image.imgzoom a")
                if 'href' in a_tag.attrs
            ]
            logging.debug(f"Extracted URLs from `<a href>`: {large_image_urls}")

        # Add a delay to prevent rate limiting or server overload
        for url in large_image_urls:
            logging.debug(f"Processing URL: {url}")
            if not isinstance(url, str):
                logging.error(f"Invalid URL type: {type(url)}. URL: {url}")
                continue
            time.sleep(1)  # 1-second delay between processing each image

        return large_image_urls
    except Exception as e:
        logging.error(f"Error in woo_commerce2: {e}")
        return []

    
def extract_default_gallery(product_soup):
    """
    Extracts images using default gallery logic with data-large_image.
    """
    try:
        return [
            tag['data-large_image']
            for tag in product_soup.select("div.woocommerce-product-gallery__image")
            if 'data-large_image' in tag.attrs
        ]
    except Exception as e:
        logging.error(f"Error in extract_default_gallery: {e}")
        return []

def extract_img_src_fallback(product_soup):
    """
    Extracts images by falling back to <img src> within a gallery.
    """
    try:
        return [
            img_tag["src"]
            for img_tag in product_soup.select("div.product-gallery img")
            if "src" in img_tag.attrs
        ]
    except Exception as e:
        logging.error(f"Error in extract_img_src_fallback: {e}")
        return []

def extract_site_specific(product_soup):
    """
    Custom extraction logic for a specific site.
    """
    try:
        # Add specific site logic here
        return []
    except Exception as e:
        logging.error(f"Error in extract_site_specific: {e}")
        return []

def fetch_images(product_soup, function_name):
    """
    Fetch images dynamically based on function name.

    Args:
        product_soup (BeautifulSoup): Parsed HTML of the product page.
        function_name (str): Name of the function to use for image extraction.

    Returns:
        list: List of image URLs.
    """
    try:
        # Dynamically fetch the function
        func = globals()[function_name]
        return func(product_soup)
    except KeyError:
        logging.error(f"Function {function_name} not found.")
        return []
    except Exception as e:
        logging.error(f"Error fetching images: {e}")
        return []
