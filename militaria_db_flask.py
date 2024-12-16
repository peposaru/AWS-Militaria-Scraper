import os
import json
from flask import Flask, jsonify
from flask_cors import CORS  # Import Flask-CORS to handle cross-origin requests
import psycopg2

app = Flask(__name__)

# Enable CORS for requests coming from Squarespace
CORS(app, origins=["https://www.keenannilson.com"])  # Restrict to your Squarespace domain

# Function to load database credentials from JSON file
def load_db_credentials():
    try:
        info_location = r'/home/ec2-user/projects/AWS-Militaria-Scraper/'
        cred_file = os.path.join(info_location, 'pgadminCredentials.json')
        with open(cred_file, 'r') as file:
            credentials = json.load(file)
        return credentials
    except Exception as e:
        raise RuntimeError(f"Error loading database credentials: {e}")

@app.route('/latest-products', methods=['GET'])
def latest_products():
    try:
        # Load database credentials
        credentials = load_db_credentials()
        connection = psycopg2.connect(
            host=credentials["hostName"],
            database=credentials["dataBase"],
            user=credentials["userName"],
            password=credentials["pwd"],
            port=credentials["portId"]
        )
        
        cursor = connection.cursor()

        # Execute the query to fetch the latest 100 products
        query = """
            SELECT title, description, price, url, date_collected, site
            FROM militaria
            ORDER BY date_collected DESC
            LIMIT 100;
        """
        cursor.execute(query)
        rows = cursor.fetchall()

        # Format the data into a list of dictionaries
        products = [
            {
                "title": row[0], 
                "description": row[1], 
                "price": row[2], 
                "url": row[3], 
                "date_added": row[4],
                "source": row[5]  # Include the source site field
            } 
            for row in rows
        ]

        # Close connections
        cursor.close()
        connection.close()

        return jsonify(products)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
