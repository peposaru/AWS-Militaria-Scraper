import psycopg2
import json
import os

def test_db_connection():
    info_location = r'C:/Users/keena/Desktop/Cloud Militaria Scraper/'
    cred_file = os.path.join(info_location, 'pgadminCredentials.json')
    with open(cred_file, 'r') as file:
        credentials = json.load(file)

    connection = psycopg2.connect(
        host=credentials["hostName"],
        database=credentials["dataBase"],
        user=credentials["userName"],
        password=credentials["pwd"],
        port=credentials["portId"]
    )
    cursor = connection.cursor()
    cursor.execute("SELECT 1;")
    print("Database connection successful:", cursor.fetchone())
    cursor.close()
    connection.close()

test_db_connection()
