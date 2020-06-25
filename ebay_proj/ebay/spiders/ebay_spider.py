import scrapy
import re
from ebay.items import Listing

class EbaySpider(scrapy.Spider):
    name = "ebay"
    # start_urls = ['https://www.ebay.com']

    def start_requests(self):
        first_url = 'https://www.ebay.com'
        yield scrapy.Request(url=first_url, callback=self.parse_firstpage)
        # first_result_page = 
        
        # urls = ['https://www.ebay.com/sch/i.html?_from=R40&_trksid=p2380057.m570.l2632.R2.TR10.TRC1.A0.H0.Xdell+r610.TRS0&_nkw=dell+r610&_sacat=175698']
        # for url in urls:
        #     yield scrapy.Request(url=url, callback=self.parse)

    def parse_firstpage(self, response):
        # defaults to iphone if product is not specified
        self.product = getattr(self, 'product', 'iphone') 
        product_query = '+'.join(self.product.split())

        # only take the first two values which corresponds to the hidden credentials
        from_id, trks_id = response.xpath('//input[@type="hidden"]/@value').getall()[:2] 
        product_search_url = f'https://www.ebay.com/sch/i.html?_from={from_id}&_trksid={trks_id}&_nkw={product_query}&_sacat=0&_ipg=200'
        return scrapy.Request(url=product_search_url) #, callback=self.parse)

    def parse(self, response):
        # self.save_html(response)
        
        listings = response.xpath('//li[contains(@class, "s-item")]')
        for listing in listings:
            
            # auction items will distort price range
            is_auc = 0
            if listing.xpath('.//span[@class="s-item__bids s-item__bidCount"]').get() != None:
                is_auc = 1

            # resolve listing title
            title = listing.xpath('.//*[@class="s-item__title"]//text()').get()
            # sponsored or new listing links have a different class
            if title is None:
                title = listing.xpath('.//*[@class="s-item__title s-item__title--has-tags"]/text()').get()
            if title is None:
                title = listing.xpath('.//*[@class="s-item__title s-item__title--has-tags"]//text()').get()
            if title == 'New Listing':
                title = listing.xpath('.//*[@class="s-item__title"]//text()').extract()[1]
            if title is None: # give up
                continue
            
            # initial default values
            stars = 0.
            # first 3 characters denotes the float rating e.g. 3.5
            stars_text = listing.xpath('.//*[@class="clipped"]/text()').extract_first()
            if stars_text is not None:
                if re.match(r'\d\.\d', stars_text[:3]) is not None:
                    stars = float(stars_text[:3])

            # price 
            # [(optional|self::*)/child]
            # price = listing.xpath('.//span[@class="s-item__price"]/text()').extract_first()
            price = listing.xpath('.//span[@class="s-item__price"][(span|self::*)/text()]').extract_first()
            price = re.sub(r'<[^<]+>', "", price)

            yield Listing(
                title = title,
                stars = stars, 
                condition = listing.xpath('.//span[@class="SECONDARY_INFO"]/text()').get(),
                price = price, # some listing has range of prices
                link = listing.xpath('.//a[@class="s-item__link"]/@href').get(),
                is_auc = is_auc
            )
            # yield {
            #     'title': title,
            #     'stars': stars,
            #     'condition': listing.xpath('.//span[@class="SECONDARY_INFO"]/text()').get(),
            #     'price': listing.xpath('.//span[@class="s-item__price"]/text()').extract_first(), # some listing has range of prices   
            #     'link': listing.xpath('.//a[@class="s-item__link"]/@href').get(),
            # }

        # go to next page URL
        next_page_url = response.xpath('//a[@aria-label="Next page"]/@href').get()
        if next_page_url is not None:
            yield scrapy.Request(url=next_page_url) #, callback=self.parse) <- this is implied
        # return super().parse(response)

    def save_html(self, response):
        """Saves the response from a HTTP Request into HTML text file

        Arguments:
            response {scrapy.Response} -- the response object returned from the spider
        """
        pageid = response.url.split("/")[-1]
        filename = response.url[-50:] + '.html'
        # filename = f'dellr610-{pageid}.html'
        with open(filename, 'wb') as f:
            f.write(response.body)
        self.log(f'Saved file {filename}')
