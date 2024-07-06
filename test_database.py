import sqlalchemy
from dotenv import load_dotenv
import os

def test_database_connection():
    load_dotenv() # Load environment variables from the .env file

    DATABASE_URI = os.getenv('TEST_DATABASE_URI')

    try:
        engine = sqlalchemy.create_engine(DATABASE_URI)
        connection = engine.connect()
        print("Successfully connected to the database.")
        connection.close()
    except Exception as e:
        print(f"Failed to connect to the database: {e}")

test_database_connection()