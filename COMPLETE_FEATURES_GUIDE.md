# JARVIS 2.0 IoT - Complete Setup & Features Guide

## 🚀 Recent Improvements

### ✅ Fixed Issues

1. **Smooth Servo Movement**
   - Added ease-in-out interpolation for natural motion
   - Eliminated stuttering and sticking
   - Configurable smooth movement duration
   - Non-blocking servo operations

2. **Robust Sensor Integration**
   - Retry logic for DHT temperature/humidity sensor
   - Improved ultrasonic sensor with timeout handling
   - Better error recovery for all sensors
   - Graceful degradation when sensors fail

3. **Sensor Fusion System** 🆕
   - Combines data from multiple sensors intelligently
   - Automatic anomaly detection
   - Contextual alerts (INFO, WARNING, CRITICAL)
   - Real-time environmental monitoring

4. **I2C Display Integration** 🆕
   - Show sensor readings on LCD display
   - Alert/warning display system
   - Scrolling messages for long text
   - Automatic sensor dashboard

5. **Auto GPIO Enable on Boot** 🆕
   - Systemd service for automatic GPIO setup
   - No manual intervention needed
   - Auto-start pigpio daemon
   - Persistent across reboots

6. **Comprehensive Error Handling**
   - Try-catch blocks throughout codebase
   - Graceful fallbacks for all failures
   - Detailed error logging
   - Simulation mode when hardware unavailable

---

## 📦 Installation on Raspberry Pi

### 1. Install Dependencies

```bash
# Update system
sudo apt-get update && sudo apt-get upgrade -y

# Install Python and GPIO libraries
sudo apt-get install -y python3 python3-pip python3-dev
sudo apt-get install -y pigpio python3-pigpio
sudo apt-get install -y i2c-tools python3-smbus

# Install Python packages
pip3 install -r requirements.txt
```

### 2. Enable Hardware Interfaces

```bash
# Run the auto-setup script
./setup_gpio_auto.sh

# Or install as systemd service (runs on every boot)
sudo ./install_gpio_service.sh
```

### 3. Verify Installation

```bash
# Check pigpio daemon
pgrep pigpiod

# Test I2C
sudo i2cdetect -y 1

# Test sensors
python3 sensors/dht.py
python3 sensors/ultrasonic_test.py
```

---

## 🎯 New Features

### 1. Smooth Servo Control

**Usage:**
```python
from actuators.multi_servo_controller import multi_servo_controller

# Smooth movement (recommended)
multi_servo_controller.set_angle('neck', 90, smooth=True, duration=0.5)

# Instant movement
multi_servo_controller.set_angle_blocking('neck', 45)
```

**Features:**
- Ease-in-out acceleration curve
- Prevents servo jitter and stuttering
- Configurable movement duration
- Thread-safe operations

---

### 2. Sensor Fusion System

**Setup:**
```python
from sensors.sensor_manager import SensorManager
from actuators.display import display

# Initialize sensors
sensor_manager = SensorManager()
sensor_manager.start()

# Enable sensor fusion with display
fusion = sensor_manager.enable_sensor_fusion(display=display)

# Start monitoring
fusion.start_monitoring(interval=2.0)
```

**Features:**
- **Intelligent Monitoring:** Combines temperature, humidity, distance, motion, alcohol sensors
- **Alert System:** Automatic detection of abnormal conditions
- **Thresholds:** Configurable for temperature, humidity, distance
- **History Tracking:** Stores last 100 readings per sensor
- **Display Integration:** Shows alerts on I2C LCD

**Thresholds (adjustable):**
```python
fusion.set_threshold('temperature_high', 35.0)  # Celsius
fusion.set_threshold('temperature_low', 10.0)
fusion.set_threshold('humidity_high', 80.0)     # Percent
fusion.set_threshold('humidity_low', 20.0)
fusion.set_threshold('distance_close', 20.0)    # cm
```

**Get Status:**
```python
# Get latest reading
temp_reading = fusion.get_latest_reading('temperature')

# Get all sensor summary
summary = fusion.get_sensor_summary()

# Get environment status string
status = fusion.get_environment_status()
print(status)  # "Temp: 24.5°C | Humidity: 55.0% | All sensors normal"
```

