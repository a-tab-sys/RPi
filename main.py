import serial
import struct
import time
import math

# Configure your serial port (usually /dev/ttyS0 or /dev/ttyAMA0 on Pi)
SERIAL_PORT = '/dev/ttyS0' 
BAUD_RATE = 115200

try:
    ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
    print(f"Connected to {SERIAL_PORT}")
except Exception as e:
    print(f"Error opening serial port: {e}")
    exit()

def send_msp_rc(channels):
    """Sends 8 RC channels to the FC using MSP_SET_RAW_RC (ID: 200)"""
    header = b'$M<'
    size = len(channels) * 2
    msg_id = 200
    
    # Payload: 8 channels as Little-Endian unsigned 16-bit integers
    payload = struct.pack('<' + 'H' * len(channels), *channels)
    
    # Checksum: XOR of Size, ID, and all bytes in Payload
    checksum = size ^ msg_id
    for b in payload:
        checksum ^= b
        
    packet = header + struct.pack('<BB', size, msg_id) + payload + struct.pack('<B', checksum)
    ser.write(packet)

print("Starting Sweep... Open Betaflight 'Receiver' tab to watch the bars.")
print("Press Ctrl+C to stop.")

try:
    start_time = time.time()
    while True:
        elapsed = time.time() - start_time
        
        # Create a sine wave oscillation between 1000 and 2000
        # math.sin returns -1 to 1; we map that to 1000 to 2000
        sweep_val = int(1500 + 500 * math.sin(elapsed * 2)) 
        
        # Channels: [Roll, Pitch, Yaw, Throttle, AUX1, AUX2, AUX3, AUX4]
        # We'll sweep the first 4 and keep AUX1 (Arm) at 1000 (Disarmed)
        channels = [sweep_val, sweep_val, sweep_val, sweep_val, 1000, 1500, 1500, 1500]
        
        send_msp_rc(channels)
        
        # Frequency: 50Hz (20ms delay) is standard for smooth movement
        time.sleep(0.02)

except KeyboardInterrupt:
    # Safety: Reset all channels to neutral/low before exiting
    print("\nStopping... Resetting channels.")
    send_msp_rc([1500, 1500, 1500, 1000, 1000, 1000, 1000, 1000])
    ser.close()
