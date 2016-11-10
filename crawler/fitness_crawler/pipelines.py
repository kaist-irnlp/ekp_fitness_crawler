# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
import re
import os
from pyArango.connection import Connection
from pyArango.theExceptions import CreationError
from scrapy.exceptions import DropItem


class CleanTextPipeline(object):
    """텍스트 노이즈 제거 (줄바꿈, 반복되는 공백 등)

    만약 필드값이 `None`일 경우 공백으로 대체
    """
    wspace_pattern = re.compile(r'[\n\s]+')

    def process_item(self, item, spider):
        """전처리 수행 메서드

        각 필드에 다음 조치를 취함:
            `None`을 공백으로 대체, 불필요한 공백 제거
        """
        fields = ['title', 'lead', 'content']

        # 각 필드에 다음 조치를 취함:
        # `None`을 공백으로 대체, 불필요한 공백 제거
        for field in fields:
            if not item[field]:
                item[field] = ''
            item[field] = re.sub(self.wspace_pattern, ' ', item[field])

        return item

class ArangoPipeline(object):
    """ArangoDB에 데이터 저정하는 파이프라인
    """
    ARANGO_URL = os.environ.get('ARANGO_HOST_PORT') or 'http://localhost:18529'
    ARANGO_DB = 'ekp'

    def __init__(self):
        self.conn = Connection(arangoURL=self.ARANGO_URL, username='root', password='ir7753nlp!')
        self.db = self.create_or_get_db(self.conn, self.ARANGO_DB)

    def create_or_get_db(self, connection, db_name):
        """Create or fetch db

        Args:
            connection (pyArango.connection.connection): connection to DB
            db_name (str): the name of DB

        Returns:
            db (pyArango.database.database): the database
        """
        try:
            db = connection.createDatabase(db_name)
        except CreationError:
            db = connection[db_name]

        return db

    def create_or_get_collection(self, collection_name):
        """ArangoDB Collection 반환 (필요시 생성)

        [흐름]]
            1. DB에 주어진 collection이 있는지 여부 체크
            2. 있으면 그대로 반환, 없으면 생성 후 반환
            3. `uid` 필드에 unique index 제약 생성 (이미 크롤링한 아이템 도달 시 종료 체크 위함)
        """
        # create or get collection
        try:
            collection = self.db.createCollection(name=collection_name)
        except CreationError:
            collection = self.db[collection_name]

        # ensure index on `uid` field
        collection.ensureHashIndex(fields=['uid'], unique=True)

        return collection

    def process_item(self, item, spider):
        """수집된 item을 ArangoDB에 삽입
        """
        collection = self.create_or_get_collection(collection_name=spider.name)
        doc = collection.createDocument()

        # Item의 모든 필드를 Arango document에 매핑
        for field, value in item.items():
            doc[field] = value

        # ArangoDB에 Item 삽입
        try:
            doc.save()
        except CreationError:
            spider.stop_crawler(item=item, reason='duplicate')
            raise DropItem('duplicate')

        return item
