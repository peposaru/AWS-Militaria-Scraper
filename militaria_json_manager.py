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
