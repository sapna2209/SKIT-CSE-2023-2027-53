import sqlite3
import csv
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "potholes.db")


def export_table_to_csv(cursor, table_name, output_file):
    cursor.execute(f"SELECT * FROM {table_name}")

    columns = [description[0] for description in cursor.description]
    rows = cursor.fetchall()

    with open(output_file, "w", newline="", encoding="utf-8-sig") as file:
        writer = csv.writer(file)
        writer.writerow(columns)
        writer.writerows(rows)

    print(f"{table_name} exported successfully!")
    print(f"Records: {len(rows)}")
    print(f"File: {output_file}\n")


def main():
    if not os.path.exists(DB_PATH):
        print("Database not found:", DB_PATH)
        return

    connection = sqlite3.connect(DB_PATH)
    cursor = connection.cursor()

    try:
        cursor.execute("""
            SELECT name
            FROM sqlite_master
            WHERE type = 'table'
              AND name NOT LIKE 'sqlite_%'
        """)

        tables = [row[0] for row in cursor.fetchall()]

        if not tables:
            print("No tables found in the database.")
            return

        print("Tables found:", tables, "\n")

        for table_name in tables:
            output_file = os.path.join(
                BASE_DIR,
                f"{table_name}_readable.csv"
            )

            export_table_to_csv(
                cursor,
                table_name,
                output_file
            )

    finally:
        connection.close()


if __name__ == "__main__":
    main()
