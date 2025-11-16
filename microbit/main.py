# Micro:bit Post Office Queue Simulator
# Buttons: A = Standard Post, B = Passports, A+B = Parcels

from microbit import *
import time

def sendServiceRequest(serviceType):
    """Send service request via serial with timestamp"""
    timestamp = time.ticks_ms()
    message = "SERVICE_REQUEST,{},{}\n".format(serviceType, timestamp)
    uart.write(message)
    # Visual feedback
    display.show(Image.HAPPY)
    sleep(200)
    display.clear()

# Initialize UART for serial communication
uart.init(baudrate=115200)

display.show(Image.HEART)
sleep(1000)
display.clear()

lastPressTime = 0
debounceMs = 300  # Debounce delay

while True:
    currentTime = time.ticks_ms()
    
    # Check for button presses with debounce
    if currentTime - lastPressTime > debounceMs:
        if button_a.is_pressed() and button_b.is_pressed():
            # Both buttons = Parcels
            sendServiceRequest("parcels")
            lastPressTime = currentTime
        elif button_a.is_pressed():
            # Button A = Standard Post
            sendServiceRequest("standard_post")
            lastPressTime = currentTime
        elif button_b.is_pressed():
            # Button B = Passports
            sendServiceRequest("passports")
            lastPressTime = currentTime
    
    sleep(50)  # Small delay to reduce CPU usage
