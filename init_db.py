import sqlite3

DATABASE_NAME = "school_system.db"

def initialize_database():
    with open("schema.sql", "r") as f:
        schema = f.read()

    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    
    cursor.executescript(schema)  # Execute the entire SQL script
    conn.commit()
    conn.close()
    print("Database initialized successfully!")

if __name__ == "__main__":
    initialize_database()
