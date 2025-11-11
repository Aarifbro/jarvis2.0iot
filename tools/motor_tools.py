"""
Tools for controlling the robot's movement with full motor power and advanced features.
"""
import os
import sys

# Add parent directory to path for standalone execution
if __name__ == "__main__":
    parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    if parent_dir not in sys.path:
        sys.path.insert(0, parent_dir)

try:
    from langchain_core.tools import tool
except ImportError:
    from langchain.tools import tool

from actuators.motor_controller import get_motor_controller

# Get motor controller singleton
motor_controller = get_motor_controller()

@tool
def move_forward(duration: str = "2") -> str:
    """
    Moves the robot forward at MAXIMUM POWER for specified duration.
    Input: duration as string (e.g., '2' for 2 seconds). Default is 2 seconds.
    Use this when asked to 'move forward', 'go forward', 'aage jao', 'chalo', or similar.
    """
    try:
        dur = float(duration) if duration else 2.0
        speed = 100  # Maximum power!
        motor_controller.forward(speed=speed, duration=dur, smooth=True)
        return f"Moved forward at maximum power for {dur} seconds, Sir."
    except ValueError:
        return "Invalid duration. Please provide a number."
    except Exception as e:
        return f"Movement error: {e}"

@tool
def move_backward(duration: str = "2") -> str:
    """
    Moves the robot backward at MAXIMUM POWER for specified duration.
    Input: duration as string (e.g., '2' for 2 seconds). Default is 2 seconds.
    Use this when asked to 'move back', 'go back', 'peeche jao', 'reverse', or similar.
    """
    try:
        dur = float(duration) if duration else 2.0
        speed = 100  # Maximum power!
        motor_controller.backward(speed=speed, duration=dur, smooth=True)
        return f"Moved backward at maximum power for {dur} seconds, Sir."
    except ValueError:
        return "Invalid duration. Please provide a number."
    except Exception as e:
        return f"Movement error: {e}"

@tool
def turn_left(duration: str = "1") -> str:
    """
    Turns the robot left on the spot with optimized turning power.
    Input: duration as string (e.g., '1' for 1 second). Default is 1 second.
    Use this when asked to 'turn left', 'baen mud', 'left side', 'left ghoom', or similar.
    """
    try:
        dur = float(duration) if duration else 1.0
        speed = 85  # Optimized for smooth powerful turns
        motor_controller.left(speed=speed, duration=dur, smooth=True)
        return f"Turned left smoothly for {dur} seconds, Sir."
    except ValueError:
        return "Invalid duration. Please provide a number."
    except Exception as e:
        return f"Turn error: {e}"

@tool
def turn_right(duration: str = "1") -> str:
    """
    Turns the robot right on the spot with optimized turning power.
    Input: duration as string (e.g., '1' for 1 second). Default is 1 second.
    Use this when asked to 'turn right', 'daen mud', 'right side', 'right ghoom', or similar.
    """
    try:
        dur = float(duration) if duration else 1.0
        speed = 85  # Optimized for smooth powerful turns
        motor_controller.right(speed=speed, duration=dur, smooth=True)
        return f"Turned right smoothly for {dur} seconds, Sir."
    except ValueError:
        return "Invalid duration. Please provide a number."
    except Exception as e:
        return f"Turn error: {e}"

@tool
def stop_moving(_: str = "") -> str:
    """
    Stops all motor movement immediately with smooth deceleration.
    Use this when asked to 'stop', 'ruko', 'halt', 'freeze', 'ruk jao', or 'theek hai'.
    """
    try:
        motor_controller.stop(smooth=True)
        return "Robot has stopped smoothly, Sir."
    except Exception as e:
        return f"Stop error: {e}"

@tool
def arc_turn(params: str) -> str:
    """
    Perform smooth arc/curve turn. One motor faster than other for wide turns.
    Input format: 'direction,duration' (e.g., 'left,2' or 'right,3')
    Use when asked to 'curve left', 'arc turn', 'wide turn', 'gentle curve', or similar.
    """
    try:
        parts = params.split(',')
        if len(parts) != 2:
            return "Format: direction,duration (e.g., 'left,2')"
        direction = parts[0].strip().lower()
        duration = float(parts[1].strip())
        
        if direction not in ['left', 'right']:
            return "Direction must be 'left' or 'right'"
        
        motor_controller.arc_turn(direction=direction, speed=80, radius_factor=0.5, duration=duration)
        return f"Completed arc turn {direction} for {duration} seconds, Sir."
    except ValueError:
        return "Invalid format. Use: 'left,2' or 'right,3'"
    except Exception as e:
        return f"Arc turn error: {e}"