---

### 3. Display Sensor Data on I2C

**Usage:**
```python
from actuators.display import display
from sensors.sensor_manager import SensorManager

sensor_manager = SensorManager()

# Show sensor readings
readings = sensor_manager.get_all_readings()
display.show_sensor_data(readings)

# Show warnings
display.show_warning("High Temperature!", level="WARNING")

# Show scrolling message
display.show_scrolling_message("This is a very long status message that needs to scroll")
```

**Display Formats:**
- **Row 1:** Temperature and Humidity (e.g., "T:24.5C H:55%")
- **Row 2:** Distance and alerts (e.g., "D:30cm ALCOHOL!")

---

### 4. Auto GPIO Enable on Boot

**Installation:**
```bash
# One-time setup (installs systemd service)
sudo ./install_gpio_service.sh
```

**What it does:**
- ✓ Adds user to `gpio` group
- ✓ Sets GPIO permissions
- ✓ Enables I2C and SPI interfaces
- ✓ Loads kernel modules
- ✓ Starts pigpio daemon
- ✓ Runs automatically on every boot

**Management:**
```bash
# Check status
sudo systemctl status jarvis-gpio

# View logs
sudo journalctl -u jarvis-gpio -f

# Restart
sudo systemctl restart jarvis-gpio

# Disable auto-start
sudo systemctl disable jarvis-gpio
```

---

## 🔧 Configuration

### Environment Variables

```bash
# Servo Pins (BCM)
SERVO_PIN_NECK=18
SERVO_PIN_ARM_L=25
SERVO_PIN_ARM_R=23

# Sensor Pins
PIR_PIN=17
ULTRASONIC_TRIGGER_PIN=27
ULTRASONIC_ECHO_PIN=22
DHT_PIN=4
DHT_TYPE=11

# MQ3 Alcohol Sensor
MQ3_ENABLED=true
MQ3_DIGITAL_PIN=26

# Display
DISPLAY_IDLE_ANIMATION_DELAY=15
```

### Servo Calibration

Edit servo config in `actuators/multi_servo_controller.py`:
```python
servo_configs = {
    'neck': {
        'pin': 18,
        'min_pulse': 500,     # Adjust if servo binds
        'max_pulse': 2400,    # Adjust if servo binds
        'angle_offset': 0,    # Logical angle offset
        'min_angle': 0,       # Safety limit
        'max_angle': 180,     # Safety limit
        'reverse': False,     # Reverse direction
    }
}
```

---

## 🧪 Testing

### Test Servo Smooth Movement
```bash
python3 test_neck_servo.py
```

### Test Sensors
```bash
# Individual sensors
python3 sensors/dht.py
python3 sensors/ultrasonic_test.py
python3 sensors/mq3_test.py

# All sensors
python3 test_sensor_commands.py
```

### Test Sensor Fusion
```python
from sensors.sensor_manager import SensorManager
from actuators.display import display

sensor_manager = SensorManager()
sensor_manager.start()

fusion = sensor_manager.enable_sensor_fusion(display=display)
fusion.start_monitoring()

# Monitor for 60 seconds
import time
time.sleep(60)

# Display dashboard
fusion.display_sensor_dashboard()

# Stop
fusion.stop_monitoring()
sensor_manager.stop()
```

---

## 📊 Sensor Fusion Dashboard

The sensor fusion system provides a real-time dashboard:

```python
fusion.display_sensor_dashboard()
```

**Shows:**
- Current temperature (°C)
- Current humidity (%)
- Distance to nearest object (cm)
- Active alert count

**Updates automatically** when monitoring is enabled.

---

## 🚨 Alert System

Sensor fusion automatically generates alerts:

| Alert Level | Trigger | Action |
|------------|---------|--------|
| **INFO** | Low humidity | Log only |
| **WARNING** | High/low temp, high humidity, close obstacle | Log + Display |
| **CRITICAL** | Alcohol detected | Log + Display + Callback |

