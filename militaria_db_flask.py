import os
import json
from flask import Flask, jsonify
from flask_cors import CORS
from datetime import datetime, timezone
import psycopg2

app = Flask(__name__)
CORS(app, origins=["https://www.keenannilson.com"])

# Function to load database credentials
def load_db_credentials():
    try:
        info_location = r'/home/ec2-user/projects/AWS-Militaria-Scraper/'
        cred_file = os.path.join(info_location, 'pgadminCredentials.json')
        with open(cred_file, 'r') as file:
            credentials = json.load(file)
        return credentials
    except Exception as e:
        raise RuntimeError(f"Error loading database credentials: {e}")

def time_ago(date_collected):
    """Calculate the time difference between now and `date_collected`."""
    try:
        collected_time = datetime.fromisoformat(str(date_collected)).replace(tzinfo=timezone.utc)
        now = datetime.now(timezone.utc)
        delta = now - collected_time

        if delta.days > 0:
            return f"{delta.days} day{'s' if delta.days > 1 else ''} ago"
        elif delta.seconds >= 3600:
            hours = delta.seconds // 3600
            return f"{hours} hour{'s' if hours > 1 else ''} ago"
        elif delta.seconds >= 60:
            minutes = delta.seconds // 60
            return f"{minutes} minute{'s' if minutes > 1 else ''} ago"
        else:
            return f"{delta.seconds} second{'s' if delta.seconds != 1 else ''} ago"
    except Exception as e:
        return "Unknown time"

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
            SELECT title, description, price, url, date_collected, site, currency, original_image_urls
            FROM militaria
            ORDER BY date_collected DESC
            LIMIT 250;
        """
        cursor.execute(query)
        rows = cursor.fetchall()

        # Format the data into a list of dictionaries
        products = []
        for row in rows:
            first_image = None
            if row[7]:  # original_image_urls column
                if isinstance(row[7], list):  # If it's already a list
                    image_urls = row[7]
                    first_image = image_urls[0] if image_urls else None
                else:  # If it's a string, parse it as JSON
                    try:
                        image_urls = json.loads(row[7])
                        first_image = image_urls[0] if image_urls else None
                    except json.JSONDecodeError:
                        print(f"Error parsing image URLs: {row[7]}")
                        first_image = None

            products.append({
                "title": row[0],
                "price": row[2],
                "url": row[3],
                "time_ago": time_ago(row[4]),
                "source": row[5],
                "currency": row[6],
                "image_url": first_image,
            })

        # Close connections
        cursor.close()
        connection.close()

        return jsonify(products)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True)
