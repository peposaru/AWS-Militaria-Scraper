import psycopg2
from psycopg2 import pool
import json  # Missing import
import logging


class PostgreSQLProcessor:
    def __init__(self, credFile):
        # Load credentials
        with open(credFile, 'r') as f:
            creds = json.load(f)
        
        try:
            # Initialize a connection pool with 5-10 connections
            self.pool = pool.SimpleConnectionPool(
                5, 10,
                user     =creds["userName"],       
                password =creds["pwd"],        
                host     =creds["hostName"],       
                database =creds["dataBase"],   
                port     =creds["portId"]          
            )

            logging.info("PostgreSQL connection pool initialized.")
        except Exception as e:
            logging.error(f"Error initializing connection pool: {e}")
            raise

    def sqlFetch(self, query, params=None):
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