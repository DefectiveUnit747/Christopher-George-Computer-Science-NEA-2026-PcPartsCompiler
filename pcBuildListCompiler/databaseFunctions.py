import sqlite3

manufacturers = [
    "Intel", "AMD", "NVIDIA", "ASUS", "MSI", "Gigabyte", "ASRock", "Biostar", "EVGA",
    "Corsair", "G.Skill", "Kingston", "Crucial", "TeamGroup", "Patriot", "ADATA",
    "Samsung", "Western Digital", "Seagate", "SK Hynix", "Toshiba",
    "Cooler Master", "Thermaltake", "be quiet!", "SilverStone", "NZXT", "Fractal Design",
    "Lian Li", "Phanteks", "Antec"
]

component_schemas = {
    "cpu": {
        "columns": [
            "name", "price", "coreCount", "coreClock", "boostClock", "microarchitecture", "tdpWatts", "year", "manufacturerId", "socketId"
        ],
        "types": {
            "coreCount": int,
            "coreClock": float,
            "boostClock": float,
            "tdpWatts": int,
            "year": int,
            "score": float
        }
    },
    "gpu": {
        "columns": [
            "partNumber", "name", "manufacturerId", "memoryGb", "coreClock",
            "boostClock", "lengthMm", "tdpWatts", "year", "price", "score"
        ],
        "types": {
            "memoryGb": int,
            "coreClock": int,
            "boostClock": int,
            "lengthMm": int,
            "tdpWatts": int,
            "year": int,
            "price": float,
            "score": float
        }
    },
    "motherboard": {
        "columns": [
            "partNumber", "name", "manufacturerId", "socketId", "formFactorId",
            "maxMemoryGb", "memorySlots", "price"
        ],
        "types": {
            "maxMemoryGb": int,
            "memorySlots": int,
            "price": float
        }
    },
    "memory": {
        "columns": [
            "partNumber", "name", "manufacturerId", "speedMhz", "modules",
            "pricePerGb", "casLatency", "price"
        ],
        "types": {
            "speedMhz": int,
            "modules": int,
            "pricePerGb": float,
            "casLatency": int,
            "price": float
        }
    },
    "pccase": {
        "columns": [
            "partNumber", "name", "manufacturerId", "formFactorId", "color",
            "psuIncluded", "price"
        ],
        "types": {
            "price": float
        }
    },
    "powerSupply": {
        "columns": [
            "partNumber", "name", "manufacturerId", "type", "efficiencyId",
            "wattage", "modular", "price"
        ],
        "types": {
            "wattage": int,
            "price": float
        }
    },
    "storage": {
        "columns": [
            "partNumber", "name", "manufacturerId", "capacityGb", "pricePerGb",
            "type", "cacheMb", "formFactorId", "price"
        ],
        "types": {
            "capacityGb": int,
            "pricePerGb": float,
            "cacheMb": int,
            "price": float
        }
    }
}
conn = sqlite3.connect("scrapingTools/pcParts.db")
cursor = conn.cursor()

for name in manufacturers:
    cursor.execute("INSERT OR IGNORE INTO manufacturer (name) VALUES (?)", (name,)) #id is automatically assigned to be the same as rowid
conn.commit()
cursor.execute("SELECT * FROM manufacturer")
conn.close()

