# config.py
import os

# Railway automatically sets PORT - we only use 8000 for local development
PORT = int(os.getenv("PORT", 8000))

# Get database URL from Railway
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    # Only used for local development
    DATABASE_URL = "postgresql://postgres:postgres@localhost/claims_management"