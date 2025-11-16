"""
Main GUI Application for Post Office Queue Simulator
PyQt5-based interface with real-time visualization
"""

import sys
import os
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                              QHBoxLayout, QLabel, QPushButton, QGroupBox,
                              QGridLayout, QComboBox, QSpinBox, QDoubleSpinBox,
                              QCheckBox, QStatusBar, QFrame, QScrollArea)
from PyQt5.QtCore import QTimer, Qt, pyqtSignal, QObject
from PyQt5.QtGui import QFont, QPalette, QColor

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from queueSimulator import QueueSimulator, DispatchStrategy
from microbitComms import MicrobitCommunicator
from database import DatabaseManager


class SimulationSignals(QObject):
    """Signals for thread-safe GUI updates"""
    customerAdded = pyqtSignal(str)
    stateUpdated = pyqtSignal()


class QueueVisualization(QWidget):
    """Widget to visualize a single queue"""
    
    def __init__(self, serviceType, parent=None):
        super().__init__(parent)
        self.serviceType = serviceType
        self.queueLength = 0
        self.initUI()
    
    def initUI(self):
        """Initialize UI components"""
        layout = QVBoxLayout()
        
        # Service type label
        titleFont = QFont()
        titleFont.setPointSize(12)
        titleFont.setBold(True)
        
        self.titleLabel = QLabel(self.serviceType.replace('_', ' ').title())
        self.titleLabel.setFont(titleFont)
        self.titleLabel.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.titleLabel)
        
        # Queue length display
        self.lengthLabel = QLabel("Queue: 0")
        self.lengthLabel.setAlignment(Qt.AlignCenter)
        queueFont = QFont()
        queueFont.setPointSize(24)
        self.lengthLabel.setFont(queueFont)
        layout.addWidget(self.lengthLabel)
        
        # Visual queue representation
        self.queueFrame = QFrame()
        self.queueFrame.setMinimumHeight(200)
        self.queueFrame.setFrameStyle(QFrame.Box | QFrame.Sunken)
        self.queueFrame.setLineWidth(2)
        layout.addWidget(self.queueFrame)
        
        self.setLayout(layout)
    
    def updateQueue(self, length):
        """Update queue visualization"""
        self.queueLength = length
        self.lengthLabel.setText(f"Queue: {length}")
        
        # Color coding based on queue length
        if length == 0:
            color = "#90EE90"  # Light green
        elif length < 5:
            color = "#FFD700"  # Gold
        elif length < 10:
            color = "#FFA500"  # Orange
        else:
            color = "#FF6347"  # Tomato red
        
        self.queueFrame.setStyleSheet(f"background-color: {color};")


