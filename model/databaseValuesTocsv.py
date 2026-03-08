import psycopg2
import sys

"""
This script connects to the PostgreSQL database, 
retrieves all records from the "ActualValues" table,
and writes them to a CSV file named "batch_values_input.csv". 
The CSV file will contain three columns: sensor_timestamp, sensor_id, and sensor_energy_value.
"""


def connect_to_database():

    try:
        conn = psycopg2.connect(
            "dbname= 'postgres' user='postgres' password='postgres' port=5432 "
        )
        if conn:
            print("Database connection establiished")
            return conn
    except psycopg2.OperationalError as e:
        print("Unable to connect to database:\n")
        print(e)
        sys.exit(1)


if __name__ == "__main__":
    conn = connect_to_database()
    cur = conn.cursor()
    cur.execute("SELECT * FROM ActualValues")
    rows = cur.fetchall()

    with open("batch_values_input.csv", "w") as f:
        f.write("sensor_timestamp,sensor_id,sensor_energy_value\n")
        for row in rows:
            f.write(f"{row[1]},{row[2]},{row[3]}\n")

    cur.close()
    conn.close()
    sys.exit(0)
