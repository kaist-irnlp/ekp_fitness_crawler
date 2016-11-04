# -*- coding: utf-8 -*-
import scrapy


class MenshealthSpider(scrapy.Spider):
    name = "menshealth"
    allowed_domains = ["menshealth.designhouse.co.kr"]
    start_urls = (
        'http://www.menshealth.designhouse.co.kr/',
    )

    def parse(self, response):
        pass
