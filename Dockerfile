FROM python:2.7

# isntall essential packages
RUN apt-get update && apt-get install -y \
        supervisor \
        cron

# install arangoDB client
RUN wget http://www.arangodb.com/repositories/arangodb31/Debian_8.0/Release.key && \
    apt-key add - < Release.key && \
    echo 'deb http://www.arangodb.com/repositories/arangodb31/Debian_8.0/ /' | tee /etc/apt/sources.list.d/arangodb.list && \
    apt-get update && \
    apt-get install arangodb3-client=3.1.0 && \
    apt-get autoremove -y && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

COPY crawler/ /crawler
COPY run.sh /run.sh

WORKDIR /crawler

RUN chmod -R +x /crawler && pip install -r requirements.txt

ENTRYPOINT ["/bin/bash", "/run.sh"]