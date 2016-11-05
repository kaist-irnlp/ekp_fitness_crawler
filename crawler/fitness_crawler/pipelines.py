# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
import re

class CleanTextPipeline(object):
    """텍스트 노이즈 제거 (줄바꿈, 반복되는 공백 등)
    
    만약 필드값이 `None`일 경우 공백으로 대체
    """
    wspace_pattern = re.compile(r'[\n\s]+')

    def process_item(self, item, spider):
        fields = ['title', 'lead', 'content'] 

        # 각 필드에 다음 조치를 취함:
        # `None`을 공백으로 대체, 불필요한 공백 제거
        for field in fields:
            if not item[field]:
                item[field] = ''
            item[field] = re.sub(self.wspace_pattern, ' ', item[field])

        return item
