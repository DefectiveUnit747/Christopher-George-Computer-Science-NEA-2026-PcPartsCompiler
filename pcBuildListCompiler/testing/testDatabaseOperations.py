import unittest
from unittest.mock import patch, MagicMock, mock_open
import sqlite3


class TestDatabaseOperations(unittest.TestCase):
    """Unit tests for Database operations using mocks - no actual DB calls"""

    def setUp(self):
        """Set up mocked Database instance"""

        # Patch sqlite3.connect in the target module
        self.connect_patcher = patch(
            'pcBuildListCompiler.databasing.createDatabase.sqlite3.connect'
        )
        mockConnect = self.connect_patcher.start()
        self.addCleanup(self.connect_patcher.stop)

        # Create connection and cursor mocks
        self.mockConn = MagicMock()
        self.mockCursor = MagicMock()
        self.mockConn.cursor.return_value = self.mockCursor
        mockConnect.return_value = self.mockConn

        # Import Database AFTER patch is active
        from pcBuildListCompiler.databasing.createDatabase import Database
        self.db = Database()

    def test_createDatabaseTablesDropsComponentTablesButPreservesManufacturer(self):
        """Test #1: createDatabaseTables() drops component tables but preserves manufacturer"""

        mockSchemaContent = "CREATE TABLE manufacturer (...); CREATE TABLE cpu (...);"

        with patch('builtins.open', mock_open(read_data=mockSchemaContent)):
            self.db.createDatabaseTables()

        # Verify DROP TABLE was called 7 times (once per component table)
        dropCalls = [
            c for c in self.mockCursor.execute.call_args_list
            if 'DROP TABLE IF EXISTS' in str(c)
        ]
        self.assertEqual(len(dropCalls), 7)

        # Verify schema was executed
        self.mockCursor.executescript.assert_called_once()
        self.mockConn.commit.assert_called()

    def test_createDatabaseTablesCreatesAllTables(self):
        """Test #2: createDatabaseTables() creates all tables from schema.sql"""

        mockSchemaContent = "CREATE TABLE manufacturer (...); CREATE TABLE cpu (...);"

        with patch('builtins.open', mock_open(read_data=mockSchemaContent)):
            self.db.createDatabaseTables()

        # Verify schema was executed with correct content
        self.mockCursor.executescript.assert_called_with(mockSchemaContent)

    def test_addInManufacturersInsertsAllAndHandlesDuplicates(self):
        """Test #3: addInManufacturers() inserts all manufacturers and handles duplicates"""

        # Reset to ignore any previous calls
        self.mockCursor.reset_mock()

        manufacturers = ["AMD", "Intel", "Nvidia"]
        self.db.addInManufacturers(manufacturers)

        # Should be called 3 times
        self.assertEqual(self.mockCursor.execute.call_count, 3)

        # Verify INSERT OR IGNORE was used
        for callArgs in self.mockCursor.execute.call_args_list:
            sql = callArgs[0][0]
            self.assertIn("INSERT OR IGNORE", sql)

        self.mockConn.commit.assert_called()

    def test_getManufacturerMapReturnsCorrectLowercaseIdMapping(self):
        """Test #4: getManufacturerMap() returns correct lowercase ID mapping"""

        # Mock fetchall return
        self.mockCursor.fetchall.return_value = [
            (1, "AMD"),
            (2, "Intel"),
            (3, "Nvidia")
        ]

        # Reset to ignore earlier calls
        self.mockCursor.reset_mock()

        result = self.db.getManufacturerMap()

        # Verify SELECT was called once
        self.assertEqual(self.mockCursor.execute.call_count, 1)
        sql = self.mockCursor.execute.call_args[0][0]
        self.assertIn("SELECT", sql)

        # Verify lowercase mapping
        self.assertEqual(result, {
            "amd": 1,
            "intel": 2,
            "nvidia": 3
        })
        self.assertNotIn("AMD", result)

    def test_insertComponentInsertsCpuWithParameterizedQuery(self):
        """Test #5: insertComponent() inserts CPU with parameterized query"""

        self.mockCursor.reset_mock()
        self.mockConn.reset_mock()

        cpuData = {
            "partNumber": "CPU-001",
            "name": "AMD Ryzen",
            "price": 299.99,
            "manufacturerId": 1,
            "url": "url",
            "score": 75.0,
            "scoreEfficiency": 65.0,
            "scoreUpgradeability": 80.0,
            "coreCount": 8,
            "coreClock": 4.5,
            "cache": 32,
            "threads": 16,
            "tdpWatts": 105,
            "socketId": 1,
            "imagePath": "path"
        }

        self.db.insertComponent("cpu", cpuData)

        callArgs = self.mockCursor.execute.call_args
        sql = callArgs[0][0]
        params = callArgs[0][1]

        self.assertIn("INSERT", sql)
        self.assertIn("cpu", sql)
        self.assertIn("?", sql)

        self.assertEqual(len(params), len(cpuData))
        self.assertIn(299.99, params)

        self.mockConn.commit.assert_called_once()

    def test_insertComponentInsertsGpuWithAllFields(self):
        """Test #6: insertComponent() inserts GPU with all fields"""

        self.mockCursor.reset_mock()
        self.mockConn.reset_mock()

        gpuData = {
            "partNumber": "GPU-001",
            "name": "RTX 4080",
            "price": 899.99,
            "manufacturerId": 2,
            "url": "url",
            "score": 95.0,
            "scoreEfficiency": 75.0,
            "scoreUpgradeability": 70.0,
            "memoryGb": 16,
            "coreClock": 2505,
            "memoryType": "GDDR6X",
            "tdpWatts": 320,
            "lengthMm": 304,
            "imagePath": "path"
        }

        self.db.insertComponent("gpu", gpuData)

        callArgs = self.mockCursor.execute.call_args
        sql = callArgs[0][0]
        params = callArgs[0][1]

        self.assertIn("INSERT", sql)
        self.assertIn("gpu", sql)
        self.assertIn(16, params)
        self.assertIn("GDDR6X", params)
        self.assertIn(304, params)

    def test_insertComponentEnforcesPrimaryKeyConstraint(self):
        """Test #7: insertComponent() enforces primary key constraint"""

        cpuData = {
            "partNumber": "CPU-DUP",
            "name": "Test",
            "price": 200.0,
            "manufacturerId": 1,
            "url": "url",
            "score": 50.0,
            "scoreEfficiency": 40.0,
            "scoreUpgradeability": 30.0,
            "coreCount": 6,
            "coreClock": 4.2,
            "cache": 32,
            "threads": 12,
            "tdpWatts": 65,
            "socketId": 1,
            "imagePath": "path"
        }

        self.mockCursor.execute.side_effect = sqlite3.IntegrityError("UNIQUE constraint failed")

        with self.assertRaises(sqlite3.IntegrityError):
            self.db.insertComponent("cpu", cpuData)

    def test_insertComponentEnforcesForeignKeyConstraint(self):
        """Test #8: insertComponent() enforces foreign key constraint"""

        cpuData = {
            "partNumber": "CPU-BAD",
            "name": "Test",
            "price": 200.0,
            "manufacturerId": 99999,
            "url": "url",
            "score": 50.0,
            "scoreEfficiency": 40.0,
            "scoreUpgradeability": 30.0,
            "coreCount": 6,
            "coreClock": 4.2,
            "cache": 32,
            "threads": 12,
            "tdpWatts": 65,
            "socketId": 1,
            "imagePath": "path"
        }

        self.mockCursor.execute.side_effect = sqlite3.IntegrityError("FOREIGN KEY constraint failed")

        with self.assertRaises(sqlite3.IntegrityError):
            self.db.insertComponent("cpu", cpuData)

    def test_insertComponentHandlesDuplicatePartNumbers(self):
        """Test #9: insertComponent() handles duplicate part numbers"""

        cpuData = {
            "partNumber": "DUPLICATE",
            "name": "Test",
            "price": 150.0,
            "manufacturerId": 1,
            "url": "url",
            "score": 55.0,
            "scoreEfficiency": 45.0,
            "scoreUpgradeability": 35.0,
            "coreCount": 4,
            "coreClock": 3.8,
            "cache": 16,
            "threads": 8,
            "tdpWatts": 95,
            "socketId": 1,
            "imagePath": "path"
        }

        self.mockCursor.execute.side_effect = sqlite3.IntegrityError("UNIQUE constraint failed")

        with self.assertRaises(sqlite3.IntegrityError):
            self.db.insertComponent("cpu", cpuData)

    def test_getManufacturerMapHandlesEmptyTable(self):
        """Test #10: getManufacturerMap() handles empty manufacturer table"""

        # Mock empty result
        self.mockCursor.fetchall.return_value = []

        with self.assertRaises(ValueError):
            self.db.getManufacturerMap()


if __name__ == "__main__":
    unittest.main(verbosity=2)
