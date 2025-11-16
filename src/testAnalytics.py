"""
Test Script for Analytics Dashboard
Creates sample data and demonstrates the analytics system
Run this to see how the analytics dashboard works!
"""

import sqlite3
import random
from datetime import datetime, timedelta
import sys
from PyQt5.QtWidgets import QApplication

def create_sample_database(db_path='queue_analysis.db'):
    """Create a sample database with test data"""
    
    print("📊 Creating sample database...")
    
    # Connect to database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Drop existing tables
    cursor.execute('DROP TABLE IF EXISTS events')
    cursor.execute('DROP TABLE IF EXISTS simulation_runs')
    cursor.execute('DROP TABLE IF EXISTS results')
    
    # Create tables
    cursor.execute('''
    CREATE TABLE events (
        event_id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp REAL NOT NULL,
        event_type TEXT NOT NULL,
        customer_id INTEGER,
        server_id INTEGER,
        queue_length INTEGER,
        light_level INTEGER,
        temperature REAL,
        recorded_date TEXT
    )
    ''')
    
    cursor.execute('''
    CREATE TABLE simulation_runs (
        run_id INTEGER PRIMARY KEY AUTOINCREMENT,
        run_timestamp TEXT NOT NULL,
        num_servers INTEGER NOT NULL,
        dispatch_strategy TEXT NOT NULL,
        avg_service_time REAL,
        arrival_rate REAL,
        simulation_duration INTEGER,
        priority_enabled BOOLEAN
    )
    ''')
    
    cursor.execute('''
    CREATE TABLE results (
        result_id INTEGER PRIMARY KEY AUTOINCREMENT,
        run_id INTEGER,
        avg_wait_time REAL,
        max_wait_time REAL,
        percentile_95_wait REAL,
        avg_queue_length REAL,
        max_queue_length INTEGER,
        server_utilization REAL,
        abandonment_rate REAL,
        customers_served INTEGER,
        FOREIGN KEY (run_id) REFERENCES simulation_runs(run_id)
    )
    ''')
    
    print("✓ Tables created")
    
    # Generate sample events (30 days of data)
    print("📝 Generating sample events...")
    
    customer_id = 1
    start_date = datetime.now() - timedelta(days=30)
    
    for day in range(30):
        current_date = start_date + timedelta(days=day)
        
        # Simulate 50-150 customers per day
        num_customers = random.randint(50, 150)
        
        for _ in range(num_customers):
            # Random time during business hours (9 AM - 5 PM)
            hour = random.randint(9, 16)
            minute = random.randint(0, 59)
            second = random.randint(0, 59)
            
            event_time = current_date.replace(hour=hour, minute=minute, second=second)
            timestamp = event_time.timestamp()
            
            # Environmental factors
            light_level = random.randint(100, 200) if 10 <= hour <= 15 else random.randint(50, 100)
            temperature = random.uniform(19, 25)
            queue_length = max(0, random.randint(-2, 8))
            
            # Arrival event
            cursor.execute('''
                INSERT INTO events (timestamp, event_type, customer_id, queue_length, 
                                  light_level, temperature, recorded_date)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (timestamp, 'arrival', customer_id, queue_length, light_level, 
                  temperature, event_time.strftime('%Y-%m-%d')))
            
            # Service start event (after 2-10 minutes)
            wait_time = random.uniform(2, 10) * 60  # seconds
            service_start_time = timestamp + wait_time
            cursor.execute('''
                INSERT INTO events (timestamp, event_type, customer_id, server_id, 
                                  queue_length, light_level, temperature, recorded_date)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (service_start_time, 'service_start', customer_id, random.randint(1, 3),
                  max(0, queue_length - 1), light_level, temperature, 
                  event_time.strftime('%Y-%m-%d')))
            
            # Service complete event (after 3-7 minutes of service)
            service_duration = random.uniform(3, 7) * 60  # seconds
            service_complete_time = service_start_time + service_duration
            cursor.execute('''
                INSERT INTO events (timestamp, event_type, customer_id, server_id,
                                  queue_length, light_level, temperature, recorded_date)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (service_complete_time, 'service_complete', customer_id, 
                  random.randint(1, 3), max(0, queue_length - 2), light_level, 
                  temperature, event_time.strftime('%Y-%m-%d')))
            
            customer_id += 1
    
    print(f"✓ Generated {customer_id - 1} customer events")
    
    # Generate simulation runs
    print("🎯 Generating simulation results...")
    
    strategies = ['FIFO', 'LongestWait', 'Priority', 'RoundRobin']
    
    for strategy in strategies:
        for num_servers in range(2, 6):  # 2-5 servers
            for _ in range(5):  # 5 runs per configuration
                
                # Insert simulation run
                cursor.execute('''
                    INSERT INTO simulation_runs 
                    (run_timestamp, num_servers, dispatch_strategy, avg_service_time,
                     arrival_rate, simulation_duration, priority_enabled)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (datetime.now().isoformat(), num_servers, strategy, 
                      random.uniform(4, 6), random.uniform(1.5, 2.5), 480, 
                      strategy == 'Priority'))
                
                run_id = cursor.lastrowid
                
                # Generate results for this run
                # LongestWait performs best, FIFO worst
                base_wait = 6.0 if strategy == 'FIFO' else 4.8 if strategy == 'LongestWait' else 5.5
                base_wait = base_wait - (num_servers - 2) * 0.8  # More servers = less wait
                
                avg_wait = base_wait + random.uniform(-0.5, 0.5)
                max_wait = avg_wait * random.uniform(2.0, 2.5)
                p95_wait = avg_wait * random.uniform(1.5, 1.8)
                
                utilization = min(0.95, 0.50 + (5 - num_servers) * 0.10 + random.uniform(0, 0.10))
                abandonment = max(0, (avg_wait - 5) * 0.005 + random.uniform(0, 0.02))
                
                cursor.execute('''
                    INSERT INTO results
                    (run_id, avg_wait_time, max_wait_time, percentile_95_wait,
                     avg_queue_length, max_queue_length, server_utilization,
                     abandonment_rate, customers_served)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (run_id, avg_wait, max_wait, p95_wait,
                      avg_wait * 0.5, int(avg_wait * 1.5), utilization,
                      abandonment, random.randint(450, 550)))
    
    print(f"✓ Generated {len(strategies) * 4 * 5} simulation results")
    
    # Commit and close
    conn.commit()
    conn.close()
    
    print(f"\n✅ Sample database created: {db_path}")
    print(f"📈 Total events: {customer_id * 3}")
    print(f"🎯 Total simulations: {len(strategies) * 4 * 5}")
    print("\nYou can now test the analytics dashboard!")


def test_analytics_console():
    """Test analytics in console mode"""
    from analytics_dashboard import QueueAnalyticsDashboard
    
    print("\n" + "="*60)
    print("TESTING ANALYTICS DASHBOARD - CONSOLE MODE")
    print("="*60 + "\n")
    
    # Create dashboard
    dashboard = QueueAnalyticsDashboard('queue_analysis.db')
    
    # Print KPIs
    dashboard.print_kpi_summary()
    
    # Export all analytics
    print("📊 Exporting analytics to HTML files...")
    dashboard.export_all_analytics('test_analytics_output')
    
    # Get some data
    print("\n📈 Performance Trends (Last 7 days):")
    df = dashboard.get_performance_trends(7)
    print(df.to_string())
    
    print("\n⚖️ Strategy Comparison:")
    df = dashboard.get_strategy_comparison()
    print(df.to_string())
    
    # Close
    dashboard.close()
    
    print("\n✅ Console test complete!")
    print("📁 Check 'test_analytics_output/' folder for HTML reports")


def test_analytics_gui():
    """Test analytics in GUI mode"""
    from analytics_ui import AnalyticsWindow
    
    print("\n" + "="*60)
    print("TESTING ANALYTICS DASHBOARD - GUI MODE")
    print("="*60 + "\n")
    print("Opening analytics window...")
    print("Close the window when done testing.\n")
    
    app = QApplication(sys.argv)
    window = AnalyticsWindow('queue_analysis.db')
    window.show()
    sys.exit(app.exec_())


def main():
    """Main test function"""
    print("\n" + "="*70)
    print(" "*20 + "ANALYTICS DASHBOARD TEST")
    print("="*70 + "\n")
    
    print("This script will:")
    print("1. Create a sample database with test data")
    print("2. Test the analytics in console mode")
    print("3. Open the analytics GUI window")
    print("\n" + "-"*70 + "\n")
    
    # Step 1: Create sample database
    create_sample_database()
    
    print("\n" + "-"*70 + "\n")
    input("Press ENTER to test analytics in console mode...")
    
    # Step 2: Test console
    test_analytics_console()
    
    print("\n" + "-"*70 + "\n")
    input("Press ENTER to open analytics GUI window...")
    
    # Step 3: Test GUI
    test_analytics_gui()


if __name__ == '__main__':
    main()