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
                user=creds["userName"],       # Change to match your JSON file
                password=creds["pwd"],        # Change to match your JSON file
                host=creds["hostName"],       # Change to match your JSON file
                database=creds["dataBase"],   # Change to match your JSON file
                port=creds["portId"]          # Change to match your JSON file
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
