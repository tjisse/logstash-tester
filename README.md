# logstash-tester
Container for testing Logstash configuration with replaying logs

Provide:
- a Logstash configuration
- a bunch of log files

Receive:
- a Kibana view of your log events being replayed

Example:

`docker run --name logstash-tester -p 9292:9292 -p 9200:9200 -v /etc/logstash/conf.d:/etc/logstash/conf.d:ro -v /var/log/<log-dir>:/tmp/logreplay-input:ro --add-host <redis_host_used_in_config>:127.0.0.1 -it tjissevdwal/logstash-tester`
