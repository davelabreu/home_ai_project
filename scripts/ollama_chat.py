import requests
import json
import sys
import os

# Check if OLLAMA_HOST is set, otherwise default to localhost
ollama_host = os.environ.get("OLLAMA_HOST", "http://localhost:11434")

if len(sys.argv) < 2:
    print("Usage: python ollama_chat.py \"Your prompt here\"") # Corrected line
    sys.exit(1)

prompt = sys.argv[1]

url = f"{ollama_host}/api/generate"
headers = {"Content-Type": "application/json"}
data = {
    "model": "qwen:1.8b",  # Ensure this matches your model tag
    "prompt": prompt,
    "stream": False,
}

try:
    response = requests.post(url, headers=headers, data=json.dumps(data))
    response.raise_for_status()
    
    result = response.json()
    if "response" in result:
        print(result["response"])
    elif "error" in result:
        print(f"Error from Ollama: {result['error']}")
    else:
        print("Unexpected response format.")

except requests.exceptions.ConnectionError:
    print("Connection Error: Is Ollama running? Check `ollama ps` and `ollama serve`.")
except requests.exceptions.RequestException as e:
    print(f"Request failed: {e}")