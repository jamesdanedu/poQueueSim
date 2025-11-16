# System Architecture - Post Office Queue Simulator

## Component Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                        HARDWARE LAYER                                │
│                                                                       │
│  ┌───────────────────────────────────────────────────────┐          │
│  │              BBC Micro:bit V1/V2                      │          │
│  │                                                       │          │
│  │   [Button A]  [Button B]                            │          │
│  │   Standard      Passports                           │          │
│  │       Post                                          │          │
│  │                                                     │          │
│  │   [A+B Together] = Parcels                        │          │
│  │                                                   │          │
│  │   USB Serial: 115200 baud                       │          │
│  └──────────────────┬──────────────────────────────┘          │
│                     │                                          │
└─────────────────────┼──────────────────────────────────────────┘
                      │
                      │ Serial Messages
                      │ "SERVICE_REQUEST,type,timestamp"
                      ▼
┌─────────────────────────────────────────────────────────────────────┐
│                   COMMUNICATION LAYER                                │
│                                                                       │
│  ┌──────────────────────────────────────────────────────┐           │
│  │         microbitComms.py                             │           │
│  │  - Auto-detect Micro:bit port                        │           │
│  │  - Background listener thread                        │           │
│  │  - Parse incoming messages                           │           │
│  │  - Callback to simulation                            │           │
│  └──────────────────┬───────────────────────────────────┘           │
│                     │                                                │
└─────────────────────┼────────────────────────────────────────────────┘
                      │
                      │ serviceType, timestamp
                      ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    SIMULATION LAYER                                  │
│                                                                       │
│  ┌──────────────────────────────────────────────────────┐           │
│  │         queueSimulator.py                            │           │
│  │                                                      │           │
│  │  ┌────────────────┐  ┌────────────────┐            │           │
│  │  │  5 Servers     │  │   4 Booths     │            │           │
│  │  │  (Staff)       │  │  (Positions)   │            │           │
│  │  └────────────────┘  └────────────────┘            │           │
│  │                                                     │           │
│  │  ┌──────────────────────────────────────┐         │           │
│  │  │    3 Service Queues (deque)         │         │           │
│  │  │  - Standard Post                    │         │           │
│  │  │  - Passports                        │         │           │
│  │  │  - Parcels                          │         │           │
│  │  └──────────────────────────────────────┘         │           │
│  │                                                    │           │
│  │  ┌──────────────────────────────────────┐         │           │
│  │  │    Dispatch Strategies               │         │           │
│  │  │  1. Longest Wait First               │         │           │
│  │  │  2. Shortest Job First               │         │           │
│  │  │  3. Round Robin                      │         │           │
│  │  │  4. Priority Order                   │         │           │
│  │  └──────────────────────────────────────┘         │           │
│  │                                                    │           │
│  │  Time Acceleration: 1x to 100x                    │           │
│  │  Abandonment: Probability-based                   │           │
│  └──────────────────┬─────────────────────────────────┘           │
│                     │                                              │
└─────────────────────┼──────────────────────────────────────────────┘
                      │
                      │ Queue states, Statistics
                      ▼
┌─────────────────────────────────────────────────────────────────────┐
│                   PERSISTENCE LAYER                                  │
│                                                                       │
│  ┌──────────────────────────────────────────────────────┐           │
│  │         database.py + SQLite                         │           │
│  │                                                      │           │
│  │  Tables:                                            │           │
│  │  ┌──────────────────────────────────┐              │           │
│  │  │  simulationRuns                  │              │           │
│  │  │  - Configuration parameters      │              │           │
│  │  │  - Start/end times               │              │           │
│  │  └──────────────────────────────────┘              │           │
│  │                                                     │           │
│  │  ┌──────────────────────────────────┐              │           │
│  │  │  customers                       │              │           │
│  │  │  - Complete journey tracking     │              │           │
│  │  │  - Wait/service durations        │              │           │
│  │  │  - Outcomes (completed/abandoned)│              │           │
│  │  └──────────────────────────────────┘              │           │
│  │                                                     │           │
│  │  ┌──────────────────────────────────┐              │           │
│  │  │  serverEvents                    │              │           │
│  │  │  - All state changes             │              │           │
│  │  └──────────────────────────────────┘              │           │
│  │                                                     │           │
│  │  ┌──────────────────────────────────┐              │           │
│  │  │  queueSnapshots                  │              │           │
│  │  │  - Periodic queue length logs    │              │           │
│  │  └──────────────────────────────────┘              │           │
│  └──────────────────────────────────────────────────────┘           │
│                                                                       │
└───────────────────────────────────────────────────────────────────────┘
                      ▲
                      │ Read states
                      │
