# Post Office Queue Simulator (poQueueSim)

A combined embedded systems and computer modeling project simulating a post office queue system with real-time visualization.

## Project Overview

This project simulates a post office offering three services:
- **Standard Post** (Button A on Micro:bit)
- **Passports** (Button B on Micro:bit)  
- **Parcels** (Both buttons A+B simultaneously)

### Key Features

- **5 servers, 4 booths** - Realistic constraint modeling
- **Multiple dispatch strategies** - Compare different queue management approaches
- **Time acceleration** - Run simulations faster than real-time (default 20x)
- **Customer abandonment** - Realistic queue behavior when waits are too long
- **Real-time visualization** - PyQt5 interface showing queues, booths, and servers
- **SQLite logging** - Complete event tracking for analytics
- **Micro:bit integration** - Physical button inputs via USB serial

## System Architecture

```
┌─────────────┐     USB Serial      ┌──────────────────┐
│  Micro:bit  │ ──────────────────> │  Python System   │
│  (Buttons)  │                     │                  │
└─────────────┘                     │  ┌────────────┐  │
                                    │  │ Queue Sim  │  │
                                    │  └────────────┘  │
                                    │  ┌────────────┐  │
                                    │  │ PyQt GUI   │  │
                                    │  └────────────┘  │
                                    │  ┌────────────┐  │
                                    │  │  SQLite DB │  │
                                    │  └────────────┘  │
                                    └──────────────────┘
```

## Project Structure

```
poQueueSim/
├── microbit/
│   └── main.py              # Micro:bit MicroPython code
├── src/
│   ├── queueSimulator.py    # Core queue simulation engine
│   ├── microbitComms.py     # Serial communication handler
│   ├── database.py          # SQLite database management
│   └── mainGui.py           # PyQt5 GUI application
├── database/
│   └── poQueueSim.db        # SQLite database (created on first run)
├── assets/                  # Future: icons, images
├── requirements.txt         # Python dependencies
└── README.md               # This file
```

## Installation

### Prerequisites

- Python 3.8 or higher
- Micro:bit (BBC micro:bit V1 or V2)
- USB cable for Micro:bit connection

### Python Dependencies

Install required packages:

```bash
pip install -r requirements.txt
```

Or install manually:

```bash
pip install pyqt5 pyserial
```

### Micro:bit Setup

1. Connect your Micro:bit to your computer via USB
2. Open the Mu Editor or use the online Python editor
3. Copy the contents of `microbit/main.py` to your Micro:bit
4. Flash the code to the Micro:bit
5. The Micro:bit will show a heart icon when ready

## Usage

### Running the Simulator

1. **Start the application:**
   ```bash
   cd poQueueSim/src
   python mainGui.py
   ```

2. **Configure the simulation:**
   - Choose dispatch strategy (Longest Wait First, Shortest Job First, etc.)
   - Set time acceleration (1x to 100x real-time)
   - Configure service times for each service type
   - Enable/disable customer abandonment

3. **Connect Micro:bit (optional):**
   - Click "Connect Micro:bit" button
   - The system will auto-detect the Micro:bit
   - Status will show "Connected" when successful

4. **Start simulation:**
   - Click "Start Simulation"
   - Press buttons on Micro:bit to add customers
   - Or use manual buttons in GUI for testing

5. **Monitor the simulation:**
   - Watch queues grow and shrink in real-time
   - See booth occupancy and service progress
   - Track server assignments
   - View live statistics

### Button Mapping

- **Button A**: Standard Post customer
- **Button B**: Passport customer  
- **A + B together**: Parcel customer

## Dispatch Strategies

The simulator supports four different queue management strategies:

### 1. Longest Wait First
Serves the customer who has waited longest across all queues. Optimizes for fairness.

### 2. Shortest Job First
Serves customers with the shortest expected service time first. Optimizes for throughput.

### 3. Round Robin
Cycles through service types in order: Standard Post → Passports → Parcels. Ensures all services get attention.

### 4. Priority Order
Fixed priority: Passports > Parcels > Standard Post. Useful when some services are more urgent.

## Configuration Options

### Time Acceleration
- Range: 1x to 100x
- Default: 20x
- Example: At 20x speed, a 5-minute service takes 15 real seconds

### Service Times
- **Standard Post**: Default 2 minutes (configurable)
- **Passports**: Default 5 minutes (configurable)
- **Parcels**: Default 3 minutes (configurable)
- All times have ±20% random variation for realism

### Customer Abandonment
When enabled:
- Wait < 5 minutes: 0% abandon rate
- Wait 5-10 minutes: 5% per minute
- Wait > 10 minutes: 15% per minute

## Database Schema

The simulator logs all events to SQLite for post-analysis:

### Tables

**simulationRuns**
- Tracks each simulation run with configuration parameters

**customers**
- Complete customer journey: arrival, wait time, service time, outcome

**serverEvents**
- All server state changes: start service, end service, idle

**queueSnapshots**
- Periodic snapshots of queue lengths for trend analysis

## Analytics

After running simulations, you can analyze the data:

```python
from database import DatabaseManager

db = DatabaseManager('database/poQueueSim.db')
stats = db.getRunStatistics(runId=1)
print(stats)
```

Example queries:
- Average wait time by service type
- Server utilization rates
- Peak queue lengths
- Abandonment rates vs. dispatch strategy

## Troubleshooting

### Micro:bit not detected
1. Check USB connection
2. Ensure Micro:bit firmware is up to date
3. Try clicking "Connect Micro:bit" multiple times
4. Check available serial ports in Device Manager (Windows) or `ls /dev/tty*` (Linux/Mac)

### Serial communication errors
1. Close other programs using the Micro:bit
2. Disconnect and reconnect the Micro:bit
3. Restart the application

### No customers being added
1. Verify simulation is started (click "Start Simulation")
2. Check Micro:bit connection status
3. Use manual buttons to test without Micro:bit

## Development Notes

### Naming Conventions
- Uses camelCase for all Python variables and functions
- Class names use PascalCase
- Database columns use camelCase

### Future Enhancements
- Add 4th service (Social Welfare) when breakout board available
- Export analytics to CSV/Excel
- Graphical charts of queue performance over time
- Server break times and shift scheduling
- Multiple simulation runs with automated comparison
- Machine learning to optimize dispatch strategies

## License

Educational project - free to use and modify.

## Authors

Created for embedded systems and computer modeling coursework.
