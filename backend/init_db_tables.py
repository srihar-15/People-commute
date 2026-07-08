import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.database import engine, Base
from sqlalchemy import text
# Import models to ensure they register on Base
from app.models import *

def main():
    print("Initializing database...")
    try:
        # Create extensions
        with engine.connect() as conn:
            print("Creating extension uuid-ossp...")
            try:
                conn.execute(text('CREATE EXTENSION IF NOT EXISTS "uuid-ossp";'))
                conn.commit()
                print("Extension uuid-ossp created successfully.")
            except Exception as e:
                print(f"Skipping uuid-ossp creation: {e}")
            
        print("Creating all tables from SQLAlchemy models...")
        Base.metadata.create_all(bind=engine)
        print("Database tables initialized successfully!")
    except Exception as e:
        print(f"Error initializing database: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
