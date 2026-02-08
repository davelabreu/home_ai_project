#!/bin/bash
cd ~/projects/dev/2.personal/home_ai_project

echo "--- 🛡️  FORCE CLEARING Port 11434 ---"
# This kills ANY process currently using the port, whether it's a service or a stray PID
sudo fuser -k 11434/tcp > /dev/null 2>&1

echo "--- 🧹 Clearing System Caches & Defragmenting Memory ---"
# This tells the kernel to release as much buff/cache as possible
sudo sync && echo 3 | sudo tee /proc/sys/vm/drop_caches > /dev/null

echo "--- 🔄 Restarting Docker Daemon (to reset CUDA hooks) ---"
sudo systemctl restart docker

echo "--- 🚀 Pulling latest code from GitHub ---"
git pull origin master

echo "--- 🛡️  Ensuring Port 11434 is free (Killing native Ollama) ---"
# This is the 'Self-Healing' part: stop the native service if it's squatting on the port
sudo systemctl stop ollama > /dev/null 2>&1

echo "--- 🛠️  Rebuilding & Restarting Stack ---"
docker compose build --no-cache
docker compose up -d --remove-orphans

if [ $? -eq 0 ]; then
    echo "--- ⏳ Waiting for Ollama container to initialize... ---"
    sleep 8 # Increased sleep to ensure the server is ready
    
    echo "--- 🧠 Priming qwen:1.8b model into VRAM ---"
    # Remove the -d and actually wait for a response to ensure VRAM allocation
    docker exec ollama_jetson ollama run qwen:1.8b "Generate a one-sentence greeting." > /dev/null
    
    echo "--- ✅ Stack is Primed & Healing Enabled ---"
    echo "--- 📊 Dashboard: http://192.168.1.11:8050 ---"
    
    echo "--- 📦 Currently Loaded Models (Inside Docker): ---"
    docker exec ollama_jetson ollama ps
else
    echo "--- ❌ ERROR: Deployment failed. ---"
fi

# Monitoring Option
echo ""
read -p "View Dashboard and Ollama container logs? (y/N): " -n 1 -r
echo    # (optional) move to a new line
if [[ $REPLY =~ ^[Yy]$ ]]
then
    echo "--- 📝 Viewing Dashboard Logs (Ctrl+C to exit) ---"
    docker logs -f home_ai_dashboard &
    DASHBOARD_PID=$!
    echo "--- 📝 Viewing Ollama Logs (Ctrl+C to exit dashboard logs to see these) ---"
    docker logs -f ollama_jetson &
    OLLAMA_PID=$!
    wait $DASHBOARD_PID $OLLAMA_PID # Wait for both to be killed by Ctrl+C
fi