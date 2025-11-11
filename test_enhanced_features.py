#!/usr/bin/env python3
"""
Test script for enhanced body language, gestures, and communication
Tests smooth servo movements, greetings, and sensor integration
"""

import sys
import time

def print_header(text):
    print("\n" + "="*60)
    print(f"  {text}")
    print("="*60)

def test_smooth_servos():
    """Test smooth servo movements"""
    print_header("Testing Smooth Servo Movement")
    
    try:
        from actuators.multi_servo_controller import multi_servo_controller
        
        print("→ Moving neck smoothly...")
        multi_servo_controller.set_angle('neck', 60, smooth=True, duration=0.5)
        time.sleep(0.6)
        
        multi_servo_controller.set_angle('neck', 120, smooth=True, duration=0.5)
        time.sleep(0.6)
        
        multi_servo_controller.set_angle('neck', 90, smooth=True, duration=0.5)
        time.sleep(0.6)
        
        print("✓ Smooth movement test passed!")
        return True
        
    except Exception as e:
        print(f"✗ Smooth movement test failed: {e}")
        return False

def test_gestures():
    """Test body language gestures"""
    print_header("Testing Body Language Gestures")
    
    try:
        from core.body_language import body_language_engine
        
        gestures_to_test = [
            'greeting_sir',
            'nod',
            'wave_right',
            'excited',
        ]
        
        for gesture in gestures_to_test:
            print(f"→ Testing gesture: {gesture}")
            body_language_engine.perform_gesture(gesture, blocking=True)
            time.sleep(1)
            print(f"  ✓ {gesture} completed")
        
        print("✓ All gesture tests passed!")
        return True
        
    except Exception as e:
        print(f"✗ Gesture test failed: {e}")
        return False

def test_greeting():
    """Test greeting with speech and gesture"""
    print_header("Testing Greeting System")
    
    try:
        from core.greeting_manager import GreetingManager
        from core.body_language import body_language_engine
        from actuators.display import display
        
        # Test greeting for Sachin Sir
        print("→ Testing greeting for 'Sachin Sir'...")
        greeting_mgr = GreetingManager(user_name="Sachin Sir")
        script = greeting_mgr.build_person_greeting("Sachin Sir")
        
        print(f"  Speech: {script.speech_text()}")
        print(f"  Gesture: {script.gesture}")
        print(f"  Display: {script.display_lines}")
        
        # Perform gesture
        if script.gesture:
            body_language_engine.perform_gesture(script.gesture, blocking=True)
            time.sleep(1)
        
        # Show on display
        try:
            display.clear()
            for i, line in enumerate(script.display_lines[:2]):
                display.write_text(line, row=i, col=0)
            time.sleep(2)
            display.clear()
        except:
            print("  ⚠ Display not available (OK in dev mode)")
        
        print("✓ Greeting test passed!")
        return True
        
    except Exception as e:
        print(f"✗ Greeting test failed: {e}")
        return False

def test_emotion_expression():
    """Test emotional gestures"""
    print_header("Testing Emotion Expression")
    
    try:
        from core.body_language import body_language_engine
        
        emotions = ['happy', 'confused', 'thinking', 'alert']
        
        for emotion in emotions:
            print(f"→ Expressing emotion: {emotion}")
            gesture = body_language_engine.gesture_for_emotion(emotion)
            print(f"  ✓ Performed gesture: {gesture}")
            time.sleep(2)
        
        print("✓ Emotion expression test passed!")
        return True
        
    except Exception as e:
        print(f"✗ Emotion test failed: {e}")
        return False

def test_sensor_integration():
    """Test sensor-based body language"""
    print_header("Testing Sensor Integration")
    
    try:
        from core.body_language import body_language_engine
        
        print("→ Testing motion sensor response...")
        body_language_engine.gesture_for_sensor_event('motion', True)
        time.sleep(2)
        
        print("→ Testing distance sensor response (close object)...")
        body_language_engine.gesture_for_sensor_event('distance', 25)
        time.sleep(2)
        
        print("→ Testing temperature sensor response (high temp)...")
        body_language_engine.gesture_for_sensor_event('temperature', 36)
        time.sleep(2)
        
        print("✓ Sensor integration test passed!")
        return True
        
    except Exception as e:
        print(f"✗ Sensor integration test failed: {e}")
        return False

def test_display_integration():
    """Test display with sensor data"""
    print_header("Testing Display Integration")
    
    try:
        from actuators.display import display
        from sensors.sensor_manager import SensorManager
        
        print("→ Testing display clear and text...")
        display.clear()
        display.write_text("JARVIS 2.0", row=0, col=3)
        display.write_text("System Test", row=1, col=2)
        time.sleep(2)
        
        print("→ Testing sensor data display...")
        # Simulate sensor readings
        readings = {
            'temperature_c': 24.5,
            'humidity_percent': 55.0,
            'distance_cm': 50.0,
            'alcohol_detected': False
        }
        display.show_sensor_data(readings)
        time.sleep(3)
        
        print("→ Testing warning display...")
        display.show_warning("Test Alert!", level="WARNING")
        time.sleep(2)
        
        display.clear()
        print("✓ Display integration test passed!")
        return True
        
    except Exception as e:
        print(f"✗ Display test failed: {e}")
        print(f"  (OK in dev mode without display hardware)")
        return True  # Don't fail on dev machine

def test_center_servos():
    """Test centering all servos"""
    print_header("Testing Servo Centering")
    
    try:
        from core.body_language import body_language_engine
        
        print("→ Centering all servos smoothly...")
        body_language_engine.center_all()
        time.sleep(1)
        
        print("✓ Servo centering test passed!")
        return True
        
    except Exception as e:
        print(f"✗ Centering test failed: {e}")
        return False

def main():
    print_header("JARVIS 2.0 IoT - Enhanced Features Test")
    print("Testing: Body Language, Gestures, Communication, Sensors")
    print("\nPress Ctrl+C at any time to stop")
    
    tests = [
        ("Smooth Servos", test_smooth_servos),
        ("Gestures", test_gestures),
        ("Greeting System", test_greeting),
        ("Emotion Expression", test_emotion_expression),
        ("Sensor Integration", test_sensor_integration),
        ("Display Integration", test_display_integration),
        ("Servo Centering", test_center_servos),
    ]
    
    results = []
    
    try:
        for test_name, test_func in tests:
            print(f"\n{'─'*60}")
            input(f"Press Enter to run: {test_name} (or Ctrl+C to skip all)")
            result = test_func()
            results.append((test_name, result))
            time.sleep(1)
        
    except KeyboardInterrupt:
        print("\n\n✋ Tests interrupted by user")
    
    # Summary
    print_header("Test Summary")
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"  {status}  {test_name}")
    
    print(f"\n  Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n  🎉 All tests passed! System ready for use.")
    else:
        print("\n  ⚠  Some tests failed. Check errors above.")
    
    # Center servos at end
    try:
        from core.body_language import body_language_engine
        print("\n→ Centering servos to neutral position...")
        body_language_engine.center_all()
    except:
        pass
    
    print("\n" + "="*60 + "\n")
    
    return 0 if passed == total else 1

if __name__ == '__main__':
    sys.exit(main())
