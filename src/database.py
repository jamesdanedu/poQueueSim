"""
Database module for Post Office Queue Simulator
Handles SQLite database initialization and schema
"""

import sqlite3
from datetime import datetime
import os

class DatabaseManager:
    """Manages SQLite database for simulation logging"""
    
    def __init__(self, dbPath='database/poQueueSim.db'):
        """Initialize database connection and create tables if needed"""
        self.dbPath = dbPath
        os.makedirs(os.path.dirname(dbPath), exist_ok=True)
        self.connection = sqlite3.connect(dbPath)
        self.cursor = self.connection.cursor()
        self._createTables()
    
    def _createTables(self):
        """Create database tables if they don't exist"""
        
        # Simulation runs table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS simulationRuns (
                runId INTEGER PRIMARY KEY AUTOINCREMENT,
                dispatchStrategy TEXT NOT NULL,
                timeAcceleration REAL NOT NULL,
                startTime TIMESTAMP NOT NULL,
                endTime TIMESTAMP,
                serviceTimeStandardPost REAL,
                serviceTimePassports REAL,
                serviceTimeParcels REAL,
                abandonmentEnabled INTEGER,
                notes TEXT
            )
        ''')
        
        # Customers table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS customers (
                customerId INTEGER PRIMARY KEY AUTOINCREMENT,
                runId INTEGER NOT NULL,
                serviceType TEXT NOT NULL,
                arrivalTime REAL NOT NULL,
                queueJoinTime REAL NOT NULL,
                serviceStartTime REAL,
                serviceEndTime REAL,
                waitDuration REAL,
                serviceDuration REAL,
                outcome TEXT NOT NULL,
                serverId INTEGER,
                boothId INTEGER,
                FOREIGN KEY (runId) REFERENCES simulationRuns(runId)
            )
        ''')
        
        # Server events table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS serverEvents (
                eventId INTEGER PRIMARY KEY AUTOINCREMENT,
                runId INTEGER NOT NULL,
                serverId INTEGER NOT NULL,
                eventType TEXT NOT NULL,
                eventTime REAL NOT NULL,
                boothId INTEGER,
                customerId INTEGER,
                serviceType TEXT,
                FOREIGN KEY (runId) REFERENCES simulationRuns(runId),
                FOREIGN KEY (customerId) REFERENCES customers(customerId)
            )
        ''')
        
        # Queue snapshots table (for analytics)
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS queueSnapshots (
                snapshotId INTEGER PRIMARY KEY AUTOINCREMENT,
                runId INTEGER NOT NULL,
                snapshotTime REAL NOT NULL,
                serviceType TEXT NOT NULL,
                queueLength INTEGER NOT NULL,
                FOREIGN KEY (runId) REFERENCES simulationRuns(runId)
            )
        ''')
        
        self.connection.commit()
    
    def startSimulationRun(self, dispatchStrategy, timeAcceleration, serviceTimes, abandonmentEnabled):
        """Create a new simulation run and return its ID"""
        self.cursor.execute('''
            INSERT INTO simulationRuns 
            (dispatchStrategy, timeAcceleration, startTime, 
             serviceTimeStandardPost, serviceTimePassports, serviceTimeParcels,
             abandonmentEnabled)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            dispatchStrategy,
            timeAcceleration,
            datetime.now(),
            serviceTimes.get('standard_post', 2.0),
            serviceTimes.get('passports', 5.0),
            serviceTimes.get('parcels', 3.0),
            1 if abandonmentEnabled else 0
        ))
        self.connection.commit()
        return self.cursor.lastrowid
    
    def endSimulationRun(self, runId):
        """Mark simulation run as ended"""
        self.cursor.execute('''
            UPDATE simulationRuns 
            SET endTime = ? 
            WHERE runId = ?
        ''', (datetime.now(), runId))
        self.connection.commit()
    
    def logCustomer(self, runId, customerId, serviceType, arrivalTime, queueJoinTime, 
                    serviceStartTime, serviceEndTime, waitDuration, serviceDuration, 
                    outcome, serverId, boothId):
        """Log a customer's complete journey"""
        self.cursor.execute('''
            INSERT INTO customers 
            (customerId, runId, serviceType, arrivalTime, queueJoinTime, 
             serviceStartTime, serviceEndTime, waitDuration, serviceDuration, 
             outcome, serverId, boothId)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (customerId, runId, serviceType, arrivalTime, queueJoinTime,
              serviceStartTime, serviceEndTime, waitDuration, serviceDuration,
              outcome, serverId, boothId))
        self.connection.commit()
    
    def logServerEvent(self, runId, serverId, eventType, eventTime, boothId=None, 
                       customerId=None, serviceType=None):
        """Log a server event"""
        self.cursor.execute('''
            INSERT INTO serverEvents 
            (runId, serverId, eventType, eventTime, boothId, customerId, serviceType)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (runId, serverId, eventType, eventTime, boothId, customerId, serviceType))
        self.connection.commit()
    
    def logQueueSnapshot(self, runId, snapshotTime, queueLengths):
        """Log queue lengths at a point in time"""
        for serviceType, length in queueLengths.items():
            self.cursor.execute('''
                INSERT INTO queueSnapshots 
                (runId, snapshotTime, serviceType, queueLength)
                VALUES (?, ?, ?, ?)
            ''', (runId, snapshotTime, serviceType, length))
        self.connection.commit()
    
    def getRunStatistics(self, runId):
        """Get statistics for a simulation run"""
        stats = {}
        
        # Average wait time by service type
        self.cursor.execute('''
            SELECT serviceType, 
                   AVG(waitDuration) as avgWait,
                   COUNT(*) as totalCustomers,
                   SUM(CASE WHEN outcome = 'completed' THEN 1 ELSE 0 END) as completed,
                   SUM(CASE WHEN outcome = 'abandoned' THEN 1 ELSE 0 END) as abandoned
            FROM customers
            WHERE runId = ?
            GROUP BY serviceType
        ''', (runId,))
        
        stats['byServiceType'] = {}
        for row in self.cursor.fetchall():
            stats['byServiceType'][row[0]] = {
                'avgWait': row[1],
                'totalCustomers': row[2],
                'completed': row[3],
                'abandoned': row[4]
            }
        
        return stats
    
    def close(self):
        """Close database connection"""
        self.connection.close()
