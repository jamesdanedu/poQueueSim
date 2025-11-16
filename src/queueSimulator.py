"""
Queue Simulation Engine for Post Office Queue Simulator
Handles queue management, server allocation, and booth assignment
"""

import time
import random
from collections import deque
from enum import Enum

class DispatchStrategy(Enum):
    """Available dispatch strategies for server assignment"""
    LONGEST_WAIT_FIRST = "longest_wait_first"
    SHORTEST_JOB_FIRST = "shortest_job_first"
    ROUND_ROBIN = "round_robin"
    PRIORITY_ORDER = "priority_order"

class ServerState(Enum):
    """Server states"""
    IDLE = "idle"
    BUSY = "busy"
    SPARE = "spare"

class Customer:
    """Represents a customer in the queue"""
    _nextId = 1
    
    def __init__(self, serviceType, arrivalTime):
        self.customerId = Customer._nextId
        Customer._nextId += 1
        self.serviceType = serviceType
        self.arrivalTime = arrivalTime
        self.queueJoinTime = arrivalTime
        self.serviceStartTime = None
        self.serviceEndTime = None
        self.serverId = None
        self.boothId = None
        self.outcome = None  # 'completed' or 'abandoned'
    
    def getWaitDuration(self):
        """Calculate wait duration"""
        if self.serviceStartTime:
            return self.serviceStartTime - self.queueJoinTime
        return None
    
    def getServiceDuration(self):
        """Calculate service duration"""
        if self.serviceStartTime and self.serviceEndTime:
            return self.serviceEndTime - self.serviceStartTime
        return None

class Server:
    """Represents a server (staff member)"""
    
    def __init__(self, serverId):
        self.serverId = serverId
        self.state = ServerState.SPARE
        self.currentCustomer = None
        self.currentBoothId = None
        self.serviceEndTime = None
    
    def startService(self, customer, boothId, serviceEndTime):
        """Assign server to serve a customer at a booth"""
        self.state = ServerState.BUSY
        self.currentCustomer = customer
        self.currentBoothId = boothId
        self.serviceEndTime = serviceEndTime
    
    def finishService(self):
        """Server finishes serving current customer"""
        customer = self.currentCustomer
        self.currentCustomer = None
        self.currentBoothId = None
        self.serviceEndTime = None
        self.state = ServerState.SPARE
        return customer
    
    def isAvailable(self):
        """Check if server is available"""
        return self.state == ServerState.SPARE

class Booth:
    """Represents a service booth"""
    
    def __init__(self, boothId):
        self.boothId = boothId
        self.occupied = False
        self.serverId = None
    
    def assignServer(self, serverId):
        """Assign a server to this booth"""
        self.occupied = True
        self.serverId = serverId
    
    def releaseServer(self):
        """Release server from booth"""
        self.occupied = False
        serverId = self.serverId
        self.serverId = None
        return serverId
    
    def isAvailable(self):
        """Check if booth is available"""
        return not self.occupied

