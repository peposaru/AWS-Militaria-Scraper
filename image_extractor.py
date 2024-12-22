import logging
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
