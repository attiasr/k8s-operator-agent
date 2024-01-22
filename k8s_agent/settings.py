import os

DEBUG = bool(os.environ.get('DEBUG', True))
LOG_LEVEL = os.environ.get('LOG_LEVEL', DEBUG and 'DEBUG' or 'WARNING')
PORT = int(os.environ.get('PORT', 8000))
