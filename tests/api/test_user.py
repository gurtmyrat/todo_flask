import psycopg2
import os

try:
    conn = psycopg2.connect(os.getenv("DATABASE_URL"))
    print("Database connected successfully!")
    conn.close()
except Exception as e:
    print(f"Failed to connect to database: {e}")
