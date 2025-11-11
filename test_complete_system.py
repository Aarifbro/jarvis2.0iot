#!/usr/bin/env python3
"""
Complete System Test for JARVIS Robot
Tests all components: sensors, motors, servos, display, and tools integration
"""

import os
import sys
import time

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("=" * 80)
print("JARVIS COMPLETE SYSTEM TEST".center(80))
print("=" * 80)
print()

# Test results tracking
test_results = {
    'sensors': {},
    'motors': {},
    'servos': {},
    'tools': {},
    'display': None
}

def print_test(category, name, status, message=""):
    """Print formatted test result"""
    symbols = {'pass': '✓', 'fail': '✗', 'skip': '⊗', 'warn': '⚠'}
    colors = {'pass': '\033[92m', 'fail': '\033[91m', 'skip': '\033[93m', 'warn': '\033[93m', 'end': '\033[0m'}
    
    symbol = symbols.get(status, '?')
    color = colors.get(status, '')
    
    print(f"{color}[{symbol}] {category:12} | {name:25} | {message}{colors['end']}")
    
    if category in test_results:
        test_results[category][name] = {'status': status, 'message': message}
    else:
        test_results[category] = status


# ==============================================================================
# 1. SENSOR TESTS
# ==============================================================================
print("\n" + "=" * 80)
print("1. TESTING SENSORS".center(80))
print("=" * 80 + "\n")

try:
    from sensors.sensor_manager import SensorManager
    sensor_manager = SensorManager()
    sensor_manager.start()
    print_test("Sensors", "Initialization", "pass", "Sensor Manager started")
    time.sleep(1)
    
    # Test DHT11 (Temperature & Humidity)
    try:
        temp = sensor_manager.get_temperature()
        humidity = sensor_manager.get_humidity()
        if temp is not None:
            print_test("Sensors", "DHT11 Temperature", "pass", f"{temp}°C")
        else:
            print_test("Sensors", "DHT11 Temperature", "warn", "No reading")
        if humidity is not None:
            print_test("Sensors", "DHT11 Humidity", "pass", f"{humidity}%")
        else:
            print_test("Sensors", "DHT11 Humidity", "warn", "No reading")
    except Exception as e:
        print_test("Sensors", "DHT11", "fail", str(e))
    
    # Test Ultrasonic
    try:
        distance = sensor_manager.get_distance()
        if distance and distance > 0:
            print_test("Sensors", "Ultrasonic Distance", "pass", f"{distance:.1f} cm")
        else:
            print_test("Sensors", "Ultrasonic Distance", "warn", "Out of range")
    except Exception as e:
        print_test("Sensors", "Ultrasonic", "fail", str(e))
    
    # Test PIR Motion
    try:
        if sensor_manager.pir_sensor:
            stats = sensor_manager.pir_sensor.get_motion_stats()
            print_test("Sensors", "PIR Motion", "pass", f"Count: {stats['total_count']}, Active: {stats['is_active']}")
        else:
            print_test("Sensors", "PIR Motion", "skip", "Not enabled")
    except Exception as e:
        print_test("Sensors", "PIR Motion", "fail", str(e))
    
    # Test MQ3 Alcohol
    try:
        alcohol = sensor_manager.get_alcohol_level()
        if alcohol is not None:
            status = "Detected!" if alcohol else "Clear"
            print_test("Sensors", "MQ3 Alcohol", "pass", status)
        else:
            print_test("Sensors", "MQ3 Alcohol", "skip", "Not enabled")
    except Exception as e:
        print_test("Sensors", "MQ3 Alcohol", "fail", str(e))
    
except Exception as e:
    print_test("Sensors", "Overall", "fail", str(e))


# ==============================================================================
# 2. MOTOR TESTS
# ==============================================================================
print("\n" + "=" * 80)
print("2. TESTING MOTORS".center(80))
print("=" * 80 + "\n")

