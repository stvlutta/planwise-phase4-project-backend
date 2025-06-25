#!/usr/bin/env python3
"""
Database initialization script for production deployment.
This script sets up the database tables without starting the Flask development server.
"""

import os
from app import app, db

def init_database():
    """Initialize the database tables."""
    with app.app_context():
        try:
            # Create all database tables
            db.create_all()
            print("✅ Database tables created successfully")
            return True
        except Exception as e:
            print(f"❌ Database initialization error: {e}")
            return False

if __name__ == '__main__':
    success = init_database()
    if success:
        print("🚀 Database initialization complete - ready for production server")
    else:
        print("💥 Database initialization failed")
        exit(1)