import sqlite3

conn = sqlite3.connect("listOfComputers.db")
cursor = conn.cursor()

def createDatabaseTables():

    #dependancy tables
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS manufacturer (
        manufacturerId INTEGER PRIMARY KEY,
        name TEXT UNIQUE
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS socket (
        socketId INTEGER PRIMARY KEY,
        name TEXT UNIQUE
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS memoryType (
        memoryTypeId INTEGER PRIMARY KEY,
        name TEXT UNIQUE
    )
    ''')

    # Component Tables
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS cpu (
        cpuId INTEGER PRIMARY KEY,
        name TEXT,
        manufacturerId INTEGER,
        socketId INTEGER,
        coreCount INTEGER,
        threadCount INTEGER,
        baseClock REAL,
        boostClock REAL,
        tdpWatts INTEGER,
        price REAL,
        normalisedScore REAL,
        FOREIGN KEY (manufacturerId) REFERENCES manufacturer(manufacturerId),
        FOREIGN KEY (socketId) REFERENCES socket(socketId)
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS motherboard (
        moboId INTEGER PRIMARY KEY,
        name TEXT,
        manufacturerId INTEGER,
        socketId INTEGER,
        formFactor TEXT,
        chipset TEXT,
        memorySlots INTEGER,
        memoryTypeId INTEGER,
        wirelessNetworking TEXT,
        price REAL,
        normalisedScore REAL,
        FOREIGN KEY (manufacturerId) REFERENCES manufacturer(manufacturerId),
        FOREIGN KEY (socketId) REFERENCES socket(socketId),
        FOREIGN KEY (memoryTypeId) REFERENCES memoryType(memoryTypeId)
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS ram (
        ramId INTEGER PRIMARY KEY,
        name TEXT,
        manufacturerId INTEGER,
        capacityGb INTEGER,
        modules INTEGER,
        speedMhz INTEGER,
        casLatency INTEGER,
        price REAL,
        normalisedScore REAL,
        FOREIGN KEY (manufacturerId) REFERENCES manufacturer(manufacturerId)
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS storage (
        storageId INTEGER PRIMARY KEY,
        manufacturerId INTEGER,
        capacityGb INTEGER,
        interface TEXT,
        price REAL,
        normalisedScore REAL,
        FOREIGN KEY (manufacturerId) REFERENCES manufacturer(manufacturerId)
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS gpu (
        gpuId INTEGER PRIMARY KEY,
        name TEXT,
        manufacturerId INTEGER,
        memoryGb INTEGER,
        coreClock INTEGER,
        tdpWatts INTEGER,
        lengthMm INTEGER,
        price REAL,
        normalisedScore REAL,
        FOREIGN KEY (manufacturerId) REFERENCES manufacturer(manufacturerId)
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS psu (
        psuId INTEGER PRIMARY KEY,
        manufacturerId INTEGER,
        model TEXT,
        wattage INTEGER,
        efficiencyRating TEXT,
        formFactor TEXT,
        price REAL,
        normalisedScore REAL,
        FOREIGN KEY (manufacturerId) REFERENCES manufacturer(manufacturerId)
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS pcCase (
        caseId INTEGER PRIMARY KEY,
        manufacturerId INTEGER,
        formFactorSupport TEXT,
        gpuMaxLengthMm INTEGER,
        price REAL,
        normalisedScore REAL,
        FOREIGN KEY (manufacturerId) REFERENCES manufacturer(manufacturerId)
    )
    ''')

    conn.commit()
    conn.close()


    conn.commit()
    conn.close() #Not gonna be using for a while
