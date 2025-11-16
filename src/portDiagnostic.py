"""
Serial Port Diagnostic Tool
Lists all available serial ports with detailed information
"""

import serial.tools.list_ports

def listAllSerialPorts():
    """List all available serial ports with detailed information"""
    print("=" * 80)
    print("SERIAL PORT DIAGNOSTIC TOOL")
    print("=" * 80)
    print()
    
    ports = serial.tools.list_ports.comports()
    
    if not ports:
        print("❌ No serial ports found!")
        print()
        print("Possible reasons:")
        print("  - No devices connected via USB")
        print("  - Drivers not installed")
        print("  - Device not recognized by Windows")
        return
    
    print(f"✅ Found {len(ports)} serial port(s):\n")
    
    for i, port in enumerate(ports, 1):
        print(f"{'=' * 80}")
        print(f"PORT #{i}")
        print(f"{'=' * 80}")
        print(f"Device:          {port.device}")
        print(f"Description:     {port.description}")
        print(f"Hardware ID:     {port.hwid}")
        
        # Additional attributes if available
        if hasattr(port, 'manufacturer') and port.manufacturer:
            print(f"Manufacturer:    {port.manufacturer}")
        if hasattr(port, 'product') and port.product:
            print(f"Product:         {port.product}")
        if hasattr(port, 'serial_number') and port.serial_number:
            print(f"Serial Number:   {port.serial_number}")
        if hasattr(port, 'location') and port.location:
            print(f"Location:        {port.location}")
        if hasattr(port, 'vid') and port.vid:
            print(f"Vendor ID:       0x{port.vid:04X}")
        if hasattr(port, 'pid') and port.pid:
            print(f"Product ID:      0x{port.pid:04X}")
        
        print()
        
        # Try to identify device type
        desc_lower = port.description.lower()
        device_lower = port.device.lower()
        hwid_lower = port.hwid.lower()
        
        all_info = f"{desc_lower} {device_lower} {hwid_lower}"
        
        print("Possible Device Type:")
        if any(keyword in all_info for keyword in ['micro:bit', 'microbit', 'bbc', 'daplink', 'mbed']):
            print("  🎯 This looks like a Micro:bit!")
        elif 'arduino' in all_info:
            print("  🔧 This might be an Arduino")
        elif 'ch340' in all_info or 'ch341' in all_info:
            print("  🔌 This might be a CH340/CH341 USB-Serial adapter")
        elif 'ftdi' in all_info or 'ft232' in all_info:
            print("  🔌 This might be an FTDI USB-Serial adapter")
        elif 'cp210' in all_info:
            print("  🔌 This might be a CP210x USB-Serial adapter")
        elif 'usb' in all_info and 'serial' in all_info:
            print("  🔌 Generic USB-Serial device")
        else:
            print("  ❓ Unknown device type")
        
        print()
    
    print("=" * 80)
    print("SEARCH SUGGESTIONS")
    print("=" * 80)
    print()
    print("To find your Micro:bit, look for ports with:")
    print("  ✓ 'USB Serial Device' in description")
    print("  ✓ VID: 0x0D28 (ARM Ltd)")
    print("  ✓ PID: 0x0204")
    print("  ✓ Manufacturer containing 'ARM' or 'mbed'")
    print()
    print("If your Micro:bit is connected but not showing:")
    print("  1. Try unplugging and replugging the USB cable")
    print("  2. Try a different USB port")
    print("  3. Make sure the Micro:bit LED is lit (powered on)")
    print("  4. Update Micro:bit firmware: https://microbit.org/get-started/user-guide/firmware/")
    print("  5. Install drivers: https://os.mbed.com/docs/mbed-os/v6.16/debug-test/serial-comm.html")
    print()


def testSerialConnection(portName):
    """Test connection to a specific port"""
    print(f"\nTesting connection to {portName}...")
    try:
        ser = serial.Serial(portName, 115200, timeout=1)
        print(f"✅ Successfully opened {portName}")
        print(f"   Baudrate: {ser.baudrate}")
        print(f"   Timeout: {ser.timeout}s")
        
        # Try to read any available data
        if ser.in_waiting > 0:
            data = ser.read(ser.in_waiting)
            print(f"   Data available: {len(data)} bytes")
        else:
            print(f"   No data currently available")
        
        ser.close()
        print(f"✅ Connection test successful!")
        return True
    except serial.SerialException as e:
        print(f"❌ Failed to open {portName}: {e}")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


if __name__ == '__main__':
    # List all ports
    listAllSerialPorts()
    
    # Ask user if they want to test a specific port
    print()
    print("=" * 80)
    test = input("Would you like to test a specific port? (y/n): ").strip().lower()
    
    if test == 'y':
        port = input("Enter port name (e.g., COM3, /dev/ttyUSB0): ").strip()
        if port:
            testSerialConnection(port)
    
    print()
    print("=" * 80)
    print("If you found your Micro:bit port, you can:")
    print("1. Update microbitComms.py to add the identifier to the keyword list")
    print("2. Manually specify the port in the GUI (I can add this feature)")
    print("=" * 80)