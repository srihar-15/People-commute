import psycopg2

def main():
    try:
        print("Connecting to default postgres database...")
        conn = psycopg2.connect(
            host="localhost",
            port=5432,
            user="postgres",
            password="postgres",  # wait! we should check if MSJB1852 is the password
            database="postgres"
        )
    except Exception:
        try:
            conn = psycopg2.connect(
                host="localhost",
                port=5432,
                user="postgres",
                password="MSJB1852",
                database="postgres"
            )
        except Exception as e:
            print(f"Failed to connect to default database: {e}")
            return
            
    conn.autocommit = True
    cur = conn.cursor()
    try:
        cur.execute("SELECT 1 FROM pg_database WHERE datname='sahayak'")
        exists = cur.fetchone()
        if not exists:
            print("Creating database 'sahayak'...")
            cur.execute("CREATE DATABASE sahayak")
            print("Database 'sahayak' created successfully!")
        else:
            print("Database 'sahayak' already exists.")
    except Exception as e:
        print(f"Error checking or creating database: {e}")
    finally:
        cur.close()
        conn.close()

if __name__ == "__main__":
    main()
