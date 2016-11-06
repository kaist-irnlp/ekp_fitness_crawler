# -*- coding: utf-8 -*-
import scrapy
from urlparse import urlparse
from urlparse import parse_qs
from urlparse import urljoin
from fitness_crawler.items import MensHealthItem
from w3lib.html import remove_tags
from scrapy.exceptions import CloseSpider


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
            2. 추출된 각각의 글 링크를 타고 들어가서 텍스트 추출 (parse_article) - 병렬적으로 처리
            3. 다음 페이지로 넘어가서 글 링크 추출 (so on)
        """
        start_url = self.get_list_url(page=self.page)
        return [scrapy.Request(url=start_url, callback=self.parse_list)]

    def stop(self, item, reason=""):
        """크롤링 중지"""
        raise CloseSpider(reason)

    def parse_list(self, response):
        """1) 게시판 페이지에서 글 링크 추출 후, 2) 각 글 링크에서 텍스트 추출 요청 (parse_article)

        Args:
            response (scrapy.Response)
        """
        _page = self.get_page_from_url(response.url)
        self.logger.info('Processing page %s', _page)

        # request each article
        # stop if none found
        urls = response.xpath('//a[@class="new_lists"]/@href').extract()
        if not urls:
            self.stop(reason='End of page reached')
        else:
            for u in urls:
                url = urljoin(self.BASE_URL, u)
                yield scrapy.Request(url=url, callback=self.parse_article, dont_filter=True)

        # request next page
        self.page += 1
        next_url = self.get_list_url(page=self.page)
        yield scrapy.Request(url=next_url, callback=self.parse_list, dont_filter=True)

    def get_url_query_value(self, url, query):
        """URL query의 특정 키의 value를 반환

        Args:
            url (str): URL
            query (str): specific key of query

        Returns:
            value (obj): value of given query key, None if not exists
        """
        try:
            query_string = urlparse(url).query
            query_value = parse_qs(query_string)[query]
            if len(query_value) == 1:
                query_value = query_value[0]
        except IndexError:
            query_value = None
        except ValueError:
            query_value = None
        except KeyError:
            self.logger.warning('{} not found in given url'.format(query))
            query_value = None
        return query_value

    def get_board_id_from_url(self, url):
        """게시판을 나타내는 c_id를 글 URL에서 추출

        Args:
            url (str): 글 URL

        Returns:
            c_id (int): c_id if exists in the url otherwise 0
        """
        return self.get_url_query_value(url=url, query='c_id')

    def get_article_id_from_url(self, url):
        """uid로 쓸 info_id를 글 URL에서 추출

        Args:
            url (str): 글 URL

        Returns:
            info_id (int): info_id if exists in the url otherwise 0
        """
        return self.get_url_query_value(url=url, query='info_id')

    def get_page_from_url(self, url):
        """URL에서 현재 페이지 추출

        Args:
            url (str): 페이지 URL

        Returns:
            page (int): page if exists in the url otherwise 0
        """
        try:
            query_string = urlparse(url).query
            page = parse_qs(query_string)['p_no'][0]
        except IndexError:
            page = 0
        except ValueError:
            page = 0
        except KeyError:
            self.logger.warning('p_no not found in url')
            page = 0
        return page

    def parse_article(self, response):
        """게시판 글 파싱
        """
        url = response.url
        self.logger.info(url)

        # item
        item = MensHealthItem()
        item['uid'] = self.get_article_id_from_url(url)
        item['title'] = response.xpath('//*[@class="dtitle"]/text()').extract_first()
        item['subtitle'] = response.xpath('//*[@class="sktitle"]/text()').extract_first()
        item['lead'] = response.xpath('//*[@class="hplead"]/text()').extract_first()
        item['content'] = " ".join([remove_tags(text.strip()) for text in response.xpath('//*[@class="hpcontents"]//text()').extract()])
        item['url'] = url
        yield item

    def get_list_url(self, page):
        """넘겨진 페이지에 해당되는 게시판 페이지 링크 반환

        Args:
            page (int): 게시판 페이지

        Returns:
            url (str): 게시판 페이지 링크
        """
        return self.BASE_URL + '&' + 'p_no={page}'.format(page=page)
