#!/bin/bash
# Automatically find the directory where the script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR" || exit

# --- Helper Functions ---
clear_memory() {
    echo "--- 🧹 Clearing System Caches & Defragmenting Memory ---"
    sudo sync && echo 3 | sudo tee /proc/sys/vm/drop_caches > /dev/null
    sudo systemctl restart docker
}

clear_ollama_port() {
    echo "--- 🛡️  FORCE CLEARING Port 11434 ---"
    sudo fuser -k 11434/tcp > /dev/null 2>&1
    sudo systemctl stop ollama > /dev/null 2>&1
}

prime_model() {
    echo "--- ⏳ Waiting for Ollama... ---"
    sleep 8
    echo "--- 🧠 Priming qwen:1.8b model into VRAM ---"
    docker exec ollama_jetson ollama run qwen:1.8b "hi" > /dev/null
    docker exec ollama_jetson ollama ps
}

# --- Menu Logic ---
PS3='Choose a deployment action: '
options=("Full System Reset (The Works)" "Update Dashboard Only" "Restart/Prime Ollama Only" "Quit")

select opt in "${options[@]}"
do
    case $opt in
        "Full System Reset (The Works)")
            clear_ollama_port
            clear_memory
            git pull origin master
            docker compose up --build -d --remove-orphans
            prime_model
            break
            ;;
        "Update Dashboard Only")
            git pull origin master
            docker compose up -d --build dashboard
            echo "--- ✅ Dashboard Updated ---"
            break
            ;;
        "Restart/Prime Ollama Only")
            clear_ollama_port
            docker compose restart ollama
            prime_model
            break
            ;;
        "Quit")
            exit
            ;;
        *) echo "invalid option $REPLY";;
    esac
done

# --- Unified Logging ---
echo ""
read -p "View logs? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    docker compose logs -f
fi