import os
from dotenv import load_dotenv

load_dotenv()

BASE_URL = os.getenv("API_BASE_URL", "http://localhost:5010")
REST_URL = f"{BASE_URL}/api"
GRAPHQL_URL = f"{BASE_URL}/graphql"
