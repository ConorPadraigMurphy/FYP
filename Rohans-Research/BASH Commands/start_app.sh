#!/bin/bash

# To make script executable chmod +x start_app.sh
# Command to start script ./start_app.sh

# Navigate to Kafka directory
cd ../kafka_2.13-3.6.0

# Start Zookeeper
./bin/zookeeper-server-start.sh ./config/zookeeper.properties &
sleep 5 # Wait for Zookeeper to start

# Start Kafka
./bin/kafka-server-start.sh ./config/server.properties &
sleep 5 # Wait for Kafka to start

# Check for existing Kafka topics
TOPICS=$(./bin/kafka-topics.sh --list --bootstrap-server localhost:9092)

# Create Kafka topics if they don't exist
if [[ ! $TOPICS =~ "incoming-videos" ]]; then
  ./bin/kafka-topics.sh --create --topic incoming-videos --bootstrap-server localhost:9092 --partitions 1 --replication-factor 1
fi

if [[ ! $TOPICS =~ "processed-videos" ]]; then
  ./bin/kafka-topics.sh --create --topic processed-videos --bootstrap-server localhost:9092 --partitions 1 --replication-factor 1
fi

# Navigate to the directory where app.py is located
cd ../../Python_Code/TensorFlow_Detection_Research

# Start Flask app
flask run &
sleep 5 # Wait for Flask app to start

# Run video_consumer script
python3 video_consumer.py &

# Navigate to the frontend directory
cd ../../frontend

# Start React frontend
npm install --force
npm start

