import sqlite3
conn = sqlite3.connect("computerParts.db")
c = conn.cursor()

def droptable():
    conn = sqlite3.connect("computerParts.db")
    c = conn.cursor()
    tables = ['cases']

    for table in tables:
        c.execute(f"DROP TABLE IF EXISTS {table}")
    conn.commit()
    print("Done")
    conn.close()
droptable()
