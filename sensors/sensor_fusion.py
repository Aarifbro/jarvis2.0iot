"""
Sensor Fusion System for JARVIS
Combines data from multiple sensors to provide intelligent monitoring and warnings.

Features:
- Multi-sensor cross-validation (PIR + Ultrasonic for motion)
- Predictive analytics (trend forecasting)
- Anomaly detection
- Pattern learning
- Context-aware alerts
- Behavioral learning
"""

import time
import threading
import json
import os
from typing import Dict, Optional, List, Callable, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
from collections import deque
import statistics
from datetime import datetime


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
    confidence: float = 1.0  # Confidence score (0-1)
    verified: bool = False  # Cross-validated by multiple sensors


@dataclass
class Prediction:
    """Predicted sensor value"""
    sensor_name: str
    predicted_value: float
    confidence: float
    time_ahead: float  # seconds
    timestamp: float


@dataclass
class Pattern:
    """Detected sensor pattern"""
    name: str
    description: str
    sensors_involved: List[str]
    frequency: int  # How many times seen
    last_seen: float
    confidence: float


class SensorFusion:
    """
    Intelligent sensor fusion system that:
    - Combines readings from multiple sensors
    - Cross-validates motion detection (PIR + Ultrasonic)
    - Detects anomalies and patterns
    - Predicts future sensor values
    - Learns behavioral patterns
    - Provides contextual alerts
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
        
        # Storage for sensor data with rolling window (last 100 readings each)
        self.readings: Dict[str, deque] = {
            'temperature': deque(maxlen=100),
            'humidity': deque(maxlen=100),
            'distance': deque(maxlen=100),
            'motion': deque(maxlen=100),
            'alcohol': deque(maxlen=100)
        }
        
        # Alert thresholds (configurable)
        self.thresholds = {
            'temperature_high': 35.0,  # Celsius
            'temperature_low': 10.0,
            'temperature_change_rate': 5.0,  # °C per minute (rapid change)
            'humidity_high': 80.0,     # Percent
            'humidity_low': 20.0,
            'distance_close': 20.0,    # cm
            'distance_very_close': 10.0,  # cm (collision warning)
            'distance_approaching_rate': 10.0,  # cm/s (approaching fast)
        }
        
        # Active alerts
        self.active_alerts: List[Alert] = []
        self.alert_callbacks: List[Callable] = []
        
        # Predictions storage
        self.predictions: Dict[str, Prediction] = {}
        
        # Pattern storage
        self.patterns: List[Pattern] = []
        self.pattern_file = "sensor_patterns.json"
        self._load_patterns()
        
        # Behavioral learning
        self.motion_events: List[Tuple[float, bool]] = []  # (timestamp, motion_detected)
        self.daily_routines: Dict[int, List[float]] = {}  # hour -> list of activity timestamps
        
        # Multi-sensor validation
        self.last_pir_state = False
        self.last_distance = None
        self.motion_confirmed_count = 0
        self.false_alarm_count = 0
        
        # Context awareness
        self.current_mode = "normal"  # normal, night, security, energy_saving
        self.occupancy_state = "unknown"  # unknown, occupied, vacant
        self.last_occupancy_change = time.time()
        
        # Monitoring state
        self._monitoring = False
        self._monitor_thread = None
        self._update_interval = 2.0  # seconds
        
        print("✓ Enhanced Sensor Fusion System initialized")
        print("  → Multi-sensor validation enabled")
        print("  → Predictive analytics enabled")
        print("  → Pattern learning enabled")
    
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
        """Main monitoring loop with enhanced intelligence"""
        while self._monitoring:
            try:
                self.update_all_sensors()
                self._cross_validate_motion()
                self._predict_sensor_values()
                self._detect_patterns()
                self._learn_behavior()
                self._update_occupancy_state()
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
                    self.last_distance = distance
            except Exception as e:
                print(f"[FUSION] Ultrasonic read error: {e}")
        
        # Motion (PIR)
        if self.sensor_manager.pir_sensor:
            try:
                motion = self.sensor_manager.is_motion_detected()
                reading = SensorReading(
                    sensor_name='motion',
                    value=1.0 if motion else 0.0,
                    unit='detected',
                    timestamp=current_time
                )
                self._add_reading('motion', reading)
                self.last_pir_state = motion
                
                # Log motion events for behavioral learning
                self.motion_events.append((current_time, motion))
                # Keep only last 1000 events
                if len(self.motion_events) > 1000:
                    self.motion_events = self.motion_events[-1000:]
            except Exception as e:
                print(f"[FUSION] PIR read error: {e}")
        
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
        """Add a reading and maintain history (deque automatically maintains max size)"""
        if sensor_type in self.readings:
            self.readings[sensor_type].append(reading)
    
    def _cross_validate_motion(self):
        """
        Cross-validate motion using PIR + Ultrasonic distance change
        Reduces false alarms significantly
        """
        if not self.sensor_manager.pir_sensor or not self.sensor_manager.ultrasonic_sensor:
            return
        
        # Get recent readings
        motion_readings = list(self.readings['motion'])
        distance_readings = list(self.readings['distance'])
        
        if len(motion_readings) < 2 or len(distance_readings) < 5:
            return
        
        # Check if PIR detects motion
        pir_motion = motion_readings[-1].value > 0
        
        # Check if distance is changing (object moving)
        if len(distance_readings) >= 5:
            recent_distances = [r.value for r in distance_readings[-5:]]
            distance_std = statistics.stdev(recent_distances) if len(recent_distances) > 1 else 0
            distance_changing = distance_std > 2.0  # More than 2cm variation
            
            # VALIDATED MOTION: Both sensors agree
            if pir_motion and distance_changing:
                self.motion_confirmed_count += 1
                if self.motion_confirmed_count == 1:  # First confirmation
                    print("✓ Motion CONFIRMED (PIR + Ultrasonic)")
                    # Generate high-confidence alert
                    alert = Alert(
                        sensor_name='motion_validated',
                        message="Validated motion detected",
                        level=AlertLevel.INFO,
                        timestamp=time.time(),
                        confidence=0.95,
                        verified=True
                    )
                    self._handle_alert(alert)
            
            # FALSE ALARM: PIR yes, but no distance change
            elif pir_motion and not distance_changing:
                self.false_alarm_count += 1
                if self.false_alarm_count % 10 == 1:  # Log every 10th
                    print("⚠ Possible false alarm: PIR motion but no distance change")
            
            # RESET: No motion
            elif not pir_motion:
                if self.motion_confirmed_count > 0:
                    print(f"  Motion cleared (was active for {self.motion_confirmed_count} cycles)")
                self.motion_confirmed_count = 0
    
    def _predict_sensor_values(self):
        """
        Predict future sensor values based on trends
        Uses simple linear regression on recent data
        """
        current_time = time.time()
        
        # Predict temperature (next 5 minutes)
        temp_readings = list(self.readings['temperature'])
        if len(temp_readings) >= 10:
            # Use last 10 readings
            recent_temps = temp_readings[-10:]
            times = [r.timestamp for r in recent_temps]
            values = [r.value for r in recent_temps]
            
            # Simple linear trend
            if len(times) > 1:
                time_diffs = [times[i] - times[0] for i in range(len(times))]
                avg_time = sum(time_diffs) / len(time_diffs)
                avg_value = sum(values) / len(values)
                
                # Calculate slope
                numerator = sum((time_diffs[i] - avg_time) * (values[i] - avg_value) for i in range(len(times)))
                denominator = sum((time_diffs[i] - avg_time) ** 2 for i in range(len(times)))
                
                if denominator > 0:
                    slope = numerator / denominator
                    intercept = avg_value - slope * avg_time
                    
                    # Predict 5 minutes ahead
                    future_time_offset = 300  # 5 minutes in seconds
                    predicted_value = slope * (current_time - times[0] + future_time_offset) + intercept
                    
                    # Calculate confidence (higher if trend is stable)
                    residuals = [values[i] - (slope * time_diffs[i] + intercept) for i in range(len(values))]
                    rmse = (sum(r**2 for r in residuals) / len(residuals)) ** 0.5
                    confidence = max(0.1, 1.0 - (rmse / 5.0))  # Lower RMSE = higher confidence
                    
                    self.predictions['temperature'] = Prediction(
                        sensor_name='temperature',
                        predicted_value=predicted_value,
                        confidence=confidence,
                        time_ahead=future_time_offset,
                        timestamp=current_time
                    )
                    
                    # Check for rapid temperature change
                    temp_change_rate = abs(slope) * 60  # °C per minute
                    if temp_change_rate > self.thresholds.get('temperature_change_rate', 5.0):
                        alert = Alert(
                            sensor_name='temperature',
                            message=f"Rapid temp change: {temp_change_rate:.1f}°C/min",
                            level=AlertLevel.WARNING,
                            timestamp=current_time,
                            confidence=confidence
                        )
                        self._handle_alert(alert)
        
        # Predict collision risk based on distance approaching rate
        distance_readings = list(self.readings['distance'])
        if len(distance_readings) >= 5:
            recent_distances = distance_readings[-5:]
            times = [r.timestamp for r in recent_distances]
            values = [r.value for r in recent_distances]
            
            if len(times) > 1:
                # Calculate approach rate (cm/s)
                time_span = times[-1] - times[0]
                if time_span > 0:
                    distance_change = values[0] - values[-1]  # Positive if approaching
                    approach_rate = distance_change / time_span
                    
                    # Warn if approaching fast
                    if approach_rate > self.thresholds.get('distance_approaching_rate', 10.0) and values[-1] < 100:
                        # Calculate time to collision
                        if approach_rate > 0:
                            time_to_collision = values[-1] / approach_rate
                            
                            alert = Alert(
                                sensor_name='distance',
                                message=f"Collision risk! {time_to_collision:.1f}s",
                                level=AlertLevel.CRITICAL,
                                timestamp=current_time,
                                value=values[-1],
                                confidence=0.85
                            )
                            self._handle_alert(alert)
    
    def _detect_patterns(self):
        """
        Detect recurring patterns in sensor data
        Examples: Regular motion at specific times, temperature cycles, etc.
        """
        current_time = time.time()
        current_hour = datetime.fromtimestamp(current_time).hour
        
        # Pattern: Regular motion at specific hours
        motion_readings = list(self.readings['motion'])
        if len(motion_readings) >= 20:
            # Check if motion occurs regularly at this hour
            motion_at_hour = [r for r in motion_readings if datetime.fromtimestamp(r.timestamp).hour == current_hour]
            
            if len(motion_at_hour) >= 5:
                # Pattern detected: regular activity at this hour
                pattern_name = f"regular_activity_hour_{current_hour}"
                
                # Check if pattern already exists
                existing = next((p for p in self.patterns if p.name == pattern_name), None)
                
                if existing:
                    existing.frequency += 1
                    existing.last_seen = current_time
                    existing.confidence = min(1.0, existing.confidence + 0.05)
                else:
                    pattern = Pattern(
                        name=pattern_name,
                        description=f"Regular activity detected at hour {current_hour}",
                        sensors_involved=['motion'],
                        frequency=1,
                        last_seen=current_time,
                        confidence=0.5
                    )
                    self.patterns.append(pattern)
                    print(f"📊 New pattern detected: {pattern.description}")
        
        # Save patterns periodically
        if len(self.patterns) > 0 and current_time % 300 < 2:  # Every 5 minutes
            self._save_patterns()
    
    def _learn_behavior(self):
        """
        Learn user behavior patterns for proactive actions
        Tracks motion patterns by hour of day
        """
        current_time = time.time()
        current_hour = datetime.fromtimestamp(current_time).hour
        
        # Track activity by hour
        if self.last_pir_state:  # Motion detected
            if current_hour not in self.daily_routines:
                self.daily_routines[current_hour] = []
            self.daily_routines[current_hour].append(current_time)
            
            # Keep only last 100 events per hour
            if len(self.daily_routines[current_hour]) > 100:
                self.daily_routines[current_hour] = self.daily_routines[current_hour][-100:]
    
    def _update_occupancy_state(self):
        """
        Determine if room is occupied based on multi-sensor fusion
        Uses PIR motion + ultrasonic distance + time since last activity
        """
        current_time = time.time()
        
        # Check recent motion (last 2 minutes)
        motion_readings = list(self.readings['motion'])
        recent_motion = any(r.value > 0 for r in motion_readings if current_time - r.timestamp < 120)
        
        # Check if distance shows person-range (30-200cm) and not changing much (sitting/standing still)
        distance_readings = list(self.readings['distance'])
        if len(distance_readings) >= 5:
            recent_distances = [r.value for r in distance_readings[-5:]]
            avg_distance = sum(recent_distances) / len(recent_distances)
            person_distance = 30 < avg_distance < 200
        else:
            person_distance = False
        
        # Determine occupancy
        old_state = self.occupancy_state
        
        if recent_motion or (person_distance and self.motion_confirmed_count > 0):
            self.occupancy_state = "occupied"
        elif current_time - self.last_occupancy_change > 600:  # 10 minutes no activity
            self.occupancy_state = "vacant"
        else:
            self.occupancy_state = "unknown"
        
        # State change notification
        if old_state != self.occupancy_state:
            self.last_occupancy_change = current_time
            print(f"🏠 Occupancy state changed: {old_state} → {self.occupancy_state}")
            
            # Context-aware mode switching
            if self.occupancy_state == "vacant" and self.current_mode == "normal":
                # Switch to energy saving after 10 min vacant
                if current_time - self.last_occupancy_change > 600:
                    self.set_mode("energy_saving")
            elif self.occupancy_state == "occupied" and self.current_mode == "energy_saving":
                self.set_mode("normal")
    
    def set_mode(self, mode: str):
        """
        Set operational mode: normal, night, security, energy_saving
        Adjusts sensor thresholds and monitoring behavior
        """
        valid_modes = ["normal", "night", "security", "energy_saving"]
        if mode not in valid_modes:
            print(f"⚠ Invalid mode: {mode}. Valid: {valid_modes}")
            return
        
        old_mode = self.current_mode
        self.current_mode = mode
        
        print(f"🔄 Mode changed: {old_mode} → {mode}")
        
        # Adjust thresholds based on mode
        if mode == "night":
            # More sensitive to motion at night
            self._update_interval = 1.0  # Check more frequently
            print("  → Night mode: Enhanced motion detection")
        
        elif mode == "security":
            # Maximum alertness
            self._update_interval = 0.5
            self.thresholds['distance_close'] = 30.0  # More sensitive
            print("  → Security mode: Maximum sensitivity")
        
        elif mode == "energy_saving":
            # Reduce monitoring frequency
            self._update_interval = 5.0
            print("  → Energy saving: Reduced monitoring frequency")
        
        else:  # normal
            self._update_interval = 2.0
            print("  → Normal mode: Standard monitoring")
    
    def _load_patterns(self):
        """Load saved patterns from file"""
        try:
            if os.path.exists(self.pattern_file):
                with open(self.pattern_file, 'r') as f:
                    data = json.load(f)
                    self.patterns = [Pattern(**p) for p in data]
                    print(f"✓ Loaded {len(self.patterns)} learned patterns")
        except Exception as e:
            print(f"⚠ Could not load patterns: {e}")
    
    def _save_patterns(self):
        """Save patterns to file"""
        try:
            data = [asdict(p) for p in self.patterns]
            with open(self.pattern_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"⚠ Could not save patterns: {e}")
    
    def _check_for_alerts(self):
        """Analyze sensor data and generate context-aware alerts"""
        new_alerts = []
        
        # Temperature alerts with prediction
        temp_readings = list(self.readings.get('temperature', []))
        if temp_readings:
            latest_temp = temp_readings[-1]
            
            # High/Low temperature
            if latest_temp.value > self.thresholds['temperature_high']:
                # Check prediction to see if it will get worse
                predicted_msg = ""
                if 'temperature' in self.predictions:
                    pred = self.predictions['temperature']
                    if pred.predicted_value > latest_temp.value:
                        predicted_msg = f" (↑{pred.predicted_value:.1f}°C in 5min)"
                
                alert = Alert(
                    sensor_name='temperature',
                    message=f"High temp: {latest_temp.value:.1f}°C{predicted_msg}",
                    level=AlertLevel.WARNING,
                    timestamp=latest_temp.timestamp,
                    value=latest_temp.value
                )
                new_alerts.append(alert)
            elif latest_temp.value < self.thresholds['temperature_low']:
                alert = Alert(
                    sensor_name='temperature',
                    message=f"Low temp: {latest_temp.value:.1f}°C",
                    level=AlertLevel.WARNING,
                    timestamp=latest_temp.timestamp,
                    value=latest_temp.value
                )
                new_alerts.append(alert)
        
        # Humidity alerts
        humidity_readings = list(self.readings.get('humidity', []))
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
        
        # Distance alerts with collision warning
        distance_readings = list(self.readings.get('distance', []))
        if distance_readings:
            latest_distance = distance_readings[-1]
            
            # Very close - critical
            if latest_distance.value < self.thresholds.get('distance_very_close', 10.0):
                alert = Alert(
                    sensor_name='distance',
                    message=f"COLLISION WARNING: {latest_distance.value:.1f}cm",
                    level=AlertLevel.CRITICAL,
                    timestamp=latest_distance.timestamp,
                    value=latest_distance.value,
                    confidence=0.95
                )
                new_alerts.append(alert)
            # Close - warning
            elif latest_distance.value < self.thresholds['distance_close']:
                alert = Alert(
                    sensor_name='distance',
                    message=f"Obstacle: {latest_distance.value:.1f}cm",
                    level=AlertLevel.WARNING,
                    timestamp=latest_distance.timestamp,
                    value=latest_distance.value
                )
                new_alerts.append(alert)
        
        # Alcohol detection
        alcohol_readings = list(self.readings.get('alcohol', []))
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
        
        # Context-aware anomaly: Motion expected but not detected
        current_time = time.time()
        current_hour = datetime.fromtimestamp(current_time).hour
        if current_hour in self.daily_routines:
            # Check if we usually have motion at this hour
            usual_motion_count = len(self.daily_routines[current_hour])
            if usual_motion_count > 20:  # Significant pattern
                # Check if we've had motion in last 10 minutes
                motion_readings = list(self.readings.get('motion', []))
                recent_motion = any(r.value > 0 for r in motion_readings if current_time - r.timestamp < 600)
                
                if not recent_motion and self.current_mode != "night":
                    alert = Alert(
                        sensor_name='behavior',
                        message=f"Unusual: No activity at hour {current_hour}",
                        level=AlertLevel.INFO,
                        timestamp=current_time,
                        confidence=0.7
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
        readings = list(self.readings.get(sensor_type, []))
        return readings[-1] if readings else None
    
    def get_sensor_summary(self) -> Dict:
        """Get summary of all sensor data including predictions and patterns"""
        summary = {}
        
        for sensor_type, readings in self.readings.items():
            readings_list = list(readings)
            if readings_list:
                latest = readings_list[-1]
                summary[sensor_type] = {
                    'value': latest.value,
                    'unit': latest.unit,
                    'status': latest.status,
                    'timestamp': latest.timestamp
                }
        
        # Add predictions
        if self.predictions:
            summary['predictions'] = {
                name: {
                    'predicted_value': pred.predicted_value,
                    'confidence': pred.confidence,
                    'time_ahead_seconds': pred.time_ahead
                }
                for name, pred in self.predictions.items()
            }
        
        # Add occupancy and mode
        summary['occupancy'] = self.occupancy_state
        summary['mode'] = self.current_mode
        summary['motion_confirmed_count'] = self.motion_confirmed_count
        summary['false_alarm_count'] = self.false_alarm_count
        
        return summary
    
    def get_learned_patterns(self) -> List[Pattern]:
        """Get all learned patterns"""
        return self.patterns.copy()
    
    def get_prediction(self, sensor_name: str) -> Optional[Prediction]:
        """Get prediction for specific sensor"""
        return self.predictions.get(sensor_name)
    
    def get_daily_activity_summary(self) -> Dict[int, int]:
        """Get count of activities per hour"""
        return {hour: len(timestamps) for hour, timestamps in self.daily_routines.items()}
    
    def get_statistics(self, sensor_type: str, window_seconds: float = 300) -> Optional[Dict]:
        """Get statistics for sensor over time window"""
        readings_list = list(self.readings.get(sensor_type, []))
        if not readings_list:
            return None
        
        current_time = time.time()
        recent = [r for r in readings_list if current_time - r.timestamp < window_seconds]
        
        if len(recent) < 2:
            return None
        
        values = [r.value for r in recent]
        
        return {
            'min': min(values),
            'max': max(values),
            'mean': statistics.mean(values),
            'median': statistics.median(values),
            'stdev': statistics.stdev(values) if len(values) > 1 else 0,
            'count': len(values),
            'window_seconds': window_seconds
        }
    
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
