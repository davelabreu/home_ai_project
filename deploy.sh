#!/bin/bash
# Navigate to the project root
cd ~/projects/dev/2.personal/home_ai_project

echo "--- 🚀 Pulling latest code from GitHub ---"
git pull origin master

echo "--- 🛠️  Building and Re-starting Dashboard + Ollama ---"
# This brings up everything in the docker-compose.yml
docker compose up --build -d --remove-orphans

if [ $? -eq 0 ]; then
    echo "--- ✅ Stack is Primed ---"
    echo "--- 📊 Dashboard: http://192.168.1.11:8050 ---"
    echo "--- 🧠 Ollama API: http://192.168.1.11:11434 ---"
    
    # Check if the models are loaded
    echo "--- 📦 Currently Loaded Models: ---"
    docker exec ollama_jetson ollama ps
else
    echo "--- ❌ ERROR: Deployment failed. ---"
fi