┌─────────────────────────────────────────────────────────────────────┐
│                  PRESENTATION LAYER                                  │
│                                                                       │
│  ┌──────────────────────────────────────────────────────┐           │
│  │         mainGui.py (PyQt5)                           │           │
│  │                                                      │           │
│  │  ┌────────────────────────────────────────┐         │           │
│  │  │  Queue Visualizations (3 panels)      │         │           │
│  │  │  - Color-coded by length              │         │           │
│  │  │  - Real-time updates                  │         │           │
│  │  └────────────────────────────────────────┘         │           │
│  │                                                     │           │
│  │  ┌────────────────────────────────────────┐         │           │
│  │  │  Booth Display (4 booths)             │         │           │
│  │  │  - Occupancy status                   │         │           │
│  │  │  - Service type & time remaining      │         │           │
│  │  └────────────────────────────────────────┘         │           │
│  │                                                     │           │
│  │  ┌────────────────────────────────────────┐         │           │
│  │  │  Server Status (5 servers)            │         │           │
│  │  │  - Busy/Spare indicator               │         │           │
│  │  │  - Current assignment                 │         │           │
│  │  └────────────────────────────────────────┘         │           │
│  │                                                     │           │
│  │  ┌────────────────────────────────────────┐         │           │
│  │  │  Configuration Panel                  │         │           │
│  │  │  - Dispatch strategy selector         │         │           │
│  │  │  - Time acceleration                  │         │           │
│  │  │  - Service time settings              │         │           │
│  │  │  - Abandonment toggle                 │         │           │
│  │  └────────────────────────────────────────┘         │           │
│  │                                                     │           │
│  │  ┌────────────────────────────────────────┐         │           │
│  │  │  Statistics Display                   │         │           │
│  │  │  - Total customers                    │         │           │
│  │  │  - Served/Abandoned counts            │         │           │
│  │  │  - Average wait time                  │         │           │
│  │  │  - Simulation time                    │         │           │
│  │  └────────────────────────────────────────┘         │           │
│  │                                                     │           │
│  │  ┌────────────────────────────────────────┐         │           │
│  │  │  Control Buttons                      │         │           │
│  │  │  - Start/Pause/Reset                  │         │           │
│  │  │  - Connect Micro:bit                  │         │           │
│  │  │  - Manual customer entry              │         │           │
│  │  └────────────────────────────────────────┘         │           │
│  └──────────────────────────────────────────────────────┘           │
│                                                                       │
│  Update Timer: 50ms (20 FPS)                                         │
└───────────────────────────────────────────────────────────────────────┘
```

## Data Flow

### Customer Addition Flow
```
Micro:bit Button Press
    │
    ├─→ Serial Message: "SERVICE_REQUEST,type,timestamp"
    │
    ├─→ microbitComms receives & parses
    │
    ├─→ Callback to GUI
    │
    ├─→ GUI calls simulator.addCustomer(serviceType)
    │
    └─→ Customer object created and added to appropriate queue
```

### Simulation Update Flow (Every 50ms)
```
QTimer triggers update()
    │
    ├─→ Calculate elapsed simulation time
    │   (realDelta * timeAcceleration / 60)
    │
    ├─→ Check for completed services
    │   └─→ Move customer from booth, mark as completed
    │
    ├─→ Check for abandonments
    │   └─→ Remove customers based on wait time probability
    │
    ├─→ Assign servers to customers
    │   ├─→ Find available servers
    │   ├─→ Find available booths
    │   ├─→ Select next customer (via dispatch strategy)
    │   └─→ Assign server to booth with customer
    │
    └─→ Update GUI displays
        ├─→ Queue visualizations
        ├─→ Booth status
        ├─→ Server status
        └─→ Statistics
```

## Key Design Decisions

### 1. Server-Booth Separation
- **5 servers** (staff members) compete for **4 booths** (physical positions)
- Allows realistic modeling: one server always "spare" or on break
- Creates natural inefficiency found in real systems

### 2. Time Acceleration
- Real-time too slow for meaningful analysis
- Accelerated time (default 20x) allows quick experimentation
- Configurable from 1x to 100x

### 3. Dispatch Strategies
- Pluggable design: easy to add new strategies
- Each strategy implements customer selection logic
- Allows direct comparison of different approaches

### 4. Abandonment Modeling
- Probability increases with wait time
- More realistic than customers waiting forever
- Configurable: can disable for deterministic testing

### 5. Database Logging
- Every event captured for post-analysis
- Separate tables for different entity types
- Enables complex queries and visualizations later

## Threading Model

```
Main Thread (GUI)
    │
    ├─→ QTimer (50ms) → Update simulation
    │
    └─→ Event handlers (button clicks, etc.)

Background Thread (Serial Listener)
    │
    └─→ Continuously read from Micro:bit serial port
        └─→ Emit signals to main thread (thread-safe)
```

## Extension Points

### Adding 4th Service (Social Welfare)
1. Add button to Micro:bit code
2. Add 'social_welfare' to serviceTypes list
3. Add queue visualization widget
4. Add to dispatch strategy logic
5. Update database schema (already supports any service type)

### Adding New Dispatch Strategy
1. Add enum value to DispatchStrategy
2. Implement selection method in QueueSimulator
3. Add to strategy combo box in GUI

### Adding Analytics Dashboard
1. Query database.py for historical runs
2. Create new PyQt widget with matplotlib
3. Display charts: wait time trends, strategy comparison, etc.
