#!/bin/bash

ls
echo "Starting Zookeeper and Kafka..."
# Start Zookeeper
./kafka_2.13-3.6.0/bin/zookeeper-server-start.sh ./kafka_2.13-3.6.0/config/zookeeper.properties > zookeeper.log 2>&1 &
sleep 10 # Wait for Zookeeper to fully start

# Start Kafka
./kafka_2.13-3.6.0/bin/kafka-server-start.sh ./kafka_2.13-3.6.0/config/server.properties > kafka.log 2>&1 &
sleep 10 # Wait for Kafka to fully start

echo "Setting up Kafka topics..."
# Check and create Kafka topics if necessary
./kafka_2.13-3.6.0/bin/kafka-topics.sh --list --bootstrap-server localhost:9092 | grep 'incoming-videos' || ./kafka_2.13-3.6.0/bin/kafka-topics.sh --create --topic incoming-videos --bootstrap-server localhost:9092 --partitions 1 --replication-factor 1
./kafka_2.13-3.6.0/bin/kafka-topics.sh --list --bootstrap-server localhost:9092 | grep 'processed-videos' || ./kafka_2.13-3.6.0/bin/kafka-topics.sh --create --topic processed-videos --bootstrap-server localhost:9092 --partitions 1 --replication-factor 1

echo "Starting Flask application..."
export FLASK_APP=app.py
export FLASK_ENV=development
flask run > flask.log 2>&1 &

echo "Running video_consumer.py script..."
python3 video_consumer.py > video_consumer.log 2>&1 &

echo "All processes started."