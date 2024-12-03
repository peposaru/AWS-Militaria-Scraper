import requests, logging, time, re
from bs4 import BeautifulSoup
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from requests.exceptions import RequestException, Timeout, ChunkedEncodingError

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

    # Adding a retry system when getting productSoup
    def fetch_with_retries(self, fetch_function, *args, max_retries=3, backoff_factor=2, **kwargs):
        retries = 0
        while retries < max_retries:
            try:
                return fetch_function(*args, **kwargs)  # Call the provided function with arguments
            except Exception as e:
                retries += 1
                wait_time = backoff_factor ** retries
                logging.warning(f"Retry {retries}/{max_retries}: {e}. Waiting {wait_time} seconds before retrying...")
                time.sleep(wait_time)
        logging.error(f"Failed after {max_retries} retries.")
        return None

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
        max_retries = 5
        for attempt in range(max_retries):
            try:
                response = self.session.get(product, headers=headers, stream=True, timeout=(5, 30))
                response.raise_for_status()

                # Combine chunks into a single content object
                content = b"".join(chunk for chunk in response.iter_content(chunk_size=1024) if chunk)
                return BeautifulSoup(content, 'html.parser')

            except ChunkedEncodingError:
                logging.warning(f"ChunkedEncodingError on attempt {attempt + 1} for {product}")
                if attempt == max_retries - 1:
                    logging.error(f"Failed to load {product} after {max_retries} retries.")
                    return None
                sleep(1)  # Wait before retrying
            except Timeout:
                logging.error(f"Timeout occurred while accessing {product}.")
                return None
            except RequestException as e:
                logging.error(f"RequestException for {product} - {e}")
                return None
    
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
            except Exception as err:
                logging.warning('Unable to retrieve product TITLE.')
                logging.warning(f"AttributeError while evaluating title element: {err}")
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
            except Exception as err:
                logging.warning('Unable to retrieve product DESCRIPTION.')
                logging.warning(f"AttributeError while evaluating description element: {err}")
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
                logging.warning('Unable to retrieve product PRICE.')
                logging.warning(f"AttributeError while evaluating price element: {err}")
                price = 0

        # Scrape Availability
            try:
                available = eval(availableElement) if productSoup else False
            except AttributeError as e:
                logging.warning(f"AttributeError while evaluating available element: {e}")
                available = False
            except Exception as err:
                logging.warning('Unable to retrieve product AVAILABLE.')
                logging.warning(f"AttributeError while evaluating available element: {err}")


        # Return all values
            return ([title,description,price,available])