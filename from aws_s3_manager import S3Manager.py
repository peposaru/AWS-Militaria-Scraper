from aws_s3_manager import S3Manager
"""
# Initialize S3Manager
s3_manager = S3Manager(r'C:/Users/keena/Desktop/Cloud Militaria Scraper/s3_credentials.json')

# Test image URL and S3 object name
test_image_url = "https://bevo-militaria.com/wp-content/uploads/2024/12/DSC_9530-scaled.jpg"
object_name = "test-folder/test-image.jpg"

# Attempt to upload
try:
    s3_manager.upload_image(test_image_url, object_name)
    print("Upload successful!")
except Exception as e:
    print(f"Upload failed: {e}")"""


from bs4 import BeautifulSoup
import requests

url = "https://bevo-militaria.com/shop/equipment/field-gear/wehrmacht-m31-aluminum-mess-kit-by-mn41/"

try:
    response = requests.get(url)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")
    
    # Print all divs with the target class for debugging
    gallery_divs = soup.find_all("div", class_="woocommerce-product-gallery__image")
    print("Found gallery divs:", gallery_divs)

    # Extract image URLs
    image_urls = [
        tag['data-large_image']
        for tag in gallery_divs
        if 'data-large_image' in tag.attrs
    ]
    
    print("Extracted image URLs:", image_urls)
except Exception as e:
    print(f"Error: {e}")



