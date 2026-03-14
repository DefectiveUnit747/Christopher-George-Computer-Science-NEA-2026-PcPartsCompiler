import sqlite3
import os
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('scraping.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class Database:
    def __init__(self):
        ROOT_DIRECTORY = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        db_path = os.path.join(ROOT_DIRECTORY, "computerParts.db")

        logger.info("Connecting to database at %s", db_path)

        self._conn = sqlite3.connect(db_path)
        self._cursor = self._conn.cursor()
        self._cursor.execute("PRAGMA foreign_keys = ON;")

        logger.info("Database connection established")

    def createDatabaseTables(self):
        logger.info("Creating database tables from schema.sql")

        tablesToDrop = ["cpu", "gpu", "ram", "motherboard", "psu", "storage", "cases"]
        for table in tablesToDrop:
            self._cursor.execute(f"DROP TABLE IF EXISTS {table}")

        schemaPath = os.path.join(os.path.dirname(__file__), "schema.sql")
        with open(schemaPath, "r") as file:
            self._cursor.executescript(file.read())
        self._conn.commit()

        logger.info("Database tables created successfully")

    def addInManufacturers(self, manufacturers):
        logger.info("Inserting %d manufacturers", len(manufacturers))

        for name in manufacturers:
            self._cursor.execute(
                "INSERT OR IGNORE INTO manufacturer (name) VALUES (?)",
                (name,)
            )
        self._conn.commit()

        logger.info("Manufacturer insert complete")

    def getManufacturerMap(self):
        logger.info("Fetching manufacturer map")

        self._cursor.execute("SELECT manufacturerId, name FROM manufacturer")
        result = {
            name.lower(): manufacturerId
            for manufacturerId, name in self._cursor.fetchall()
            if name is not None
        }

        if not result:  # ← ADDED
            logger.error("Manufacturer table is empty!")
            raise ValueError("No manufacturers found in database")

        logger.info("Loaded %d manufacturers", len(result))
        return result

    def insertComponent(self, table, data):
        logger.info("Inserting component into table '%s': %s", table, data.get("partNumber"))

        keys = ", ".join(data.keys())
        placeholders = ", ".join(["?"] * len(data))
        values = tuple(data.values())
        query = f"INSERT OR REPLACE INTO {table} ({keys}) VALUES ({placeholders})"

        self._cursor.execute(query, values)
        self._conn.commit()

        logger.info("Component %s inserted into %s", data.get("partNumber"), table)

    def close(self):
        logger.info("Closing database connection")
        self._conn.close()
