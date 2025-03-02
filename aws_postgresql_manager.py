import logging
import json
from psycopg2 import pool

class PostgreSQLProcessor:
    def __init__(self, credFile):
        """
        Initialize PostgreSQL connection with credentials from a file.

        Args:
            credFile (str): Path to the credentials JSON file.
        """
        with open(credFile, 'r') as f:
            creds = json.load(f)

        try:
            # Initialize a connection pool with 5-10 connections
            self.pool = pool.SimpleConnectionPool(
                5, 10,
                user      =creds["userName"],
                password  =creds["pwd"],
                host      =creds["hostName"],
                database  =creds["dataBase"],
                port      =creds["portId"]
            )

            logging.info("PostgreSQL connection pool initialized.")
        except Exception as e:
            logging.error(f"Error initializing connection pool: {e}")
            raise

    def sqlFetch(self, query, params=None):
        """
        Execute a query and fetch results.

        Args:
            query (str): SQL query to execute.
            params (tuple): Parameters for the query.

        Returns:
            list: Query results.
        """
        conn = self.pool.getconn()
        try:
            with conn.cursor() as cur:
                cur.execute(query, params)
                return cur.fetchall()
        except Exception as e:
            logging.error(f"Error executing fetch query: {e}")
            return []
        finally:
            self.pool.putconn(conn)  # Return the connection to the pool

    def sqlExecute(self, query, params=None):
        """
        Execute a query that modifies the database.

        Args:
            query (str): SQL query to execute.
            params (tuple): Parameters for the query.
        """
        conn = self.pool.getconn()
        try:
            with conn.cursor() as cur:
                cur.execute(query, params)
                conn.commit()
        except Exception as e:
            logging.error(f"Error executing update query: {e}")
            conn.rollback()
        finally:
            self.pool.putconn(conn)  # Return the connection to the pool

    def get_product_id(self, product_url):
        """
        Retrieve the product ID from the database using the product URL.

        Args:
            product_url (str): The URL of the product.

        Returns:
            int: The product ID if found, otherwise None.
        """
        try:
            query = "SELECT id FROM militaria WHERE url = %s;"
            result = self.sqlFetch(query, (product_url,))
            if result:
                product_id = result[0][0]  # Extract the ID from the query result
                logging.debug(f"Product ID for URL '{product_url}' is {product_id}")
                return product_id
            logging.warning(f"No product ID found for URL '{product_url}'")
            return None
        except Exception as e:
            logging.error(f"Error fetching product ID for URL '{product_url}': {e}")
            return None

    def update_product_images(self, product_id, original_image_urls, s3_image_urls):
        """
        Update product images in the database.

        Args:
            product_id (int): The product ID.
            original_image_urls (list): List of original image URLs.
            s3_image_urls (list): List of S3 image URLs.

        Returns:
            bool: True if the update was successful, False otherwise.
        """
        try:
            if not original_image_urls or not s3_image_urls:
                logging.debug(f"Skipping image update for product ID {product_id} due to empty URL lists.")
                return False

            query = """
                UPDATE militaria
                SET original_image_urls = %s, s3_image_urls = %s
                WHERE id = %s;
            """
            params = (json.dumps(original_image_urls), json.dumps(s3_image_urls), product_id)
            self.sqlExecute(query, params)
            logging.info(f"Updated image URLs for product ID {product_id}.")
            return True
        except Exception as e:
            logging.error(f"Error updating images for product ID {product_id}: {e}")
            return False

    def close_pool(self):
        """
        Close all connections in the pool.
        """
        try:
            self.pool.closeall()
            logging.info("PostgreSQL connection pool closed.")
        except Exception as e:
            logging.error(f"Error closing PostgreSQL connection pool: {e}")

    def should_skip_image_upload(self, product_url):
        """
        Check if the images for the given product URL are already uploaded.

        Args:
            product_url (str): The product URL to check.

        Returns:
            bool: True if image upload can be skipped, False otherwise.
        """
        try:
            query = """
            SELECT original_image_urls, s3_image_urls
            FROM militaria
            WHERE url = %s;
            """
            result = self.sqlFetch(query, (product_url,))
            
            if not result:
                logging.info(f"No record found for product URL: {product_url}. Proceeding with image upload.")
                return False

            original_image_urls, s3_image_urls = result[0]
            # Ensure both columns have values and their lengths match
            if original_image_urls and s3_image_urls and len(original_image_urls) == len(s3_image_urls):
                logging.debug(f"Image upload already completed for product URL: {product_url}.")
                return True

            logging.debug(f"Image upload needed for product URL: {product_url}.")
            return False
        except Exception as e:
            logging.error(f"Error checking image upload status for URL {product_url}: {e}")
            return False
