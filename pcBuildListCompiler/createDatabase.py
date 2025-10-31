import sqlite3

class Database:
    def __init__(self, dbName):
        self.conn = sqlite3.connect(dbName)
        self.cursor = self.conn.cursor()

    def createDatabaseTables(self):
        try:
            self.name = pcParts
            conn = sqlite3.connect("scrapingTools/pcParts.db")
            cursor = conn.cursor()

            cursor.execute('''
            CREATE TABLE IF NOT EXISTS manufacturer (
                manufacturerId INTEGER PRIMARY KEY,
                name TEXT UNIQUE NOT NULL
            )
            ''')

            # Component Tables
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS cpu (
                partNumber TEXT PRIMARY KEY,
                name TEXT,
                price REAL,
                manufacturerId INTEGER,
                url TEXT,
                score REAL,
                coreCount INTEGER,
                coreClock REAL,
                tdp INTEGER,
                socket TEXT,
                manufacturerId INTEGER,
                FOREIGN KEY (manufacturerId) REFERENCES manufacturer(manufacturerId)
            )
            ''')

            cursor.execute('''
            CREATE TABLE IF NOT EXISTS motherboard (
                partNumber TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                price REAL,
                manufacturerId INTEGER,
                url TEXT,
                socket TEXT,
                formFactor TEXT,
                tdp INTEGER,
                memorySlots INTEGER,
                memoryType TEXT,
                FOREIGN KEY (manufacturerId) REFERENCES manufacturer(manufacturerId)
            )
            ''')

            cursor.execute('''
            CREATE TABLE IF NOT EXISTS ram (
                partNumber TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                price REAL,
                manufacturerId INTEGER,
                url TEXT,
                score REAL,
                capacityGb INTEGER,
                numberOfModules INTEGER,
                speedMhz INTEGER,
                ddrType TEXT,
                FOREIGN KEY (manufacturerId) REFERENCES manufacturer(manufacturerId)
            )
            ''')

            cursor.execute('''
            CREATE TABLE IF NOT EXISTS storage (
                partNumber TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                price REAL,
                manufacturerId INTEGER,
                url TEXT,
                score REAL,
                capacityGb INTEGER,
                readSpeed INTEGER,
                writeSpeed INTEGER,
                FOREIGN KEY (manufacturerId) REFERENCES manufacturer(manufacturerId)
            )
            ''')

            cursor.execute('''
            CREATE TABLE IF NOT EXISTS gpu (
                partNumber TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                price REAL,
                manufacturerId INTEGER,
                url TEXT,
                score REAL,
                memoryGb INTEGER,
                coreClock INTEGER,
                memoryType TEXT,
                tdp INTEGER,
                length INTEGER,
                FOREIGN KEY (manufacturerId) REFERENCES manufacturer(manufacturerId)
            )
            ''')

            cursor.execute('''
            CREATE TABLE IF NOT EXISTS psu (
                partNumber TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                price REAL,
                manufacturerId INTEGER,
                url TEXT,
                score REAL,
                wattage INTEGER,
                efficiencyRating TEXT,
                formFactor TEXT,
                FOREIGN KEY (manufacturerId) REFERENCES manufacturer(manufacturerId)
            )
            ''')

            cursor.execute('''
            CREATE TABLE IF NOT EXISTS pcCase (
                partNumber TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                price REAL,
                manufacturerId INTEGER,
                url TEXT,
                formFactorSupport TEXT,
                gpuMaxLength INTEGER,
                FOREIGN KEY (manufacturerId) REFERENCES manufacturer(manufacturerId)
            )
            ''')

            conn.commit()
            conn.close()
            print("Database tables created successfully.")

        except sqlite3.Error as e:
            print(f"Database error: {e}")

    def getManufacturerMap(self):
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

pcParts = Database()