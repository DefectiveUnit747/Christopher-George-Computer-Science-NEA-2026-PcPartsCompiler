import sqlite3
import os

manufacturers = [
    "ADATA", "Aerocool", "AMD", "Antec", "ASRock", "ASUS", "be quiet!", "Biostar", "CaseLabs", "Colorful",
    "Cooler Master", "Corsair", "Cougar", "Crucial", "Deepcool", "ECS", "Enermax", "EVGA", "Foxconn", "Fractal Design",
    "Gainward", "GALAX", "Gigabyte", "G.Skill", "HIS", "Hitachi", "In Win", "Inno3D", "Intel", "Kingston",
    "Lian Li", "Matrox", "MSI", "Mushkin", "NVIDIA", "NZXT", "Palit", "Patriot", "Phanteks", "Plextor",
    "PNY", "PowerColor", "Rosewill", "Sapphire", "Samsung", "SanDisk", "Seagate", "Seasonic", "SilverStone", "SK Hynix",
    "Super Flower", "Supermicro", "TeamGroup", "Thermaltake", "Toshiba", "VisionTek", "Western Digital", "XFX", "Zotac"
                ]

class Database:
    def __init__(self, dbName):
        # single connection, used everywhere
        self.conn = sqlite3.connect(dbName)
        self.cursor = self.conn.cursor()

    def createDatabaseTables(self):
        try:
            with open("schema.sql", "r") as file:
                self.cursor.executescript(file.read())
                self.conn.commit()
                print("Database Tables Successfully Created")
        except sqlite3.Error as e:
            print(f"Database error: {e}")

    def addInManufacturers(self, manufacturers):
        conn = sqlite3.connect("computerParts.db")
        cursor = conn.cursor()

        for name in manufacturers:
            cursor.execute("INSERT OR IGNORE INTO manufacturer (name) VALUES (?)",
                           (name,))  # id is automatically assigned to be the same as rowid
        conn.commit()
        cursor.execute("SELECT * FROM manufacturer")
        conn.close()

    def getManufacturerMap(self):
        self.cursor.execute("SELECT manufacturerId, name FROM manufacturer")
        return {name.lower(): manufacturerId
                for manufacturerId, name in self.cursor.fetchall()
                if name is not None}

    def insertComponent(self, table, data):
        keys = ", ".join(data.keys())
        placeholders = ", ".join(["?"] * len(data))
        values = tuple(data.values())
        query = f"INSERT OR REPLACE INTO {table} ({keys}) VALUES ({placeholders})"
        self.cursor.execute(query, values)
        self.conn.commit()

    def close(self):
        self.conn.close()