class BoothDisplay(QWidget):
    """Widget to display booth status"""
    
    def __init__(self, boothId, parent=None):
        super().__init__(parent)
        self.boothId = boothId
        self.initUI()
    
    def initUI(self):
        """Initialize UI components"""
        layout = QVBoxLayout()
        layout.setSpacing(5)
        layout.setContentsMargins(5, 5, 5, 5)
        
        # Booth number with icon
        titleLayout = QHBoxLayout()
        self.iconLabel = QLabel("🏢")
        iconFont = QFont()
        iconFont.setPointSize(14)
        self.iconLabel.setFont(iconFont)
        titleLayout.addWidget(self.iconLabel)
        
        self.titleLabel = QLabel(f"Booth {self.boothId + 1}")
        self.titleLabel.setAlignment(Qt.AlignCenter)
        titleFont = QFont()
        titleFont.setBold(True)
        titleFont.setPointSize(10)
        self.titleLabel.setFont(titleFont)
        titleLayout.addWidget(self.titleLabel)
        titleLayout.addStretch()
        layout.addLayout(titleLayout)
        
        # Status frame - SMALLER
        self.statusFrame = QFrame()
        self.statusFrame.setMinimumSize(120, 80)
        self.statusFrame.setMaximumSize(160, 100)
        self.statusFrame.setFrameStyle(QFrame.Box | QFrame.Raised)
        self.statusFrame.setLineWidth(2)
        
        # Status content
        statusLayout = QVBoxLayout()
        statusLayout.setAlignment(Qt.AlignCenter)
        statusLayout.setSpacing(3)
        
        # Staff indicator
        self.serverLabel = QLabel("👤")
        self.serverLabel.setAlignment(Qt.AlignCenter)
        serverFont = QFont()
        serverFont.setPointSize(16)
        self.serverLabel.setFont(serverFont)
        statusLayout.addWidget(self.serverLabel)
        
        # Status text
        self.statusLabel = QLabel("IDLE")
        self.statusLabel.setAlignment(Qt.AlignCenter)
        statusFont = QFont()
        statusFont.setPointSize(9)
        statusFont.setBold(True)
        self.statusLabel.setFont(statusFont)
        statusLayout.addWidget(self.statusLabel)
        
        # Service info
        self.serviceLabel = QLabel("")
        self.serviceLabel.setAlignment(Qt.AlignCenter)
        self.serviceLabel.setWordWrap(True)
        infoFont = QFont()
        infoFont.setPointSize(8)
        self.serviceLabel.setFont(infoFont)
        statusLayout.addWidget(self.serviceLabel)
        
        self.statusFrame.setLayout(statusLayout)
        layout.addWidget(self.statusFrame)
        
        self.setLayout(layout)
        self.updateStatus(False, None, None, 0)
    
    def updateStatus(self, occupied, serverId, serviceType, timeRemaining):
        """Update booth status"""
        if occupied:
            self.statusFrame.setStyleSheet("background-color: #FF6347; border: 2px solid #CC0000;")
            self.serverLabel.setText("👷")
            self.statusLabel.setText("SERVING")
            self.statusLabel.setStyleSheet("color: white; font-weight: bold;")
            
            serverText = f"Server {serverId + 1}" if serverId is not None else "Server ?"
            serviceText = serviceType.replace('_', ' ').title() if serviceType else "Unknown"
            self.serviceLabel.setText(f"{serverText}\n{serviceText}\n⏱ {timeRemaining:.1f}min")
            self.serviceLabel.setStyleSheet("color: white;")
            self.titleLabel.setStyleSheet("color: #CC0000;")
        else:
            self.statusFrame.setStyleSheet("background-color: #90EE90; border: 2px solid #228B22;")
            self.serverLabel.setText("🪑")
            self.statusLabel.setText("AVAILABLE")
            self.statusLabel.setStyleSheet("color: #228B22; font-weight: bold;")
            self.serviceLabel.setText("Ready")
            self.serviceLabel.setStyleSheet("color: #228B22;")
            self.titleLabel.setStyleSheet("color: #228B22;")


class ServerDisplay(QWidget):
    """Widget to display server status with icon"""
    
    def __init__(self, serverId, parent=None):
        super().__init__(parent)
        self.serverId = serverId
        self.initUI()
    
    def initUI(self):
        """Initialize UI components"""
        layout = QVBoxLayout()
        layout.setSpacing(3)
        layout.setContentsMargins(3, 3, 3, 3)
        
        # Server icon (person emoji/symbol)
        self.iconLabel = QLabel("👤")
        self.iconLabel.setAlignment(Qt.AlignCenter)
        iconFont = QFont()
        iconFont.setPointSize(18)
        self.iconLabel.setFont(iconFont)
        layout.addWidget(self.iconLabel)
        
        # Server number
        self.idLabel = QLabel(f"Server {self.serverId + 1}")
        self.idLabel.setAlignment(Qt.AlignCenter)
        idFont = QFont()
        idFont.setBold(True)
        idFont.setPointSize(9)
        self.idLabel.setFont(idFont)
        layout.addWidget(self.idLabel)
        
        # Status frame with color - SMALLER
        self.statusFrame = QFrame()
        self.statusFrame.setMinimumSize(70, 40)
        self.statusFrame.setMaximumSize(100, 50)
        self.statusFrame.setFrameStyle(QFrame.Box | QFrame.Raised)
        self.statusFrame.setLineWidth(2)
        layout.addWidget(self.statusFrame)
        
        # Status text
        self.statusLabel = QLabel("SPARE")
        self.statusLabel.setAlignment(Qt.AlignCenter)
        self.statusLabel.setWordWrap(True)
        statusFont = QFont()
        statusFont.setPointSize(7)
        self.statusLabel.setFont(statusFont)
        layout.addWidget(self.statusLabel)
        
        self.setLayout(layout)
        self.updateStatus("spare", None, None)
        self.setMaximumWidth(110)
    
    def updateStatus(self, state, boothId, serviceType):
        """Update server status"""
        if state == "busy":
            self.iconLabel.setText("👷")
            self.statusFrame.setStyleSheet("background-color: #FF6347; border: 2px solid #CC0000;")
            self.idLabel.setStyleSheet("color: #CC0000;")
            
            boothText = f"Booth {boothId + 1}" if boothId is not None else "?"
            serviceText = serviceType.replace('_', ' ').title() if serviceType else ""
            self.statusLabel.setText(f"BUSY\n{boothText}")
            self.statusLabel.setStyleSheet("color: #CC0000; font-weight: bold;")
        else:
            self.iconLabel.setText("👤")
            self.statusFrame.setStyleSheet("background-color: #90EE90; border: 2px solid #228B22;")
            self.idLabel.setStyleSheet("color: #228B22;")
            self.statusLabel.setText("AVAILABLE")
            self.statusLabel.setStyleSheet("color: #228B22; font-weight: bold;")


