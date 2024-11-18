# This is the AWS Cloud version of this program designed to be used with EC2 and RDS

# Making a more universal scraper which just takes a json library as input

import requests, re, os, psycopg2,json, logging
from bs4 import BeautifulSoup
from datetime import date
from datetime import datetime
from re import sub
from tqdm import tqdm
from tqdm import trange
from time import sleep
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from requests.exceptions import RequestException, ChunkedEncodingError, Timeout


class ProductScraper:
    def __init__(self, spreadSheetManager):
        self.spreadSheetManager = spreadSheetManager
        # This part of init just helps with errors from websites and what not.
        # Initialize a session with retries
        self.session = requests.Session()
        retry = Retry(
            total=5,  # Retry up to 5 times
            backoff_factor=1,  # Wait 1 second between retries, exponentially increasing
            status_forcelist=[500, 502, 503, 504],  # Retry on these HTTP errors
        )
        adapter = HTTPAdapter(max_retries=retry)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)

    def readProductPage(self, url):
        headers = {
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:60.0) Gecko/20100101 Firefox/60.0"
        }
        try:
            # Set timeout to 10 seconds
            response = self.session.get(url, headers=headers, timeout=10)
            response.raise_for_status()
        except Timeout:
            logging.info(f"Timeout occurred while accessing {url}.")
            return None
        except RequestException as e:
            logging.error(f"Error occurred while accessing {url} - {e}")
            return None
        
        return BeautifulSoup(response.content, 'html.parser')
    
    def scrapePage(self, product):
        headers = {
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:60.0) Gecko/20100101 Firefox/60.0"
        }
        try:
            response = self.session.get(product, headers=headers, stream=True, timeout=10)
            response.raise_for_status()
            
            # Combine chunks into a single content object
            content = b"".join(chunk for chunk in response.iter_content(chunk_size=1024) if chunk)
            
        except ChunkedEncodingError:
            logging.error(f"ChunkedEncodingError encountered while accessing {product}.")
            return None
        except Timeout:
            logging.error(f"Timeout occurred while accessing {product}.")
            return None
        except RequestException as e:
            logging.error(f"General RequestException for {product} - {e}")
            return None
        
        return BeautifulSoup(content, 'html.parser')
    
    def scrapeData(self,productSoup,titleElement,descElement,priceElement,availableElement,currency,source):
            
        # Scrape Title
            try:
                title  = eval(titleElement)
                title  = title.strip()
                title  = title.replace("'","*")
                title  = title.replace('"',"*")
                title  = title.replace('‘','*')
                title  = title.replace('’','*')
                title  = title.replace('click image for larger view.','')
                title  = title.strip()
            except:
                title = 'NULL'

        # Scrape Description
            try:
                description = eval(descElement)
                description = description.replace("'","*")
                description = description.replace('"',"*")
                description = description.replace('‘','*')
                description = description.replace('’','*')
                description = description.replace('Description','')
                description = description.replace('Description','')
                description = description.replace('Full image','')
                description = description.split('USD', 1)[0]
                description = description.strip()
            except:
                description = 'NULL'

        # Scrape Price
            try:
                if source == 'VIRTUAL_GRENADIER':
                    priceRegex  = r'\$(\d+(?:,\d+)*)\b'
                    price       = eval(priceElement)
                    priceMatch1 = re.search(priceRegex,price)
                    price       = priceMatch1.group(1).replace(",", "")
                    price       = price.replace('$','')
                    price       = int(price)

                else:
                    priceRegex  = r"[\d.,]+"
                    price       = eval(priceElement)
                    priceMatch1 = re.search(priceRegex,price)
                    price       = priceMatch1.group()
                    price       = price.replace(',','.')
                    periodRegex = r'\.(?=.*\.)'
                    price       = re.sub(periodRegex,'',price)
                    if source == 'RUPTURED_DUCK':
                        price = price.replace('.','')

            except Exception as err:
                    print (err)
                    price = 0

        # Scrape Availability
            available = eval(availableElement)

        # Return all values
            return ([title,description,price,available])

