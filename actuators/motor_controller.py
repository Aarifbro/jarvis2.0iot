"""
Motor Controller for Jarvis Robot Chassis.

This module controls a 2-wheel drive chassis using a dual H-bridge motor
driver like the L298N. It provides functions for forward, backward,
left, right, and stop movements.

Assumed Pinout (BCM numbering):
- Left Motor (Motor A on L298N):
  - Enable Pin (ENA): BCM 12
  - Input 1 (IN1): BCM 5
  - Input 2 (IN2): BCM 6
- Right Motor (Motor B on L298N):
  - Enable Pin (ENB): BCM 13
  - Input 1 (IN3): BCM 26
  - Input 2 (IN4): BCM 16

These pins can be overridden with environment variables:
- MOTOR_L_EN, MOTOR_L_IN1, MOTOR_L_IN2
- MOTOR_R_EN, MOTOR_R_IN1, MOTOR_R_IN2
"""

from core.hardware_manager import hardware_manager
import RPi.GPIO as GPIO
import os
import time

class MotorController:
    def __init__(self):
        self.simulation_mode = hardware_manager.simulation_mode
        self._cleaned_up = False  # Track cleanup state

        # Get pin numbers from environment variables or use defaults
        self.L_EN = int(os.getenv('MOTOR_L_EN', 12))
        self.L_IN1 = int(os.getenv('MOTOR_L_IN1', 5))
        self.L_IN2 = int(os.getenv('MOTOR_L_IN2', 6))
        self.R_EN = int(os.getenv('MOTOR_R_EN', 13))
        self.R_IN1 = int(os.getenv('MOTOR_R_IN1', 26))
        self.R_IN2 = int(os.getenv('MOTOR_R_IN2', 16))

        if not self.simulation_mode:
            self._setup_gpio()
        else:
            print("MotorController initialized (Simulation Mode)")

    def _setup_gpio(self):
        """Sets up GPIO pins for motor control."""
        pins = [self.L_EN, self.L_IN1, self.L_IN2, self.R_EN, self.R_IN1, self.R_IN2]
        GPIO.setup(pins, GPIO.OUT)
        
        # Set up PWM for speed control
        self.l_pwm = GPIO.PWM(self.L_EN, 100) # 100 Hz frequency
        self.r_pwm = GPIO.PWM(self.R_EN, 100)
        self.l_pwm.start(0)
        self.r_pwm.start(0)
        print("MotorController GPIO initialized.")

    def _set_speed(self, left_speed, right_speed):
        """Sets the speed of the motors. Speed is a value from 0 to 100."""
        if self.simulation_mode:
            print(f"[SIM] Setting motor speed: Left={left_speed}, Right={right_speed}")
            return
        
        # Clamp speed values to 0-100 range
        left_speed = max(0, min(100, left_speed))
        right_speed = max(0, min(100, right_speed))
        
        self.l_pwm.ChangeDutyCycle(left_speed)
        self.r_pwm.ChangeDutyCycle(right_speed)

    def _smooth_speed_change(self, target_left, target_right, ramp_time=0.3):
        """
        Smoothly ramps speed to target values to prevent jerky starts.
        
        Args:
            target_left: Target speed for left motor (0-100)
            target_right: Target speed for right motor (0-100)
            ramp_time: Time in seconds to reach target speed (default: 0.3)
        """
        if self.simulation_mode:
            self._set_speed(target_left, target_right)
            return
        
        steps = 10
        step_delay = ramp_time / steps
        
        # Get current speeds (approximate from last command)
        current_left = 0
        current_right = 0
        
        for i in range(1, steps + 1):
            progress = i / steps
            left_speed = current_left + (target_left - current_left) * progress
            right_speed = current_right + (target_right - current_right) * progress
            self._set_speed(left_speed, right_speed)
            time.sleep(step_delay)

    def forward(self, speed=100, duration=None, smooth=True):
        """
        Move the robot forward with full motor power.
        
        Args:
            speed: Motor speed 0-100 (default: 100 for maximum power)
            duration: Optional duration in seconds
            smooth: Apply smooth acceleration (default: True)
        """
        if self.simulation_mode:
            print(f"[SIM] Moving forward at speed {speed}")
        else:
            GPIO.output(self.L_IN1, GPIO.HIGH)
            GPIO.output(self.L_IN2, GPIO.LOW)
            GPIO.output(self.R_IN1, GPIO.HIGH)
            GPIO.output(self.R_IN2, GPIO.LOW)
        
        if smooth:
            self._smooth_speed_change(speed, speed)
        else:
            self._set_speed(speed, speed)
        
        if duration:
            time.sleep(duration)
            self.stop(smooth=smooth)

    def backward(self, speed=100, duration=None, smooth=True):
        """
        Move the robot backward with full motor power.
        
        Args:
            speed: Motor speed 0-100 (default: 100 for maximum power)
            duration: Optional duration in seconds
            smooth: Apply smooth acceleration (default: True)
        """
        if self.simulation_mode:
            print(f"[SIM] Moving backward at speed {speed}")
        else:
            GPIO.output(self.L_IN1, GPIO.LOW)
            GPIO.output(self.L_IN2, GPIO.HIGH)
            GPIO.output(self.R_IN1, GPIO.LOW)
            GPIO.output(self.R_IN2, GPIO.HIGH)
        
        if smooth:
            self._smooth_speed_change(speed, speed)
        else:
            self._set_speed(speed, speed)
        
        if duration:
            time.sleep(duration)
            self.stop(smooth=smooth)

    def left(self, speed=85, duration=None, smooth=True):
        """
        Turn the robot left on the spot with optimized power.
        
        Args:
            speed: Motor speed 0-100 (default: 85 for smooth turning)
            duration: Optional duration in seconds
            smooth: Apply smooth acceleration (default: True)
        """
        if self.simulation_mode:
            print(f"[SIM] Turning left at speed {speed}")
        else:
            GPIO.output(self.L_IN1, GPIO.LOW)
            GPIO.output(self.L_IN2, GPIO.HIGH) # Left motor backward
            GPIO.output(self.R_IN1, GPIO.HIGH)
            GPIO.output(self.R_IN2, GPIO.LOW)  # Right motor forward
        
        if smooth:
            self._smooth_speed_change(speed, speed)
        else:
            self._set_speed(speed, speed)
        
        if duration:
            time.sleep(duration)
            self.stop(smooth=smooth)

    def right(self, speed=85, duration=None, smooth=True):
        """
        Turn the robot right on the spot with optimized power.
        
        Args:
            speed: Motor speed 0-100 (default: 85 for smooth turning)
            duration: Optional duration in seconds
            smooth: Apply smooth acceleration (default: True)
        """
        if self.simulation_mode:
            print(f"[SIM] Turning right at speed {speed}")
        else:
            GPIO.output(self.L_IN1, GPIO.HIGH)
            GPIO.output(self.L_IN2, GPIO.LOW)  # Left motor forward
            GPIO.output(self.R_IN1, GPIO.LOW)
            GPIO.output(self.R_IN2, GPIO.HIGH) # Right motor backward
        
        if smooth:
            self._smooth_speed_change(speed, speed)
        else:
            self._set_speed(speed, speed)
        
        if duration:
            time.sleep(duration)
            self.stop(smooth=smooth)

    def stop(self, smooth=False):
        """
        Stop all motor movement.
        
        Args:
            smooth: Apply smooth deceleration (default: False for immediate stop)
        """
        if smooth:
            # Gradually reduce speed for smooth stop
            if not self.simulation_mode:
                for i in range(10, 0, -1):
                    self._set_speed(i * 10, i * 10)
                    time.sleep(0.02)
        
        if self.simulation_mode:
            print("[SIM] Stopping motors")
        else:
            GPIO.output(self.L_IN1, GPIO.LOW)
            GPIO.output(self.L_IN2, GPIO.LOW)
            GPIO.output(self.R_IN1, GPIO.LOW)
            GPIO.output(self.R_IN2, GPIO.LOW)
        self._set_speed(0, 0)
    
    def arc_turn(self, direction='left', speed=80, radius_factor=0.5, duration=None):
        """
        Perform an arc turn by running one motor faster than the other.
        
        Args:
            direction: 'left' or 'right'
            speed: Speed of faster motor (0-100)
            radius_factor: Speed ratio of slower motor (0.0-1.0, default: 0.5)
            duration: Optional duration in seconds
        """
        slow_speed = int(speed * radius_factor)
        
        if self.simulation_mode:
            print(f"[SIM] Arc turning {direction} at speed {speed}/{slow_speed}")
        else:
            GPIO.output(self.L_IN1, GPIO.HIGH)
            GPIO.output(self.L_IN2, GPIO.LOW)
            GPIO.output(self.R_IN1, GPIO.HIGH)
            GPIO.output(self.R_IN2, GPIO.LOW)
        
        if direction == 'left':
            self._set_speed(slow_speed, speed)  # Left slower, right faster
        else:
            self._set_speed(speed, slow_speed)  # Left faster, right slower
        
        if duration:
            time.sleep(duration)
            self.stop()
    
    def pivot(self, direction='left', speed=60, duration=None):
        """
        Pivot on one wheel (one motor off, other motor on).
        
        Args:
            direction: 'left' or 'right' - which direction to pivot
            speed: Speed of the active motor (0-100)
            duration: Optional duration in seconds
        """
        if self.simulation_mode:
            print(f"[SIM] Pivoting {direction} at speed {speed}")
        else:
            if direction == 'left':
                # Right motor forward, left motor off
                GPIO.output(self.L_IN1, GPIO.LOW)
                GPIO.output(self.L_IN2, GPIO.LOW)
                GPIO.output(self.R_IN1, GPIO.HIGH)
                GPIO.output(self.R_IN2, GPIO.LOW)
                self._set_speed(0, speed)
            else:
                # Left motor forward, right motor off
                GPIO.output(self.L_IN1, GPIO.HIGH)
                GPIO.output(self.L_IN2, GPIO.LOW)
                GPIO.output(self.R_IN1, GPIO.LOW)
                GPIO.output(self.R_IN2, GPIO.LOW)
                self._set_speed(speed, 0)
        
        if duration:
            time.sleep(duration)
            self.stop()
    
    def differential_drive(self, left_speed, right_speed, duration=None):
        """
        Direct control of individual motor speeds for advanced maneuvers.
        
        Args:
            left_speed: Left motor speed -100 to 100 (negative = reverse)
            right_speed: Right motor speed -100 to 100 (negative = reverse)
            duration: Optional duration in seconds
        """
        if self.simulation_mode:
            print(f"[SIM] Differential drive: L={left_speed}, R={right_speed}")
        else:
            # Set left motor direction
            if left_speed >= 0:
                GPIO.output(self.L_IN1, GPIO.HIGH)
                GPIO.output(self.L_IN2, GPIO.LOW)
            else:
                GPIO.output(self.L_IN1, GPIO.LOW)
                GPIO.output(self.L_IN2, GPIO.HIGH)
            
            # Set right motor direction
            if right_speed >= 0:
                GPIO.output(self.R_IN1, GPIO.HIGH)
                GPIO.output(self.R_IN2, GPIO.LOW)
            else:
                GPIO.output(self.R_IN1, GPIO.LOW)
                GPIO.output(self.R_IN2, GPIO.HIGH)
            
            self._set_speed(abs(left_speed), abs(right_speed))
        
        if duration:
            time.sleep(duration)
            self.stop()

    def cleanup(self):
        """Clean up GPIO resources."""
        if self._cleaned_up:
            print("MotorController already cleaned up, skipping.")
            return
        
        self._cleaned_up = True
        
        if not self.simulation_mode:
            try:
                self.l_pwm.stop()
                self.r_pwm.stop()
                print("MotorController cleaned up.")
            except Exception as e:
                print(f"Error cleaning up MotorController: {e}")
            # GPIO.cleanup() is handled by HardwareManager

# Singleton instance
_motor_controller = None

def get_motor_controller():
    """Get or create the motor controller singleton"""
    global _motor_controller
    if _motor_controller is None:
        _motor_controller = MotorController()
    return _motor_controller

if __name__ == '__main__':
    # Example usage
    motors = MotorController()
    try:
        print("Moving forward for 2 seconds")
        motors.forward(speed=90, duration=2)
        
        print("Moving backward for 2 seconds")
        motors.backward(speed=90, duration=2)

        print("Turning left for 1 second")
        motors.left(duration=1)

        print("Turning right for 1 second")
        motors.right(duration=1)

        print("Test complete.")
    except KeyboardInterrupt:
        print("Stopping...")
    finally:
        motors.cleanup()
        hardware_manager.cleanup()
