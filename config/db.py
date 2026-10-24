"""
MongoDB connection utility using PyMongo.
Provides a singleton database connection.
"""
import os
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

_client = None
_db = None


def get_db():
    """Return the MongoDB database instance (singleton)."""
    global _client, _db
    if _db is None:
        uri = os.getenv('MONGODB_URI', 'mongodb://localhost:27017/jobtrack')
        name = os.getenv('MONGODB_NAME', 'jobtrack')
        _client = MongoClient(uri, serverSelectionTimeoutMS=5000)
        _db = _client[name]
        # Ensure indexes
        _ensure_indexes(_db)
    return _db


def _ensure_indexes(db):
    """Create required indexes for performance."""
    db.users.create_index('email', unique=True)
    db.jobs.create_index([('title', 'text'), ('description', 'text')])
    db.jobs.create_index('status')
    db.jobs.create_index('company_id')
    db.applications.create_index('user_id')
    db.applications.create_index([('user_id', 1), ('job_id', 1)], unique=True)
    db.interviews.create_index('user_id')
    db.interviews.create_index('date')
    db.notifications.create_index([('user_id', 1), ('is_read', 1)])
    db.saved_jobs.create_index([('user_id', 1), ('job_id', 1)], unique=True)
    db.companies.create_index('name')


def close_db():
    """Close the MongoDB connection."""
    global _client, _db
    if _client:
        _client.close()
        _client = None
        _db = None
