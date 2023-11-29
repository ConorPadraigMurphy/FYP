How I have Set up Zookeeper and Kafka

To Start Zookeeper
./bin/zookeeper-server-start.sh ./config/zookeeper.properties

To Start Kafka
./bin/kafka-server-start.sh ./config/server.properties

Created two Topics

For Incoming Video File Paths:
bin/kafka-topics.sh --create --topic incoming-videos --bootstrap-server localhost:9092 --partitions 1 --replication-factor 1

For Processed Video Information:
bin/kafka-topics.sh --create --topic processed-videos --bootstrap-server localhost:9092 --partitions 1 --replication-factor 1

Check Topics created properly:
bin/kafka-topics.sh --list --bootstrap-server localhost:9092


Install Confluent Kafka for Python
pip install confluent-kafka

Added Kafka to python and Produces a message which is a unique id given to the video.

How to check what Messages are in the topic:
bin/kafka-console-consumer.sh --bootstrap-server localhost:9092 --topic incoming-videos --from-beginning
