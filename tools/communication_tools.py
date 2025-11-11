"""
Enhanced Speaking and Communication Tools for Jarvis
Combines voice output with body language, display, and sensors
"""

from langchain.agents import tool
from typing import Optional
import time


@tool
def speak_with_gesture(params: str) -> str:
    """
    Speak text while performing a gesture and showing on display.
    
    Format: "text|gesture|display_text"
    - text: What to speak
    - gesture: Gesture to perform (optional, use 'none' to skip)
    - display_text: Text to show on LCD (optional)
    
    Example: "Hello Sir|greeting_sir|Hello!" or "Yes sir|nod"
    
    Use when you want synchronized speech, gesture, and display.
    """
    try:
        parts = params.split('|')
        text = parts[0] if len(parts) > 0 else ""
        gesture = parts[1] if len(parts) > 1 and parts[1].lower() != 'none' else None
        display_text = parts[2] if len(parts) > 2 else text[:16]
        
        result = []
        
        # Show on display
        try:
            from actuators.display import display
            if display_text:
                display.clear()
                display.write_text(display_text[:16], row=0, col=0)
                result.append("✓ Display updated")
        except Exception as e:
            result.append(f"⚠ Display: {e}")
        
        # Perform gesture
        if gesture:
            try:
                from core.body_language import body_language_engine
                body_language_engine.perform_gesture(gesture, blocking=False)
                result.append(f"✓ Gesture: {gesture}")
            except Exception as e:
                result.append(f"⚠ Gesture: {e}")
        
        # Speak (this will be handled by voice engine)
        result.append(f"✓ Speech: '{text}'")
        
        return " | ".join(result)
        
    except Exception as e:
        return f"❌ Error: {e}. Format: 'text|gesture|display_text'"


@tool
def greet_with_speech(person_name: str = "Sir") -> str:
    """
    Complete greeting with speech, gesture, and display for a person.
    
    Args:
        person_name: Name of person (e.g., "Sachin Sir", "Madam", "Guest")
    
    This performs:
    1. Appropriate greeting gesture
    2. Speech greeting
    3. Display greeting message
    
    Use when: "greet Sachin sir", "welcome the guest", "say hello to madam"
    """
    try:
        from core.greeting_manager import GreetingManager
        from core.body_language import body_language_engine
        from actuators.display import display
        
        # Build greeting
        greeting_mgr = GreetingManager(user_name=person_name)
        greeting_script = greeting_mgr.build_person_greeting(person_name)
        
        # Show on display
        if greeting_script.display_lines:
            try:
                display.clear()
                for i, line in enumerate(greeting_script.display_lines[:2]):
                    display.write_text(line, row=i, col=0)
            except:
                pass
        
        # Perform gesture
        if greeting_script.gesture:
            try:
                body_language_engine.perform_gesture(greeting_script.gesture, blocking=False)
            except:
                pass
        
        # Return speech text for voice engine
        speech = greeting_script.speech_text()
        
        return f"✓ Greeting {person_name}: '{speech}' [Gesture: {greeting_script.gesture}]"
        
    except Exception as e:
        return f"❌ Error greeting: {e}"


@tool
def respond_with_emotion(params: str) -> str:
    """
    Respond to something with emotional body language and speech.
    
    Format: "emotion|response_text"
    Emotions: happy, excited, sad, confused, thinking, alert, agree, disagree
    
    Example: "excited|That's amazing!" or "thinking|Let me consider that"
    
    Use when responding to user with emotion.
    """
    try:
        parts = params.split('|', 1)
        emotion = parts[0].strip() if len(parts) > 0 else "happy"
        text = parts[1].strip() if len(parts) > 1 else "Understood"
        
        # Express emotion through gesture
        try:
            from core.body_language import body_language_engine
            gesture = body_language_engine.gesture_for_emotion(emotion)
            gesture_status = f"✓ Gesture: {gesture}"
        except Exception as e:
            gesture_status = f"⚠ Gesture failed: {e}"
        
        # Show on display
        try:
            from actuators.display import display
            display.clear()
            display.write_text(emotion.upper()[:16], row=0, col=0)
            display.write_text(text[:16], row=1, col=0)
            display_status = "✓ Display updated"
        except:
            display_status = "⚠ Display unavailable"
        
        return f"✓ Response: '{text}' | Emotion: {emotion} | {gesture_status} | {display_status}"
        
    except Exception as e:
        return f"❌ Error: {e}. Format: 'emotion|text'"


@tool  
def announce_sensor_alert(params: str) -> str:
    """
    Announce sensor alert with appropriate body language.
    
    Format: "sensor_type|message"
    Sensor types: temperature, humidity, distance, motion, alcohol
    
    Example: "temperature|Temperature is high!" or "motion|Motion detected"
    
    Use when announcing sensor-based alerts.
    """
    try:
        parts = params.split('|', 1)
        sensor_type = parts[0].strip().lower() if len(parts) > 0 else "general"
        message = parts[1].strip() if len(parts) > 1 else "Alert!"
        
        # Gesture based on sensor type
        gesture_map = {
            'temperature': 'confused',
            'humidity': 'think',
            'distance': 'alert',
            'motion': 'alert',
            'alcohol': 'disagree',
        }
        gesture = gesture_map.get(sensor_type, 'nod')
        
        try:
            from core.body_language import body_language_engine
            body_language_engine.perform_gesture(gesture, blocking=False)
        except:
            pass
        
        # Show warning on display
        try:
            from actuators.display import display
            display.show_warning(message, level="WARNING")
        except:
            pass
        
        return f"✓ Alert announced: '{message}' [Sensor: {sensor_type}, Gesture: {gesture}]"
        
    except Exception as e:
        return f"❌ Error: {e}. Format: 'sensor_type|message'"


all_communication_tools = [
    speak_with_gesture,
    greet_with_speech,
    respond_with_emotion,
    announce_sensor_alert,
]
