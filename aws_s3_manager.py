import boto3
import requests
import logging
import json

class S3Manager:
    def __init__(self, credentials_file):
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

    def upload_image(self, image_url, object_name):
        """
        Upload an image to the S3 bucket with the specified object name.

        Args:
            image_url (str): URL of the image to upload.
            object_name (str): Object name in the S3 bucket.
        """
        try:
            logging.debug(f"Uploading image: {image_url} to {object_name}")
            response = requests.get(image_url, stream=True)
            response.raise_for_status()
            self.s3.upload_fileobj(response.raw, self.bucket_name, object_name)
            logging.info(f"Image uploaded to S3: {object_name}")
        except Exception as e:
            logging.error(f"Error uploading image to S3: {e}")
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
