# Quick Start Guide - Post Office Queue Simulator

## 1. Setup (First Time Only)

### Install Python Dependencies
```bash
cd poQueueSim
pip install -r requirements.txt
```

### Flash Micro:bit (Optional)
1. Connect Micro:bit via USB
2. Open Mu Editor or online Python editor
3. Copy code from `microbit/main.py`
4. Flash to Micro:bit
5. Wait for heart icon to appear

## 2. Run the Simulator

### Option A: With GUI (Recommended)
```bash
cd src
python mainGui.py
```

### Option B: Test Without GUI
```bash
cd src
python testSimulator.py
```

## 3. Quick Test (Without Micro:bit)

1. Launch `python mainGui.py`
2. Click "Start Simulation"
3. Use the "Manual Customer Entry" buttons:
   - Click "Add Standard Post" 
   - Click "Add Passport"
   - Click "Add Parcel"
4. Watch the queues and booths update in real-time!

## 4. Using Micro:bit

1. In the GUI, click "Connect Micro:bit"
2. Wait for "Status: Connected"
3. Press buttons on Micro:bit:
   - **Button A** = Standard Post customer
   - **Button B** = Passport customer
   - **Both A+B** = Parcel customer

## 5. Experiment with Strategies

Try different dispatch strategies:
- **Longest Wait First** - Most fair
- **Shortest Job First** - Best throughput
- **Round Robin** - Balanced service
- **Priority Order** - Passports served first

Change the dropdown and click "Reset" then "Start Simulation" again.

## 6. Adjust Speed

- Increase "Time Acceleration" to 100x for very fast simulation
- Decrease to 5x for slower, easier to watch
- Default 20x is good balance

## 7. View Results

After running for a while:
- Check "Statistics" panel for metrics
- Database file saved in `database/poQueueSim.db`
- Open with SQLite browser to analyze data

## Common Issues

**"Module not found" error**: Run `pip install -r requirements.txt`

**Micro:bit not connecting**: Try unplugging and reconnecting, then click Connect button again

**Nothing happening**: Make sure to click "Start Simulation" button!

## Next Steps

- Run for 5-10 minutes with different strategies
- Compare average wait times
- Try enabling/disabling abandonment
- Experiment with different service time configurations
