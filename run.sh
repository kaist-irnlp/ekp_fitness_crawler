# create `fitness` db
arangosh \
    --server.username root \
    --server.database _system \
    --javascript.execute-string db._createDatabase("fitness");

cd /crawler && scrapy crawl menshealth