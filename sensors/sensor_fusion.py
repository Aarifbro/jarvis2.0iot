"""
Sensor Fusion System for JARVIS
Combines data from multiple sensors to provide intelligent monitoring and warnings.
"""

import time
import threading
from typing import Dict, Optional, List, Callable
from dataclasses import dataclass
from enum import Enum


class AlertLevel(Enum):
    """Alert severity levels"""
    NORMAL = 0
    INFO = 1
    WARNING = 2
    CRITICAL = 3


@dataclass
class SensorReading:
    """Container for sensor reading with metadata"""
    sensor_name: str
    value: float
    unit: str
    timestamp: float
    status: str = "OK"
    alert_level: AlertLevel = AlertLevel.NORMAL


@dataclass
class Alert:
    """Sensor alert/warning"""
    sensor_name: str
    message: str
    level: AlertLevel
    timestamp: float
    value: Optional[float] = None


class SensorFusion:
    """
    Intelligent sensor fusion system that:
    - Combines readings from multiple sensors
    - Detects anomalies and patterns
    - Generates contextual alerts
    - Provides aggregated environmental data
    """
    
    def __init__(self, sensor_manager, display=None):
        """
        Initialize sensor fusion system
        
        Args:
            sensor_manager: SensorManager instance
            display: Display instance for showing alerts (optional)
        """
        self.sensor_manager = sensor_manager
        self.display = display
        
        # Storage for sensor data
        self.readings: Dict[str, List[SensorReading]] = {
            'temperature': [],
            'humidity': [],
            'distance': [],
            'motion': [],
            'alcohol': []
        }
        
        # Alert thresholds (configurable)
        self.thresholds = {
            'temperature_high': 35.0,  # Celsius
            'temperature_low': 10.0,
            'humidity_high': 80.0,     # Percent
            'humidity_low': 20.0,
            'distance_close': 20.0,    # cm
            'distance_far': 300.0
        }
        
        # Active alerts
        self.active_alerts: List[Alert] = []
        self.alert_callbacks: List[Callable] = []
        
        # Monitoring state
        self._monitoring = False
        self._monitor_thread = None
        self._update_interval = 2.0  # seconds
        
        print("✓ Sensor Fusion System initialized")
    
    def add_alert_callback(self, callback: Callable):
        """Add a callback function to be called when alerts are generated"""
        self.alert_callbacks.append(callback)
    
    def set_threshold(self, name: str, value: float):
        """Update a threshold value"""
        if name in self.thresholds:
            self.thresholds[name] = value
            print(f"✓ Threshold '{name}' updated to {value}")
        else:
            print(f"⚠ Unknown threshold: {name}")
    
    def start_monitoring(self, interval: float = 2.0):
        """Start continuous sensor monitoring and fusion"""
        if self._monitoring:
            print("Sensor fusion already monitoring")
            return
        
        self._update_interval = interval
        self._monitoring = True
        self._monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self._monitor_thread.start()
        print("✓ Sensor fusion monitoring started")
    
    def stop_monitoring(self):
        """Stop sensor monitoring"""
        if self._monitoring:
            self._monitoring = False
            if self._monitor_thread:
                self._monitor_thread.join(timeout=5)
            print("✓ Sensor fusion monitoring stopped")
    
    def _monitor_loop(self):
        """Main monitoring loop"""
        while self._monitoring:
            try:
                self.update_all_sensors()
                self._check_for_alerts()
                time.sleep(self._update_interval)
            except Exception as e:
                print(f"[FUSION] Monitor loop error: {e}")
                time.sleep(1)
    
    def update_all_sensors(self):
        """Read and update all sensor data"""
        current_time = time.time()
        
        # Temperature & Humidity (DHT)
        if self.sensor_manager.dht_sensor:
            try:
                temp = self.sensor_manager.get_temperature()
                if temp is not None:
                    reading = SensorReading(
                        sensor_name='temperature',
                        value=temp,
                        unit='°C',
                        timestamp=current_time
                    )
                    self._add_reading('temperature', reading)
                
                humidity = self.sensor_manager.get_humidity()
                if humidity is not None:
                    reading = SensorReading(
                        sensor_name='humidity',
                        value=humidity,
                        unit='%',
                        timestamp=current_time
                    )
                    self._add_reading('humidity', reading)
            except Exception as e:
                print(f"[FUSION] DHT read error: {e}")
        
        # Distance (Ultrasonic)
        if self.sensor_manager.ultrasonic_sensor:
            try:
                distance = self.sensor_manager.get_distance()
                if distance is not None and distance > 0:
                    reading = SensorReading(
                        sensor_name='distance',
                        value=distance,
                        unit='cm',
                        timestamp=current_time
                    )
                    self._add_reading('distance', reading)
            except Exception as e:
                print(f"[FUSION] Ultrasonic read error: {e}")
        
        # Alcohol (MQ3)
        if self.sensor_manager.mq3_sensor:
            try:
                alcohol = self.sensor_manager.get_alcohol_level()
                if alcohol is not None:
                    reading = SensorReading(
                        sensor_name='alcohol',
                        value=1.0 if alcohol else 0.0,
                        unit='detected',
                        timestamp=current_time
                    )
                    self._add_reading('alcohol', reading)
            except Exception as e:
                print(f"[FUSION] MQ3 read error: {e}")
    
    def _add_reading(self, sensor_type: str, reading: SensorReading):
        """Add a reading and maintain history (keep last 100)"""
        if sensor_type not in self.readings:
            self.readings[sensor_type] = []
        
        self.readings[sensor_type].append(reading)
        
        # Keep only last 100 readings
        if len(self.readings[sensor_type]) > 100:
            self.readings[sensor_type] = self.readings[sensor_type][-100:]
    
    def _check_for_alerts(self):
        """Analyze sensor data and generate alerts"""
        new_alerts = []
        
        # Temperature alerts
        temp_readings = self.readings.get('temperature', [])
        if temp_readings:
            latest_temp = temp_readings[-1]
            if latest_temp.value > self.thresholds['temperature_high']:
                alert = Alert(
                    sensor_name='temperature',
                    message=f"High temperature: {latest_temp.value:.1f}°C",
                    level=AlertLevel.WARNING,
                    timestamp=latest_temp.timestamp,
                    value=latest_temp.value
                )
                new_alerts.append(alert)
            elif latest_temp.value < self.thresholds['temperature_low']:
                alert = Alert(
                    sensor_name='temperature',
                    message=f"Low temperature: {latest_temp.value:.1f}°C",
                    level=AlertLevel.WARNING,
                    timestamp=latest_temp.timestamp,
                    value=latest_temp.value
                )
                new_alerts.append(alert)
        
        # Humidity alerts
        humidity_readings = self.readings.get('humidity', [])
        if humidity_readings:
            latest_humidity = humidity_readings[-1]
            if latest_humidity.value > self.thresholds['humidity_high']:
                alert = Alert(
                    sensor_name='humidity',
                    message=f"High humidity: {latest_humidity.value:.1f}%",
                    level=AlertLevel.WARNING,
                    timestamp=latest_humidity.timestamp,
                    value=latest_humidity.value
                )
                new_alerts.append(alert)
            elif latest_humidity.value < self.thresholds['humidity_low']:
                alert = Alert(
                    sensor_name='humidity',
                    message=f"Low humidity: {latest_humidity.value:.1f}%",
                    level=AlertLevel.INFO,
                    timestamp=latest_humidity.timestamp,
                    value=latest_humidity.value
                )
                new_alerts.append(alert)
        
        # Distance alerts (obstacle detection)
        distance_readings = self.readings.get('distance', [])
        if distance_readings:
            latest_distance = distance_readings[-1]
            if latest_distance.value < self.thresholds['distance_close']:
                alert = Alert(
                    sensor_name='distance',
                    message=f"Obstacle detected: {latest_distance.value:.1f}cm",
                    level=AlertLevel.WARNING,
                    timestamp=latest_distance.timestamp,
                    value=latest_distance.value
                )
                new_alerts.append(alert)
        
        # Alcohol detection
        alcohol_readings = self.readings.get('alcohol', [])
        if alcohol_readings:
            latest_alcohol = alcohol_readings[-1]
            if latest_alcohol.value > 0:
                alert = Alert(
                    sensor_name='alcohol',
                    message="Alcohol detected!",
                    level=AlertLevel.CRITICAL,
                    timestamp=latest_alcohol.timestamp,
                    value=latest_alcohol.value
                )
                new_alerts.append(alert)
        
        # Process new alerts
        for alert in new_alerts:
            self._handle_alert(alert)
    
    def _handle_alert(self, alert: Alert):
        """Handle a new alert"""
        # Avoid duplicate alerts (within 30 seconds)
        for existing in self.active_alerts:
            if (existing.sensor_name == alert.sensor_name and 
                alert.timestamp - existing.timestamp < 30):
                return  # Skip duplicate
        
        # Add to active alerts
        self.active_alerts.append(alert)
        
        # Keep only last 50 alerts
        if len(self.active_alerts) > 50:
            self.active_alerts = self.active_alerts[-50:]
        
        # Log alert
        level_icons = {
            AlertLevel.INFO: "ℹ️",
            AlertLevel.WARNING: "⚠️",
            AlertLevel.CRITICAL: "🚨"
        }
        icon = level_icons.get(alert.level, "•")
        print(f"{icon} ALERT [{alert.sensor_name}]: {alert.message}")
        
        # Display on screen if available
        if self.display:
            try:
                self._display_alert(alert)
            except Exception as e:
                print(f"[FUSION] Display error: {e}")
        
        # Call callbacks
        for callback in self.alert_callbacks:
            try:
                callback(alert)
            except Exception as e:
                print(f"[FUSION] Callback error: {e}")
    
    def _display_alert(self, alert: Alert):
        """Display alert on screen"""
        if not self.display:
            return
        
        try:
            self.display.clear()
            
            # Show alert icon based on level
            if alert.level == AlertLevel.CRITICAL:
                self.display.write_text("! ALERT !", row=0, col=4)
            elif alert.level == AlertLevel.WARNING:
                self.display.write_text("WARNING", row=0, col=4)
            else:
                self.display.write_text("Notice", row=0, col=5)
            
            # Show message (truncate if needed)
            msg = alert.message[:20]  # Fit to display width
            self.display.write_text(msg, row=1, col=0)
            
        except Exception as e:
            print(f"[FUSION] Display alert error: {e}")
    
    def get_latest_reading(self, sensor_type: str) -> Optional[SensorReading]:
        """Get the most recent reading for a sensor type"""
        readings = self.readings.get(sensor_type, [])
        return readings[-1] if readings else None
    
    def get_sensor_summary(self) -> Dict:
        """Get summary of all sensor data"""
        summary = {}
        
        for sensor_type, readings in self.readings.items():
            if readings:
                latest = readings[-1]
                summary[sensor_type] = {
                    'value': latest.value,
                    'unit': latest.unit,
                    'status': latest.status,
                    'timestamp': latest.timestamp
                }
        
        return summary
    
    def display_sensor_dashboard(self):
        """Display all sensor readings on the I2C display"""
        if not self.display:
            print("No display available")
            return
        
        try:
            self.display.clear()
            
            # Get latest readings
            temp = self.get_latest_reading('temperature')
            humidity = self.get_latest_reading('humidity')
            distance = self.get_latest_reading('distance')
            
            row = 0
            
            # Temperature
            if temp:
                line = f"T:{temp.value:.1f}C"
                self.display.write_text(line, row=row, col=0)
                row += 1
            
            # Humidity
            if humidity:
                line = f"H:{humidity.value:.1f}%"
                self.display.write_text(line, row=row, col=0)
                row += 1
            
            # Distance
            if distance:
                line = f"D:{distance.value:.1f}cm"
                self.display.write_text(line, row=row, col=0)
                row += 1
            
            # Alert count
            if self.active_alerts:
                recent_alerts = [a for a in self.active_alerts 
                               if time.time() - a.timestamp < 60]
                if recent_alerts:
                    line = f"Alerts:{len(recent_alerts)}"
                    self.display.write_text(line, row=row, col=0)
            
        except Exception as e:
            print(f"[FUSION] Display dashboard error: {e}")
    
    def clear_old_alerts(self, max_age_seconds: float = 300):
        """Clear alerts older than specified age"""
        current_time = time.time()
        self.active_alerts = [
            a for a in self.active_alerts 
            if current_time - a.timestamp < max_age_seconds
        ]
    
    def get_environment_status(self) -> str:
        """Get overall environment status as string"""
        summary = self.get_sensor_summary()
        
        if not summary:
            return "No sensor data available"
        
        status_parts = []
        
        if 'temperature' in summary:
            temp = summary['temperature']['value']
            status_parts.append(f"Temp: {temp:.1f}°C")
        
        if 'humidity' in summary:
            hum = summary['humidity']['value']
            status_parts.append(f"Humidity: {hum:.1f}%")
        
        if 'distance' in summary:
            dist = summary['distance']['value']
            if dist < 50:
                status_parts.append(f"Object at {dist:.0f}cm")
        
        # Check for active critical alerts
        critical = [a for a in self.active_alerts if a.level == AlertLevel.CRITICAL]
        if critical:
            status_parts.append(f"{len(critical)} critical alerts!")
        
        return " | ".join(status_parts) if status_parts else "All sensors normal"
