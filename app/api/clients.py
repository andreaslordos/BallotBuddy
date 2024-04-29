from playhouse.sqlite_ext import PostgresqlDatabase
from twilio.rest import Client
from dotenv import load_dotenv
import openai
import os

'''
import logging

logger = logging.getLogger('peewee')
logger.addHandler(logging.StreamHandler())
logger.setLevel(logging.DEBUG)
'''
# prepares db, twilio client and openai client for export

# Get the absolute path of the current script
script_dir = os.path.dirname(os.path.abspath(__file__))

# Get the absolute path of the project root directory
project_root = os.path.dirname(os.path.dirname(script_dir))

# Define the absolute path of the .env file
ENV_PATH = os.path.join(project_root, ".env")

if not load_dotenv(ENV_PATH):
    raise FileNotFoundError("Failed to load .env file")

DB_NAME = os.getenv("DB_NAME")
DB_USERNAME = os.getenv("DB_USERNAME")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_URL = os.getenv("DB_URL")
DB_PORT = int(os.getenv("DB_PORT"))

db = PostgresqlDatabase(DB_NAME, user=DB_USERNAME, password=DB_PASSWORD, host=DB_URL, port=DB_PORT)

accountSID = os.getenv("TWILIO_ACCOUNT_SID")
authToken = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_PHONE = os.getenv("TWILIO_PHONE_NUMBER")

# twilio_client = Client(accountSID, authToken)

APIkey = os.getenv("OPENAI_API_KEY_BALLOTBUDDY")
org = os.getenv("OPENAI_ORGANIZATION_ID")
ASSISTANT_ID = os.getenv("ASST_ID")

openai.log = "debug"

openai_client = openai.OpenAI(organization=org, api_key=APIkey)

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")