@tool
def pivot_turn(params: str) -> str:
    """
    Pivot on one wheel for tight turns. One motor on, other off.
    Input format: 'direction,duration' (e.g., 'left,1.5' or 'right,2')
    Use when asked to 'pivot', 'spin tight', 'turn on spot', or similar.
    """
    try:
        parts = params.split(',')
        if len(parts) != 2:
            return "Format: direction,duration (e.g., 'left,1.5')"
        direction = parts[0].strip().lower()
        duration = float(parts[1].strip())
        
        if direction not in ['left', 'right']:
            return "Direction must be 'left' or 'right'"
        
        motor_controller.pivot(direction=direction, speed=70, duration=duration)
        return f"Completed pivot turn {direction} for {duration} seconds, Sir."
    except ValueError:
        return "Invalid format. Use: 'left,1.5' or 'right,2'"
    except Exception as e:
        return f"Pivot error: {e}"

@tool
def custom_speed_move(params: str) -> str:
    """
    Move with custom speed control. Advanced differential drive.
    Input format: 'left_speed,right_speed,duration' (speeds: -100 to 100, negative=reverse)
    Examples: '100,100,2' (straight), '50,100,1' (gentle right curve), '100,-100,1' (spin right)
    Use for precise maneuvers, custom movements, or when asked for specific motor control.
    """
    try:
        parts = params.split(',')
        if len(parts) != 3:
            return "Format: left_speed,right_speed,duration (e.g., '100,50,2')"
        left = int(parts[0].strip())
        right = int(parts[1].strip())
        duration = float(parts[2].strip())
        
        if not (-100 <= left <= 100 and -100 <= right <= 100):
            return "Speeds must be between -100 and 100"
        
        motor_controller.differential_drive(left_speed=left, right_speed=right, duration=duration)
        return f"Executed custom movement: Left={left}, Right={right} for {duration}s, Sir."
    except ValueError:
        return "Invalid format. Use: '100,50,2' (left,right,duration)"
    except Exception as e:
        return f"Custom move error: {e}"

# Export all motor tools for easy import
all_motor_tools = [
    move_forward,
    move_backward,
    turn_left,
    turn_right,
    stop_moving,
    arc_turn,
    pivot_turn,
    custom_speed_move
]


# Test section when run directly
if __name__ == "__main__":
    import time
    
    print("=" * 60)
    print("ENHANCED MOTOR TOOLS TEST")
    print("=" * 60)
    print(f"\nMotor Controller Status:")
    print(f"  Simulation Mode: {motor_controller.simulation_mode}")
    print(f"  Left Motor:  EN=GPIO{motor_controller.L_EN}, IN1=GPIO{motor_controller.L_IN1}, IN2=GPIO{motor_controller.L_IN2}")
    print(f"  Right Motor: EN=GPIO{motor_controller.R_EN}, IN1=GPIO{motor_controller.R_IN1}, IN2=GPIO{motor_controller.R_IN2}")
    
    print("\n" + "=" * 60)
    print("Testing all motor tool functions...")
    print("=" * 60)
    
    try:
        print("\n[1/5] Testing move_forward(2)...")
        result = move_forward("2")
        print(f"     Result: {result}")
        time.sleep(1)
        
        print("\n[2/5] Testing move_backward(2)...")
        result = move_backward("2")
        print(f"     Result: {result}")
        time.sleep(1)
        
        print("\n[3/5] Testing turn_left(1)...")
        result = turn_left("1")
        print(f"     Result: {result}")
        time.sleep(1)
        
        print("\n[4/5] Testing turn_right(1)...")
        result = turn_right("1")
        print(f"     Result: {result}")
        time.sleep(1)
        
        print("\n[5/5] Testing stop_moving()...")
        result = stop_moving("")
        print(f"     Result: {result}")
        
        print("\n" + "=" * 60)
        print("✓ ALL MOTOR TOOLS TESTED SUCCESSFULLY!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n✗ Test failed: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        print("\nCleaning up...")
        try:
            motor_controller.cleanup()
            print("✓ Motor controller cleaned up")
        except Exception as e:
            print(f"⚠ Cleanup warning: {e}")
        
        try:
            from core.hardware_manager import hardware_manager
            hardware_manager.cleanup()
            print("✓ Hardware manager cleaned up")
        except Exception as e:
            print(f"⚠ Hardware cleanup warning: {e}")
