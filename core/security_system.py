"""
Enhanced Security System for JARVIS
Multi-sensor intrusion detection with intelligent alerting
"""

import time
import threading
from typing import Optional, List, Callable
from dataclasses import dataclass
from enum import Enum
from datetime import datetime


class SecurityLevel(Enum):
    """Security alert levels"""
    SAFE = 0
    SUSPICIOUS = 1
    THREAT = 2
    INTRUSION = 3


@dataclass
class SecurityEvent:
    """Security event record"""
    event_type: str
    level: SecurityLevel
    description: str
    timestamp: float
    sensor_data: dict
    verified: bool = False


class SecuritySystem:
    """
    Intelligent security system using multi-sensor fusion:
    - PIR motion + Ultrasonic distance for verified intruder detection
    - Pattern analysis for known vs unknown movement
    - Time-based security modes (enhanced at night)
    - Alert escalation system
    """
    
    def __init__(self, sensor_manager, display=None):
        """
        Initialize security system
        
        Args:
            sensor_manager: SensorManager instance
            display: Display for showing alerts
        """
        self.sensor_manager = sensor_manager
        self.display = display
        
        # Security state
        self.armed = False
        self.security_mode = "disarmed"  # disarmed, home, away, night
        self.last_motion_time = 0
        self.last_distance = None
        
        # Event storage
        self.events: List[SecurityEvent] = []
        self.alert_callbacks: List[Callable] = []
        
        # Intrusion detection
        self.intrusion_detected = False
        self.intrusion_start_time = None
        self.motion_sequence = []  # Track motion patterns
        
        # Configuration
        self.motion_timeout = 300  # 5 minutes no motion = clear
        self.distance_threshold_intruder = 150  # cm - person detected within this range
        self.consecutive_motion_threshold = 3  # How many consecutive detections = threat
        
        # Monitoring
        self._monitoring = False
        self._monitor_thread = None
        
        print("✓ Security System initialized")
    
    def arm(self, mode: str = "away"):
        """
        Arm security system
        
        Args:
            mode: Security mode - 'home', 'away', or 'night'
        """
        valid_modes = ["home", "away", "night"]
        if mode not in valid_modes:
            print(f"⚠ Invalid mode: {mode}. Valid: {valid_modes}")
            return
        
        self.armed = True
        self.security_mode = mode
        self.intrusion_detected = False
        self.motion_sequence = []
        
        print(f"🔒 Security system ARMED - Mode: {mode.upper()}")
        
        if self.display:
            try:
                self.display.clear()
                self.display.write_text("SECURITY ARMED", row=0, col=2)
                self.display.write_text(f"Mode: {mode.upper()}", row=1, col=0)
            except:
                pass
        
        # Log event
        event = SecurityEvent(
            event_type="system_armed",
            level=SecurityLevel.SAFE,
            description=f"Security armed in {mode} mode",
            timestamp=time.time(),
            sensor_data={}
        )
        self._log_event(event)
        
        # Start monitoring if not already running
        if not self._monitoring:
            self.start_monitoring()
    
    def disarm(self):
        """Disarm security system"""
        self.armed = False
        self.security_mode = "disarmed"
        self.intrusion_detected = False
        
        print("🔓 Security system DISARMED")
        
        if self.display:
            try:
                self.display.clear()
                self.display.write_text("DISARMED", row=0, col=5)
            except:
                pass
        
        # Log event
        event = SecurityEvent(
            event_type="system_disarmed",
            level=SecurityLevel.SAFE,
            description="Security disarmed",
            timestamp=time.time(),
            sensor_data={}
        )
        self._log_event(event)
    
    def start_monitoring(self):
        """Start continuous security monitoring"""
        if self._monitoring:
            return
        
        self._monitoring = True
        self._monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self._monitor_thread.start()
        print("✓ Security monitoring started")
    
    def stop_monitoring(self):
        """Stop security monitoring"""
        if self._monitoring:
            self._monitoring = False
            if self._monitor_thread:
                self._monitor_thread.join(timeout=5)
            print("✓ Security monitoring stopped")
    
    def _monitor_loop(self):
        """Main security monitoring loop"""
        while self._monitoring:
            try:
                if self.armed:
                    self._check_security()
                time.sleep(0.5)  # Check twice per second when armed
            except Exception as e:
                print(f"[SECURITY] Monitor error: {e}")
                time.sleep(1)
    
    def _check_security(self):
        """Check all sensors for security threats"""
        current_time = time.time()
        
        # Get sensor readings
        motion_detected = self.sensor_manager.is_motion_detected()
        distance = self.sensor_manager.get_distance()
        
        # Multi-sensor verification
        if motion_detected:
            self.last_motion_time = current_time
            
            # Add to motion sequence
            self.motion_sequence.append({
                'time': current_time,
                'motion': True,
                'distance': distance
            })
            
            # Keep only last 10 readings
            if len(self.motion_sequence) > 10:
                self.motion_sequence = self.motion_sequence[-10:]
            
            # Verify with distance sensor
            verified_threat = False
            if distance and 0 < distance < self.distance_threshold_intruder:
                verified_threat = True
            
            # Count consecutive motion detections
            recent_motion_count = sum(1 for m in self.motion_sequence 
                                     if current_time - m['time'] < 5)
            
            # THREAT DETECTION: Multiple consecutive motion + distance confirmation
            if recent_motion_count >= self.consecutive_motion_threshold and verified_threat:
                if not self.intrusion_detected:
                    self._handle_intrusion(distance)
            
            # SUSPICIOUS: Motion but can't verify with distance
            elif recent_motion_count >= self.consecutive_motion_threshold and not verified_threat:
                self._handle_suspicious_activity()
        
        else:
            # Clear intrusion after timeout
            if self.intrusion_detected and current_time - self.last_motion_time > self.motion_timeout:
                self._clear_intrusion()
    
    def _handle_intrusion(self, distance: float):
        """Handle verified intrusion"""
        if self.intrusion_detected:
            return  # Already handling
        
        self.intrusion_detected = True
        self.intrusion_start_time = time.time()
        
        print("🚨🚨🚨 INTRUSION DETECTED! 🚨🚨🚨")
        print(f"  → Distance: {distance:.1f}cm")
        print(f"  → Mode: {self.security_mode}")
        
        # Display alert
        if self.display:
            try:
                self.display.clear()
                self.display.write_text("!! INTRUSION !!", row=0, col=2)
                self.display.write_text(f"Dist:{distance:.0f}cm", row=1, col=0)
            except:
                pass
        
        # Log event
        event = SecurityEvent(
            event_type="intrusion",
            level=SecurityLevel.INTRUSION,
            description=f"Intrusion detected at {distance:.1f}cm",
            timestamp=time.time(),
            sensor_data={'distance': distance, 'mode': self.security_mode},
            verified=True
        )
        self._log_event(event)
        self._notify_callbacks(event)
    
    def _handle_suspicious_activity(self):
        """Handle suspicious but unverified activity"""
        current_time = time.time()
        
        # Don't spam - only alert once per minute
        recent_suspicious = [e for e in self.events 
                            if e.event_type == "suspicious" 
                            and current_time - e.timestamp < 60]
        if recent_suspicious:
            return
        
        print("⚠️ Suspicious activity detected (motion only)")
        
        # Log event
        event = SecurityEvent(
            event_type="suspicious",
            level=SecurityLevel.SUSPICIOUS,
            description="Suspicious motion detected",
            timestamp=current_time,
            sensor_data={'mode': self.security_mode},
            verified=False
        )
        self._log_event(event)
        self._notify_callbacks(event)
    
    def _clear_intrusion(self):
        """Clear intrusion alert after timeout"""
        if not self.intrusion_detected:
            return
        
        duration = time.time() - self.intrusion_start_time
        
        print(f"✓ Intrusion cleared (duration: {duration:.0f}s)")
        
        self.intrusion_detected = False
        self.intrusion_start_time = None
        self.motion_sequence = []
        
        if self.display:
            try:
                self.display.clear()
                self.display.write_text("SECURITY ARMED", row=0, col=2)
                self.display.write_text(f"Mode:{self.security_mode}", row=1, col=0)
            except:
                pass
        
        # Log event
        event = SecurityEvent(
            event_type="intrusion_cleared",
            level=SecurityLevel.SAFE,
            description=f"Intrusion cleared after {duration:.0f}s",
            timestamp=time.time(),
            sensor_data={'duration': duration}
        )
        self._log_event(event)
    
    def _log_event(self, event: SecurityEvent):
        """Log security event"""
        self.events.append(event)
        
        # Keep only last 100 events
        if len(self.events) > 100:
            self.events = self.events[-100:]
    
    def add_alert_callback(self, callback: Callable):
        """Add callback function for security alerts"""
        self.alert_callbacks.append(callback)
    
    def _notify_callbacks(self, event: SecurityEvent):
        """Notify all registered callbacks"""
        for callback in self.alert_callbacks:
            try:
                callback(event)
            except Exception as e:
                print(f"[SECURITY] Callback error: {e}")
    
    def get_status(self) -> dict:
        """Get current security status"""
        return {
            'armed': self.armed,
            'mode': self.security_mode,
            'intrusion_detected': self.intrusion_detected,
            'last_motion_time': self.last_motion_time,
            'total_events': len(self.events),
            'monitoring': self._monitoring
        }
    
    def get_recent_events(self, count: int = 10) -> List[SecurityEvent]:
        """Get recent security events"""
        return self.events[-count:]
    
    def get_event_summary(self) -> dict:
        """Get summary of security events"""
        if not self.events:
            return {'total': 0}
        
        # Count by type
        type_counts = {}
        level_counts = {}
        
        for event in self.events:
            type_counts[event.event_type] = type_counts.get(event.event_type, 0) + 1
            level_name = event.level.name
            level_counts[level_name] = level_counts.get(level_name, 0) + 1
        
        return {
            'total': len(self.events),
            'by_type': type_counts,
            'by_level': level_counts,
            'oldest': datetime.fromtimestamp(self.events[0].timestamp).strftime('%Y-%m-%d %H:%M:%S'),
            'newest': datetime.fromtimestamp(self.events[-1].timestamp).strftime('%Y-%m-%d %H:%M:%S')
        }


# Singleton instance
_security_system_instance = None

def get_security_system(sensor_manager=None, display=None) -> SecuritySystem:
    """Get or create security system singleton"""
    global _security_system_instance
    if _security_system_instance is None:
        if sensor_manager is None:
            raise ValueError("sensor_manager required for first initialization")
        _security_system_instance = SecuritySystem(sensor_manager, display)
    return _security_system_instance
