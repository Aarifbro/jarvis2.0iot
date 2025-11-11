"""
Body Language and Gesture Engine for Jarvis.

This module defines and executes pre-programmed sequences of servo movements
to create lifelike gestures. It uses the MultiServoController to orchestrate
the neck, left arm, and right arm servos.

Each gesture is a sequence of (servo_name, angle, delay_after_move) tuples.
"""

from actuators.multi_servo_controller import multi_servo_controller
import time
import threading

class BodyLanguage:
    def __init__(self, controller=None):
        self.controller = controller or multi_servo_controller
        self.is_gesturing = False
        self.gesture_lock = threading.Lock()

        # --- Gesture Definitions ---
        # Each gesture is a list of tuples: (servo_name, angle, delay_ms)
        self.gestures = {
            "nod": [
                ("neck", 70, 300),
                ("neck", 110, 300),
                ("neck", 90, 200),
            ],
            "shake_head": [
                ("neck", 60, 350),
                ("neck", 120, 350),
                ("neck", 60, 350),
                ("neck", 120, 350),
                ("neck", 90, 200),
            ],
            "wave_right": [
                ("arm_r", 45, 200),
                ("arm_r", 0, 400),
                ("arm_r", 45, 400),
                ("arm_r", 0, 400),
                ("arm_r", 45, 400),
                ("arm_r", 90, 200), # Return to rest
            ],
            "wave_left": [
                ("arm_l", 135, 200),
                ("arm_l", 180, 400),
                ("arm_l", 135, 400),
                ("arm_l", 180, 400),
                ("arm_l", 135, 400),
                ("arm_l", 90, 200), # Return to rest
            ],
            "agree": [
                # A more enthusiastic nod
                ("neck", 80, 200),
                ("neck", 100, 200),
                ("neck", 80, 200),
                ("neck", 100, 200),
                ("neck", 90, 100),
            ],
            "disagree": [
                # A shorter, faster head shake
                ("neck", 75, 250),
                ("neck", 105, 250),
                ("neck", 75, 250),
                ("neck", 90, 100),
            ],
            "think": [
                ("neck", 80, 500),
                ("neck", 100, 1000),
                ("neck", 90, 200),
            ],
            "namaste": [
                # Traditional Indian greeting - both hands raised and joined
                ("arm_l", 120, 300),   # Raise left arm
                ("arm_r", 60, 300),    # Raise right arm (mirror)
                ("neck", 80, 300),     # Slight bow
                ("neck", 90, 500),     # Return head
                ("arm_l", 120, 800),   # Hold position
                ("arm_r", 60, 800),
                ("arm_l", 90, 300),    # Lower arms
                ("arm_r", 90, 300),
            ],
            "greeting_wave": [
                # Friendly wave with right hand
                ("arm_r", 45, 200),
                ("arm_r", 20, 300),
                ("arm_r", 45, 300),
                ("arm_r", 20, 300),
                ("arm_r", 90, 200),
            ],
            "raise_hand": [
                # Single hand raise (right hand)
                ("arm_r", 30, 400),    # Raise hand up
                ("arm_r", 30, 1000),   # Hold
                ("arm_r", 90, 300),    # Lower
            ],
            "raise_both_hands": [
                # Raise both hands up
                ("arm_l", 130, 400),
                ("arm_r", 50, 400),
                ("arm_l", 130, 1000),  # Hold
                ("arm_r", 50, 1000),
                ("arm_l", 90, 300),    # Lower
                ("arm_r", 90, 300),
            ],
            "salute": [
                # Military-style salute
                ("arm_r", 40, 300),    # Raise right hand
                ("neck", 95, 200),     # Slight head tilt
                ("arm_r", 40, 800),    # Hold
                ("arm_r", 90, 300),    # Lower
                ("neck", 90, 200),
            ],
            "greeting_sir": [
                # Professional greeting with hand gesture
                ("neck", 85, 300),     # Slight bow
                ("arm_r", 45, 400),    # Raise right hand  
                ("arm_r", 20, 300),    # Wave once
                ("arm_r", 45, 300),    # Wave twice
                ("arm_r", 90, 300),    # Lower hand
                ("neck", 90, 200),     # Head back up
            ],
            "excited": [
                # Excited/happy gesture - both hands up
                ("neck", 85, 200),
                ("arm_l", 130, 300),
                ("arm_r", 50, 300),
                ("neck", 95, 200),
                ("neck", 85, 200),
                ("arm_l", 90, 300),
                ("arm_r", 90, 300),
                ("neck", 90, 200),
            ],
            "confused": [
                # Confused - head tilt and hand to side
                ("neck", 75, 400),     # Tilt head
                ("arm_r", 70, 400),    # Hand halfway up
                ("neck", 105, 400),    # Tilt other way
                ("arm_r", 90, 300),    # Hand down
                ("neck", 90, 300),     # Center head
            ],
            "listening": [
                # Attentive listening pose
                ("neck", 85, 300),     # Lean forward slightly
                ("arm_l", 95, 200),    # Arms relaxed
                ("arm_r", 85, 200),
            ],
            "alert": [
                # Alert/cautious - quick head movements
                ("neck", 70, 200),     # Look down
                ("neck", 110, 200),    # Look up
                ("neck", 60, 300),     # Look left
                ("neck", 120, 300),    # Look right
                ("neck", 90, 200),     # Center
            ],
            "celebrate": [
                # Celebration - both hands up enthusiastically
                ("arm_l", 140, 250),
                ("arm_r", 40, 250),
                ("neck", 95, 150),
                ("arm_l", 120, 250),
                ("arm_r", 60, 250),
                ("neck", 85, 150),
                ("arm_l", 140, 250),
                ("arm_r", 40, 250),
                ("arm_l", 90, 300),
                ("arm_r", 90, 300),
                ("neck", 90, 200),
            ],
            "point_forward": [
                # Point ahead
                ("arm_r", 45, 300),    # Extend arm
                ("neck", 90, 500),     # Look forward
                ("arm_r", 90, 300),    # Retract
            ],
            "scan_area": [
                # Look around scanning
                ("neck", 45, 400),     # Look far left
                ("neck", 90, 400),     # Center
                ("neck", 135, 400),    # Look far right
                ("neck", 90, 300),     # Center
            ],
            "reset_position": [
                ("neck", 90, 300),
                ("arm_l", 90, 300),
                ("arm_r", 90, 300),
            ]
        }

    def list_gestures(self):
        """Returns a list of all available gesture names."""
        return list(self.gestures.keys())

    def perform_gesture(self, gesture_name: str, blocking=False):
        """
        Performs a named gesture.

        Args:
            gesture_name (str): The name of the gesture to perform.
            blocking (bool): If True, this call will wait for the gesture to finish.
                             If False, it runs in a background thread.
        """
        if gesture_name not in self.gestures:
            raise ValueError(f"Gesture '{gesture_name}' not found.")

        if self.is_gesturing:
            print(f"Cannot perform '{gesture_name}': another gesture is in progress.")
            return

        if blocking:
            self._execute_sequence(gesture_name)
        else:
            thread = threading.Thread(target=self._execute_sequence, args=(gesture_name,), daemon=True)
            thread.start()

    def _execute_sequence(self, gesture_name: str):
        """The core logic for executing a gesture sequence with smooth movements."""
        with self.gesture_lock:
            self.is_gesturing = True
            
        sequence = self.gestures[gesture_name]
        print(f"✓ Performing gesture: {gesture_name}")

        try:
            for servo_name, angle, delay_ms in sequence:
                try:
                    # Use smooth movement to prevent servo jerking/attacking
                    # Calculate duration based on delay for natural motion
                    duration = min(delay_ms / 1000.0, 0.5)  # Max 0.5s smooth movement
                    self.controller.set_angle(servo_name, angle, smooth=True, duration=duration)
                    
                    # Wait for movement + additional delay
                    time.sleep(delay_ms / 1000.0)
                except ValueError as e:
                    print(f"⚠ Skipping step in '{gesture_name}': {e}")
                except RuntimeError as e:
                    # Servo busy - wait and try again once
                    print(f"⚠ Servo busy, retrying...")
                    time.sleep(0.2)
                    try:
                        self.controller.set_angle(servo_name, angle, smooth=True, duration=duration)
                        time.sleep(delay_ms / 1000.0)
                    except:
                        print(f"⚠ Skipped step due to busy servo")
                        time.sleep(delay_ms / 1000.0)
                except Exception as e:
                    print(f"⚠ Error in gesture step: {e}")
                    time.sleep(delay_ms / 1000.0)
        finally:
            with self.gesture_lock:
                self.is_gesturing = False
            print(f"✓ Finished gesture: {gesture_name}")

    def center_all(self):
        """Centers all known servos to 90 degrees with smooth movement."""
        for servo_name in ("neck", "arm_l", "arm_r"):
            try:
                self.controller.set_angle(servo_name, 90, smooth=True, duration=0.5)
            except Exception as exc:  # pragma: no cover - hardware dependent
                print(f"Failed to center {servo_name}: {exc}")
        time.sleep(0.6)  # Wait for all to complete
    
    def gesture_for_greeting(self, person_name: str = "Sir") -> str:
        """
        Select and perform appropriate greeting gesture based on person.
        Returns the gesture name performed.
        """
        person_lower = person_name.lower()
        
        # Special greetings for specific people
        if "sachin" in person_lower or "sir" in person_lower:
            self.perform_gesture("greeting_sir", blocking=False)
            return "greeting_sir"
        elif "mam" in person_lower or "madam" in person_lower:
            self.perform_gesture("namaste", blocking=False)
            return "namaste"
        else:
            self.perform_gesture("greeting_wave", blocking=False)
            return "greeting_wave"
    
    def gesture_for_emotion(self, emotion: str):
        """
        Perform gesture based on emotion/context.
        
        Args:
            emotion: One of 'happy', 'sad', 'confused', 'excited', 'thinking', 'alert'
        """
        emotion_to_gesture = {
            'happy': 'celebrate',
            'excited': 'excited',
            'sad': 'think',
            'confused': 'confused',
            'thinking': 'think',
            'alert': 'alert',
            'agree': 'agree',
            'disagree': 'disagree',
            'listening': 'listening',
        }
        
        gesture = emotion_to_gesture.get(emotion.lower(), 'nod')
        self.perform_gesture(gesture, blocking=False)
        return gesture
    
    def gesture_for_sensor_event(self, sensor_type: str, value: any):
        """
        React with appropriate body language based on sensor readings.
        
        Args:
            sensor_type: Type of sensor ('motion', 'distance', 'temperature', 'alcohol')
            value: Sensor value
        """
        if sensor_type == 'motion':
            # Someone detected - turn head to look
            self.perform_gesture('alert', blocking=False)
            
        elif sensor_type == 'distance':
            if value and value < 30:  # Something very close
                self.perform_gesture('alert', blocking=False)
            elif value and value < 100:
                self.perform_gesture('scan_area', blocking=False)
        
        elif sensor_type == 'temperature':
            if value and value > 35:  # Hot
                self.perform_gesture('confused', blocking=False)
            elif value and value < 15:  # Cold
                self.perform_gesture('think', blocking=False)
        
        elif sensor_type == 'alcohol':
            if value:  # Alcohol detected
                self.perform_gesture('disagree', blocking=False)
    
    def look_at_angle(self, angle: int, duration: float = 0.5):
        """
        Turn neck to look at specific angle smoothly.
        
        Args:
            angle: Angle to look at (0-180)
            duration: Duration of movement
        """
        try:
            self.controller.set_angle('neck', angle, smooth=True, duration=duration)
        except Exception as e:
            print(f"⚠ Could not move neck: {e}")
    
    def point_direction(self, direction: str):
        """
        Point in a direction (left/right/forward).
        
        Args:
            direction: 'left', 'right', 'forward', 'up', 'down'
        """
        direction = direction.lower()
        
        if direction in ['left', 'baen']:
            self.perform_gesture('scan_area', blocking=False)  # Look left
        elif direction in ['right', 'daen']:
            self.perform_gesture('scan_area', blocking=False)  # Look right
        elif direction in ['forward', 'aage', 'ahead']:
            self.perform_gesture('point_forward', blocking=False)
        else:
            self.perform_gesture('nod', blocking=False)


# Singleton instance
body_language_engine = BodyLanguage()

if __name__ == '__main__':
    print("Running Body Language Engine test...")
    print("Available gestures:", body_language_engine.list_gestures())
    
    try:
        print("\nPerforming 'nod' (blocking)...")
        body_language_engine.perform_gesture("nod", blocking=True)
        
        print("\nPerforming 'shake_head' (non-blocking)...")
        body_language_engine.perform_gesture("shake_head")
        time.sleep(3) # Give it time to finish

        print("\nPerforming 'wave_right'...")
        body_language_engine.perform_gesture("wave_right")
        time.sleep(4)

        print("\nResetting position...")
        body_language_engine.perform_gesture("reset_position", blocking=True)

        print("\nTest complete.")

    except KeyboardInterrupt:
        print("\nTest interrupted.")
    finally:
        # In a real app, cleanup is handled by the main HardwareManager
        print("Test finished.")
