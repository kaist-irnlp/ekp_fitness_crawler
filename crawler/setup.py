#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages
from codecs import open


def readme():
    with open('README.md', 'r', encoding='utf-8') as f:
        return f.read()

setup(
    name='fitness_crawler',
    version='0.0.1',
    packages=find_packages(exclude=['contrib', 'docs', 'tests']),
    url='https://github.com/kaist-irnlp/ekp_fitness_crawler',
    license='',
    description='Fitness resource crawler',
    long_description=readme(),
    author='Kyoung-Rok Jang',
    author_email='kyoungrok.jang@gmail.com',
    install_requires=[
        'scrapy',
        'pyarango',
        'click'
    ],
    entry_points='''
        [console_scripts]
        fitness_crawler=fitness_crawler.__main__:main
    ''',
    zip_safe=False
)