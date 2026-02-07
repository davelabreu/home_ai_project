import requests
import json
import sys
import os
import argparse # Import argparse

# Check if OLLAMA_HOST is set, otherwise default to localhost
ollama_host = os.environ.get("OLLAMA_HOST", "http://localhost:11434")

# Setup argument parser
parser = argparse.ArgumentParser(description="Chat with Ollama model.")
parser.add_argument("prompt", help="Your prompt here")
parser.add_argument("-m", "--model", default="qwen:1.8b",
                    help="The Ollama model to use (e.g., 'llama2', 'mistral'). Default is 'qwen:1.8b'.")
args = parser.parse_args()

prompt = args.prompt
model_name = args.model

url = f"{ollama_host}/api/generate"
headers = {"Content-Type": "application/json"}
data = {
    "model": model_name,
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