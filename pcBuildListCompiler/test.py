import sqlite3
conn = sqlite3.connect("computerParts.db")
c = conn.cursor()

def droptable():
    conn = sqlite3.connect("computerParts.db")
    c = conn.cursor()
    c.execute(""" DROP TABLE cpu""")
    print("done")
droptable()