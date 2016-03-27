# logstash-tester
ELK+Redis container that can replay log events from a bunch of files in a random way for the purpose of testing Logstash configurations

Provide:
- a Logstash configuration
- a bunch of log files

Receive:
- a Kibana dashboard on http://localhost:9292 on which your log events are being replayed

Example:

`docker run --name logstash-tester -p 9292:9292 -p 9200:9200 -v /etc/logstash/conf.d:/etc/logstash/conf.d:ro -v /var/log/<log_dir>:/tmp/logreplay-input:ro --add-host <redis_host_used_in_config>:127.0.0.1 -it tjisse/logstash-tester`