class QueueSimulator:
    """Main queue simulation engine"""
    
    def __init__(self, numServers=5, numBooths=4, dispatchStrategy=DispatchStrategy.LONGEST_WAIT_FIRST,
                 serviceTimes=None, timeAcceleration=20.0, abandonmentEnabled=True):
        """
        Initialize queue simulator
        
        Args:
            numServers: Number of servers (default 5)
            numBooths: Number of booths (default 4)
            dispatchStrategy: Strategy for dispatching customers
            serviceTimes: Dict of service times in minutes {service_type: duration}
            timeAcceleration: Simulation speed multiplier (default 20x)
            abandonmentEnabled: Whether customers can abandon queues
        """
        self.numServers = numServers
        self.numBooths = numBooths
        self.dispatchStrategy = dispatchStrategy
        self.timeAcceleration = timeAcceleration
        self.abandonmentEnabled = abandonmentEnabled
        
        # Service times in minutes
        self.serviceTimes = serviceTimes or {
            'standard_post': 2.0,
            'passports': 5.0,
            'parcels': 3.0
        }
        
        # Initialize servers and booths
        self.servers = [Server(i) for i in range(numServers)]
        self.booths = [Booth(i) for i in range(numBooths)]
        
        # Initialize queues for each service type
        self.queues = {
            'standard_post': deque(),
            'passports': deque(),
            'parcels': deque()
        }
        
        # Simulation state
        self.simulationTime = 0.0  # Simulation time in minutes
        self.running = False
        self.lastUpdateTime = None
        
        # Statistics
        self.totalCustomersServed = 0
        self.totalCustomersAbandoned = 0
        self.completedCustomers = []
        self.abandonedCustomers = []
        
        # Round robin counter for round robin strategy
        self.roundRobinIndex = 0
        self.serviceTypesList = list(self.queues.keys())
    
    def addCustomer(self, serviceType):
        """Add a customer to the appropriate queue"""
        if serviceType not in self.queues:
            return None
        
        customer = Customer(serviceType, self.simulationTime)
        self.queues[serviceType].append(customer)
        return customer
    
    def update(self):
        """Update simulation state - call this regularly"""
        currentRealTime = time.time()
        
        if self.lastUpdateTime is None:
            self.lastUpdateTime = currentRealTime
            return
        
        # Calculate elapsed simulation time
        realDeltaTime = currentRealTime - self.lastUpdateTime
        simDeltaTime = realDeltaTime * self.timeAcceleration / 60.0  # Convert to simulation minutes
        
        self.simulationTime += simDeltaTime
        self.lastUpdateTime = currentRealTime
        
        # Check for completed services
        self._checkCompletedServices()
        
        # Check for abandonments
        if self.abandonmentEnabled:
            self._checkAbandonments()
        
        # Assign available servers to waiting customers
        self._assignServersToCustomers()
    
    def _checkCompletedServices(self):
        """Check if any servers have completed their service"""
        for server in self.servers:
            if server.state == ServerState.BUSY and self.simulationTime >= server.serviceEndTime:
                # Service completed
                boothId = server.currentBoothId
                customer = server.finishService()
                customer.serviceEndTime = self.simulationTime
                customer.outcome = 'completed'
                
                # Release booth
                if boothId is not None:
                    booth = self.booths[boothId]
                    booth.releaseServer()
                
                # Record completed customer
                self.completedCustomers.append(customer)
                self.totalCustomersServed += 1
    
    def _checkAbandonments(self):
        """Check if any customers abandon the queue"""
        for serviceType, queue in self.queues.items():
            customersToRemove = []
            
            for customer in queue:
                waitTime = self.simulationTime - customer.queueJoinTime
                
                # Abandonment probability increases with wait time
                abandonProb = 0.0
                if waitTime > 5.0:
                    abandonProb = 0.05 * (waitTime - 5.0)  # 5% per minute after 5 min
                if waitTime > 10.0:
                    abandonProb = 0.15 * (waitTime - 5.0)  # 15% per minute after 10 min
                
                abandonProb = min(abandonProb, 0.5)  # Cap at 50%
                
                if random.random() < abandonProb * (1.0 / self.timeAcceleration):
                    customer.outcome = 'abandoned'
                    customer.serviceEndTime = self.simulationTime
                    customersToRemove.append(customer)
                    self.abandonedCustomers.append(customer)
                    self.totalCustomersAbandoned += 1
            
            # Remove abandoned customers
            for customer in customersToRemove:
                queue.remove(customer)
    
    def _assignServersToCustomers(self):
        """Assign available servers to waiting customers"""
        # Find available servers and booths
        availableServers = [s for s in self.servers if s.isAvailable()]
        availableBooths = [b for b in self.booths if b.isAvailable()]
        
        # While we have both available servers and booths, and customers waiting
        while availableServers and availableBooths:
            # Select next customer based on dispatch strategy
            customer = self._selectNextCustomer()
            
            if customer is None:
                break  # No more customers waiting
            
            # Assign server and booth
            server = availableServers.pop(0)
            booth = availableBooths.pop(0)
            
            # Calculate service end time
            serviceTime = self.serviceTimes.get(customer.serviceType, 3.0)
            # Add some randomness (±20%)
            serviceTime *= random.uniform(0.8, 1.2)
            serviceEndTime = self.simulationTime + serviceTime
            
            # Update customer
            customer.serviceStartTime = self.simulationTime
            customer.serverId = server.serverId
            customer.boothId = booth.boothId
            
            # Update server and booth
            server.startService(customer, booth.boothId, serviceEndTime)
            booth.assignServer(server.serverId)
    
    def _selectNextCustomer(self):
        """Select next customer to serve based on dispatch strategy"""
        if self.dispatchStrategy == DispatchStrategy.LONGEST_WAIT_FIRST:
            return self._selectLongestWaitFirst()
        elif self.dispatchStrategy == DispatchStrategy.SHORTEST_JOB_FIRST:
            return self._selectShortestJobFirst()
        elif self.dispatchStrategy == DispatchStrategy.ROUND_ROBIN:
            return self._selectRoundRobin()
        elif self.dispatchStrategy == DispatchStrategy.PRIORITY_ORDER:
            return self._selectPriorityOrder()
        else:
            return self._selectLongestWaitFirst()
    
    def _selectLongestWaitFirst(self):
        """Select customer who has waited longest across all queues"""
        longestWaitCustomer = None
        longestWaitTime = -1
        selectedQueue = None
        
        for serviceType, queue in self.queues.items():
            if queue:
                customer = queue[0]
                waitTime = self.simulationTime - customer.queueJoinTime
                if waitTime > longestWaitTime:
                    longestWaitTime = waitTime
                    longestWaitCustomer = customer
                    selectedQueue = queue
        
        if longestWaitCustomer:
            selectedQueue.popleft()
            return longestWaitCustomer
        return None
    
    def _selectShortestJobFirst(self):
        """Select customer with shortest expected service time"""
        shortestJobCustomer = None
        shortestJobTime = float('inf')
        selectedQueue = None
        
        for serviceType, queue in self.queues.items():
            if queue:
                customer = queue[0]
                jobTime = self.serviceTimes.get(customer.serviceType, 3.0)
                if jobTime < shortestJobTime:
                    shortestJobTime = jobTime
                    shortestJobCustomer = customer
                    selectedQueue = queue
        
        if shortestJobCustomer:
            selectedQueue.popleft()
            return shortestJobCustomer
        return None
    
    def _selectRoundRobin(self):
        """Select customer in round-robin fashion across service types"""
        attempts = 0
        while attempts < len(self.serviceTypesList):
            serviceType = self.serviceTypesList[self.roundRobinIndex]
            self.roundRobinIndex = (self.roundRobinIndex + 1) % len(self.serviceTypesList)
            
            queue = self.queues[serviceType]
            if queue:
                return queue.popleft()
            
            attempts += 1
        
        return None
    
    def _selectPriorityOrder(self):
        """Select customer based on priority: passports > parcels > standard_post"""
        priorityOrder = ['passports', 'parcels', 'standard_post']
        
        for serviceType in priorityOrder:
            queue = self.queues[serviceType]
            if queue:
                return queue.popleft()
        
        return None
    
    def getQueueLengths(self):
        """Get current queue lengths"""
        return {serviceType: len(queue) for serviceType, queue in self.queues.items()}
    
    def getServerStates(self):
        """Get current server states"""
        return [
            {
                'serverId': s.serverId,
                'state': s.state.value,
                'boothId': s.currentBoothId,
                'customerId': s.currentCustomer.customerId if s.currentCustomer else None,
                'serviceType': s.currentCustomer.serviceType if s.currentCustomer else None,
                'timeRemaining': max(0, s.serviceEndTime - self.simulationTime) if s.serviceEndTime else 0
            }
            for s in self.servers
        ]
    
    def getBoothStates(self):
        """Get current booth states"""
        return [
            {
                'boothId': b.boothId,
                'occupied': b.occupied,
                'serverId': b.serverId
            }
            for b in self.booths
        ]
    
    def getStatistics(self):
        """Get simulation statistics"""
        totalCustomers = len(self.completedCustomers) + len(self.abandonedCustomers)
        
        if totalCustomers == 0:
            return {
                'totalCustomers': 0,
                'totalServed': 0,
                'totalAbandoned': 0,
                'avgWaitTime': 0,
                'avgServiceTime': 0,
                'simulationTime': self.simulationTime
            }
        
        avgWaitTime = sum(c.getWaitDuration() or 0 for c in self.completedCustomers) / max(len(self.completedCustomers), 1)
        avgServiceTime = sum(c.getServiceDuration() or 0 for c in self.completedCustomers) / max(len(self.completedCustomers), 1)
        
        return {
            'totalCustomers': totalCustomers,
            'totalServed': self.totalCustomersServed,
            'totalAbandoned': self.totalCustomersAbandoned,
            'avgWaitTime': avgWaitTime,
            'avgServiceTime': avgServiceTime,
            'simulationTime': self.simulationTime
        }
    
    def reset(self):
        """Reset simulation to initial state"""
        # Reset servers
        for server in self.servers:
            server.state = ServerState.SPARE
            server.currentCustomer = None
            server.currentBoothId = None
            server.serviceEndTime = None
        
        # Reset booths
        for booth in self.booths:
            booth.occupied = False
            booth.serverId = None
        
        # Clear queues
        for queue in self.queues.values():
            queue.clear()
        
        # Reset statistics
        self.simulationTime = 0.0
        self.lastUpdateTime = None
        self.totalCustomersServed = 0
        self.totalCustomersAbandoned = 0
        self.completedCustomers = []
        self.abandonedCustomers = []
        Customer._nextId = 1