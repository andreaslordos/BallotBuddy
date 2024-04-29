import argparse
from app.api import db, User, Thread, createAssistant, openai_client, ENV_PATH
import dotenv

def clearDb():
    MODELS = [User, Thread]
    db.connect()
    print("Connected to db")
    db.drop_tables(MODELS)
    print("Dropped tables")
    db.create_tables(MODELS)
    print("Created tables")
    db.close()
    print("Built new database")

def generateNewAssistant():
    assistant = createAssistant(openai_client)
    ASSISTANT_ID = assistant.id
    print("Created assistant with ID",ASSISTANT_ID)
    # Write changes to .env file.
    dotenv.set_key(ENV_PATH, "ASST_ID", ASSISTANT_ID)
    print("Wrote new assistant to dotenv file")

parser = argparse.ArgumentParser(description="Set up or reset database and assistant.")

# Add the arguments
parser.add_argument("-db", action="store_true", help="Drop all tables in the database and start from scratch (WARNING: Do not perform on prod)")
parser.add_argument("-assistant", action="store_true", help="Generate a new assistant based on the instructions in agent/agent_instructions.py, print out assistant ID and store it in .env")
parser.add_argument("-all", action="store_true", help="Clears database and generates new assistant (WARNING: Do not perform on prod)")

# Parse the arguments
args = parser.parse_args()

# Perform actions based on the arguments
if args.db:
    clearDb()
elif args.assistant:
    generateNewAssistant()
elif args.all:
    generateNewAssistant()
    clearDb()
else:
    parser.print_help()