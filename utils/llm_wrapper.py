"""
LLM Wrapper - Uses Ollama for free local inference
"""
import json
import requests
import os
from dotenv import load_dotenv

load_dotenv()


class LocalLLM:
    """Wrapper for local Ollama LLM"""
    
    def __init__(self, model=None, temperature=0.3):
        self.model = model or os.getenv('OLLAMA_MODEL', 'llama3.2:3b')
        self.base_url = os.getenv('OLLAMA_BASE_URL', 'http://localhost:11434')
        self.temperature = temperature
        
    def invoke(self, prompt):
        """Send prompt to Ollama and get response"""
        url = f"{self.base_url}/api/generate"
        
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "temperature": self.temperature,
            "options": {
                "num_predict": 2048
            }
        }
        
        try:
            response = requests.post(url, json=payload, timeout=120)
            response.raise_for_status()
            result = response.json()
            
            # Create a response object similar to Anthropic
            class Response:
                def __init__(self, content):
                    self.content = content
            
            return Response(result['response'])
            
        except requests.exceptions.RequestException as e:
            print(f"⚠️  Ollama request failed: {e}")
            print("Make sure Ollama is running: ollama serve")
            raise