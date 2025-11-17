import sqlite3

manufacturers = [
    "Intel", "AMD", "NVIDIA", "ASUS", "MSI", "Gigabyte", "ASRock", "Biostar", "EVGA",
    "Corsair", "G.Skill", "Kingston", "Crucial", "TeamGroup", "Patriot", "ADATA",
    "Samsung", "Western Digital", "Seagate", "SK Hynix", "Toshiba",
    "Cooler Master", "Thermaltake", "be quiet!", "SilverStone", "NZXT", "Fractal Design",
    "Lian Li", "Phanteks", "Antec"
]

class Database:
    def __init__(self, dbName):
        # single connection, used everywhere
        self.conn = sqlite3.connect(dbName)
        self.cursor = self.conn.cursor()

    def createDatabaseTables(self):
        try:
            # Manufacturer table
            self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS manufacturer (
                manufacturerId INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL
            )
            ''')

            # CPU table
            self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS cpu (
                partNumber TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                price REAL,
                manufacturerId INTEGER,
                url TEXT,
                score REAL,
                coreCount INTEGER,
                coreClock REAL,
                boostClock REAL,
                cache INTEGER,
                threads INTEGER,
                tdpWatts INTEGER,
                socketId TEXT,
                FOREIGN KEY (manufacturerId) REFERENCES manufacturer(manufacturerId)
            )
            ''')

            # Motherboard table
            self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS motherboard (
                partNumber TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                price REAL,
                manufacturerId INTEGER,
                url TEXT,
                socketId TEXT,
                formFactor TEXT,
                chipset TEXT,
                tdpWatts INTEGER,
                memorySlots INTEGER,
                memoryType TEXT,
                maxMemoryGb INTEGER,
                pcieSlots INTEGER,
                m2Slots INTEGER,    
                sataPorts INTEGER,
                FOREIGN KEY (manufacturerId) REFERENCES manufacturer(manufacturerId)
            )
            ''')

            # RAM table
            self.cursor.execute('''
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
                voltage REAL,
                eccSupport BOOLEAN,
                FOREIGN KEY (manufacturerId) REFERENCES manufacturer(manufacturerId)
            )
            ''')

            # Storage table
            self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS storage (
                partNumber TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                price REAL,
                manufacturerId INTEGER,
                url TEXT,
                score REAL,
                capacityGb INTEGER,
                readSpeed REAL,
                writeSpeed REAL,
                interface TEXT,
                formFactor TEXT,
                cacheMb INTEGER,
                FOREIGN KEY (manufacturerId) REFERENCES manufacturer(manufacturerId)
            )
            ''')

            # GPU table
            self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS gpu (
                partNumber TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                price REAL,
                manufacturerId INTEGER,
                url TEXT,
                score REAL,
                memoryGb INTEGER,
                coreClock REAL,
                memoryType TEXT,
                tdpWatts INTEGER,
                lengthMm INTEGER,
                FOREIGN KEY (manufacturerId) REFERENCES manufacturer(manufacturerId)
            )
            ''')

            # PSU table
            self.cursor.execute('''
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
                modular BOOLEAN,
                noiseLevelDb REAL,
                connectorCount INTEGER,
                FOREIGN KEY (manufacturerId) REFERENCES manufacturer(manufacturerId)
            )
            ''')

            # Case table
            self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS pcCase (
                partNumber TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                price REAL,
                manufacturerId INTEGER,
                url TEXT,
                formFactorSupport TEXT,
                gpuMaxLength INTEGER,
                radiatorSupport TEXT,
                psuFormFactorSupport TEXT,
                FOREIGN KEY (manufacturerId) REFERENCES manufacturer(manufacturerId)
            )
            ''')

            self.conn.commit()
            print("Database tables created successfully.")

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




