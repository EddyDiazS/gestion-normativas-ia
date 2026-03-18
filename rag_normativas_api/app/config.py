import os
from dotenv import load_dotenv

APP_ENV = os.getenv("APP_ENV", "local")
 
if APP_ENV == "production":
    load_dotenv(".env.prod", override=True)
else:
    load_dotenv(".env.local", override=True)
 
# Variables
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
DATA_PATH      = os.getenv("DATA_PATH", "data/normativas")
 
DB_USER            = os.getenv("DB_USER")
DB_PASSWORD        = os.getenv("DB_PASSWORD")
DB_HOST            = os.getenv("DB_HOST")
DB_PORT            = os.getenv("DB_PORT")
DB_SERVICE         = os.getenv("DB_SERVICE")
ORACLE_CLIENT_PATH = os.getenv("ORACLE_CLIENT_PATH")
 
if not GOOGLE_API_KEY:
    raise RuntimeError("❌ GOOGLE_API_KEY no configurada")