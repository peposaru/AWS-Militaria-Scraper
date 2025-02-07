import logging, json

class JsonManager:
    def load_json_selectors(self, selectorJson):
        """
        Load and validate the JSON selectors file.
        """
        try:
            with open(selectorJson, 'r') as userFile:
                jsonData = json.load(userFile)
            return jsonData
        except FileNotFoundError:
            logging.error(f'JSON selector file not found: {selectorJson}')
            raise
        except json.JSONDecodeError as e:
            logging.error(f'Error decoding JSON selector file: {e}')
            raise

    def jsonSelectors(self, militariaSite):
        """Safely unpack JSON site profile into expected fields, ignoring unwanted keys."""
        try:
            base_url            = militariaSite['base_url']
            source              = militariaSite['source']
            pageIncrement       = militariaSite['page_increment']
            currency            = militariaSite['currency']
            products            = militariaSite['products']
            productUrlElement   = militariaSite['product_url_element']
            titleElement        = militariaSite['title_element']
            descElement         = militariaSite['desc_element']
            priceElement        = militariaSite['price_element']
            availableElement    = militariaSite['available_element']
            conflict            = militariaSite['conflict_element']
            nation              = militariaSite['nation_element']
            item_type           = militariaSite['item_type_element']
            grade               = militariaSite['grade_element']
            productsPageUrl     = militariaSite['productsPageUrl']
            
            # Handle image_element: Treat empty string or placeholder as None
            imageElement = militariaSite.get('image_element', None)
            if imageElement in ["", "skip", "none"]:  # Add any placeholders here
                imageElement = None

            # Return only the required fields
            return (
                conflict, nation, item_type, grade, source, pageIncrement, currency, products,
                productUrlElement, titleElement, descElement, priceElement, availableElement,
                productsPageUrl, base_url, imageElement
            )
        except KeyError as e:
            logging.error(f"Missing key in JSON selectors: {e}")
            raise
        except Exception as e:
            logging.error(f"Error unpacking JSON selectors: {e}")
            raise

    # This makes sure that the json profile has the required elements.
    def validate_json_profile(self,militariaSite):
        """Validate required keys in JSON profile."""
        # Define all possible keys in the JSON profile
        all_keys = {
            "source",
            "product_url_element",
            "productsPageUrl",
            "base_url",
            "page_increment",
            "currency",
            "products",
            "title_element",
            "desc_element",
            "price_element",
            "available_element",
            "image_element",
            "conflict_element",
            "nation_element",
            "item_type_element",
            "grade_element"
        }

        # Define optional keys
        optional_keys = {"conflict_element", "nation_element", "item_type_element", "grade_element"}

        # Calculate required keys by excluding optional keys
        required_keys = all_keys - optional_keys

        # Determine missing keys by comparing the JSON keys to the required keys
        missing_keys = required_keys - set(militariaSite.keys())
        if missing_keys:
            raise ValueError(f"Missing required keys in JSON profile: {missing_keys}")
