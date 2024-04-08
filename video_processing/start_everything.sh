#!/bin/bash

# Start Zookeeper and Kafka
echo "Starting Zookeeper and Kafka..."
cd ../Rohans-Research/kafka_2.13-3.6.0
./bin/zookeeper-server-start.sh ./config/zookeeper.properties > zookeeper.log 2>&1 &
sleep 10 # Wait for Zookeeper to fully start
./bin/kafka-server-start.sh ./config/server.properties > kafka.log 2>&1 &
sleep 10 # Wait for Kafka to fully start

# Check and create Kafka topics if necessary
echo "Setting up Kafka topics..."
./bin/kafka-topics.sh --list --bootstrap-server localhost:9092 | grep 'incoming-videos' || ./bin/kafka-topics.sh --create --topic incoming-videos --bootstrap-server localhost:9092 --partitions 1 --replication-factor 1
./bin/kafka-topics.sh --list --bootstrap-server localhost:9092 | grep 'processed-videos' || ./bin/kafka-topics.sh --create --topic processed-videos --bootstrap-server localhost:9092 --partitions 1 --replication-factor 1

# Navigate to your Flask application directory
echo "Starting Flask application..."
cd /path/to/your/flask/app
export FLASK_APP=app.py
flask run > flask.log 2>&1 &

# Run the video_consumer.py script
echo "Running video_consumer.py script..."
python3 video_consumer.py > video_consumer.log 2>&1 &

echo "All processes started."
