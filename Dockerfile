FROM otasys/elk-redis

RUN apt-get update -qq \
 && apt-get install -qqy python-pip
RUN pip install docopt \
 && pip install trollius

ADD ./logreplay.py /usr/local/bin/
RUN chmod +x /usr/local/bin/logreplay.py
RUN mkdir /tmp/logreplay-input/
ADD ./supervisor/logreplay.conf /etc/supervisor/conf.d/

ADD ./logstash/logstash-indexer.conf /etc/logstash/
ADD ./supervisor/logstash-indexer.conf /etc/supervisor/conf.d/

CMD /usr/bin/supervisord -n -c /etc/supervisor/supervisord.conf
