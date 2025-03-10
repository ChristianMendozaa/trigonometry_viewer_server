from dotenv import load_dotenv
import os

load_dotenv()

class Settings:
    FIREBASE_CREDENTIALS: str = os.getenv("FIREBASE_CREDENTIALS")

settings = Settings()