**Add custom alert callback:**
```python
def my_alert_handler(alert):
    print(f"ALERT: {alert.message}")
    # Send notification, trigger action, etc.

fusion.add_alert_callback(my_alert_handler)
```

---

## 🛠️ Troubleshooting

### Servos Not Moving
1. Check pigpio daemon: `pgrep pigpiod`
2. Start daemon: `sudo pigpiod` or `./setup_gpio_auto.sh`
3. Check wiring: Servo signal wire to correct GPIO pin
4. Check power: Servos need external 5V power supply

### Sensors Not Reading
1. Check I2C devices: `sudo i2cdetect -y 1`
2. Enable interfaces: `sudo raspi-config` → Interfacing Options
3. Check wiring: Use BCM pin numbers (not physical)
4. Test individual sensors with test scripts

### Display Not Working
1. Check I2C address: `sudo i2cdetect -y 1` (usually 0x27 or 0x3F)
2. Update address in code if different
3. Check contrast potentiometer on display backpack
4. Verify 5V power to display

### GPIO Permissions
```bash
# Add user to gpio group
sudo usermod -a -G gpio $USER

# Reboot or re-login
sudo reboot
```

---

## 📝 Code Examples

### Complete Integration Example

```python
from sensors.sensor_manager import SensorManager
from actuators.display import display
from actuators.multi_servo_controller import multi_servo_controller

# Initialize everything
sensor_manager = SensorManager()
sensor_manager.start()

# Enable sensor fusion
fusion = sensor_manager.enable_sensor_fusion(display=display)
fusion.start_monitoring(interval=2.0)

# Add custom alert handler
def handle_alert(alert):
    if alert.level == AlertLevel.CRITICAL:
        # Turn neck servo to look at alert source
        multi_servo_controller.set_angle('neck', 90, smooth=True)
    display.show_warning(alert.message, level=alert.level.name)

fusion.add_alert_callback(handle_alert)

# Main loop
try:
    while True:
        # Display sensor dashboard every 5 seconds
        fusion.display_sensor_dashboard()
        time.sleep(5)
except KeyboardInterrupt:
    print("Shutting down...")
finally:
    fusion.stop_monitoring()
    sensor_manager.stop()
    display.cleanup()
```

---

## 📚 API Reference

### Servo Control
- `set_angle(name, angle, smooth=True, duration=0.5)` - Move servo smoothly
- `set_angle_blocking(name, angle)` - Instant movement
- `center(name)` - Move to 90°

### Sensor Manager
- `start()` - Start sensor monitoring
- `stop()` - Stop monitoring
- `get_temperature()` - Get DHT temperature (°C)
- `get_humidity()` - Get DHT humidity (%)
- `get_distance()` - Get ultrasonic distance (cm)
- `get_alcohol_level()` - Get MQ3 detection (bool)
- `enable_sensor_fusion(display)` - Enable fusion system

### Sensor Fusion
- `start_monitoring(interval)` - Start fusion monitoring
- `stop_monitoring()` - Stop monitoring
- `get_latest_reading(sensor_type)` - Get latest reading
- `get_sensor_summary()` - Get all sensor summary
- `display_sensor_dashboard()` - Update display
- `set_threshold(name, value)` - Update threshold
- `add_alert_callback(callback)` - Add alert handler

### Display
- `show_sensor_data(readings)` - Display sensor data
- `show_warning(message, level)` - Display warning
- `show_scrolling_message(message)` - Scroll long text
- `show_face(name)` - Show emoji face
- `write_text(text, row, col)` - Write text
- `clear()` - Clear display

---

## 🎓 Best Practices

1. **Always use smooth servo movement** for natural motion
2. **Enable sensor fusion** for intelligent monitoring
3. **Install auto GPIO service** on Raspberry Pi for convenience
4. **Add error callbacks** to sensor fusion for custom actions
5. **Use try-except blocks** when calling hardware functions
6. **Check sensor availability** before reading (`if sensor_manager.dht_sensor:`)
7. **Display sensor data regularly** to monitor system health

---

## 📄 License

MIT License - See LICENSE file for details

---

## 👨‍💻 Developer: @Aarifbro

**Version:** 2.0  
**Last Updated:** November 11, 2025
