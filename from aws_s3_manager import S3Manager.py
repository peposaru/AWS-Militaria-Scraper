import logging
from bs4 import BeautifulSoup

# Function to extract image links
def extract_block_image_links(product_soup):
    """
    Extracts image links from HTML structured with 'content-part block-image' divs.

    Args:
        product_soup (BeautifulSoup): Parsed HTML of the product page.

    Returns:
        list: List of URLs for images found within the block-image divs.
    """
    try:
        # Extract `href` attributes from <a> tags within the block-image div
        image_urls = [
            tag['href']
            for tag in product_soup.select("div.content-part.block-image a")
            if 'href' in tag.attrs
        ]
        return image_urls
    except Exception as e:
        logging.error(f"Error in extract_block_image_links: {e}")
        return []

# Sample HTML inputs for testing
html_samples = [
    """
    <div class="content-part block-image">
        <a href="/photos/53750.jpg" class="fullImg" rel="prettyPhoto[53750]"><img src="/photos/53750.jpg"></a>
        <a href="/photos/53750a.jpg" class="thumbnail" rel="prettyPhoto[53750]"><img src="/photos/53750a.jpg"></a>
    </div>
    """,
    """
    <div class="content-part block-image">
        <a href="/photos/135.jpg" class="fullImg" rel="prettyPhoto[135]"><img src="/photos/135.jpg"></a>
        <a href="/photos/135a.jpg" class="thumbnail" rel="prettyPhoto[135]"><img src="/photos/135a.jpg"></a>
        <a href="/photos/135b.jpg" class="thumbnail" rel="prettyPhoto[135]"><img src="/photos/135b.jpg"></a>
    </div>
    """,
    """
    <div class="content-part block-image">
        <a href="/photos/7136.jpg" class="fullImg" rel="prettyPhoto[7136]"><img src="/photos/7136.jpg"></a>
        <a href="/photos/7136a.jpg" class="thumbnail" rel="prettyPhoto[7136]"><img src="/photos/7136a.jpg"></a>
        <a href="/photos/7136b.jpg" class="thumbnail" rel="prettyPhoto[7136]"><img src="/photos/7136b.jpg"></a>
    </div>
    """
]

# Set up logging
logging.basicConfig(level=logging.INFO)

# Test the function
if __name__ == "__main__":
    for idx, html in enumerate(html_samples, start=1):
        soup = BeautifulSoup(html, "html.parser")
        extracted_links = extract_block_image_links(soup)
        print(f"Sample {idx} - Extracted Links:")
        for link in extracted_links:
            print(link)
        print()  # Blank line for readability
