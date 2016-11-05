# -*- coding: utf-8 -*-
import scrapy
from urlparse import urlparse
from urlparse import parse_qs
from urlparse import urljoin
from fitness_crawler.items import MensHealthItem
from w3lib.html import remove_tags


class MenshealthSpider(scrapy.Spider):
    name = "menshealth"
    allowed_domains = ["menshealth.designhouse.co.kr"]

    BASE_URL = 'http://menshealth.designhouse.co.kr/in_magazine/sub.html?c_id=00010006'
    """Fitness & Sports 게시판의 base url"""

    page = 1
    """작업중인 게시판 페이지 번호를 나타냄"""

    def start_requests(self):
        """최초 크롤링 요청을 시작하는 곳

        게시판 최신(첫) 페이지부터 시작

            [흐름]
            1. 게시판 페이지에서 글 링크 추출
            2. 추출된 각각의 글 링크를 타고 들어가서 텍스트 추출 - 비동기 처리 (parse_article)
            3. 다음 페이지로 넘어가서 글 링크 추출 (so on)
        """
        start_url = self.get_list_url(page=self.page)
        return [scrapy.Request(url=start_url, callback=self.parse_list)]

    def get_list_url(self, page):
        """넘겨진 페이지에 해당되는 게시판 페이지 링크 반환

        Argument:
            page (int): 게시판 페이지

        Returns:
            url (str): 게시판 페이지 링크
        """
        return self.BASE_URL + '&' + 'p_no={page}'.format(page=page)

    def parse_list(self, response):
        """1) 게시판 페이지에서 글 링크 추출 후, 2) 각 글 링크에서 텍스트 추출 요청 (parse_article)

        Argument:
            response (scrapy.Response)
        """
        urls = response.xpath('//a[@class="new_lists"]/@href').extract()
        for u in urls:
            url = urljoin(self.BASE_URL, u)
            yield scrapy.Request(url=url, callback=self.parse_article, dont_filter=True)

    def get_info_id(self, url):
        """uid로 쓸 info_id를 글 URL에서 추출

        Argument:
            url (str): 글 URL

        Returns:
            info_id (int): info_id if exist otherwise 0
        """
        try:
            query_string = urlparse(url).query
            info_id = parse_qs(query_string)['info_id'][0]
        except IndexError:
            info_id = 0
        except ValueError:
            info_id = 0

        return info_id

    def parse_article(self, response):
        """게시판 글 파싱
        """
        url = response.url
        self.logger.info(url)

        # item
        item = MensHealthItem()
        item['uid'] = self.get_info_id(url)
        item['title'] = response.xpath('//*[@class="dtitle"]/text()').extract_first()
        item['subtitle'] = response.xpath('//*[@class="sktitle"]/text()').extract_first()
        item['lead'] = response.xpath('//*[@class="hplead"]/text()').extract_first()
        item['content'] = "\n".join([remove_tags(text.strip()) for text in response.xpath('//*[@class="hpcontents"]//text()').extract()])
        item['url'] = url
        yield item
