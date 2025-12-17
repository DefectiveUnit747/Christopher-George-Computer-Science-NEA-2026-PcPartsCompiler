CREATE TABLE IF NOT EXISTS manufacturer (
    manufacturerId INTEGER PRIMARY KEY AUTOINCREMENT,
    name           TEXT UNIQUE NOT NULL
);

CREATE TABLE IF NOT EXISTS cpu (
    partNumber TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    price REAL,
    manufacturerId INTEGER,
    url TEXT,
    score REAL,
    scoreEfficiency REAL,
    scoreUpgradeability REAL,
    coreCount INTEGER,
    coreClock REAL,
    cache INTEGER,
    threads INTEGER,
    tdpWatts INTEGER,
    socketId TEXT,
    imagePath TEXT,
    FOREIGN KEY (manufacturerId) REFERENCES manufacturer(manufacturerId)
);

CREATE TABLE IF NOT EXISTS motherboard (
    partNumber TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    price REAL,
    manufacturerId INTEGER,
    url TEXT,
    score REAL,
    scoreEfficiency REAL,
    scoreUpgradeability REAL,
    socketId TEXT,
    formFactor TEXT,
    tdpWatts INTEGER,
    memorySlots INTEGER,
    memoryType TEXT,
    maxMemory INTEGER,
    imagePath TEXT,
    FOREIGN KEY (manufacturerId) REFERENCES manufacturer(manufacturerId)
);


CREATE TABLE IF NOT EXISTS ram (
    partNumber TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    price REAL,
    manufacturerId INTEGER,
    url TEXT,
    score REAL,
    scoreEfficiency REAL,
    scoreUpgradeability REAL,
    capacityGb INTEGER,
    numberOfModules INTEGER,
    speedMhz INTEGER,
    ddrType TEXT,
    imagePath TEXT,
    FOREIGN KEY (manufacturerId) REFERENCES manufacturer(manufacturerId)
);

CREATE TABLE IF NOT EXISTS storage (
    partNumber TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    price REAL,
    manufacturerId INTEGER,
    url TEXT,
    score REAL,
    scoreEfficiency REAL,
    scoreUpgradeability REAL,
    capacityGb INTEGER,
    readSpeed REAL,
    writeSpeed REAL,
    formFactor TEXT,
    imagePath TEXT,
    FOREIGN KEY (manufacturerId) REFERENCES manufacturer(manufacturerId)
);

CREATE TABLE IF NOT EXISTS gpu (
    partNumber TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    price REAL,
    manufacturerId INTEGER,
    url TEXT,
    score REAL,
    scoreEfficiency REAL,
    scoreUpgradeability REAL,
    memoryGb INTEGER,
    coreClock REAL,
    memoryType TEXT,
    tdpWatts INTEGER,
    lengthMm INTEGER,
    imagePath TEXT,
    FOREIGN KEY (manufacturerId) REFERENCES manufacturer(manufacturerId)
);

CREATE TABLE IF NOT EXISTS psu (
    partNumber TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    price REAL,
    manufacturerId INTEGER,
    url TEXT,
    score REAL,
    scoreEfficiency REAL,
    scoreUpgradeability REAL,
    wattage INTEGER,
    efficiencyRating TEXT,
    formFactor TEXT,
    modular BOOLEAN,
    imagePath TEXT,
    FOREIGN KEY (manufacturerId) REFERENCES manufacturer(manufacturerId)
);

CREATE TABLE IF NOT EXISTS cases (
    partNumber TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    price REAL,
    manufacturerId INTEGER,
    url TEXT,
    score REAL,
    scoreEfficiency REAL,
    scoreUpgradeability REAL,
    formFactorSupport TEXT,
    gpuMaxLength INTEGER,
    imagePath TEXT,
    FOREIGN KEY (manufacturerId) REFERENCES manufacturer(manufacturerId)
)





