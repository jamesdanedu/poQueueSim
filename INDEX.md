# Post Office Queue Simulator - File Index

## 📁 Project Structure

```
poQueueSim/
├── 📄 README.md                    ← Start here: Full project documentation
├── 📄 QUICKSTART.md                ← Quick setup guide (5 minutes)
├── 📄 PROJECT_SUMMARY.md           ← What's included and how it works
├── 📄 ARCHITECTURE.md              ← System design and data flow
├── 📄 STRATEGY_GUIDE.md            ← Compare dispatch strategies
├── 📄 requirements.txt             ← Python dependencies
│
├── 📁 microbit/
│   └── main.py                     ← Flash this to your Micro:bit
│
└── 📁 src/
    ├── mainGui.py                  ← Run this: Main PyQt5 application
    ├── queueSimulator.py           ← Core simulation engine
    ├── microbitComms.py            ← Serial communication with Micro:bit
    ├── database.py                 ← SQLite database management
    └── testSimulator.py            ← Test without GUI
```

## 🚀 Getting Started (3 Steps)

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the simulator:**
   ```bash
   cd src
   python mainGui.py
   ```

3. **Start testing:**
   - Click "Start Simulation"
   - Use "Manual Customer Entry" buttons
   - Watch the magic happen! ✨

## 📖 Documentation Guide

### For Quick Start
→ Read **QUICKSTART.md** (2 minutes)

### For Understanding the Project
→ Read **PROJECT_SUMMARY.md** (5 minutes)

### For System Design
→ Read **ARCHITECTURE.md** (10 minutes)

### For Experiment Ideas
→ Read **STRATEGY_GUIDE.md** (10 minutes)

### For Complete Details
→ Read **README.md** (15 minutes)

## 🎯 Key Features

✅ **3 service queues** with realistic timing
✅ **5 servers managing 4 booths** (capacity constraint)
✅ **4 dispatch strategies** to compare
✅ **Time acceleration** (up to 100x speed)
✅ **Real-time PyQt5 visualization**
✅ **SQLite database logging**
✅ **Micro:bit hardware integration**
✅ **Customer abandonment modeling**

## 🔬 What to Test

1. **Compare strategies:**
   - Which gives lowest wait times?
   - Which is most fair?
   - Which handles peak loads best?

2. **Vary parameters:**
   - Change service times
   - Adjust time acceleration
   - Enable/disable abandonment

3. **Analyze data:**
   - Query the SQLite database
   - Calculate server utilization
   - Find bottlenecks

## 📊 Project Stats

- **Lines of Code:** ~1,500+
- **Python Modules:** 4 core + 1 test
- **Documentation Files:** 5
- **Total Files:** 12
- **Archive Size:** 35 KB

## 🛠️ Technologies Used

- **Python 3.8+** - Main language
- **PyQt5** - GUI framework
- **SQLite3** - Database
- **PySerial** - Micro:bit communication
- **MicroPython** - Micro:bit firmware

## 💡 Tips

- **Test without Micro:bit first** - Use manual buttons
- **Start with 20x acceleration** - Good balance
- **Run for 5-10 sim minutes** - Collect meaningful data
- **Try all 4 strategies** - Compare results
- **Check the database** - Rich analytics available

## 🐛 Troubleshooting

**Problem:** GUI won't start
**Solution:** Install PyQt5: `pip install PyQt5`

**Problem:** Micro:bit not detected
**Solution:** Check USB connection, try clicking Connect button twice

**Problem:** No customers appearing
**Solution:** Make sure to click "Start Simulation" button first!

## 📞 Need Help?

1. Check QUICKSTART.md for common setup issues
2. Read ARCHITECTURE.md to understand the system
3. Run testSimulator.py to verify core functionality

## 🎓 Learning Outcomes

This project demonstrates:
- **Embedded systems integration** (Micro:bit)
- **Queue theory and simulation** (Operations research)
- **Event-driven programming** (PyQt)
- **Database design** (SQLite)
- **Real-time visualization** (Graphics)
- **Comparative analysis** (Dispatch strategies)

## 🎉 You're Ready!

Everything is set up and tested. Just run `python mainGui.py` and start experimenting!

---

**Created:** November 2025
**Version:** 1.0
**License:** Educational use