try:
    from actuators.motor_controller import get_motor_controller
    motor_controller = get_motor_controller()
    print_test("Motors", "Initialization", "pass", "Motor Controller ready")
    
    # Test forward movement
    try:
        print("Testing forward movement (1 second at 50% speed)...")
        motor_controller.forward(speed=50, duration=1, smooth=True)
        print_test("Motors", "Forward Movement", "pass", "Smooth acceleration")
    except Exception as e:
        print_test("Motors", "Forward Movement", "fail", str(e))
    
    time.sleep(0.5)
    
    # Test turn
    try:
        print("Testing left turn (0.5 seconds)...")
        motor_controller.left(speed=60, duration=0.5, smooth=True)
        print_test("Motors", "Turn Left", "pass", "Smooth turning")
    except Exception as e:
        print_test("Motors", "Turn Left", "fail", str(e))
    
    time.sleep(0.5)
    
    # Test arc turn
    try:
        print("Testing arc turn (1 second)...")
        motor_controller.arc_turn(direction='right', speed=70, duration=1)
        print_test("Motors", "Arc Turn", "pass", "Differential speed")
    except Exception as e:
        print_test("Motors", "Arc Turn", "fail", str(e))
    
    time.sleep(0.5)
    
    # Test stop
    try:
        motor_controller.stop(smooth=True)
        print_test("Motors", "Smooth Stop", "pass", "Deceleration applied")
    except Exception as e:
        print_test("Motors", "Smooth Stop", "fail", str(e))
    
except Exception as e:
    print_test("Motors", "Overall", "fail", str(e))


# ==============================================================================
# 3. SERVO TESTS
# ==============================================================================
print("\n" + "=" * 80)
print("3. TESTING SERVOS".center(80))
print("=" * 80 + "\n")

try:
    from actuators.multi_servo_controller import multi_servo_controller
    print_test("Servos", "Initialization", "pass", "Multi-Servo Controller ready")
    
    # Test neck servo
    try:
        neck = multi_servo_controller.get_servo('neck')
        if neck:
            print("Testing neck servo smooth movement...")
            neck.set_angle(60, smooth=True, duration=0.5)
            time.sleep(0.6)
            neck.set_angle(90, smooth=True, duration=0.5)
            time.sleep(0.6)
            print_test("Servos", "Neck Movement", "pass", "Smooth ease-in-out")
        else:
            print_test("Servos", "Neck Movement", "skip", "Not available")
    except Exception as e:
        print_test("Servos", "Neck Movement", "fail", str(e))
    
    # Test arm servos
    try:
        arm_l = multi_servo_controller.get_servo('arm_l')
        arm_r = multi_servo_controller.get_servo('arm_r')
        if arm_l and arm_r:
            print("Testing both arm servos...")
            multi_servo_controller.set_angle('arm_l', 45, smooth=True)
            multi_servo_controller.set_angle('arm_r', 135, smooth=True)
            time.sleep(0.8)
            multi_servo_controller.set_angle('arm_l', 90, smooth=True)
            multi_servo_controller.set_angle('arm_r', 90, smooth=True)
            time.sleep(0.8)
            print_test("Servos", "Arm Movement", "pass", "Both arms synchronized")
        else:
            print_test("Servos", "Arm Movement", "skip", "Not available")
    except Exception as e:
        print_test("Servos", "Arm Movement", "fail", str(e))
    
except Exception as e:
    print_test("Servos", "Overall", "fail", str(e))


# ==============================================================================
# 4. BODY LANGUAGE TESTS
# ==============================================================================
print("\n" + "=" * 80)
print("4. TESTING BODY LANGUAGE".center(80))
print("=" * 80 + "\n")

try:
    from core.body_language import body_language_engine
    print_test("Body Language", "Initialization", "pass", "Engine loaded")
    
    # Test greeting gesture
    try:
        print("Performing greeting_sir gesture...")
        body_language_engine.perform_gesture('greeting_sir', blocking=True)
        print_test("Body Language", "Greeting Gesture", "pass", "Bow + wave completed")
    except Exception as e:
        print_test("Body Language", "Greeting Gesture", "fail", str(e))
    
    time.sleep(1)
    
    # Test nod gesture
    try:
        print("Performing nod gesture...")
        body_language_engine.perform_gesture('nod', blocking=True)
        print_test("Body Language", "Nod Gesture", "pass", "Head movement")
    except Exception as e:
        print_test("Body Language", "Nod Gesture", "fail", str(e))
    
except Exception as e:
    print_test("Body Language", "Overall", "fail", str(e))


