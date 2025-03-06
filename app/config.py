import logging
import os

MEALIE_API_KEY = os.environ.get("MEALIE_API_KEY")
GROCY_API_KEY = os.environ.get("GROCY_API_KEY")

MEALIE_ENDPOINT = os.environ.get("MEALIE_BASE_URL")
GROCY_ENDPOINT = os.environ.get("GROCY_BASE_URL")

API_PORT = 9193
API_KEYS = os.environ.get("API_KEYS", "").split("\n")
LOG_LEVEL = logging.INFO
