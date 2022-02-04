import scrapy
from scrapy.linkextractors import LinkExtractor

from toscrapy_book.items import BookItem


class TocrapyBookSpider(scrapy.Spider):
    name = 'tocrapy_book'
    allowed_domains = ['books.toscrape.com']
    # start_urls = ['http://books.toscrape.com/']

    def start_requests(self):
        yield scrapy.Request('http://books.toscrape.com/',
                             callback=self.parse,
                             headers={'User-Agent': 'Mozill/5.0'},
                             dont_filter=True)



    # 书籍列表页面的解析函数
    def parse(self, response):


        # 提取书籍列表页面中每本书的链接
        links = LinkExtractor(restrict_css="[class='image_container']").extract_links(response)
        for link in links:
            yield scrapy.Request(link.url, callback=self.parse_book)
        # 提取下一页链接
        next_link = LinkExtractor(restrict_css="[class='next']").extract_links(response)
        if next_link:
            next_url = next_link[0].url
            yield scrapy.Request(next_url, callback=self.parse)

        # le = LinkExtractor(restrict_css='article.product_pod h3')
        # for link in le.extract_links(response):
        #     yield scrapy.Request(link.url, callback=self.parse_book)
        # le = LinkExtractor(restrict_css='ul.pager li.next')
        # links = le.extract_links(response)
        # if links:
        #     next_url = links[0].url
        #     yield scrapy.Request(next_url, callback=self.parse)

    # 书籍页面的解析函数
    # def parse_book(self, response):
    #     book_information = BookItem
    #
    #     book_information["name"] = response.css('[class="col-sm-6 product_main"]').xpath("//h1").extract()  # 书名
    #     book_information['price'] = response.css('div.product_main').css('p.price_color::text').extract_first()  # 价格
    #     book_information['review_rating'] = response.css('div.product_main').css('p.star-rating::attr(class)').re_first(
    #         'star-rating ([A-Za-z]+)')  # 评价等级，1～5 星
    #     book_information['review_num'] = response.css('table.table.table-striped').xpath(
    #         '(.//tr)[last()]/td/text()').extract_first()  # 评价数量
    #     book_information["upc"] = response.css("[class ='table table-striped']").xpath(
    #         "//tbody/tr[1]/td").extract()  # 产品编码
    #     book_information['stock'] = response.css('table.table.table-striped').xpath('(.//tr)[last()-1]/td/text()') \
    #         .re_first('\((\d+) available\)')  # 库存量
    #
    #     yield book_information

    def parse_book(self, response):
        book = BookItem()

        sel = response.css('div.product_main')
        book['name'] = sel.xpath('./h1/text()').extract_first()
        book['price'] = sel.css('p.price_color::text').extract_first()
        book['review_rating'] = sel.css('p.star-rating::attr(class)').re_first('star-rating ([A-Za-z]+)')
        sel = response.css('table.table.table-striped')
        book['upc'] = sel.xpath('(.//tr)[1]/td/text()').extract_first()
        book['stock'] = sel.xpath('(.//tr)[last()-1]/td/text()').re_first('\((\d+) available\)')
        book['review_num'] = sel.xpath('(.//tr)[last()]/td/text()').extract_first()
        yield book
