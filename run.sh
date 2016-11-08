#!/bin/bash

#!/bin/bash
bash /wait-for-it.sh arango:8529
sleep 5

cd /crawler && scrapy crawl menshealth