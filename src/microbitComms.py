"""
Serial Communication Handler for Micro:bit
Listens for button press events from Micro:bit via serial USB
"""

import serial
import serial.tools.list_ports
import threading
import time

class MicrobitCommunicator:
    """Handles serial communication with Micro:bit"""
    
    def __init__(self, baudRate=115200, timeout=1):
        """Initialize Micro:bit communicator"""
        self.baudRate = baudRate
        self.timeout = timeout
        self.serialPort = None
        self.connected = False
        self.listening = False
        self.listenerThread = None
        self.callback = None
    
    def findMicrobit(self):
        """Automatically find Micro:bit serial port"""
        ports = serial.tools.list_ports.comports()
        
        # Look for common Micro:bit identifiers
        microbitKeywords = ['micro:bit', 'microbit', 'BBC', 'DAPLink', 'mbed']
        
        for port in ports:
            portDesc = port.description.lower()
            portName = port.device.lower()
            
            # Check for Micro:bit Vendor ID and Product ID (most reliable)
            if hasattr(port, 'vid') and hasattr(port, 'pid'):
                if port.vid == 0x0D28 and port.pid == 0x0204:
                    print(f"Found Micro:bit on {port.device} (VID:PID match)")
                    return port.device
            
            # Fallback to keyword search
            for keyword in microbitKeywords:
                if keyword.lower() in portDesc or keyword.lower() in portName:
                    return port.device
        
        return None
    
    def connect(self, portName=None):
        """
        Connect to Micro:bit
        
        Args:
            portName: Serial port name (e.g., 'COM3' or '/dev/ttyACM0')
                      If None, will attempt to auto-detect
        
        Returns:
            bool: True if connected successfully
        """
        if portName is None:
            portName = self.findMicrobit()
            if portName is None:
                print("Could not auto-detect Micro:bit. Please specify port manually.")
                return False
        
        try:
            self.serialPort = serial.Serial(
                port=portName,
                baudrate=self.baudRate,
                timeout=self.timeout
            )
            self.connected = True
            print(f"Connected to Micro:bit on {portName}")
            time.sleep(2)  # Give time for connection to stabilize
            return True
        except serial.SerialException as e:
            print(f"Failed to connect to {portName}: {e}")
            return False
    
    def disconnect(self):
        """Disconnect from Micro:bit"""
        self.stopListening()
        if self.serialPort and self.serialPort.is_open:
            self.serialPort.close()
        self.connected = False
        print("Disconnected from Micro:bit")
    
    def setCallback(self, callback):
        """
        Set callback function for received messages
        
        Args:
            callback: Function to call when message received
                      Should accept (serviceType, timestamp) as parameters
        """
        self.callback = callback
    
    def startListening(self):
        """Start listening for messages from Micro:bit in background thread"""
        if not self.connected:
            print("Not connected to Micro:bit")
            return False
        
        if self.listening:
            print("Already listening")
            return True
        
        self.listening = True
        self.listenerThread = threading.Thread(target=self._listenLoop, daemon=True)
        self.listenerThread.start()
        print("Started listening for Micro:bit messages")
        return True
    
    def stopListening(self):
        """Stop listening for messages"""
        self.listening = False
        if self.listenerThread:
            self.listenerThread.join(timeout=2)
        print("Stopped listening for Micro:bit messages")
    
    def _listenLoop(self):
        """Internal loop for listening to serial messages"""
        while self.listening and self.connected:
            try:
                if self.serialPort and self.serialPort.in_waiting > 0:
                    line = self.serialPort.readline().decode('utf-8').strip()
                    self._processMessage(line)
            except serial.SerialException as e:
                print(f"Serial error: {e}")
                self.connected = False
                break
            except Exception as e:
                print(f"Error processing message: {e}")
            
            time.sleep(0.01)  # Small delay to prevent CPU spinning
    
    def _processMessage(self, message):
        """
        Process received message from Micro:bit
        
        Expected format: SERVICE_REQUEST,service_type,timestamp
        """
        if not message:
            return
        
        parts = message.split(',')
        
        if len(parts) >= 2 and parts[0] == 'SERVICE_REQUEST':
            serviceType = parts[1]
            timestamp = parts[2] if len(parts) > 2 else None
            
            print(f"Received service request: {serviceType}")
            
            if self.callback:
                self.callback(serviceType, timestamp)
    
    def sendMessage(self, message):
        """
        Send message to Micro:bit
        
        Args:
            message: String message to send
        """
        if not self.connected or not self.serialPort:
            print("Not connected to Micro:bit")
            return False
        
        try:
            self.serialPort.write(f"{message}\n".encode('utf-8'))
            return True
        except serial.SerialException as e:
            print(f"Failed to send message: {e}")
            return False
    
    def listAvailablePorts(self):
        """List all available serial ports"""
        ports = serial.tools.list_ports.comports()
        print("\nAvailable serial ports:")
        for i, port in enumerate(ports):
            print(f"{i+1}. {port.device} - {port.description}")
        return [port.device for port in ports]
    
    def isConnected(self):
        """Check if connected to Micro:bit"""
        return self.connected and self.serialPort and self.serialPort.is_open


# Example usage and testing
if __name__ == '__main__':
    def testCallback(serviceType, timestamp):
        print(f"Test callback: Service={serviceType}, Timestamp={timestamp}")
    
    communicator = MicrobitCommunicator()
    
    # List available ports
    communicator.listAvailablePorts()
    
    # Try to connect
    if communicator.connect():
        communicator.setCallback(testCallback)
        communicator.startListening()
        
        print("\nListening for button presses on Micro:bit...")
        print("Press Ctrl+C to stop")
        
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\nStopping...")
            communicator.disconnect()
    else:
        print("Failed to connect to Micro:bit")