import sqlite3
conn = sqlite3.connect("computerParts.db")
c = conn.cursor()

def droptable(names):
    conn = sqlite3.connect("computerParts.db")
    c = conn.cursor()
    for n in names:
        c.execute(f""" DROP TABLE {n}""")
    print("done")
droptable(["cpu", "gpu", "ram", "motherboard", "storage", "psu", "cases"])
