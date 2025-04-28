import os
from pathlib import Path

from dotenv import load_dotenv

DB_PASS = os.getenv('DB_PASSWORD')
DB_NAME = os.getenv('DB_NAME')
DB_USER = os.getenv('DB_USER')
DB_HOST = os.getenv('DB_HOST')
BOT_TOKEN = os.getenv('BOT_TOKEN')
PORT = os.getenv('DB_PORT')

WORKDIR = Path(__file__).parent.parent