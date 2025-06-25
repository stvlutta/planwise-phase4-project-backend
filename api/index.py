import sys
import os

# Add the server directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'server'))

from app import app

# Export the app for Vercel
application = app

if __name__ == "__main__":
    app.run(debug=True)