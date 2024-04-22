This is the README for Rohan and Conor's Final Year Project

**Frontend URL:** https://conorpadraigmurphy.github.io/FYP/

## Project Kanban + Gantt Chart

    - Kanban: https://rohansikder4.atlassian.net/jira/software/projects/KAN/boards/1
    - Gantt Chart: https://rohansikder4.atlassian.net/jira/software/projects/KAN/boards/1/timeline

## Project Dependencies

1. Install Anaconda(python) or Python

2. Installs for app.py
   - pip install ultralytics
   - pip install numpy
   - pip install opencv-python
   - pip install flask
   - pip install confluent-kafka
   - pip install pymongo
   - pip install python-dotenv
   - Model: YoloV8 (Ultralytics)

3. Install Node packages (Run in Frontend folder)
   - npm install

## How to run the application On a Mac/Linux Machine (Run each command in separate terminals)

1. Use Command where app.py is located
   - flask run
2. Run video_consumer python script
   - python3 video_consumer.py
3. Run Frontend backend
   - node server.js
4. Run react frontend (Run command in frontend folder)
   - npm start

## How to run the application on a Windows Machine (Run each command in separate terminals)

1. Start Zookeeper (windows)
   .\bin\windows\zookeeper-server-start.bat .\config\zookeeper.properties

2. Start Kafka
   .\bin\windows\kafka-server-start.bat .\config\server.properties

3. Check if kafka topics are listed
   .\bin\windows\kafka-topics.bat --list --bootstrap-server localhost:9092

4. If there are no topics created, create them using the below commands
   .\bin\windows\kafka-topics.bat --create --topic incoming-videos --bootstrap-server localhost:9092 --partitions 1 --replication-factor 1
   .\bin\windows\kafka-topics.bat --create --topic processed-videos --bootstrap-server localhost:9092 --partitions 1 --replication-factor 1

5. Run this command in the directory of the project
   flask run

6. Run video_consumer python script
   python video_consumer.py

7. Run react frontend in frontend folder
   npm start

Dependencies
npm install OR npm install --force
npm install @mui/icons-material
npm install @emotion/react @emotion/styled @mui/system
