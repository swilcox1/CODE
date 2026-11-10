import time
import serial


SERIAL_PORT = 'COM3'
BAUD_RATE = 9600  # Korad PSUs default to 9600 baud

def send_cmd(ser, cmd, delay=0.1):
    """Sends a raw text command to the PSU and pauses briefly for processing."""
    ser.write(cmd.encode('ascii'))
    time.sleep(delay)

def read_response(ser):
    """Reads whatever data is sitting in the incoming buffer."""
    if ser.in_waiting > 0:
        return ser.read(ser.in_waiting).decode('ascii').strip()
    return ""

try:
    # Open the serial port connection
    with serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1) as psu:
        print(f"Connected to {SERIAL_PORT}")

        # 1. Identify device
        send_cmd(psu, '*IDN?')
        print("Device Identity:", read_response(psu))

        # 2. Set Voltage
        # For 5 Volts -> VSET1:05.00
        send_cmd(psu, 'VSET1:3.00')

        # 3. Set Current 
        # For 1.5 Amps -> ISET1:1.500
        send_cmd(psu, 'ISET1:1.500')

        # 4. Turn Output ON
        send_cmd(psu, 'OUT1')
        print("Power supply output turned ON.")

        # Wait 5 seconds
        time.sleep(5)

        # 5. Turn Output OFF
        send_cmd(psu, 'OUT0')
        print("Power supply output turned OFF.")

except serial.SerialException as e:
    print(f"Serial communication error: {e}")
