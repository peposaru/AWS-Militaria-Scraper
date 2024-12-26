from bs4 import BeautifulSoup
import logging

def militaria_plaza(product_soup):
    """
    Extracts high-resolution images from Militaria Plaza product pages.

    Args:
        product_soup (BeautifulSoup): Parsed HTML of the product page.

    Returns:
        list: List of URLs for the largest images.
    """
    try:
        # Collect high-resolution image URLs from the `href` attribute of links with `rel="vm-additional-images"`
        image_urls = [
            tag['href']
            for tag in product_soup.select("a[rel='vm-additional-images']")
            if 'href' in tag.attrs
        ]
        return image_urls
    except Exception as e:
        logging.error(f"Error in militaria_plaza: {e}")
        return []

# Sample usage
if __name__ == "__main__":
    # Sample HTML (Replace with actual HTML for real testing)
    sample_html = """
    <div class="product-container productdetails-view productdetails">

	
		<div class="back-to-category">
		<a href="/awards-medals" class="product-details" title="Awards &amp; Medals">Back to: Awards &amp; Medals</a>
	</div>

		<h2>Panzer Assault Badge in Bronze - FLL</h2>
	
	
	
	
	
	<div class="vm-product-container">
	<div class="vm-product-media-container">
		<div class="main-image">
			<a title="28979_1" rel="vm-additional-images" href="https://militariaplaza.nl/images/stories/virtuemart/product/28979_1.jpg"><img width="800" height="800" loading="lazy" src="/images/stories/virtuemart/product/resized/28979_1_0x800.webp" alt="28979_1"></a>			<div class="clear"></div>
		</div>
			</div>

	<div class="vm-product-details-container">
		<div class="spacer-buy-area">

		
		<div class="product-price" id="productPrice26502" data-vm="product-prices">
	<span class="price-crossed"></span><div class="PricesalesPrice vm-display vm-price-value"><span class="PricesalesPrice">€ 400,00</span></div></div> <div class="clear"></div>	<div class="addtocart-area">
		<form method="post" class="product js-recalculate" action="#" autocomplete="off">
			<div class="vm-customfields-wrap">
							</div>			
				
	<div class="addtocart-bar">
			<img src="/./components/com_virtuemart/assets/images/sold.gif" alt="Sold" width="113" height="40">
        
	</div>			<input type="hidden" name="option" value="com_virtuemart">
			<input type="hidden" name="view" value="cart">

			<input type="hidden" name="pname" value="Panzer Assault Badge in Bronze - FLL">
			<input type="hidden" name="pid" value="26502">
			<input type="hidden" name="Itemid" value="1693">		</form>

	</div>

			<div class="ask-a-question">
				<a class="ask-a-question" href="/awards-medals/panzer-assault-badge-in-bronze-fll-detail?task=askquestion&amp;tmpl=component" rel="nofollow">Ask a question about this product</a>
			</div>
		
		
		</div>
	</div>
	<div class="clear"></div>


	</div>


			<div class="product-description">
			<span class="title">Description</span>
	<p>Panzer Assault Badge in Bronze (Panzerkampfabzeichen in Bronze). The Panzer Assault Badge in bronze was instituted by 'Generaloberst Walther von Brauchitsch' on '1 june 1940' for award to Panzer-Grenadier, medical, and armored car personnel who participated in three different armored assaults on three different days. This is a nice 'Feinzink' example which shows outstanding detail and still retains most of its original bronze finish. The badge is not visible maker marked but can be attributed to production by the company of 'Friedrich Linden', based in Lüdenscheid. Of course are the pin and catch fully functional. This is a less often seen early solid zinc construction curved variant. Nice and desirable original badge in very good condition!</p>		</div>
	
			<span class="title">Product Images</span>
<div class="additional-images">
			<div class="floatleft">
			<a title="28979_2" rel="vm-additional-images" href="https://militariaplaza.nl/images/stories/virtuemart/product/28979_2.jpg"><img width="296" height="296" loading="lazy" src="/images/stories/virtuemart/product/resized/28979_2_296x320.webp" alt="28979_2"></a>		</div>
			<div class="floatleft">
			<a title="28979_3" rel="vm-additional-images" href="https://militariaplaza.nl/images/stories/virtuemart/product/28979_3.jpg"><img width="296" height="296" loading="lazy" src="/images/stories/virtuemart/product/resized/28979_3_296x320.webp" alt="28979_3"></a>		</div>
			<div class="floatleft">
			<a title="28979_4" rel="vm-additional-images" href="https://militariaplaza.nl/images/stories/virtuemart/product/28979_4.jpg"><img width="296" height="296" loading="lazy" src="/images/stories/virtuemart/product/resized/28979_4_296x320.webp" alt="28979_4"></a>		</div>
		<div class="clear"></div>
</div>



<script id="updDynamicListeners-js" type="text/javascript">//<![CDATA[ 
jQuery(document).ready(function() { // GALT: Start listening for dynamic content update.
	// If template is aware of dynamic update and provided a variable let's
	// set-up the event listeners.
	if (typeof Virtuemart.containerSelector === 'undefined') { Virtuemart.containerSelector = '.productdetails-view'; }
	if (typeof Virtuemart.container === 'undefined') { Virtuemart.container = jQuery(Virtuemart.containerSelector); }
	if (Virtuemart.container){
		Virtuemart.updateDynamicUpdateListeners();
	}
	
}); //]]>
</script>



<script id="ready.vmprices-js" type="text/javascript">//<![CDATA[ 
jQuery(document).ready(function($) {

		Virtuemart.product($("form.product"));
}); //]]>
</script>
<script id="popups-js" type="text/javascript">//<![CDATA[ 
jQuery(document).ready(function($) {
		
		$('a.ask-a-question, a.printModal, a.recommened-to-friend, a.manuModal').click(function(event){
		  event.preventDefault();
		  $.fancybox({
			href: $(this).attr('href'),
			type: 'iframe',
			height: 550
			});
		  });
		
	}); //]]>
</script>
<script id="imagepopup-js" type="text/javascript">//<![CDATA[ 
jQuery(document).ready(function() {
	Virtuemart.updateImageEventListeners()
});
Virtuemart.updateImageEventListeners = function() {
	jQuery("a[rel=vm-additional-images]").fancybox({
		"titlePosition" 	: "inside",
		"transitionIn"	:	"elastic",
		"transitionOut"	:	"elastic"
	});
	jQuery(".additional-images a.product-image.image-0").removeAttr("rel");
	jQuery(".additional-images img.product-image").click(function() {
		jQuery(".additional-images a.product-image").attr("rel","vm-additional-images" );
		jQuery(this).parent().children("a.product-image").removeAttr("rel");
		var src = jQuery(this).parent().children("a.product-image").attr("href");
		jQuery(".main-image img").attr("src",src);
		jQuery(".main-image img").attr("alt",this.alt );
		jQuery(".main-image a").attr("href",src );
		jQuery(".main-image a").attr("title",this.alt );
		jQuery(".main-image .vm-img-desc").html(this.alt);
		}); 
	} //]]>
</script>
<script id="ajaxContent-js" type="text/javascript">//<![CDATA[ 
Virtuemart.container = jQuery('.productdetails-view');
Virtuemart.containerSelector = '.productdetails-view';
//Virtuemart.recalculate = true;	//Activate this line to recalculate your product after ajax //]]>
</script>
<script id="vmPreloader-js" type="text/javascript">//<![CDATA[ 
jQuery(document).ready(function($) {
	Virtuemart.stopVmLoading();
	var msg = '';
	$('a[data-dynamic-update="1"]').off('click', Virtuemart.startVmLoading).on('click', {msg:msg}, Virtuemart.startVmLoading);
	$('[data-dynamic-update="1"]').off('change', Virtuemart.startVmLoading).on('change', {msg:msg}, Virtuemart.startVmLoading);
}); //]]>
</script>
<script type="application/ld+json">
{
  "@context": "http://schema.org/",
  "@type": "Product",
  "name": "Panzer Assault Badge in Bronze - FLL",
  "description":"Panzer Assault Badge in Bronze - FLL Awards &amp; Medals Panzer Assault Badge in Bronze (Panzerkampfabzeichen in Bronze). The badge is an unmarked example which can be attributed to the company of &#039;Friedrich Linden&#039; from Lüdenscheid. Nice early curved solid zinc badge in very good condition!",
  "productID":"28979",
  "sku": "28979",
  "image": [
    "https://militariaplaza.nl/images/stories/virtuemart/product/28979_1.jpg",     "https://militariaplaza.nl/images/stories/virtuemart/product/28979_2.jpg",     "https://militariaplaza.nl/images/stories/virtuemart/product/28979_3.jpg",     "https://militariaplaza.nl/images/stories/virtuemart/product/28979_4.jpg"  ],
  "offers": {
    "@type": "Offer",
    "priceCurrency": "EUR",
    "availability": "OutOfStock",
    "price": "400",
    "url": "https://militariaplaza.nl/awards-medals/panzer-assault-badge-in-bronze-fll-detail",
    "itemCondition": "UsedCondition"
  }
}
</script></div>
    """
    soup = BeautifulSoup(sample_html, 'html.parser')
    
    # Test the function
    image_urls = militaria_plaza(soup)
    print("Extracted Image URLs:")
    for url in image_urls:
        print(url)
