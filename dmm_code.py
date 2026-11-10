import time
import traceback
import threading
import pyvisa

rm = pyvisa.ResourceManager()
inst_address = "ASRL6::INSTR"

def run_measurement_loop(delay, total_duration, task):
    """Runs `task` every `delay` seconds for `total_duration` seconds."""
    start_time = time.monotonic()
    next_time = start_time
    
    readings = []
    timestamps = []

    while True:
        now = time.monotonic()
        elapsed = now - start_time
        
        if elapsed >= total_duration:
            break

        # Sleep until the next scheduled tick
        sleep_time = next_time - now
        if sleep_time > 0:
            time.sleep(sleep_time)

        try:
            # Record exact timestamp and measurement
            current_elapsed = time.monotonic() - start_time
            val = task()
            
            readings.append(val)
            timestamps.append(current_elapsed)
            print(f"[{current_elapsed:6.2f}s] Current: {val} Amps")
            
        except Exception:
            traceback.print_exc()

        # Schedule next execution, skipping missed intervals if behind schedule
        now_after = time.monotonic()
        next_time += ((now_after - next_time) // delay + 1) * delay

    return timestamps, readings

dmm = None
try:
    dmm = rm.open_resource(inst_address)
    dmm.baud_rate = 9600
    dmm.data_bits = 8
    dmm.parity = pyvisa.constants.Parity.none
    dmm.stop_bits = pyvisa.constants.StopBits.one
    dmm.read_termination = '\n'
    dmm.write_termination = '\n'
    dmm.timeout = 5000  

    # --- 1. Query Identification cleanly ---
    dmm.write("*IDN?")
    echo1 = dmm.read()      
    idn_data = dmm.read()   
    print(f"Connected to: {idn_data.strip()}")

    # --- 2. Configure for resistance ---
    dmm.write("FUNC CURR")
    echo2 = dmm.read()      
    time.sleep(0.5)         

    # --- 3. Define the measurement task ---
    def read_resistance():
        dmm.write("FETC?")
        echo3 = dmm.read()      
        reading = dmm.read()    
        return float(reading.strip())

    # --- 4. Run for 200 seconds at 0.1s (10Hz) intervals ---
    time_evo, current_evolution = run_measurement_loop(
        delay=1, 
        total_duration=200, 
        task=read_resistance
    )

    print(f"Finished! Collected {len(current_evolution)} samples.")

except Exception as e:
    print(f"Communication error: {e}")

finally:
    if dmm is not None:
        dmm.close()
