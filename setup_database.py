import psycopg2
from streamlit import secrets
import os

def setup_database():
    # Read the SQL file
    with open('schema.sql', 'r') as file:
        sql_commands = file.read()

    # Connect to the database
    try:
        conn = psycopg2.connect(
            dbname=secrets.DB_NAME,
            user=secrets.DB_USER,
            password=secrets.DB_PASSWORD,
            host=secrets.DB_HOST,
            port=secrets.DB_PORT
        )
        
        # Create a cursor and execute the SQL commands
        with conn.cursor() as cur:
            cur.execute(sql_commands)
        
        # Commit the changes
        conn.commit()
        print("Database schema created successfully!")
        
    except Exception as e:
        print(f"An error occurred: {e}")
        
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    setup_database() 