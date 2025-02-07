import boto3
import requests
import logging
import json
from urllib.parse import urlparse


class S3Manager:
    def __init__(self, credentials_file):
        """
        Initialize the S3 Manager with provided AWS credentials.
        
        Args:
            credentials_file (str): Path to the JSON file containing S3 credentials.
        """
        credentials = self.load_s3_credentials(credentials_file)
        self.bucket_name = credentials["bucketName"]
        self.s3 = boto3.client(
            's3',
            aws_access_key_id=credentials["accessKey"],
            aws_secret_access_key=credentials["secretKey"],
            region_name=credentials["region"]
        )
        logging.info(f"S3Manager initialized for bucket {self.bucket_name}")

    @staticmethod
    def load_s3_credentials(file_path):
        """
        Load S3 credentials from a JSON file.
        
        Args:
            file_path (str): Path to the JSON file containing credentials.
        
        Returns:
            dict: Dictionary with S3 credentials.
        """
        try:
            with open(file_path, "r") as file:
                return json.load(file)
        except Exception as e:
            raise RuntimeError(f"Error loading S3 credentials: {e}")

    def object_exists(self, object_name):
        """
        Check if an object exists in the S3 bucket.
        
        Args:
            object_name (str): The object key to check in the S3 bucket.
        
        Returns:
            bool: True if the object exists, False otherwise.
        """
        try:
            self.s3.head_object(Bucket=self.bucket_name, Key=object_name)
            logging.debug(f"Object {object_name} exists in S3 bucket.")
            return True
        except self.s3.exceptions.ClientError as e:
            if e.response['Error']['Code'] == "404":
                logging.debug(f"Object {object_name} does not exist in S3 bucket.")
                return False
            logging.error(f"Error checking object {object_name} existence: {e}")
            raise

    def upload_image(self, image_url, object_name):
        """
        Upload an image to S3.
        
        Args:
            image_url (str): URL of the image to upload.
            object_name (str): S3 object key to use for the uploaded image.
        """
        try:
            # Fetch image data
            logging.debug(f"Fetching image from {image_url}")
            response = requests.get(image_url, stream=True, timeout=10)
            response.raise_for_status()

            # Upload image to S3
            self.s3.upload_fileobj(response.raw, self.bucket_name, object_name)
            logging.info(f"Uploaded to S3: {object_name}")
        except requests.exceptions.RequestException as e:
            logging.error(f"Error fetching image {image_url}: {e}")
        except Exception as e:
            logging.error(f"Error uploading image to S3: {e}")

    def upload_images_for_product(self, product_id, image_urls, site_name, product_url):
        """
        Upload multiple images for a product to S3, avoiding duplicates.
        
        Args:
            product_id (int): ID of the product associated with the images.
            image_urls (list): List of image URLs to upload.
            site_name (str): Name of the site being scraped.
            product_url (str): URL of the product page.
        
        Returns:
            list: List of successfully uploaded S3 object URLs.
        """
        uploaded_image_urls = []
        for idx, image_url in enumerate(image_urls, start=1):
            # Construct object name for S3
            parsed_url = urlparse(image_url)
            extension = parsed_url.path.split('.')[-1]
            object_name = f"{site_name}/{product_id}/{product_id}-{idx}.{extension}"

            # Skip upload if the object already exists
            if self.object_exists(object_name):
                logging.info(f"Skipping upload for {object_name}, already exists in S3.")
                uploaded_image_urls.append(f"s3://{self.bucket_name}/{object_name}")
                continue

            # Upload image
            self.upload_image(image_url, object_name)
            uploaded_image_urls.append(f"s3://{self.bucket_name}/{object_name}")

        return uploaded_image_urls
    

    def should_skip_image_upload(self, product_url):
        """
        Determines if the image upload should be skipped for a given product URL.
        
        Args:
            product_url (str): The product URL to check.

        Returns:
            bool: True if image upload should be skipped, False otherwise.
        """
        try:
            query = """
            SELECT original_image_urls, s3_image_urls 
            FROM militaria 
            WHERE url = %s;
            """
            result = self.sqlFetch(query, (product_url,))
            if result:
                original_image_urls, s3_image_urls = result[0]
                if original_image_urls and s3_image_urls and len(original_image_urls) == len(s3_image_urls):
                    return True
            return False
        except Exception as e:
            logging.error(f"Error checking if image upload should be skipped for {product_url}: {e}")
            return False

