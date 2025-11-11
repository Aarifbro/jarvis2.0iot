#!/usr/bin/env python3
"""
Ultrasonic Sensor Diagnostic Test
Tests and diagnoses HC-SR04 ultrasonic sensor issues
"""

import os
import sys
import time

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("=" * 80)
print("ULTRASONIC SENSOR DIAGNOSTIC TEST".center(80))
print("=" * 80)
print()

# Configuration
TRIGGER_PIN = int(os.getenv('ULTRASONIC_TRIGGER_PIN', '27'))
ECHO_PIN = int(os.getenv('ULTRASONIC_ECHO_PIN', '22'))

print(f"Configuration:")
print(f"  Trigger Pin (BCM): {TRIGGER_PIN}")
print(f"  Echo Pin (BCM):    {ECHO_PIN}")
print()

# Test 1: Import ultrasonic module
print("[1/5] Testing module import...")
try:
    from sensors.ultrasonic import Ultrasonic
    print("✓ Ultrasonic module imported successfully")
except Exception as e:
    print(f"✗ Failed to import: {e}")
    sys.exit(1)

# Test 2: Create sensor instance
print("\n[2/5] Creating sensor instance...")
try:
    sensor = Ultrasonic(trigger_pin=TRIGGER_PIN, echo_pin=ECHO_PIN)
    print("✓ Ultrasonic sensor instance created")
except Exception as e:
    print(f"✗ Failed to create sensor: {e}")
    sys.exit(1)

# Test 3: Single measurement test
print("\n[3/5] Testing single measurement...")
try:
    distance = sensor.measure_distance(retries=3)
    
    if distance == -1:
        print("✗ Echo pin error detected!")
        print("  Possible causes:")
        print(f"    - Echo pin (GPIO {ECHO_PIN}) not connected properly")
        print(f"    - Trigger pin (GPIO {TRIGGER_PIN}) not connected properly")
        print("    - Sensor not powered (needs 5V)")
        print("    - Sensor malfunction")
    elif distance == -2:
        print("⚠ Out of range")
        print("  - No object within 4 meters")
        print("  - This is NORMAL if nothing is in front")
    elif distance == -3:
        print("⚠ Signal interference")
        print("  - Electrical noise detected")
        print("  - Try moving away from other electronics")
    elif distance is None:
        print("✗ Sensor not available")
    elif distance > 0:
        print(f"✓ Valid reading: {distance:.1f} cm")
    else:
        print(f"? Unknown result: {distance}")
        
except Exception as e:
    print(f"✗ Measurement failed: {e}")
    import traceback
    traceback.print_exc()

# Test 4: Multiple measurements (stability test)
print("\n[4/5] Testing measurement stability (10 readings)...")
try:
    readings = []
    errors = {'timeout': 0, 'out_of_range': 0, 'noise': 0, 'valid': 0}
    
    for i in range(10):
        distance = sensor.measure_distance(retries=2)
        readings.append(distance)
        
        if distance == -1:
            errors['timeout'] += 1
            print(f"  [{i+1}/10] Timeout/Echo error")
        elif distance == -2:
            errors['out_of_range'] += 1
            print(f"  [{i+1}/10] Out of range")
        elif distance == -3:
            errors['noise'] += 1
            print(f"  [{i+1}/10] Signal noise")
        elif distance and distance > 0:
            errors['valid'] += 1
            print(f"  [{i+1}/10] {distance:.1f} cm")
        
        time.sleep(0.2)  # 200ms between readings
    
    print(f"\n  Results:")
    print(f"    Valid readings:  {errors['valid']}/10")
    print(f"    Timeouts:        {errors['timeout']}/10")
    print(f"    Out of range:    {errors['out_of_range']}/10")
    print(f"    Noise:           {errors['noise']}/10")
    
    # Calculate statistics for valid readings
    valid_readings = [r for r in readings if r and r > 0]
    if valid_readings:
        avg = sum(valid_readings) / len(valid_readings)
        min_val = min(valid_readings)
        max_val = max(valid_readings)
        variation = max_val - min_val
        
        print(f"\n  Statistics (valid readings only):")
        print(f"    Average:    {avg:.1f} cm")
        print(f"    Min:        {min_val:.1f} cm")
        print(f"    Max:        {max_val:.1f} cm")
        print(f"    Variation:  {variation:.1f} cm")
        
        if variation < 5:
            print(f"    ✓ Excellent stability!")
        elif variation < 10:
            print(f"    ✓ Good stability")
        elif variation < 20:
            print(f"    ⚠ Moderate stability")
        else:
            print(f"    ✗ Poor stability - check sensor mounting")
    
    if errors['valid'] >= 8:
        print("\n✓ Sensor is working reliably!")
    elif errors['valid'] >= 5:
        print("\n⚠ Sensor is working but has some issues")
    else:
        print("\n✗ Sensor is unreliable - check wiring and power")
        
except KeyboardInterrupt:
    print("\n\nTest interrupted by user")
except Exception as e:
    print(f"✗ Stability test failed: {e}")

# Test 5: Sensor integration test
print("\n[5/5] Testing sensor manager integration...")
try:
    from sensors.sensor_manager import SensorManager
    mgr = SensorManager()
    
    distance = mgr.get_distance()
    if distance and distance > 0:
        print(f"✓ Sensor manager integration working: {distance:.1f} cm")
    elif distance == -2:
        print("✓ Sensor manager working (out of range reading)")
    else:
        print(f"⚠ Sensor manager returned: {distance}")
        
except Exception as e:
    print(f"⚠ Sensor manager test skipped: {e}")

# Summary and recommendations
print("\n" + "=" * 80)
print("DIAGNOSTIC SUMMARY".center(80))
print("=" * 80)
print()

print("WIRING CHECKLIST:")
print(f"  ☐ VCC  → 5V power")
print(f"  ☐ GND  → Ground")
print(f"  ☐ TRIG → GPIO {TRIGGER_PIN} (BCM numbering)")
print(f"  ☐ ECHO → GPIO {ECHO_PIN} (BCM numbering)")
print()

print("COMMON ISSUES & FIXES:")
print()
print("1. Echo pin stuck LOW (never goes HIGH):")
print("   → Check ECHO wire connection to GPIO {ECHO_PIN}")
print("   → Check sensor has 5V power")
print("   → Try different GPIO pins")
print()
print("2. Echo pin stuck HIGH (never goes LOW):")
print("   → Check TRIGGER wire connection to GPIO {TRIGGER_PIN}")
print("   → Sensor may be damaged")
print()
print("3. Out of range readings:")
print("   → NORMAL if no object within 4 meters")
print("   → Sensor works best with flat surfaces")
print("   → Avoid testing on sound-absorbing materials")
print()
print("4. Unstable/varying readings:")
print("   → Secure sensor mounting (vibrations cause issues)")
print("   → Keep sensor away from motors")
print("   → Add small capacitor (100nF) between VCC and GND")
print()

print("=" * 80)
print()

# Cleanup
try:
    import RPi.GPIO as GPIO
    GPIO.cleanup()
    print("✓ GPIO cleanup complete")
except:
    pass

print("\nDiagnostic test complete!")
print()
print("TIP: For live monitoring, run:")
print(f"  python3 sensors/ultrasonic_test.py")