# ==============================================================================
# 5. DISPLAY TESTS
# ==============================================================================
print("\n" + "=" * 80)
print("5. TESTING DISPLAY".center(80))
print("=" * 80 + "\n")

try:
    from actuators.display import display
    display.clear()
    print_test("Display", "Initialization", "pass", "LCD ready")
    
    # Test text display
    try:
        display.write_text("JARVIS", row=0, col=5)
        display.write_text("System OK", row=1, col=3)
        print_test("Display", "Text Display", "pass", "Characters shown")
        time.sleep(2)
    except Exception as e:
        print_test("Display", "Text Display", "fail", str(e))
    
    # Test sensor data display
    try:
        if sensor_manager:
            display.show_sensor_data(sensor_manager)
            print_test("Display", "Sensor Data", "pass", "Temp/Distance shown")
            time.sleep(2)
    except Exception as e:
        print_test("Display", "Sensor Data", "fail", str(e))
    
    # Test face display
    try:
        display.show_face("happy")
        print_test("Display", "Emoji Face", "pass", "Happy face shown")
        time.sleep(2)
        display.clear()
    except Exception as e:
        print_test("Display", "Emoji Face", "fail", str(e))
    
except Exception as e:
    print_test("Display", "Overall", "fail", str(e))


# ==============================================================================
# 6. TOOLS INTEGRATION TEST
# ==============================================================================
print("\n" + "=" * 80)
print("6. TESTING TOOLS INTEGRATION".center(80))
print("=" * 80 + "\n")

# Test Motor Tools
try:
    from tools.motor_tools import all_motor_tools
    print_test("Tools", "Motor Tools", "pass", f"{len(all_motor_tools)} tools loaded")
except Exception as e:
    print_test("Tools", "Motor Tools", "fail", str(e))

# Test Robot Tools
try:
    from tools.robot_tools import all_robot_tools
    print_test("Tools", "Robot Tools", "pass", f"{len(all_robot_tools)} tools loaded")
except Exception as e:
    print_test("Tools", "Robot Tools", "fail", str(e))

# Test Sensor Tools
try:
    from tools.sensor_tools import all_sensor_tools
    print_test("Tools", "Sensor Tools", "pass", f"{len(all_sensor_tools)} tools loaded")
except Exception as e:
    print_test("Tools", "Sensor Tools", "fail", str(e))

# Test Communication Tools
try:
    from tools.communication_tools import all_communication_tools
    print_test("Tools", "Communication Tools", "pass", f"{len(all_communication_tools)} tools loaded")
except Exception as e:
    print_test("Tools", "Communication Tools", "fail", str(e))


# ==============================================================================
# FINAL SUMMARY
# ==============================================================================
print("\n" + "=" * 80)
print("TEST SUMMARY".center(80))
print("=" * 80 + "\n")

total_tests = 0
passed_tests = 0
failed_tests = 0
skipped_tests = 0

for category, tests in test_results.items():
    if isinstance(tests, dict):
        for name, result in tests.items():
            total_tests += 1
            if result['status'] == 'pass':
                passed_tests += 1
            elif result['status'] == 'fail':
                failed_tests += 1
            elif result['status'] == 'skip':
                skipped_tests += 1

print(f"Total Tests:   {total_tests}")
print(f"✓ Passed:      {passed_tests}")
print(f"✗ Failed:      {failed_tests}")
print(f"⊗ Skipped:     {skipped_tests}")
print()

pass_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
print(f"Pass Rate:     {pass_rate:.1f}%")

if pass_rate >= 80:
    print("\n" + "🎉 EXCELLENT! System is working great! 🎉".center(80))
elif pass_rate >= 60:
    print("\n" + "👍 GOOD! Most systems operational.".center(80))
else:
    print("\n" + "⚠️  WARNING! Multiple system failures detected.".center(80))

print("\n" + "=" * 80)

# Cleanup
try:
    if 'sensor_manager' in locals():
        sensor_manager.stop()
    if 'motor_controller' in locals():
        motor_controller.cleanup()
    if 'multi_servo_controller' in locals():
        multi_servo_controller.cleanup()
    print("\n✓ Cleanup completed")
except:
    pass

print("\nTest complete!")
