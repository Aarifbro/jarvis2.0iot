"""
MQTT/IoT Cloud Integration for JARVIS
Enables remote monitoring, control, and data logging

Supports:
- MQTT publish/subscribe for sensor data
- Remote command execution
- Cloud data logging
- Mobile app integration
- Home Assistant integration
"""

import time
import threading
import json
from typing import Optional, Dict, Callable, Any
from datetime import datetime


try:
    import paho.mqtt.client as mqtt
    MQTT_AVAILABLE = True
except ImportError:
    MQTT_AVAILABLE = False
    print("⚠️  paho-mqtt not installed. Run: pip3 install paho-mqtt")


class IoTHub:
    """
    IoT Hub for cloud connectivity
    - Publishes sensor data to MQTT broker
    - Subscribes to command topics
    - Manages connection and reconnection
    """
    
    def __init__(self, broker: str = "localhost", port: int = 1883, 
                 client_id: str = "jarvis", username: Optional[str] = None, 
                 password: Optional[str] = None):
        """
        Initialize IoT Hub
        
        Args:
            broker: MQTT broker address (e.g., "mqtt.example.com" or "localhost")
            port: MQTT broker port (default: 1883)
            client_id: Unique client ID
            username: MQTT username (optional)
            password: MQTT password (optional)
        """
        if not MQTT_AVAILABLE:
            raise RuntimeError("paho-mqtt library not available")
        
        self.broker = broker
        self.port = port
        self.client_id = client_id
        self.username = username
        self.password = password
        
        # MQTT client
        self.client = mqtt.Client(client_id=client_id)
        
        # Set callbacks
        self.client.on_connect = self._on_connect
        self.client.on_disconnect = self._on_disconnect
        self.client.on_message = self._on_message
        
        # Authentication
        if username and password:
            self.client.username_pw_set(username, password)
        
        # State
        self.connected = False
        self.command_callbacks: Dict[str, Callable] = {}
        
        # Topics
        self.topic_prefix = f"jarvis/{client_id}"
        self.topics = {
            'status': f"{self.topic_prefix}/status",
            'sensors': f"{self.topic_prefix}/sensors",
            'temperature': f"{self.topic_prefix}/sensors/temperature",
            'humidity': f"{self.topic_prefix}/sensors/humidity",
            'distance': f"{self.topic_prefix}/sensors/distance",
            'motion': f"{self.topic_prefix}/sensors/motion",
            'alcohol': f"{self.topic_prefix}/sensors/alcohol",
            'alerts': f"{self.topic_prefix}/alerts",
            'commands': f"{self.topic_prefix}/commands/#",  # Subscribe to all commands
            'response': f"{self.topic_prefix}/response"
        }
        
        # Publishing
        self._publishing = False
        self._publish_thread = None
        self._publish_interval = 10.0  # seconds
        
        # Sensor manager reference (set externally)
        self.sensor_manager = None
        self.security_system = None
        self.sensor_fusion = None
        
        print(f"✓ IoT Hub initialized (broker: {broker}:{port})")
    
    def connect(self) -> bool:
        """Connect to MQTT broker"""
        try:
            print(f"Connecting to MQTT broker: {self.broker}:{self.port}...")
            self.client.connect(self.broker, self.port, keepalive=60)
            self.client.loop_start()
            return True
        except Exception as e:
            print(f"❌ MQTT connection failed: {e}")
            return False
    
    def disconnect(self):
        """Disconnect from MQTT broker"""
        self.stop_publishing()
        self.client.loop_stop()
        self.client.disconnect()
        print("✓ Disconnected from MQTT broker")
    
    def _on_connect(self, client, userdata, flags, rc):
        """Callback when connected to broker"""
        if rc == 0:
            self.connected = True
            print(f"✓ Connected to MQTT broker: {self.broker}")
            
            # Subscribe to command topics
            self.client.subscribe(self.topics['commands'])
            print(f"  → Subscribed to: {self.topics['commands']}")
            
            # Publish online status
            self.publish_status("online")
        else:
            self.connected = False
            print(f"❌ MQTT connection failed with code: {rc}")
    
    def _on_disconnect(self, client, userdata, rc):
        """Callback when disconnected from broker"""
        self.connected = False
        if rc != 0:
            print(f"⚠️  Unexpected disconnect from MQTT broker (code: {rc})")
        else:
            print("✓ Disconnected from MQTT broker")
    
    def _on_message(self, client, userdata, msg):
        """Callback when message received"""
        try:
            topic = msg.topic
            payload = msg.payload.decode('utf-8')
            
            print(f"📩 MQTT message received: {topic}")
            
            # Parse command
            if '/commands/' in topic:
                command_type = topic.split('/commands/')[-1]
                self._handle_command(command_type, payload)
        
        except Exception as e:
            print(f"❌ Error handling MQTT message: {e}")
    
    def _handle_command(self, command_type: str, payload: str):
        """Handle incoming command"""
        try:
            data = json.loads(payload) if payload else {}
        except json.JSONDecodeError:
            data = {'raw': payload}
        
        print(f"  Command: {command_type}")
        print(f"  Data: {data}")
        
        # Check for registered callbacks
        if command_type in self.command_callbacks:
            try:
                result = self.command_callbacks[command_type](data)
                self._publish_command_response(command_type, result, success=True)
            except Exception as e:
                print(f"❌ Command callback error: {e}")
                self._publish_command_response(command_type, str(e), success=False)
        else:
            # Default command handlers
            self._handle_default_command(command_type, data)
    
    def _handle_default_command(self, command_type: str, data: dict):
        """Handle built-in commands"""
        response = None
        success = True
        
        try:
            if command_type == "status":
                # Get system status
                response = self._get_system_status()
            
            elif command_type == "arm_security":
                # Arm security system
                if self.security_system:
                    mode = data.get('mode', 'away')
                    self.security_system.arm(mode)
                    response = f"Security armed in {mode} mode"
                else:
                    response = "Security system not available"
            
            elif command_type == "disarm_security":
                # Disarm security
                if self.security_system:
                    self.security_system.disarm()
                    response = "Security disarmed"
                else:
                    response = "Security system not available"
            
            elif command_type == "get_sensors":
                # Get all sensor readings
                if self.sensor_manager:
                    response = {
                        'temperature': self.sensor_manager.get_temperature(),
                        'humidity': self.sensor_manager.get_humidity(),
                        'distance': self.sensor_manager.get_distance(),
                        'motion': self.sensor_manager.is_motion_detected(),
                        'alcohol': self.sensor_manager.get_alcohol_level()
                    }
                else:
                    response = "Sensor manager not available"
            
            elif command_type == "set_mode":
                # Set fusion mode
                if self.sensor_fusion:
                    mode = data.get('mode', 'normal')
                    self.sensor_fusion.set_mode(mode)
                    response = f"Mode set to {mode}"
                else:
                    response = "Sensor fusion not available"
            
            else:
                response = f"Unknown command: {command_type}"
                success = False
        
        except Exception as e:
            response = str(e)
            success = False
        
        self._publish_command_response(command_type, response, success)
    
    def _get_system_status(self) -> dict:
        """Get complete system status"""
        status = {
            'timestamp': time.time(),
            'online': True
        }
        
        if self.sensor_manager:
            status['sensors'] = {
                'temperature': self.sensor_manager.get_temperature(),
                'humidity': self.sensor_manager.get_humidity(),
                'distance': self.sensor_manager.get_distance(),
                'motion': self.sensor_manager.is_motion_detected()
            }
        
        if self.security_system:
            status['security'] = self.security_system.get_status()
        
        if self.sensor_fusion:
            status['fusion'] = {
                'occupancy': self.sensor_fusion.occupancy_state,
                'mode': self.sensor_fusion.current_mode
            }
        
        return status
    
    def _publish_command_response(self, command: str, response: Any, success: bool):
        """Publish command response"""
        payload = {
            'command': command,
            'success': success,
            'response': response,
            'timestamp': time.time()
        }
        self.publish(self.topics['response'], json.dumps(payload))
    
    def register_command_callback(self, command_type: str, callback: Callable):
        """Register callback for specific command type"""
        self.command_callbacks[command_type] = callback
        print(f"✓ Registered command callback: {command_type}")
    
    def publish(self, topic: str, payload: str, qos: int = 0, retain: bool = False) -> bool:
        """Publish message to topic"""
        if not self.connected:
            return False
        
        try:
            result = self.client.publish(topic, payload, qos=qos, retain=retain)
            return result.rc == mqtt.MQTT_ERR_SUCCESS
        except Exception as e:
            print(f"❌ Publish error: {e}")
            return False
    
    def publish_json(self, topic: str, data: dict, qos: int = 0, retain: bool = False) -> bool:
        """Publish JSON data to topic"""
        try:
            payload = json.dumps(data)
            return self.publish(topic, payload, qos, retain)
        except Exception as e:
            print(f"❌ JSON publish error: {e}")
            return False
    
    def publish_status(self, status: str):
        """Publish online/offline status"""
        self.publish(self.topics['status'], status, qos=1, retain=True)
    
    def publish_sensor_data(self):
        """Publish all sensor data"""
        if not self.sensor_manager or not self.connected:
            return
        
        timestamp = time.time()
        
        # Temperature
        temp = self.sensor_manager.get_temperature()
        if temp is not None:
            self.publish_json(self.topics['temperature'], {
                'value': temp,
                'unit': '°C',
                'timestamp': timestamp
            })
        
        # Humidity
        humidity = self.sensor_manager.get_humidity()
        if humidity is not None:
            self.publish_json(self.topics['humidity'], {
                'value': humidity,
                'unit': '%',
                'timestamp': timestamp
            })
        
        # Distance
        distance = self.sensor_manager.get_distance()
        if distance is not None and distance > 0:
            self.publish_json(self.topics['distance'], {
                'value': distance,
                'unit': 'cm',
                'timestamp': timestamp
            })
        
        # Motion
        motion = self.sensor_manager.is_motion_detected()
        self.publish_json(self.topics['motion'], {
            'detected': motion,
            'timestamp': timestamp
        })
        
        # Combined sensors payload
        all_sensors = {
            'temperature': temp,
            'humidity': humidity,
            'distance': distance,
            'motion': motion,
            'timestamp': timestamp
        }
        self.publish_json(self.topics['sensors'], all_sensors)
    
    def publish_alert(self, alert_type: str, message: str, level: str = "info"):
        """Publish alert/notification"""
        if not self.connected:
            return
        
        alert_data = {
            'type': alert_type,
            'message': message,
            'level': level,
            'timestamp': time.time()
        }
        self.publish_json(self.topics['alerts'], alert_data)
    
    def start_publishing(self, interval: float = 10.0):
        """Start automatic sensor data publishing"""
        if self._publishing:
            return
        
        self._publish_interval = interval
        self._publishing = True
        self._publish_thread = threading.Thread(target=self._publish_loop, daemon=True)
        self._publish_thread.start()
        print(f"✓ Auto-publishing started (interval: {interval}s)")
    
    def stop_publishing(self):
        """Stop automatic publishing"""
        if self._publishing:
            self._publishing = False
            if self._publish_thread:
                self._publish_thread.join(timeout=5)
            print("✓ Auto-publishing stopped")
    
    def _publish_loop(self):
        """Automatic publishing loop"""
        while self._publishing:
            try:
                if self.connected:
                    self.publish_sensor_data()
                time.sleep(self._publish_interval)
            except Exception as e:
                print(f"[IOT] Publish loop error: {e}")
                time.sleep(1)


# Singleton instance
_iot_hub_instance = None

def get_iot_hub(**kwargs) -> Optional[IoTHub]:
    """Get or create IoT Hub singleton"""
    global _iot_hub_instance
    
    if not MQTT_AVAILABLE:
        return None
    
    if _iot_hub_instance is None and kwargs:
        _iot_hub_instance = IoTHub(**kwargs)
    
    return _iot_hub_instance