class MainWindow(QMainWindow):
    """Main application window"""
    
    def __init__(self):
        super().__init__()
        self.simulator = None
        self.microbit = None
        self.database = None
        self.currentRunId = None
        self.signals = SimulationSignals()
        
        # Connect signals
        self.signals.customerAdded.connect(self.addCustomer)
        
        self.initUI()
        self.initSimulator()
        self.initMicrobit()
        self.setupTimer()
    
    def initUI(self):
        """Initialize user interface"""
        self.setWindowTitle("Post Office Queue Simulator")
        self.setGeometry(100, 100, 1400, 900)
        
        # Central widget
        centralWidget = QWidget()
        self.setCentralWidget(centralWidget)
        mainLayout = QHBoxLayout(centralWidget)
        
        # Left panel - Queue visualizations
        leftPanel = self.createQueuePanel()
        mainLayout.addWidget(leftPanel, stretch=2)
        
        # Right panel - Controls and status
        rightPanel = self.createControlPanel()
        mainLayout.addWidget(rightPanel, stretch=1)
        
        # Status bar
        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)
        self.statusBar.showMessage("Ready")
    
    def createQueuePanel(self):
        """Create panel showing queue visualizations with intuitive flow"""
        panel = QWidget()
        layout = QVBoxLayout()
        layout.setSpacing(10)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Title
        titleLabel = QLabel("Post Office Queue Simulation")
        titleFont = QFont()
        titleFont.setPointSize(16)
        titleFont.setBold(True)
        titleLabel.setFont(titleFont)
        titleLabel.setAlignment(Qt.AlignCenter)
        layout.addWidget(titleLabel)
        
        # Server status panel at TOP (showing who's working) - COMPACT
        serverGroupBox = QGroupBox("Available Staff (5 Servers)")
        serverLayout = QHBoxLayout()
        serverLayout.setSpacing(10)
        self.serverDisplays = []
        
        for i in range(5):
            serverDisplay = ServerDisplay(i)
            self.serverDisplays.append(serverDisplay)
            serverLayout.addWidget(serverDisplay)
        
        serverGroupBox.setLayout(serverLayout)
        serverGroupBox.setMaximumHeight(180)  # Limit height
        layout.addWidget(serverGroupBox)
        
        # Visual separator
        separator1 = QFrame()
        separator1.setFrameShape(QFrame.HLine)
        separator1.setFrameShadow(QFrame.Sunken)
        separator1.setLineWidth(2)
        layout.addWidget(separator1)
        
        # Booth displays in MIDDLE (service positions) - COMPACT
        boothGroupBox = QGroupBox("Service Booths (4 Positions)")
        boothLayout = QHBoxLayout()
        boothLayout.setSpacing(15)
        self.boothDisplays = []
        
        for i in range(4):
            boothDisplay = BoothDisplay(i)
            self.boothDisplays.append(boothDisplay)
            boothLayout.addWidget(boothDisplay)
        
        boothGroupBox.setLayout(boothLayout)
        boothGroupBox.setMaximumHeight(200)  # Limit height to reduce wasted space
        layout.addWidget(boothGroupBox)
        
        # Visual separator with arrow
        arrowLabel = QLabel("▲ Customers Called Up ▲")
        arrowLabel.setAlignment(Qt.AlignCenter)
        arrowLabel.setFont(QFont("Arial", 10, QFont.Bold))
        arrowLabel.setStyleSheet("color: #2196F3; padding: 5px;")
        layout.addWidget(arrowLabel)
        
        # Queue visualizations at BOTTOM (customers waiting) - FLEXIBLE HEIGHT
        queueGroupBox = QGroupBox("Waiting Queues")
        queueLayout = QHBoxLayout()
        queueLayout.setSpacing(15)
        self.queueVisualizations = {}
        
        for serviceType in ['standard_post', 'passports', 'parcels']:
            queueViz = QueueVisualization(serviceType)
            self.queueVisualizations[serviceType] = queueViz
            queueLayout.addWidget(queueViz)
        
        queueGroupBox.setLayout(queueLayout)
        # Let queues take remaining space
        layout.addWidget(queueGroupBox, stretch=1)
        
        panel.setLayout(layout)
        return panel
    
    def createControlPanel(self):
        """Create control panel with tabs"""
        panel = QWidget()
        layout = QVBoxLayout()
        
        # Create tab widget
        from PyQt5.QtWidgets import QTabWidget, QTextEdit
        tabWidget = QTabWidget()
        
        # Tab 1: Controls
        controlTab = QWidget()
        controlLayout = QVBoxLayout()
        
        # Simulation controls
        controlGroup = QGroupBox("Simulation Controls")
        controlGroupLayout = QVBoxLayout()
        
        self.startButton = QPushButton("Start Simulation")
        self.startButton.clicked.connect(self.startSimulation)
        controlGroupLayout.addWidget(self.startButton)
        
        self.pauseButton = QPushButton("Pause")
        self.pauseButton.clicked.connect(self.pauseSimulation)
        self.pauseButton.setEnabled(False)
        controlGroupLayout.addWidget(self.pauseButton)
        
        self.resetButton = QPushButton("Reset")
        self.resetButton.clicked.connect(self.resetSimulation)
        controlGroupLayout.addWidget(self.resetButton)
        
        controlGroup.setLayout(controlGroupLayout)
        controlLayout.addWidget(controlGroup)
        
        # Configuration
        configGroup = QGroupBox("Configuration")
        configLayout = QGridLayout()
        
        # Dispatch strategy
        configLayout.addWidget(QLabel("Dispatch Strategy:"), 0, 0)
        self.strategyCombo = QComboBox()
        self.strategyCombo.addItems([
            "Longest Wait First",
            "Shortest Job First",
            "Round Robin",
            "Priority Order"
        ])
        configLayout.addWidget(self.strategyCombo, 0, 1)
        
        # Time acceleration
        configLayout.addWidget(QLabel("Time Acceleration:"), 1, 0)
        self.timeAccelSpin = QDoubleSpinBox()
        self.timeAccelSpin.setRange(1.0, 100.0)
        self.timeAccelSpin.setValue(20.0)
        self.timeAccelSpin.setSuffix("x")
        configLayout.addWidget(self.timeAccelSpin, 1, 1)
        
        # Abandonment
        self.abandonmentCheck = QCheckBox("Enable Abandonment")
        self.abandonmentCheck.setChecked(True)
        configLayout.addWidget(self.abandonmentCheck, 2, 0, 1, 2)
        
        configGroup.setLayout(configLayout)
        controlLayout.addWidget(configGroup)
        
        # Service times configuration
        serviceTimeGroup = QGroupBox("Service Times (minutes)")
        serviceTimeLayout = QGridLayout()
        
        self.serviceTimeSpins = {}
        serviceTypes = [
            ('standard_post', 'Standard Post', 2.0),
            ('passports', 'Passports', 5.0),
            ('parcels', 'Parcels', 3.0)
        ]
        
        for i, (key, label, defaultVal) in enumerate(serviceTypes):
            serviceTimeLayout.addWidget(QLabel(label + ":"), i, 0)
            spinBox = QDoubleSpinBox()
            spinBox.setRange(0.5, 30.0)
            spinBox.setValue(defaultVal)
            spinBox.setSuffix(" min")
            self.serviceTimeSpins[key] = spinBox
            serviceTimeLayout.addWidget(spinBox, i, 1)
        
        serviceTimeGroup.setLayout(serviceTimeLayout)
        controlLayout.addWidget(serviceTimeGroup)
        
        # Statistics display
        statsGroup = QGroupBox("Statistics")
        statsLayout = QVBoxLayout()
        statsLayout.setSpacing(8)  # Add spacing between labels
        
        self.simTimeLabel = QLabel("Simulation Time: 0.0 min")
        statsLayout.addWidget(self.simTimeLabel)
        
        self.totalCustomersLabel = QLabel("Total Customers: 0")
        statsLayout.addWidget(self.totalCustomersLabel)
        
        self.servedLabel = QLabel("Served: 0")
        statsLayout.addWidget(self.servedLabel)
        
        self.abandonedLabel = QLabel("Abandoned: 0")
        statsLayout.addWidget(self.abandonedLabel)
        
        self.avgWaitLabel = QLabel("Avg Wait: 0.0 min")
        statsLayout.addWidget(self.avgWaitLabel)
        
        statsGroup.setLayout(statsLayout)
        controlLayout.addWidget(statsGroup)
        
        # Micro:bit controls
        microbitGroup = QGroupBox("Micro:bit Connection")
        microbitLayout = QVBoxLayout()
        
        self.connectButton = QPushButton("Connect Micro:bit")
        self.connectButton.clicked.connect(self.connectMicrobit)
        microbitLayout.addWidget(self.connectButton)
        
        self.microbitStatusLabel = QLabel("Status: Not Connected")
        microbitLayout.addWidget(self.microbitStatusLabel)
        
        microbitGroup.setLayout(microbitLayout)
        controlLayout.addWidget(microbitGroup)
        
        # Manual customer buttons (for testing without Micro:bit)
        manualGroup = QGroupBox("Manual Customer Entry")
        manualLayout = QVBoxLayout()
        
        self.manualPostButton = QPushButton("Add Standard Post")
        self.manualPostButton.clicked.connect(lambda: self.addCustomer('standard_post'))
        manualLayout.addWidget(self.manualPostButton)
        
        self.manualPassportButton = QPushButton("Add Passport")
        self.manualPassportButton.clicked.connect(lambda: self.addCustomer('passports'))
        manualLayout.addWidget(self.manualPassportButton)
        
        self.manualParcelButton = QPushButton("Add Parcel")
        self.manualParcelButton.clicked.connect(lambda: self.addCustomer('parcels'))
        manualLayout.addWidget(self.manualParcelButton)
        
        manualGroup.setLayout(manualLayout)
        controlLayout.addWidget(manualGroup)
        
        controlLayout.addStretch()
        controlTab.setLayout(controlLayout)
        
        # Tab 2: Analytics
        analyticsTab = QWidget()
        analyticsLayout = QVBoxLayout()
        analyticsLayout.setSpacing(15)  # Add spacing
        
        # Analytics title
        analyticsTitle = QLabel("Current Run Analytics")
        analyticsTitle.setFont(QFont("Arial", 12, QFont.Bold))
        analyticsLayout.addWidget(analyticsTitle)
        
        # By Service Type section
        byServiceGroup = QGroupBox("Statistics by Service Type")
        byServiceLayout = QVBoxLayout()
        byServiceLayout.setSpacing(12)  # More spacing
        
        self.standardPostStatsLabel = QLabel("Standard Post:\n  Waiting: 0 | Avg Wait: 0.0 min")
        self.standardPostStatsLabel.setStyleSheet("padding: 5px;")
        byServiceLayout.addWidget(self.standardPostStatsLabel)
        
        self.passportsStatsLabel = QLabel("Passports:\n  Waiting: 0 | Avg Wait: 0.0 min")
        self.passportsStatsLabel.setStyleSheet("padding: 5px;")
        byServiceLayout.addWidget(self.passportsStatsLabel)
        
        self.parcelsStatsLabel = QLabel("Parcels:\n  Waiting: 0 | Avg Wait: 0.0 min")
        self.parcelsStatsLabel.setStyleSheet("padding: 5px;")
        byServiceLayout.addWidget(self.parcelsStatsLabel)
        
        byServiceGroup.setLayout(byServiceLayout)
        analyticsLayout.addWidget(byServiceGroup)
        
        # Server Utilization section
        utilizationGroup = QGroupBox("Server Utilization")
        utilizationLayout = QVBoxLayout()
        utilizationLayout.setSpacing(10)
        
        self.serverUtilLabel = QLabel("Busy Servers: 0 / 5 (0%)")
        self.serverUtilLabel.setStyleSheet("padding: 5px; font-size: 11pt;")
        utilizationLayout.addWidget(self.serverUtilLabel)
        
        self.boothUtilLabel = QLabel("Occupied Booths: 0 / 4 (0%)")
        self.boothUtilLabel.setStyleSheet("padding: 5px; font-size: 11pt;")
        utilizationLayout.addWidget(self.boothUtilLabel)
        
        utilizationGroup.setLayout(utilizationLayout)
        analyticsLayout.addWidget(utilizationGroup)
        
        # Performance Metrics section
        performanceGroup = QGroupBox("Performance Metrics")
        performanceLayout = QVBoxLayout()
        performanceLayout.setSpacing(10)
        
        self.throughputLabel = QLabel("Throughput: 0.0 customers/hour")
        self.throughputLabel.setStyleSheet("padding: 5px;")
        performanceLayout.addWidget(self.throughputLabel)
        
        self.abandonmentRateLabel = QLabel("Abandonment Rate: 0.0%")
        self.abandonmentRateLabel.setStyleSheet("padding: 5px;")
        performanceLayout.addWidget(self.abandonmentRateLabel)
        
        performanceGroup.setLayout(performanceLayout)
        analyticsLayout.addWidget(performanceGroup)
        
        # Database info
        dbGroup = QGroupBox("Database")
        dbLayout = QVBoxLayout()
        dbLayout.setSpacing(8)
        
        self.currentRunLabel = QLabel("Current Run ID: None")
        self.currentRunLabel.setStyleSheet("padding: 5px;")
        dbLayout.addWidget(self.currentRunLabel)
        
        self.dbLocationLabel = QLabel("Database: database/poQueueSim.db")
        self.dbLocationLabel.setStyleSheet("padding: 5px;")
        self.dbLocationLabel.setWordWrap(True)
        dbLayout.addWidget(self.dbLocationLabel)
        
        dbGroup.setLayout(dbLayout)
        analyticsLayout.addWidget(dbGroup)
        
        analyticsLayout.addStretch()
        analyticsTab.setLayout(analyticsLayout)
        
        # Add tabs
        tabWidget.addTab(controlTab, "Controls")
        tabWidget.addTab(analyticsTab, "Analytics")
        
        layout.addWidget(tabWidget)
        panel.setLayout(layout)
        return panel
    
    def initSimulator(self):
        """Initialize queue simulator"""
        self.simulator = QueueSimulator(
            numServers=5,
            numBooths=4,
            dispatchStrategy=DispatchStrategy.LONGEST_WAIT_FIRST,
            serviceTimes={
                'standard_post': 2.0,
                'passports': 5.0,
                'parcels': 3.0
            },
            timeAcceleration=20.0,
            abandonmentEnabled=True
        )
        
        # Initialize database
        self.database = DatabaseManager('database/poQueueSim.db')
    
    def initMicrobit(self):
        """Initialize Micro:bit communicator"""
        self.microbit = MicrobitCommunicator()
        self.microbit.setCallback(self.onMicrobitMessage)
    
    def setupTimer(self):
        """Setup update timer"""
        self.updateTimer = QTimer()
        self.updateTimer.timeout.connect(self.updateSimulation)
        self.updateTimer.start(50)  # Update every 50ms
    
    def startSimulation(self):
        """Start simulation"""
        # Update simulator configuration
        strategyMap = {
            0: DispatchStrategy.LONGEST_WAIT_FIRST,
            1: DispatchStrategy.SHORTEST_JOB_FIRST,
            2: DispatchStrategy.ROUND_ROBIN,
            3: DispatchStrategy.PRIORITY_ORDER
        }
        
        self.simulator.dispatchStrategy = strategyMap[self.strategyCombo.currentIndex()]
        self.simulator.timeAcceleration = self.timeAccelSpin.value()
        self.simulator.abandonmentEnabled = self.abandonmentCheck.isChecked()
        
        # Update service times
        for serviceType, spinBox in self.serviceTimeSpins.items():
            self.simulator.serviceTimes[serviceType] = spinBox.value()
        
        # Start database run
        self.currentRunId = self.database.startSimulationRun(
            self.simulator.dispatchStrategy.value,
            self.simulator.timeAcceleration,
            self.simulator.serviceTimes,
            self.simulator.abandonmentEnabled
        )
        
        self.simulator.running = True
        self.startButton.setEnabled(False)
        self.pauseButton.setEnabled(True)
        self.statusBar.showMessage("Simulation Running")
    
    def pauseSimulation(self):
        """Pause simulation"""
        self.simulator.running = False
        self.startButton.setEnabled(True)
        self.pauseButton.setEnabled(False)
        self.statusBar.showMessage("Simulation Paused")
    
    def resetSimulation(self):
        """Reset simulation"""
        if self.currentRunId:
            self.database.endSimulationRun(self.currentRunId)
        
        self.simulator.reset()
        self.updateDisplay()
        self.statusBar.showMessage("Simulation Reset")
    
    def updateSimulation(self):
        """Update simulation state"""
        if self.simulator.running:
            self.simulator.update()
            self.updateDisplay()
    
    def updateDisplay(self):
        """Update all display elements"""
        # Update queue visualizations
        queueLengths = self.simulator.getQueueLengths()
        for serviceType, viz in self.queueVisualizations.items():
            viz.updateQueue(queueLengths[serviceType])
        
        # Update booth displays
        serverStates = self.simulator.getServerStates()
        boothStates = self.simulator.getBoothStates()
        
        for booth in boothStates:
            boothId = booth['boothId']
            if booth['occupied']:
                # Find server at this booth
                serverAtBooth = next((s for s in serverStates if s['boothId'] == boothId), None)
                if serverAtBooth:
                    self.boothDisplays[boothId].updateStatus(
                        True,
                        serverAtBooth['serverId'],
                        serverAtBooth['serviceType'],
                        serverAtBooth['timeRemaining']
                    )
            else:
                self.boothDisplays[boothId].updateStatus(False, None, None, 0)
        
        # Update server displays
        for serverState in serverStates:
            serverId = serverState['serverId']
            self.serverDisplays[serverId].updateStatus(
                serverState['state'],
                serverState['boothId'],
                serverState['serviceType']
            )
        
        # Update statistics
        stats = self.simulator.getStatistics()
        self.simTimeLabel.setText(f"Simulation Time: {stats['simulationTime']:.1f} min")
        self.totalCustomersLabel.setText(f"Total Customers: {stats['totalCustomers']}")
        self.servedLabel.setText(f"Served: {stats['totalServed']}")
        self.abandonedLabel.setText(f"Abandoned: {stats['totalAbandoned']}")
        self.avgWaitLabel.setText(f"Avg Wait: {stats['avgWaitTime']:.1f} min")
        
        # Update analytics tab
        self.updateAnalytics(queueLengths, serverStates, boothStates, stats)
    
    def updateAnalytics(self, queueLengths, serverStates, boothStates, stats):
        """Update analytics tab with current statistics"""
        # Calculate per-service statistics
        serviceStats = {
            'standard_post': {'waiting': queueLengths['standard_post'], 'avgWait': 0, 'served': 0},
            'passports': {'waiting': queueLengths['passports'], 'avgWait': 0, 'served': 0},
            'parcels': {'waiting': queueLengths['parcels'], 'avgWait': 0, 'served': 0}
        }
        
        # Calculate average wait times per service type
        for customer in self.simulator.completedCustomers:
            if customer.serviceType in serviceStats:
                waitDuration = customer.getWaitDuration() or 0
                serviceStats[customer.serviceType]['served'] += 1
                serviceStats[customer.serviceType]['avgWait'] += waitDuration
        
        for serviceType in serviceStats:
            if serviceStats[serviceType]['served'] > 0:
                serviceStats[serviceType]['avgWait'] /= serviceStats[serviceType]['served']
        
        # Update service type labels
        self.standardPostStatsLabel.setText(
            f"Standard Post:\n"
            f"  Waiting: {serviceStats['standard_post']['waiting']} | "
            f"Served: {serviceStats['standard_post']['served']} | "
            f"Avg Wait: {serviceStats['standard_post']['avgWait']:.1f} min"
        )
        
        self.passportsStatsLabel.setText(
            f"Passports:\n"
            f"  Waiting: {serviceStats['passports']['waiting']} | "
            f"Served: {serviceStats['passports']['served']} | "
            f"Avg Wait: {serviceStats['passports']['avgWait']:.1f} min"
        )
        
        self.parcelsStatsLabel.setText(
            f"Parcels:\n"
            f"  Waiting: {serviceStats['parcels']['waiting']} | "
            f"Served: {serviceStats['parcels']['served']} | "
            f"Avg Wait: {serviceStats['parcels']['avgWait']:.1f} min"
        )
        
        # Calculate server utilization
        busyServers = sum(1 for s in serverStates if s['state'] == 'busy')
        serverUtilPercent = (busyServers / len(serverStates)) * 100
        self.serverUtilLabel.setText(f"Busy Servers: {busyServers} / {len(serverStates)} ({serverUtilPercent:.0f}%)")
        
        # Calculate booth utilization
        occupiedBooths = sum(1 for b in boothStates if b['occupied'])
        boothUtilPercent = (occupiedBooths / len(boothStates)) * 100
        self.boothUtilLabel.setText(f"Occupied Booths: {occupiedBooths} / {len(boothStates)} ({boothUtilPercent:.0f}%)")
        
        # Calculate throughput (customers per hour)
        simTimeHours = stats['simulationTime'] / 60.0
        throughput = stats['totalServed'] / simTimeHours if simTimeHours > 0 else 0
        self.throughputLabel.setText(f"Throughput: {throughput:.1f} customers/hour")
        
        # Calculate abandonment rate
        abandonmentRate = 0
        if stats['totalCustomers'] > 0:
            abandonmentRate = (stats['totalAbandoned'] / stats['totalCustomers']) * 100
        self.abandonmentRateLabel.setText(f"Abandonment Rate: {abandonmentRate:.1f}%")
        
        # Update run ID
        if self.currentRunId:
            self.currentRunLabel.setText(f"Current Run ID: {self.currentRunId}")
    
    def addCustomer(self, serviceType):
        """Add a customer to the queue"""
        if self.simulator:
            customer = self.simulator.addCustomer(serviceType)
            if customer:
                self.statusBar.showMessage(f"Customer added to {serviceType.replace('_', ' ').title()} queue", 2000)
    
    def connectMicrobit(self):
        """Connect to Micro:bit"""
        if self.microbit.isConnected():
            self.microbit.disconnect()
            self.connectButton.setText("Connect Micro:bit")
            self.microbitStatusLabel.setText("Status: Not Connected")
        else:
            if self.microbit.connect():
                self.microbit.startListening()
                self.connectButton.setText("Disconnect Micro:bit")
                self.microbitStatusLabel.setText("Status: Connected")
            else:
                self.microbitStatusLabel.setText("Status: Connection Failed")
    
    def onMicrobitMessage(self, serviceType, timestamp):
        """Handle message from Micro:bit - runs in serial thread, emit signal for GUI thread"""
        # Emit signal to GUI thread instead of directly calling addCustomer
        self.signals.customerAdded.emit(serviceType)
    
    def closeEvent(self, event):
        """Handle window close event"""
        if self.microbit:
            self.microbit.disconnect()
        if self.database:
            if self.currentRunId:
                self.database.endSimulationRun(self.currentRunId)
            self.database.close()
        event.accept()


def main():
    """Main entry point"""
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
