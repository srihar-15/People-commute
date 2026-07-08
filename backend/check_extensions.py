import psycopg2

def check_port(port):
    print(f"\nChecking port {port}...")
    try:
        conn = psycopg2.connect(
            host="localhost",
            port=port,
            user="postgres",
            password="MSJB1852",
            database="postgres"
        )
        cur = conn.cursor()
        cur.execute("SELECT name, default_version, installed_version, comment FROM pg_available_extensions WHERE name IN ('vector', 'uuid-ossp')")
        rows = cur.fetchall()
        for row in rows:
            print(f"  Extension: {row[0]} | Default: {row[1]} | Installed: {row[2]} | Comment: {row[3]}")
        cur.close()
        conn.close()
    except Exception as e:
        print(f"  Error on port {port}: {e}")

check_port(5432)
check_port(5434)
