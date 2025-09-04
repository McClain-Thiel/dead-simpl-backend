import firebase_admin
from firebase_admin import credentials
import os

FIREBASE_PROJECT_ID = os.environ.get("FIREBASE_PROJECT_ID", "your-project-id")
FIREBASE_SERVICE_ACCOUNT_KEY = os.environ.get("FIREBASE_SERVICE_ACCOUNT_KEY")

if FIREBASE_SERVICE_ACCOUNT_KEY:
    cred = credentials.Certificate(FIREBASE_SERVICE_ACCOUNT_KEY)
    firebase_admin.initialize_app(cred, {
        'projectId': FIREBASE_PROJECT_ID,
    })
