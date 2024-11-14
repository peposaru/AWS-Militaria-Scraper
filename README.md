# Military Antiques Data Scraper on AWS

An attempt to consolidate military antiques from various websites into one unified PostgreSQL database for analysis. This scraper collects titles, descriptions, prices, categories, and more from a variety of online military antiques shops.

**Link to Portfolio**: [AWS Militaria Scraper Portfolio Project](https://www.keenannilson.com/aws-militaria-database)

---

## Project Description

This Python-based program scrapes military antiques data from multiple sources and feeds it into a cloud-hosted PostgreSQL database on AWS RDS. Leveraging AWS infrastructure, the program is designed to run continuously, collecting and storing information on thousands of items in a structured format, enabling efficient analysis and market insights.

### Program Features

- **Web Scraping**: Uses `BeautifulSoup` and `Selenium` to access and scrape product information from military antiques websites.
- **Data Collection**: Extracts key details like title, description, price, categories, and other useful data.
- **Cloud Infrastructure**: Runs on an AWS EC2 instance, with data stored in an AWS RDS PostgreSQL database.
- **Scalable Database**: Centralizes all data in one RDS database, providing a single source for product details across various sites.

## Process Overview

1. **Data Extraction**: The program starts by visiting each target site, reading its HTML structure, and identifying product lists. For each product, it collects relevant details (title, description, price, categories, etc.).
2. **Data Loading**: The extracted data is then stored in a PostgreSQL database hosted on AWS RDS using the `psycopg2` library for seamless interaction.
3. **Continuous Updating**: The program runs persistently on an AWS EC2 instance, allowing for regular data updates and ongoing collection.

## Motivation

My passion for military antiques and history stems from family influence—both of my grandparents were veterans, which sparked my interest. Over time, collecting historical items turned into a profession. This project fulfills a long-standing goal to create a centralized, analyzable dataset for military antiques, helping enthusiasts and collectors understand market trends and valuations.

## From Local to Cloud: Transition to AWS

Initially, this program was designed to run locally, but I’ve now updated it for the cloud using AWS infrastructure:

- **Version Control**: Code is managed through GitHub for easy collaboration and versioning.
- **Deployment on EC2**: The scraper program is deployed on an AWS EC2 instance, providing consistent performance and availability for data collection.
- **Database on RDS**: The PostgreSQL database is hosted on AWS RDS, ensuring secure, scalable, and accessible storage of collected data.
- **Automation**: With tools like `nohup` and `screen`, the program runs persistently on EC2, even when disconnected from the SSH session.

### Technical Setup for AWS Deployment

1. **Clone the Repository**: Start by cloning this GitHub repository to your local machine.
2. **Create an EC2 Instance**: Launch an AWS EC2 instance and set up SSH access.
3. **Install Required Libraries**: Install Python libraries on EC2 (`BeautifulSoup`, `Selenium`, `psycopg2`).
4. **Set Up RDS**: Create a PostgreSQL instance on AWS RDS for cloud database management.
5. **Configure Security Groups**: Set up security groups for EC2 and RDS to allow database connections over port 5432.
6. **Deploy Code on EC2**: Clone the GitHub repository on EC2 and configure the scraper to use the RDS database credentials.

## Challenges and Limitations

1. **Inconsistent Website Designs**: Each site has unique HTML and CSS structures, making it challenging to scrape data consistently.
2. **Limited Access to Sold Data**: Many sites remove or obscure information on sold items, requiring extrapolation through forums and personal insights.
3. **Data Quality Issues**: Small, family-run shops often have inconsistent product titles and descriptions, introducing errors and variations in the data.
4. **AWS Familiarity**: Going from running a program on my compute with the database on my computer to moving everything to the cloud requires a lot more knowledge of things like linux and AWS interface.

## Problem Solved

Military antiques websites lack uniformity and centralization, complicating market analysis. This program consolidates data from multiple sources into a single format, enabling:
- **Price Estimation**: Helps estimate fair market prices based on aggregated data.
- **Market Insights**: Provides insights into demand, supply, and price trends for various military antique categories.
- **Regional Analysis**: Identifies location concentrations and availability of specific items.

## Usage

### Running Locally

To run the scraper locally:
1. Install the necessary libraries.
2. Update database connection details to match a local PostgreSQL setup.
3. Run the Python program to begin scraping.

### Running on AWS EC2

1. **Upload Code to GitHub**: Keep your code versioned and easily accessible.
2. **Clone Repository on EC2**: Download the latest code version to your EC2 instance.
3. **Connect to RDS**: Update the database connection in the program to point to the RDS endpoint.
4. **Run the Program**: Start the scraper using `nohup` or `screen` to keep it running continuously on EC2.

## Intended Use

This project is designed to streamline the collection and analysis of military antiques data, enabling collectors and historians to:
- Analyze price trends.
- Study market demand and supply.
- Gain insights into the geographic distribution of collectible items.

## Credits

Thanks to Ryan for the ongoing support throughout this project.
