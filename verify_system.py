#!/usr/bin/env python3
"""
JARVIS System Verification Script
Checks all components and reports status
"""

import sys
import os

def print_header(text):
    print("\n" + "="*60)
    print(f"  {text}")
    print("="*60)

def check_import(module_name, package_name=None):
    """Check if a module can be imported"""
    try:
        __import__(module_name)
        print(f"  ✓ {package_name or module_name}")
        return True
    except ImportError as e:
        print(f"  ✗ {package_name or module_name} - {e}")
        return False

def check_file(filepath):
    """Check if a file exists"""
    if os.path.exists(filepath):
        print(f"  ✓ {filepath}")
        return True
    else:
        print(f"  ✗ {filepath} - Not found")
        return False

def main():
    print_header("JARVIS 2.0 IoT - System Verification")
    
    all_ok = True
    
    # Check Python version
    print_header("Python Version")
    version = sys.version_info
    if version.major >= 3 and version.minor >= 8:
        print(f"  ✓ Python {version.major}.{version.minor}.{version.micro}")
    else:
        print(f"  ✗ Python {version.major}.{version.minor}.{version.micro} (Need 3.8+)")
        all_ok = False
    
    # Check critical files
    print_header("Core Files")
    files = [
        'actuators/servo.py',
        'actuators/multi_servo_controller.py',
        'actuators/display.py',
        'sensors/sensor_manager.py',
        'sensors/sensor_fusion.py',
        'sensors/dht.py',
        'sensors/ultrasonic.py',
        'sensors/pir.py',
        'sensors/mq3.py',
        'core/jarvis_core.py',
        'setup_gpio_auto.sh',
    ]
    for f in files:
        if not check_file(f):
            all_ok = False
    
    # Check Python imports (non-hardware)
    print_header("Python Packages (Development)")
    packages = {
        'threading': 'threading',
        'time': 'time',
        'os': 'os',
        'typing': 'typing',
        'dataclasses': 'dataclasses',
        'enum': 'enum',
    }
    for module, name in packages.items():
        check_import(module, name)
    
    # Check hardware-specific imports (may fail on dev machine)
    print_header("Hardware Packages (Raspberry Pi Only)")
    hardware_packages = {
        'pigpio': 'pigpio',
        'RPi.GPIO': 'RPi.GPIO',
        'board': 'board (Adafruit Blinka)',
        'adafruit_dht': 'adafruit_dht',
        'RPLCD.i2c': 'RPLCD',
    }
    hw_count = 0
    for module, name in hardware_packages.items():
        if check_import(module, name):
            hw_count += 1
    
    if hw_count < len(hardware_packages):
        print("\n  ⚠ Some hardware packages missing (OK on dev machine)")
        print("  → Install on Raspberry Pi: pip3 install pigpio RPi.GPIO adafruit-circuitpython-dht RPLCD")
    
    # Check executable scripts
    print_header("Executable Scripts")
    scripts = [
        'setup_gpio_auto.sh',
        'install_gpio_service.sh',
    ]
    for script in scripts:
        if os.path.exists(script):
            is_executable = os.access(script, os.X_OK)
            if is_executable:
                print(f"  ✓ {script} (executable)")
            else:
                print(f"  ⚠ {script} (not executable - run: chmod +x {script})")
        else:
            print(f"  ✗ {script} - Not found")
            all_ok = False
    
    # Check new features
    print_header("New Features")
    features = {
        'Smooth Servo Movement': 'actuators/servo.py contains _smooth_move',
        'Sensor Fusion': 'sensors/sensor_fusion.py exists',
        'Display Integration': 'actuators/display.py contains show_sensor_data',
        'Auto GPIO Setup': 'setup_gpio_auto.sh exists',
    }
    
    # Simple checks for features
    if os.path.exists('actuators/servo.py'):
        with open('actuators/servo.py', 'r') as f:
            if '_smooth_move' in f.read():
                print("  ✓ Smooth Servo Movement")
            else:
                print("  ✗ Smooth Servo Movement - Not found")
                all_ok = False
    
    if os.path.exists('sensors/sensor_fusion.py'):
        print("  ✓ Sensor Fusion System")
    else:
        print("  ✗ Sensor Fusion System - Not found")
        all_ok = False
    
    if os.path.exists('actuators/display.py'):
        with open('actuators/display.py', 'r') as f:
            if 'show_sensor_data' in f.read():
                print("  ✓ Display Integration")
            else:
                print("  ✗ Display Integration - Not found")
                all_ok = False
    
    if os.path.exists('setup_gpio_auto.sh'):
        print("  ✓ Auto GPIO Setup")
    else:
        print("  ✗ Auto GPIO Setup - Not found")
        all_ok = False
    
    # Summary
    print_header("Summary")
    if all_ok:
        print("  ✓ All critical components verified!")
        print("  ✓ System ready for deployment to Raspberry Pi")
        print("\n  Next steps:")
        print("    1. Transfer to Raspberry Pi: git push/pull")
        print("    2. Install dependencies: pip3 install -r requirements.txt")
        print("    3. Setup GPIO: sudo ./install_gpio_service.sh")
        print("    4. Reboot: sudo reboot")
    else:
        print("  ⚠ Some components missing or not configured")
        print("  → Review errors above and fix before deploying")
    
    print("\n" + "="*60 + "\n")
    
    return 0 if all_ok else 1

if __name__ == '__main__':
    sys.exit(main())
