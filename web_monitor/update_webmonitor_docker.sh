#!/bin/bash

# Navigate to the project root (assuming this script is in web_monitor/)
cd ~/projects/dev/2.personal/home_ai_project/web_monitor

echo "--- Stopping and removing existing web_monitor container (if any) ---"
docker stop web_monitor_container > /dev/null 2>&1
docker rm web_monitor_container > /dev/null 2>&1

echo "--- Pulling latest changes from Git ---"
git pull origin master

echo "--- Building new Docker image for web_monitor_app ---"
docker build -t web_monitor_app .

if [ $? -eq 0 ]; then
    echo "--- Docker image built successfully. Running new container ---"
    docker run -d -p 8050:5000 --name web_monitor_container web_monitor_app
    if [ $? -eq 0 ]; then
        echo "--- web_monitor_container started successfully on port 8050 ---"
        echo "--- Access dashboard at http://<Jetson-IP>:8050 ---"
        docker logs web_monitor_container &
    else
        echo "ERROR: Failed to run Docker container."
    fi
else
    echo "ERROR: Docker image build failed."
fi
