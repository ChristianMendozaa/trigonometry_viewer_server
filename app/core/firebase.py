# app/core/firebase.py
import firebase_admin
from firebase_admin import credentials, auth, firestore
from .config import settings

def initialize_firebase():
    if not firebase_admin._apps:
        cred = credentials.Certificate(settings.FIREBASE_CREDENTIALS)
        firebase_admin.initialize_app(cred)

initialize_firebase()

firebase_auth = auth
db = firestore.client() 
