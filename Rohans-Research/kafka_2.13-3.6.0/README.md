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

Now when multiple videos are uploaded they are saved with unique id and are put into the queue to get processed

How it works: App.py gets post requests and saves video with UUID and sends a message to the topic with the UUID, video_consumer.py is alway listening for new messages, As soon as new message is received it used the UUID in the message to queue the next video to get processed.

# To - Do

- Sending final information to endpoint still not brought into this implementation 

- Videos replace previews video information on text

- User ID will be used to id videos and track them to make it easier to track back to the user who uploaded

- Send Video Data to mongo straight away
