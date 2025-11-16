"""
Test script for Queue Simulator
Tests basic functionality without GUI
"""

import sys
import os
import time

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from queueSimulator import QueueSimulator, DispatchStrategy

def testBasicSimulation():
    """Test basic simulation functionality"""
    print("=" * 60)
    print("Testing Post Office Queue Simulator")
    print("=" * 60)
    
    # Create simulator
    simulator = QueueSimulator(
        numServers=5,
        numBooths=4,
        dispatchStrategy=DispatchStrategy.LONGEST_WAIT_FIRST,
        serviceTimes={
            'standard_post': 2.0,
            'passports': 5.0,
            'parcels': 3.0
        },
        timeAcceleration=100.0,  # Very fast for testing
        abandonmentEnabled=False  # Disable for deterministic test
    )
    
    print("\nSimulator initialized:")
    print(f"  Servers: {simulator.numServers}")
    print(f"  Booths: {simulator.numBooths}")
    print(f"  Strategy: {simulator.dispatchStrategy.value}")
    print(f"  Time Acceleration: {simulator.timeAcceleration}x")
    
    # Add some customers
    print("\n" + "-" * 60)
    print("Adding customers to queues...")
    print("-" * 60)
    
    customers = []
    customers.append(simulator.addCustomer('standard_post'))
    print("Added customer to Standard Post queue")
    
    customers.append(simulator.addCustomer('passports'))
    print("Added customer to Passports queue")
    
    customers.append(simulator.addCustomer('parcels'))
    print("Added customer to Parcels queue")
    
    customers.append(simulator.addCustomer('standard_post'))
    print("Added customer to Standard Post queue")
    
    customers.append(simulator.addCustomer('passports'))
    print("Added customer to Passports queue")
    
    # Check initial queue lengths
    queueLengths = simulator.getQueueLengths()
    print(f"\nInitial queue lengths: {queueLengths}")
    
    # Run simulation for a while
    print("\n" + "-" * 60)
    print("Running simulation...")
    print("-" * 60)
    
    simulator.running = True
    startTime = time.time()
    
    while time.time() - startTime < 5:  # Run for 5 real seconds
        simulator.update()
        time.sleep(0.05)
    
    # Get final statistics
    print("\n" + "=" * 60)
    print("Simulation Results")
    print("=" * 60)
    
    stats = simulator.getStatistics()
    print(f"\nSimulation Time: {stats['simulationTime']:.2f} minutes")
    print(f"Total Customers: {stats['totalCustomers']}")
    print(f"Customers Served: {stats['totalServed']}")
    print(f"Customers Abandoned: {stats['totalAbandoned']}")
    print(f"Average Wait Time: {stats['avgWaitTime']:.2f} minutes")
    print(f"Average Service Time: {stats['avgServiceTime']:.2f} minutes")
    
    # Final queue lengths
    finalQueueLengths = simulator.getQueueLengths()
    print(f"\nFinal queue lengths: {finalQueueLengths}")
    
    # Server states
    print("\nServer States:")
    serverStates = simulator.getServerStates()
    for server in serverStates:
        print(f"  Server {server['serverId']}: {server['state']}")
    
    # Booth states
    print("\nBooth States:")
    boothStates = simulator.getBoothStates()
    for booth in boothStates:
        status = "Occupied" if booth['occupied'] else "Available"
        print(f"  Booth {booth['boothId']}: {status}")
    
    print("\n" + "=" * 60)
    print("Test Complete!")
    print("=" * 60)


def testDispatchStrategies():
    """Test different dispatch strategies"""
    print("\n" + "=" * 60)
    print("Testing Different Dispatch Strategies")
    print("=" * 60)
    
    strategies = [
        DispatchStrategy.LONGEST_WAIT_FIRST,
        DispatchStrategy.SHORTEST_JOB_FIRST,
        DispatchStrategy.ROUND_ROBIN,
        DispatchStrategy.PRIORITY_ORDER
    ]
    
    for strategy in strategies:
        print(f"\n{'-' * 60}")
        print(f"Testing: {strategy.value}")
        print(f"{'-' * 60}")
        
        simulator = QueueSimulator(
            numServers=5,
            numBooths=4,
            dispatchStrategy=strategy,
            timeAcceleration=200.0,
            abandonmentEnabled=False
        )
        
        # Add multiple customers
        for _ in range(3):
            simulator.addCustomer('standard_post')
        for _ in range(2):
            simulator.addCustomer('passports')
        for _ in range(2):
            simulator.addCustomer('parcels')
        
        print(f"Added 7 customers total")
        
        # Run simulation
        simulator.running = True
        startTime = time.time()
        
        while time.time() - startTime < 3:
            simulator.update()
            time.sleep(0.05)
        
        stats = simulator.getStatistics()
        print(f"Served: {stats['totalServed']}, Avg Wait: {stats['avgWaitTime']:.2f} min")


if __name__ == '__main__':
    # Run tests
    testBasicSimulation()
    testDispatchStrategies()
    
    print("\n" + "=" * 60)
    print("All tests completed successfully!")
    print("=" * 60)
