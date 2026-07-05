'''
Script to set is_verified=True for all users.
Run with: python backend/backend/scripts/verify_all_users.py
'''

import os, sys
# Add the backend package directory to sys.path so that 'app' can be imported
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(BASE_DIR)

from sqlalchemy import update
from app.db.session import SessionLocal
from app.models.user import User

def main():
    db = SessionLocal()
    try:
        db.execute(update(User).values(is_verified=True))
        db.commit()
        print('All users marked as verified.')
    finally:
        db.close()

if __name__ == "__main__":
    main()
