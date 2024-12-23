import logging

class JsonManager:
    def jsonSelectors(self, militariaSite):
        """Safely unpack JSON site profile into expected fields, ignoring unwanted keys."""
        try:
            base_url = militariaSite['base_url']
            source = militariaSite['source']
            pageIncrement = militariaSite['page_increment']
            currency = militariaSite['currency']
            products = militariaSite['products']
            productUrlElement = militariaSite['product_url_element']
            titleElement = militariaSite['title_element']
            descElement = militariaSite['desc_element']
            priceElement = militariaSite['price_element']
            availableElement = militariaSite['available_element']
            conflict = militariaSite['conflict_element']
            nation = militariaSite['nation_element']
            item_type = militariaSite['item_type_element']
            grade = militariaSite['grade_element']
            productsPageUrl = militariaSite['productsPageUrl']
            
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
