import os

os.environ['LANGCHAIN_ENDPOINT'] = "https://api.smith.langchain.com"
os.environ['LANGCHAIN_PROJECT'] = "k8s-agent"

DEBUG = bool(os.environ.get('DEBUG', True))
LOG_LEVEL = os.environ.get('LOG_LEVEL', DEBUG and 'DEBUG' or 'WARNING')
PORT = int(os.environ.get('PORT', 8000))
OPENAI_MODEL = os.environ.get('OPENAI_MODEL', 'gpt-4-0125-preview')
OPENAI_MODEL_TEMP = float(os.environ.get('OPENAI_MODEL_TEMP', 0))
OLLAMA_BASE_URL = os.environ.get('OLLAMA_BASE_URL', 'http://localhost:11434')
OLLAMA_MODEL = os.environ.get('OLLAMA_MODEL', 'http://localhost:11434')
REDIS_URL = os.environ.get('REDIS_URL', 'redis://localhost:6379/0')
