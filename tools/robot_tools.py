"""
This module provides tools for controlling the robot's physical movements and gestures.
Enhanced with smooth movements, context-aware gestures, and sensor integration.
"""

from langchain.agents import tool
from core.body_language import body_language_engine
from actuators.multi_servo_controller import multi_servo_controller

@tool
def perform_gesture(gesture_name: str) -> str:
    """
    Performs a pre-programmed body gesture with smooth servo movements.
    
    Available gestures:
    - Basic: 'nod', 'shake_head', 'agree', 'disagree', 'think'
    - Arms: 'wave_right', 'wave_left', 'raise_hand', 'raise_both_hands'
    - Greetings: 'greeting_sir', 'greeting_wave', 'namaste', 'salute'
    - Emotions: 'excited', 'confused', 'celebrate'
    - Actions: 'listening', 'alert', 'point_forward', 'scan_area'
    
    Use this when asked to gesture, wave, nod, salute, greet, celebrate, etc.
    """
    try:
        available_gestures = body_language_engine.list_gestures()
        
        if gesture_name not in available_gestures:
            return f"❌ Gesture '{gesture_name}' not found. Available: {', '.join(available_gestures)}"
        
        body_language_engine.perform_gesture(gesture_name, blocking=False)
        return f"✓ Performing gesture '{gesture_name}' with smooth movements"
        
    except Exception as e:
        return f"❌ Error performing gesture '{gesture_name}': {e}"

@tool
def greet_person(person_name: str = "Sir") -> str:
    """
    Greet a specific person with appropriate gesture and body language.
    
    Args:
        person_name: Name of person to greet (e.g., "Sachin Sir", "Madam", "Guest")
    
    This automatically selects the right gesture:
    - "Sachin Sir" or "Sir" → greeting_sir (professional with hand wave)
    - "Mam" or "Madam" → namaste (traditional greeting)
    - Others → greeting_wave (friendly wave)
    
    Use when: "greet Sachin sir", "say hello to", "welcome", etc.
    """
    try:
        gesture_performed = body_language_engine.gesture_for_greeting(person_name)
        return f"✓ Greeting {person_name} with {gesture_performed} gesture"
    except Exception as e:
        return f"❌ Error greeting {person_name}: {e}"

@tool
def express_emotion(emotion: str) -> str:
    """
    Express an emotion through body language.
    
    Emotions: 'happy', 'excited', 'sad', 'confused', 'thinking', 'alert', 'agree', 'disagree', 'listening'
    
    Use when: "look happy", "show excitement", "act confused", "be alert", etc.
    """
    try:
        gesture = body_language_engine.gesture_for_emotion(emotion)
        return f"✓ Expressing '{emotion}' with {gesture} gesture"
    except Exception as e:
        return f"❌ Error expressing emotion: {e}"

@tool
def look_direction(direction: str) -> str:
    """
    Turn head/neck to look in a direction.
    
    Directions: 'left', 'right', 'forward', 'up', 'down', 'baen' (left), 'daen' (right)
    
    Use when: "look left", "turn your head right", "look forward", etc.
    """
    try:
        body_language_engine.point_direction(direction)
        return f"✓ Looking {direction}"
    except Exception as e:
        return f"❌ Error turning head: {e}"

@tool
def set_servo_position(params: str) -> str:
    """
    Sets a single servo to a specific angle smoothly.
    Input format: "servo_name,angle" (e.g., "neck,90").
    Servo names: 'neck', 'arm_l', 'arm_r'.
    Angle: 0-180.
    
    Use for precise servo control when needed.
    """
    try:
        servo_name, angle_str = params.split(',')
        angle = int(angle_str)
        multi_servo_controller.set_angle(servo_name.strip(), angle, smooth=True, duration=0.5)
        return f"✓ Servo '{servo_name.strip()}' moved smoothly to {angle}°"
    except Exception as e:
        return f"❌ Error: {e}. Use format 'servo_name,angle'"

@tool
def center_all_servos(_: str = "") -> str:
    """
    Centers all servos to their default 90-degree position smoothly.
    Use when: "reset position", "center servos", "go to neutral", etc.
    """
    try:
        body_language_engine.center_all()
        return "✓ All servos centered smoothly to neutral position"
    except Exception as e:
        return f"❌ Error centering servos: {e}"

@tool
def scan_surroundings(_: str = "") -> str:
    """
    Make robot scan the surroundings by looking left, center, and right.
    Use when: "scan area", "look around", "check surroundings", etc.
    """
    try:
        body_language_engine.perform_gesture('scan_area', blocking=False)
        return "✓ Scanning surroundings with head movement"
    except Exception as e:
        return f"❌ Error scanning: {e}"

all_robot_tools = [
    perform_gesture,
    greet_person,
    express_emotion,
    look_direction,
    set_servo_position,
    center_all_servos,
    scan_surroundings,
]
