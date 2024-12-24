from bs4 import BeautifulSoup
from image_extractor import woo_commerce

# Sample HTML (shortened for brevity)
html = """
<div class="woocommerce-product-gallery__wrapper">
    <div class="woocommerce-product-gallery__image" data-large_image="https://fjm44.com/wp-content/uploads/2024/12/fjm_11866-scaled.jpg">
        <a href="https://fjm44.com/wp-content/uploads/2024/12/fjm_11866-scaled.jpg">
            <img src="https://fjm44.com/wp-content/uploads/2024/12/fjm_11866-100x100.jpg">
        </a>
    </div>
    <div class="woocommerce-product-gallery__image" data-large_image="https://fjm44.com/wp-content/uploads/2024/12/fjm_11865-scaled.jpg">
        <a href="https://fjm44.com/wp-content/uploads/2024/12/fjm_11865-scaled.jpg">
            <img src="https://fjm44.com/wp-content/uploads/2024/12/fjm_11865-100x100.jpg">
        </a>
    </div>
</div>
"""

soup = BeautifulSoup(html, "html.parser")
images = woo_commerce(soup)
print(images)