class PostgreSQLProcessor:
    def __init__(self,hostName, dataBase,userName,pwd,portId):
        self.hostName = hostName
        self.dataBase = dataBase
        self.userName = userName
        self.pwd      = pwd
        self.portId   = portId
        self.conn     = psycopg2.connect(
                        host = hostName,
                        dbname = dataBase,
                        user = userName,
                        password = pwd,
                        port = portId)
        self.cur      = self.conn.cursor()


    def sqlExecute(self,query):
        self.cur.execute(query)
        self.conn.commit()

    def sqlFetch(self,query):
        self.cur.execute(query)
        cellValue = self.cur.fetchall()
        return cellValue

    def sqlClose(self):
        self.cur.close()
        self.conn.close()

class JsonManager:        
    def jsonSelectors(self,militariaSite):
        base_url         = militariaSite['base_url']
        source           = militariaSite['source']
        pageIncrement    = militariaSite['page_increment']
        currency         = militariaSite['currency']
        products         = militariaSite['products']
        productUrlElement= militariaSite['product_url_element']
        titleElement     = militariaSite['title_element']
        descElement      = militariaSite['desc_element']
        priceElement     = militariaSite['price_element']
        availableElement = militariaSite['available_element']
        conflict         = militariaSite['conflict_element']
        nation           = militariaSite['nation_element']
        item_type        = militariaSite['item_type_element']
        productsPageUrl  = militariaSite['productsPageUrl']
        grade            = militariaSite['grade_element']

        return conflict,nation,item_type,grade,source,pageIncrement,currency,products,productUrlElement,titleElement,descElement,priceElement,availableElement,productsPageUrl,base_url

class MainPrinting:
    def create_log_header(self, message, width=60):
        """Helper method to create a formatted log header."""
        border = '-' * width
        return f"\n{border}\n{message.center(width)}\n{border}"

    def newInstance(self, source, productsPage, runCycle, productsProcessed):
        """Log the start of a new scraping instance."""
        current_datetime = datetime.now()
        logging.info(self.create_log_header("NEW INSTANCE STARTED"))
        logging.info(f"MILITARIA SITE      : {source}")
        logging.info(f"PRODUCTS URL        : {productsPage}")
        logging.info(f"CYCLES RUN          : {runCycle}")
        logging.info(f"PRODUCTS PROCESSED  : {productsProcessed}")
        logging.info(f"TIMESTAMP           : {current_datetime}")

    def terminating(self, source, consecutiveMatches, runCycle, productsProcessed):
        """Log the termination of a scraping instance."""
        current_datetime = datetime.now()
        logging.info(self.create_log_header("INSTANCE TERMINATED"))
        logging.info(f"MILITARIA SITE      : {source}")
        logging.info(f"CONSECUTIVE MATCHES : {consecutiveMatches}")
        logging.info(f"CYCLES RUN          : {runCycle}")
        logging.info(f"PRODUCTS PROCESSED  : {productsProcessed}")
        logging.info(f"TIMESTAMP           : {current_datetime}")

    def sysUpdate(self, page, urlCount, consecutiveMatches, productUrl):
        """Log when a product in the system is updated."""
        current_datetime = datetime.now()
        logging.info(self.create_log_header("PRODUCT UPDATED"))
        logging.info(f"CURRENT PAGE        : {page}")
        logging.info(f"PRODUCTS PROCESSED  : {urlCount}")
        logging.info(f"CONSECUTIVE MATCHES : {consecutiveMatches}")
        logging.info(f"PRODUCT URL         : {productUrl}")
        logging.info(f"TIMESTAMP           : {current_datetime}")

    def noUpdate(self, page, urlCount, consecutiveMatches, productUrl):
        """Log when no updates are made to a product in the system."""
        current_datetime = datetime.now()
        logging.info(self.create_log_header("NO PRODUCT UPDATE"))
        logging.info(f"CURRENT PAGE        : {page}")
        logging.info(f"PRODUCTS PROCESSED  : {urlCount}")
        logging.info(f"CONSECUTIVE MATCHES : {consecutiveMatches}")
        logging.info(f"PRODUCT URL         : {productUrl}")
        logging.info(f"TIMESTAMP           : {current_datetime}")

    def newProduct(self, page, urlCount, title, productUrl, description, price, available):
        """Log details of a newly scraped product."""
        current_datetime = datetime.now()
        logging.info(self.create_log_header("NEW PRODUCT FOUND"))
        logging.info(f"CURRENT PAGE        : {page}")
        logging.info(f"PRODUCTS PROCESSED  : {urlCount}")
        logging.info(f"TITLE               : {title}")
        logging.info(f"PRODUCT URL         : {productUrl}")
        logging.info(f"DESCRIPTION         : {description}")
        logging.info(f"PRICE               : {price}")
        logging.info(f"AVAILABLE           : {available}")
        logging.info(f"TIMESTAMP           : {current_datetime}")

    def standby(self):
        """Log when the scraper enters a standby period between cycles."""
        current_datetime = datetime.now()
        logging.info(self.create_log_header("CYCLE COMPLETED"))
        logging.info(f"PROCESS COMPLETED AT: {current_datetime}")
        logging.info("STANDING BY FOR NEXT CYCLE...")

