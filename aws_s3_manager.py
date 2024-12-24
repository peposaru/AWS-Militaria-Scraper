import boto3
import requests
import logging
import json
import time
from urllib.parse import urlparse

class S3Manager:
    def __init__(self, credentials_file, dataManager):
        """
        Initialize the S3 Manager with provided credentials.

        Args:
            credentials_file (str): Path to the JSON file containing credentials.
        """
        credentials = self.load_s3_credentials(credentials_file)
        self.bucket_name = credentials["bucketName"]
        self.s3 = boto3.client(
            's3',
            aws_access_key_id=credentials["accessKey"],
            aws_secret_access_key=credentials["secretKey"],
            region_name=credentials["region"]
        )
        self.dataManager = dataManager

    @staticmethod
    def load_s3_credentials(file_path):
        """
        Load S3 credentials from a JSON file.

        Args:
            file_path (str): Path to the JSON file containing credentials.

        Returns:
            dict: A dictionary with S3 credentials.

        Raises:
            RuntimeError: If the file cannot be read or parsed.
        """
        try:
            with open(file_path, "r") as file:
                return json.load(file)
        except Exception as e:
            raise RuntimeError(f"Error loading S3 credentials: {e}")

    def upload_image(self, image_url, product_url, site_name):
        """
        Upload an image to S3 with structured naming.

        Args:
            image_url (str): URL of the image to upload.
            product_url (str): URL of the product associated with the image.
            site_name (str): Name of the site being scraped.

        Raises:
            ValueError: If the product ID or file extension is invalid.
        """
        try:
            # Retrieve the product ID from the database
            product_id = self.dataManager.get_product_id(product_url)
            if product_id is None:
                raise ValueError(f"Product ID not found for URL: {product_url}")

            # Fetch the list of existing images to determine the next index
            existing_images = self.list_objects(f"{site_name}/{product_id}/")
            image_index = len(existing_images) + 1

            # Extract clean filename from URL
            parsed_url = urlparse(image_url)
            extension = parsed_url.path.split('.')[-1]  # Get the file extension
            if not extension:
                raise ValueError(f"Invalid image URL: {image_url} (no extension found)")

            # Construct the S3 object name
            object_name = f"{site_name}/{product_id}/{product_id}-{image_index}.{extension}"

            logging.debug(f"Uploading to S3: {object_name}")

            # Fetch the image data
            response = requests.get(image_url, stream=True, timeout=10)
            response.raise_for_status()

            # Upload to S3
            self.s3.upload_fileobj(response.raw, self.bucket_name, object_name)
            logging.info(f"Uploaded to S3: {object_name}")
        except requests.exceptions.RequestException as e:
            logging.error(f"Error fetching image {image_url}: {e}")
        except Exception as e:
            logging.error(f"Error uploading image to S3: {e}")



    def upload_image_with_retries(self, image_url, object_name, max_retries=3, delay=2):
        for attempt in range(1, max_retries + 1):
            try:
                logging.debug(f"Attempt {attempt} to upload {object_name}")
                self.upload_image(image_url, object_name)
                return
            except Exception as e:
                logging.error(f"Attempt {attempt} failed: {e}")
                if attempt < max_retries:
                    time.sleep(delay)
        logging.warning(f"Failed to upload {object_name} after {max_retries} attempts")

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
            return True
        except self.s3.exceptions.ClientError as e:
            if e.response['Error']['Code'] == "404":
                return False
            logging.error(f"Error checking existence of {object_name}: {e}")
            raise

    def list_objects(self, prefix=""):
        """
        List objects in the S3 bucket with an optional prefix.

        Args:
            prefix (str): The prefix to filter objects (default is "").

        Returns:
            list: A list of object keys in the bucket.
        """
        try:
            response = self.s3.list_objects_v2(Bucket=self.bucket_name, Prefix=prefix)
            return [obj["Key"] for obj in response.get("Contents", [])]
        except Exception as e:
            logging.error(f"Error listing objects in S3 bucket: {e}")
            return []

    def delete_object(self, object_name):
        """
        Delete an object from the S3 bucket.

        Args:
            object_name (str): The name of the object to delete.

        Raises:
            Exception: If the deletion fails.
        """
        try:
            self.s3.delete_object(Bucket=self.bucket_name, Key=object_name)
            logging.info(f"Deleted object from S3: {object_name}")
        except Exception as e:
            logging.error(f"Error deleting object from S3: {e}")
            raise
