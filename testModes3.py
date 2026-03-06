import serial
import struct
import time

# Initialize serial - ensure /dev/ttyS0 is correct for your Pi
ser = serial.Serial('/dev/ttyS0', 115200, timeout=0.01)
time.sleep(1) # Wait for serial to stabilize

def send_msp_rc(channels):
    header = b'$M<'
    size = len(channels) * 2
    msg_id = 200 
    payload = struct.pack('<' + 'H' * len(channels), *channels)
    checksum = size ^ msg_id
    for b in payload: checksum ^= b
    packet = header + struct.pack('<BB', size, msg_id) + payload + struct.pack('<B', checksum)
    ser.write(packet)
    ser.flush()

try:
    print("Sending Heartbeat at 50Hz... Check 'RX rate' in Betaflight.")
    
    # We use a state counter instead of long sleeps
    counter = 0
    
    while True:
        # Update state logic every 150 iterations (~3 seconds at 50Hz)
        if counter < 150:
            state = "DISARMED"
            # [R, P, Y, T, AUX1, AUX2...]
            current_channels = [1500, 1500, 1500, 1000, 1000, 1000, 1500, 1500]
        elif counter < 300:
            state = "ARMED"
            current_channels = [1500, 1500, 1500, 1000, 2000, 1000, 1500, 1500]
        else:
            counter = 0 # Reset cycle
            continue

        send_msp_rc(current_channels)
        
        # INCREMENT AND SLEEP
        counter += 1
        time.sleep(0.02) # This 20ms delay creates the 50Hz RX rate

except KeyboardInterrupt:
    send_msp_rc([1500, 1500, 1500, 1000, 1000, 1000, 1000, 1000])
    ser.close()
