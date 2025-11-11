from core.hardware_manager import hardware_manager
import RPi.GPIO as GPIO
import time
import random
import os

class Ultrasonic:
    def __init__(self, trigger_pin, echo_pin):
        self.trigger_pin = trigger_pin
        self.echo_pin = echo_pin
        self.simulation_mode = hardware_manager.simulation_mode

        if not self.simulation_mode:
            # Configure pins. Use an internal pull-down on ECHO to avoid floating reads
            GPIO.setup(self.trigger_pin, GPIO.OUT)
            # Ensure trigger is low initially
            GPIO.output(self.trigger_pin, False)
            # ECHO should be input with pull-down to avoid spurious HIGH
            try:
                GPIO.setup(self.echo_pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
            except TypeError:
                # Some older RPi.GPIO versions may not accept pull_up_down here
                GPIO.setup(self.echo_pin, GPIO.IN)

            print(f"Ultrasonic Sensor initialized with TRIGGER={self.trigger_pin} and ECHO={self.echo_pin}")
        else:
            print(f"Ultrasonic Sensor initialized (Simulation Mode)")

    def measure_distance(self, retries=2):
        """
        Measures the distance using the ultrasonic sensor with retry logic.
        Returns the distance in centimeters, or negative value on error.
        
        Returns:
            float: Distance in cm (2-400cm range)
            -1: Timeout error (echo pin issue)
            -2: Out of range (too far or too close)
            -3: Signal noise/interference
        """
        if self.simulation_mode:
            # Simulate a distance reading
            return random.uniform(5, 200)

        for attempt in range(retries + 1):
            try:
                # Ensure trigger is low for a clean start
                GPIO.output(self.trigger_pin, False)
                time.sleep(0.00002)  # 20 microseconds settle time
                
                # Send 10us trigger pulse
                GPIO.output(self.trigger_pin, True)
                time.sleep(0.00001)  # 10 microseconds pulse
                GPIO.output(self.trigger_pin, False)

                # Wait for echo to start (go HIGH)
                timeout_start = time.time()
                pulse_start = time.time()
                
                # Wait for echo pin to go HIGH (with timeout)
                while GPIO.input(self.echo_pin) == 0:
                    pulse_start = time.time()
                    if (pulse_start - timeout_start) > 0.05:  # 50ms timeout
                        if attempt < retries:
                            time.sleep(0.01)  # 10ms delay before retry
                            break
                        print(f"[ULTRASONIC] Error: Echo pin stuck LOW (never went HIGH)")
                        print(f"[ULTRASONIC] Check: 1) Wiring to GPIO {self.echo_pin}, 2) Sensor power, 3) Trigger pin GPIO {self.trigger_pin}")
                        return -1
                
                # Check if we timed out
                if GPIO.input(self.echo_pin) == 0:
                    continue  # Retry
                
                # Echo started - now wait for it to go LOW
                pulse_end = time.time()
                echo_timeout = time.time()
                
                while GPIO.input(self.echo_pin) == 1:
                    pulse_end = time.time()
                    # Longer timeout for echo (max distance is ~4m = ~23ms round trip)
                    if (pulse_end - echo_timeout) > 0.03:  # 30ms timeout
                        if attempt < retries:
                            time.sleep(0.01)
                            break
                        print(f"[ULTRASONIC] Error: Echo pin stuck HIGH (never went LOW)")
                        print(f"[ULTRASONIC] This could mean: 1) No object in range, 2) Sensor malfunction")
                        return -1
                
                # Calculate time elapsed
                time_elapsed = pulse_end - pulse_start
                
                # Validate pulse width (should be between 150us and 25ms for HC-SR04)
                if time_elapsed < 0.00015:  # Less than 150 microseconds
                    if attempt < retries:
                        time.sleep(0.01)
                        continue
                    print(f"[ULTRASONIC] Error: Pulse too short ({time_elapsed*1000000:.1f}us) - signal noise")
                    return -3
                
                if time_elapsed > 0.025:  # More than 25 milliseconds
                    if attempt < retries:
                        time.sleep(0.01)
                        continue
                    # This is actually valid - just means object is far away
                    pass
                
                # Speed of sound: 343 m/s = 34300 cm/s
                # Distance = (Time x Speed) / 2 (round trip)
                distance = (time_elapsed * 34300) / 2
                
                # Sanity check: HC-SR04 range is 2cm to 400cm
                if distance < 2:
                    if attempt < retries:
                        time.sleep(0.01)
                        continue
                    print(f"[ULTRASONIC] Warning: Distance too close ({distance:.1f}cm) - may be inaccurate")
                    return 2.0  # Return minimum valid distance
                
                if distance > 400:
                    if attempt < retries:
                        time.sleep(0.01)
                        continue
                    # Object too far or no object detected
                    return -2
                
                # Valid reading
                return round(distance, 1)
                
            except Exception as e:
                print(f"[ULTRASONIC] Exception during measurement: {e}")
                if attempt < retries:
                    time.sleep(0.01)
                    continue
                return -1
        
        # All retries failed
        print(f"[ULTRASONIC] All {retries + 1} attempts failed")
        return -1

if __name__ == '__main__':
    # This block allows testing this file directly
    # It is not used when imported by SensorManager
    print("--- Ultrasonic Sensor Direct Test ---")
    # NOTE: This test uses BCM pins 23/24 by default.
    # The main app uses 27/22. We will use the main app's pins for this test.
    trigger = int(os.getenv('ULTRASONIC_TRIGGER_PIN', '27'))
    echo = int(os.getenv('ULTRASONIC_ECHO_PIN', '22'))
    
    ultrasonic_sensor = Ultrasonic(trigger_pin=trigger, echo_pin=echo)
    
    print(f"Testing with TRIGGER={trigger}, ECHO={echo}. Press Ctrl+C to exit.")
    
    try:
        while True:
            dist = ultrasonic_sensor.measure_distance()
            if dist == -1:
                # Timeout error already printed
                pass
            elif dist == -2:
                print("Measurement out of range.")
            else:
                print(f"Measured Distance = {dist:.1f} cm")
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nMeasurement stopped by User.")
    finally:
        GPIO.cleanup()
        print("GPIO cleanup complete.")