def main():
    print ('INITIALIZING. PLEASE WAIT...')
    current_datetime = datetime.now()
    logging.info(f"""
------------------------------------------------------------
                     PROGRAM INITIALIZED
                     {current_datetime}          
------------------------------------------------------------""")
    # Location where credentials are located
    infoLocation = r'/home/ec2-user/projects/AWS-Militaria-Scraper/'
    pgAdminCred  = 'pgadminCredentials.json'
    selectorJson = 'MILITARIA_SELECTORS.json'
    os.chdir(infoLocation)

    # pgAdmin 4 Credentials
    with open (pgAdminCred,'r') as credFile:
        jsonData = json.load(credFile)
        hostName = jsonData['hostName'] 
        dataBase = jsonData['dataBase']
        userName = jsonData['userName']
        pwd      = jsonData['pwd']
        portId   = jsonData['portId']

    # Postgresql - Web Scraping / Beautiful Soup - Json Manager
    dataManager      = PostgreSQLProcessor(hostName, dataBase,userName,pwd,portId)
    webScrapeManager = ProductScraper(dataManager)
    jsonManager      = JsonManager()
    prints           = MainPrinting()

    # Setting up counts
    runCycle          = 0
    productsProcessed = 0
    
    # Set how many in a row you want to match
    targetMatch = 50

    # Opening the JSON file containing website specific selectors
    with open(selectorJson,'r') as userFile:
        jsonData = json.load(userFile)

    # Main Loop
    while True:

        # Iterating over each site in the JSON file and grabbing their respective selectors.
        for militariaSite in jsonData:
            conflict,nation,item_type,grade,source,pageIncrement,currency,products,productUrlElement,titleElement,descElement,priceElement,availableElement,productsPageUrl,base_url = jsonManager.jsonSelectors(militariaSite)
            
            # Counters for current site
            urlCount           = 0
            consecutiveMatches = 0
            page               = 0

            # Iterating over all the products on a the products list.
            while consecutiveMatches != targetMatch:
                productsPage = base_url + productsPageUrl.format(page=page)
                logging.debug(f"Navigating to products page: {productsPage}")

                soup             = webScrapeManager.readProductPage(productsPage)

                # Checking if page loaded correctly
                if soup is None:
                    logging.warning(f"Failed to load products page: {productsPage}")
                    break

                prints.newInstance(source,productsPage,runCycle,productsProcessed)

                # Confirm the products selector and check if products are found
                product_list = eval(products)
                if not product_list:
                    logging.warning(f"No products found on page: {productsPage}")
                    break

                for product in product_list :
                    if len(product) == 0:
                        logging.info(f"Empty product element found, skipping.")
                        continue

                    urlCount += 1
                    productsProcessed += 1

                    # Confirm the product URL is extracted correctly
                    try:
                        productUrl = eval(productUrlElement)
                        # Only add base_url if productUrl is a relative URL
                        if not productUrl.startswith("http"):
                            productUrl = base_url + productUrl
                        logging.debug(f"Product URL extracted: {productUrl}")
                    except Exception as e:
                        logging.debug(f"Error extracting product URL: {e}")
                        continue
                    # Fetch the individual product page and check if it loads
                    productSoup = webScrapeManager.scrapePage(productUrl)
                    if productSoup is None:
                        logging.warning(f"DEBUG: Failed to load product page: {productUrl}")
                        continue
                    
                    # Confirm title, description, price, and availability extraction
                    try:
                        title, description, price, available = webScrapeManager.scrapeData(
                            productSoup, titleElement, descElement, priceElement, availableElement, currency, source
                        )
                        logging.debug(f"Extracted data - Title: {title}, Price: {price}, Available: {available}")
                    except Exception as e:
                        logging.debug(f"Error extracting data from product page: {e}")
                        continue

                    # If x amount of matches are met, end this run for this site
                    if consecutiveMatches == targetMatch:

                        # Notifying user of cycle termination
                        prints.terminating(source,consecutiveMatches,runCycle,productsProcessed)
                        break

                    productUrl  = eval(productUrlElement)
                    productSoup = webScrapeManager.scrapePage(productUrl)

                    ([title,description,price,available]) = webScrapeManager.scrapeData(productSoup,titleElement,descElement,priceElement,availableElement,currency,source)
                    todayDate = date.today()

                    #IF ITEM IN LIST, UPDATE IT
                    searchQuery = f"SELECT url FROM militaria WHERE url LIKE '{productUrl}'"
                    cellValue = dataManager.sqlFetch(searchQuery)
                    match = [tup[0] for tup in cellValue]

                    # If the product url is in the database
                    if productUrl in match:
                        consecutiveMatches += 1

                        soldDateExists = f"""SELECT date_sold FROM militaria WHERE url LIKE '{productUrl}'"""

                        # If the product url is in the database and the item has been sold
                        if available == False:
                            cellValue = dataManager.sqlFetch(soldDateExists)

                            match = [tup[0] for tup in cellValue]
                            if match != False:
                                updateStatus = f''' UPDATE militaria
                                                    SET available = False
                                                    WHERE url = '{productUrl}';'''
                                updateSoldDate = f'''  UPDATE militaria
                                                    SET date_sold = '{todayDate}'
                                                    WHERE url = '{productUrl}';'''
                                
                                # COMMENT THIS APPENDQUERY LINE OUT IF YOU WANT TO TEST BEFORE WRITING TO DATABASE 
                                dataManager.sqlExecute(updateStatus)
                                # COMMENT THIS APPENDQUERY LINE OUT IF YOU WANT TO TEST BEFORE WRITING TO DATABASE 
                                dataManager.sqlExecute(updateSoldDate)

                                prints.sysUpdate(page,urlCount,consecutiveMatches,productUrl)
                                continue
                        else:
                            prints.noUpdate(page,urlCount,consecutiveMatches,productUrl)

                    if productUrl not in match:
                        consecutiveMatches = 0
                        appendQuery = f'''INSERT INTO militaria (url, title, description, price, available,date,site,currency,conflict,nation,item_type) VALUES ('{productUrl}','{title}','{description}',{price},{available},'{todayDate}','{source}','{currency}','{conflict}','{nation}','{item_type}')'''
                        # COMMENT THIS APPENDQUERY LINE OUT IF YOU WANT TO TEST BEFORE WRITING TO DATABASE 
                        dataManager.sqlExecute(appendQuery)
                        prints.newProduct(page,urlCount,title,productUrl,description,price,available)

                page += int(pageIncrement)
        # Pauses in between instances
        sleepTime = int(os.getenv('CYCLE_PAUSE_SECONDS', 300))  # Default: 300 seconds
        runCycle += 1
        prints.standby()

        for _ in trange(sleepTime, desc="Waiting for the next cycle", unit="seconds"):
            sleep(1)


# Configure logging
logging.basicConfig(
    level=logging.DEBUG,  # Set the logging level
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("AWS_militaria_scraper.log"),  # Save logs to a file
        logging.StreamHandler()              # Print logs to the console
    ]
)


if __name__ == "__main__":
    main()
