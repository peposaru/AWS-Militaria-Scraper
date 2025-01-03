import os
import json
from flask import Flask, jsonify
from flask_cors import CORS
from datetime import datetime, timezone
import psycopg2
from flask import request


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

@app.route('/sites', methods=['GET'])
def get_sites():
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

        # Query to fetch distinct site values
        query = "SELECT DISTINCT site FROM militaria;"
        cursor.execute(query)
        rows = cursor.fetchall()

        # Close connections
        cursor.close()
        connection.close()

        # Format results as a list
        sites = [row[0] for row in rows]
        return jsonify(sites)
    except Exception as e:
        return jsonify({"error": str(e)}), 500



@app.route('/latest-products', methods=['GET'])
def latest_products():
    try:
        # Get query parameters
        site_filter = request.args.get('sites', None)  # Comma-separated list of sources
        limit = int(request.args.get('limit', 250))  # Default limit to 250

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

        # Base query
        query = """
            SELECT title, description, price, url, date_collected, site, currency, original_image_urls
            FROM militaria
        """
        params = []

        # Add WHERE clause if filtering by sites
        if site_filter:
            site_list = site_filter.split(",")  # Convert to a list
            placeholders = ','.join(['%s'] * len(site_list))  # Generate placeholders for SQL IN clause
            query += f" WHERE site IN ({placeholders})"
            params.extend(site_list)

        # Add ORDER BY and LIMIT
        query += " ORDER BY date_collected DESC LIMIT %s"
        params.append(limit)

        cursor.execute(query, params)
        rows = cursor.fetchall()

        # Format the results
        products = []
        for row in rows:
            first_image = None
            if row[7]:  # original_image_urls column
                try:
                    image_urls = json.loads(row[7]) if isinstance(row[7], str) else row[7]
                    first_image = image_urls[0] if image_urls else None
                except json.JSONDecodeError:
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

        cursor.close()
        connection.close()

        return jsonify(products)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/stats', methods=['GET'])
def get_stats():
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

        # Query to count unique sites and total products
        site_count_query = "SELECT COUNT(DISTINCT site) FROM militaria;"
        product_count_query = "SELECT COUNT(*) FROM militaria;"

        cursor.execute(site_count_query)
        unique_sites = cursor.fetchone()[0]

        cursor.execute(product_count_query)
        total_products = cursor.fetchone()[0]

        # Close connection
        cursor.close()
        connection.close()

        return jsonify({
            "unique_sites": unique_sites,
            "total_products": total_products
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
