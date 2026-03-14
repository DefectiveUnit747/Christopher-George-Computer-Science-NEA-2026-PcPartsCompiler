import unittest
import sqlite3
import logging
import os
from pcBuildListCompiler.databasing.createDatabase import Database

logging.basicConfig(level=logging.DEBUG, format="%(levelname)s:%(message)s")
logger = logging.getLogger()

SCHEMA_PATH = os.path.join(os.path.dirname(__file__), '..', 'databasing', 'schema.sql')

class TestCreateDatabase(unittest.TestCase):

    def setUp(self):
        logger.info(f"Running {self._testMethodName}")
        self.db = Database.__new__(Database)
        self.db._conn = sqlite3.connect(":memory:")
        self.db._cursor = self.db._conn.cursor()
        self.db._cursor.execute("PRAGMA foreign_keys = ON;")

    def testDropsComponentTablesButPreservesManufacturer(self):
        self.db._cursor.executescript(open(SCHEMA_PATH).read())
        self.db._cursor.execute("INSERT INTO manufacturer (name) VALUES ('AMD')")
        self.db._cursor.execute("INSERT INTO cpu (partNumber, name) VALUES ('AMD-001', 'Ryzen 7')")
        self.db._conn.commit()
        logger.info("Inserted AMD into manufacturer and AMD-001 into cpu")

        self.db.createDatabaseTables()

        self.db._cursor.execute("SELECT COUNT(*) FROM manufacturer")
        manufacturerCount = self.db._cursor.fetchone()[0]
        logger.info(f"Manufacturer rows after recreate: {manufacturerCount}")
        self.assertEqual(manufacturerCount, 1)

        self.db._cursor.execute("SELECT COUNT(*) FROM cpu")
        cpuCount = self.db._cursor.fetchone()[0]
        logger.info(f"CPU rows after recreate: {cpuCount}")
        self.assertEqual(cpuCount, 0)

    def testMakesAllTheTablesFromSchema(self):
        self.db.createDatabaseTables()
        logger.info("Called createDatabaseTables()")

        tables = ["cpu", "gpu", "ram", "motherboard", "psu", "storage", "cases", "manufacturer"]
        self.db._cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        actualTables = [row[0] for row in self.db._cursor.fetchall()]
        logger.info(f"Tables found in database: {actualTables}")

        for table in tables:
            self.assertIn(table, actualTables)
            logger.info(f"Table '{table}' confirmed present")

    def testAddInManufacturersAndDuplicatesHandled(self):
        self.db._cursor.executescript(open(SCHEMA_PATH).read())
        listOfManufacturers = ["AMD", "Nvidia", "AMD", "Intel", "EVGA"]
        logger.info(f"Inserting manufacturers: {listOfManufacturers}")

        self.db.addInManufacturers(listOfManufacturers)

        self.db._cursor.execute("SELECT COUNT(*) FROM manufacturer")
        count = self.db._cursor.fetchone()[0]
        logger.info(f"Manufacturer count after insert: {count} (expected 4, AMD duplicate ignored)")
        self.assertEqual(count, 4)

    def testGetManufacturerMapReturnsCorrectLowercaseIdMapping(self):
        self.db._cursor.executescript(open(SCHEMA_PATH).read())
        self.db._cursor.execute("INSERT INTO manufacturer (name) VALUES ('AMD')")
        self.db._cursor.execute("INSERT INTO manufacturer (name) VALUES ('Nvidia')")
        self.db._conn.commit()
        logger.info("Inserted AMD and Nvidia into manufacturer table")

        result = self.db.getManufacturerMap()
        logger.info(f"Manufacturer map returned: {result}")

        self.assertIn("amd", result)
        self.assertIn("nvidia", result)
        self.assertIsInstance(result["amd"], int)
        self.assertIsInstance(result["nvidia"], int)
        self.assertEqual(result["amd"], 1)
        self.assertEqual(result["nvidia"], 2)

    def testGetManufacturerMapRaisesValueErrorOnEmptyTable(self):
        self.db._cursor.executescript(open(SCHEMA_PATH).read())
        logger.info("Manufacturer table is empty, expecting ValueError")

        with self.assertRaises(ValueError) as context:
            self.db.getManufacturerMap()
        logger.info(f"ValueError raised as expected: {context.exception}")
        self.assertIn("No manufacturers found", str(context.exception))

    def testInsertCPU(self):
        self.db._cursor.executescript(open(SCHEMA_PATH).read())
        self.db._cursor.execute("INSERT INTO manufacturer (name) VALUES ('AMD')")
        self.db._conn.commit()
        self.db._cursor.execute("SELECT manufacturerId FROM manufacturer WHERE name='AMD'")
        self.amdId = self.db._cursor.fetchone()[0]
        logger.info(f"AMD manufacturerId: {self.amdId}")

        cpu = {
            "partNumber": "AMD-001",
            "name": "Ryzen 7 7800X3D",
            "price": 399.99,
            "manufacturerId": self.amdId,
            "url": "https://www.cclonline.com/amd-ryzen-7-7800x3d",
            "score": 85.0,
            "scoreEfficiency": 70.0,
            "scoreUpgradeability": 60.0,
            "coreCount": 8,
            "coreClock": 4.5,
            "cache": 96,
            "threads": 16,
            "tdpWatts": 120,
            "socketId": "AM5",
            "imagePath": "images/cpu/AMD-001.jpg"
        }
        logger.info(f"Inserting CPU: {cpu}")

        self.db.insertComponent("cpu", cpu)

        self.db._cursor.execute("SELECT * FROM cpu WHERE partNumber='AMD-001'")
        result = self.db._cursor.fetchone()
        logger.info(f"Row retrieved from cpu table: {result}")

        count = 0
        for key, value in cpu.items():
            logger.info(f"Checking {key}: expected={value}, actual={result[count]}")
            self.assertEqual(value, result[count])
            count += 1

    def testInsertGPU(self):
        self.db._cursor.executescript(open(SCHEMA_PATH).read())
        self.db._cursor.execute("INSERT INTO manufacturer (name) VALUES ('Nvidia')")
        self.db._conn.commit()
        self.db._cursor.execute("SELECT manufacturerId FROM manufacturer WHERE name='Nvidia'")
        self.nvidiaId = self.db._cursor.fetchone()[0]
        logger.info(f"Nvidia manufacturerId: {self.nvidiaId}")

        gpu = {
            "partNumber": "NV-001",
            "name": "RTX 4070",
            "price": 599.99,
            "manufacturerId": self.nvidiaId,
            "url": "https://www.cclonline.com/rtx-4070",
            "score": 90.0,
            "scoreEfficiency": 80.0,
            "scoreUpgradeability": 50.0,
            "memoryGb": 12,
            "coreClock": 2475.0,
            "memoryType": "GDDR6X",
            "tdpWatts": 200,
            "lengthMm": 336,
            "imagePath": "images/gpu/NV-001.jpg"
        }
        logger.info(f"Inserting GPU: {gpu}")

        self.db.insertComponent("gpu", gpu)

        self.db._cursor.execute("SELECT * FROM gpu WHERE partNumber='NV-001'")
        result = self.db._cursor.fetchone()
        logger.info(f"Row retrieved from gpu table: {result}")

        count = 0
        for key, value in gpu.items():
            logger.info(f"Checking {key}: expected={value}, actual={result[count]}")
            self.assertEqual(value, result[count])
            count += 1

    def testDuplicatePartNumberRaisesIntegrityError(self):
        self.db._cursor.executescript(open(SCHEMA_PATH).read())
        self.db._cursor.execute("INSERT INTO manufacturer (name) VALUES ('AMD')")
        self.db._conn.commit()
        self.db._cursor.execute("SELECT manufacturerId FROM manufacturer WHERE name='AMD'")
        self.amdId = self.db._cursor.fetchone()[0]

        cpu = {
            "partNumber": "AMD-001",
            "name": "Ryzen 7 7800X3D",
            "price": 399.99,
            "manufacturerId": self.amdId,
            "url": "https://www.cclonline.com/amd-ryzen-7-7800x3d",
            "score": 85.0,
            "scoreEfficiency": 70.0,
            "scoreUpgradeability": 60.0,
            "coreCount": 8,
            "coreClock": 4.5,
            "cache": 96,
            "threads": 16,
            "tdpWatts": 120,
            "socketId": "AM5",
            "imagePath": "images/cpu/AMD-001.jpg"
        }

        self.db.insertComponent("cpu", cpu)
        logger.info(f"First insert of AMD-001 successful")

        try:
            self.db._cursor.execute("INSERT OR FAIL INTO cpu (partNumber) VALUES ('AMD-001')")
            self.db._conn.commit()
            self.fail("Expected IntegrityError was not raised")
        except sqlite3.IntegrityError as e:
            logger.info(f"IntegrityError raised as expected: {e}")

    def testInsertOrReplaceUpdatesExistingRow(self):
        self.db._cursor.executescript(open(SCHEMA_PATH).read())
        self.db._cursor.execute("INSERT INTO manufacturer (name) VALUES ('AMD')")
        self.db._conn.commit()
        self.db._cursor.execute("SELECT manufacturerId FROM manufacturer WHERE name='AMD'")
        self.amdId = self.db._cursor.fetchone()[0]

        cpu = {
            "partNumber": "AMD-001",
            "name": "Ryzen 7 7800X3D",
            "price": 399.99,
            "manufacturerId": self.amdId,
            "url": "https://www.cclonline.com/amd-ryzen-7-7800x3d",
            "score": 85.0,
            "scoreEfficiency": 70.0,
            "scoreUpgradeability": 60.0,
            "coreCount": 8,
            "coreClock": 4.5,
            "cache": 96,
            "threads": 16,
            "tdpWatts": 120,
            "socketId": "AM5",
            "imagePath": "images/cpu/AMD-001.jpg"
        }

        self.db.insertComponent("cpu", cpu)
        logger.info(f"Inserted CPU with price={cpu['price']}")

        cpu["price"] = 349.99
        self.db.insertComponent("cpu", cpu)
        logger.info(f"Re-inserted CPU with updated price={cpu['price']}")

        self.db._cursor.execute("SELECT price FROM cpu WHERE partNumber='AMD-001'")
        price = self.db._cursor.fetchone()[0]
        logger.info(f"Price after INSERT OR REPLACE: {price} (expected 349.99)")
        self.assertEqual(price, 349.99)

    def testInsertCpuWithPriceAtZero(self):
        self.db._cursor.executescript(open(SCHEMA_PATH).read())
        self.db._cursor.execute("INSERT INTO manufacturer (name) VALUES ('AMD')")
        self.db._conn.commit()
        self.db._cursor.execute("SELECT manufacturerId FROM manufacturer WHERE name='AMD'")
        self.amdId = self.db._cursor.fetchone()[0]

        cpu = {
            "partNumber": "AMD-002",
            "name": "Ryzen 5 7600",
            "price": 0,
            "manufacturerId": self.amdId,
            "url": "https://www.cclonline.com/amd-ryzen-5-7600",
            "score": 70.0,
            "scoreEfficiency": 60.0,
            "scoreUpgradeability": 50.0,
            "coreCount": 6,
            "coreClock": 3.8,
            "cache": 32,
            "threads": 12,
            "tdpWatts": 65,
            "socketId": "AM5",
            "imagePath": "images/cpu/AMD-002.jpg"
        }
        logger.info(f"Inserting CPU with price=0")

        self.db.insertComponent("cpu", cpu)

        self.db._cursor.execute("SELECT price FROM cpu WHERE partNumber='AMD-002'")
        price = self.db._cursor.fetchone()[0]
        logger.info(f"Price stored at zero: {price} (expected 0)")
        self.assertEqual(price, 0)

    def tearDown(self):
        self.db._conn.close()
        logger.info(f"{self._testMethodName} torn down")


if __name__ == "__main__":
    unittest.main()