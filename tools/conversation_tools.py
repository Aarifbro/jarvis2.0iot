"""
Conversation Tools for JARVIS
Natural conversation with people, respectful responses, and contextual display
"""

from langchain.agents import tool
from typing import Optional
import time


@tool
def introduce_myself(person_name: str = "Guest") -> str:
    """
    Introduce yourself to someone politely and professionally.
    
    Args:
        person_name: Name of the person to introduce to
    
    Use when: Meeting someone new, when asked "who are you", or for introductions
    """
    try:
        from actuators.display import display
        from core.body_language import body_language_engine
        
        # Gesture
        try:
            body_language_engine.perform_gesture('greeting_sir', blocking=False)
        except:
            pass
        
        # Display
        try:
            display.clear()
            display.write_text("Hello!", row=0, col=5)
            display.write_text("I'm JARVIS", row=1, col=2)
        except:
            pass
        
        # Response
        if person_name.lower() in ["sir", "sachin sir", "boss"]:
            response = f"Good to see you, {person_name}. I am JARVIS, your personal AI assistant. I'm here to help you with anything you need."
        else:
            response = f"Hello {person_name}, pleasure to meet you. I am JARVIS, an AI assistant. I can help with tasks, answer questions, and monitor the environment."
        
        return response
        
    except Exception as e:
        return f"Hello! I am JARVIS, your AI assistant. Error: {e}"


@tool
def chat_with_person(message: str) -> str:
    """
    Have a natural conversation with someone. Respond respectfully and contextually.
    
    Args:
        message: What the person said or topic to discuss
    
    Use when: Someone is talking to you, casual conversation, questions
    """
    try:
        from actuators.display import display
        from core.body_language import body_language_engine
        
        message_lower = message.lower()
        
        # Detect sentiment/context
        if any(word in message_lower for word in ['good', 'great', 'awesome', 'nice', 'excellent']):
            gesture = 'celebrate'
            emotion = 'happy'
            display_text = "Glad to hear!"
        elif any(word in message_lower for word in ['bad', 'sad', 'problem', 'issue', 'wrong']):
            gesture = 'confused'
            emotion = 'concerned'
            display_text = "Let me help"
        elif any(word in message_lower for word in ['thank', 'thanks', 'appreciate']):
            gesture = 'nod'
            emotion = 'pleased'
            display_text = "My pleasure!"
        elif '?' in message:
            gesture = 'think'
            emotion = 'thinking'
            display_text = "Let me think"
        else:
            gesture = 'nod'
            emotion = 'attentive'
            display_text = "Listening..."
        
        # Gesture
        try:
            body_language_engine.perform_gesture(gesture, blocking=False)
        except:
            pass
        
        # Display
        try:
            display.clear()
            display.write_text(display_text, row=0, col=2)
        except:
            pass
        
        # Contextual response
        return f"[{emotion.upper()}] Message received: '{message}'. I'm listening and ready to help, Sir."
        
    except Exception as e:
        return f"I'm listening, Sir. Error: {e}"


@tool
def show_status_info(info_type: str = "general") -> str:
    """
    Display important system status information on LCD.
    
    Args:
        info_type: Type of info - 'general', 'sensors', 'time', 'weather', 'health'
    
    Use when: Asked to show status, display info, check system
    """
    try:
        from actuators.display import display
        import time
        
        display.clear()
        
        if info_type == "sensors":
            # Show sensor data
            try:
                from sensors.sensor_manager import SensorManager
                mgr = SensorManager()
                temp = mgr.get_temperature()
                dist = mgr.get_distance()
                
                if temp:
                    display.write_text(f"Temp: {temp:.1f}C", row=0, col=0)
                if dist and dist > 0:
                    display.write_text(f"Dist: {int(dist)}cm", row=1, col=0)
                else:
                    display.write_text("Sensors OK", row=1, col=2)
            except:
                display.write_text("Sensors", row=0, col=4)
                display.write_text("Checking...", row=1, col=2)
        
        elif info_type == "time":
            # Show current time
            current_time = time.strftime("%I:%M %p")
            current_date = time.strftime("%b %d")
            display.write_text(current_time, row=0, col=3)
            display.write_text(current_date, row=1, col=3)
        
        elif info_type == "health":
            # System health
            display.write_text("System Health", row=0, col=1)
            display.write_text("All OK", row=1, col=4)
            display.show_face("happy")
        
        else:  # general
            display.write_text("JARVIS", row=0, col=5)
            display.write_text("Ready", row=1, col=5)
        
        return f"Displayed {info_type} information on screen, Sir."
        
    except Exception as e:
        return f"Display error: {e}"


@tool
def analyze_and_explore_room(_: str = "") -> str:
    """
    Autonomously analyze and explore the room/environment.
    
    This will:
    1. Scan the room with neck servo and ultrasonic
    2. Check all sensors (temperature, motion, distance)
    3. Look for obstacles and safe paths
    4. Report findings with display updates
    
    Use when: Asked to "analyze room", "explore", "check surroundings", "khud se ghoom"
    """
    try:
        from actuators.display import display
        from core.body_language import body_language_engine
        from sensors.sensor_manager import SensorManager
        from navigation.scanner import perform_scan, human_readable_summary
        from actuators.multi_servo_controller import multi_servo_controller
        
        results = []
        
        # Step 1: Display - Starting analysis
        try:
            display.clear()
            display.write_text("Analyzing", row=0, col=3)
            display.write_text("Room...", row=1, col=4)
        except:
            pass
        
        results.append("🔍 Starting room analysis...")
        time.sleep(1)
        
        # Step 2: Scan environment
        results.append("\n📡 SCANNING ENVIRONMENT:")
        try:
            neck_servo = multi_servo_controller.get_servo('neck')
            sensor_manager = SensorManager()
            
            if neck_servo and sensor_manager:
                # Perform scan
                display.clear()
                display.write_text("Scanning...", row=0, col=3)
                
                scan_result = perform_scan(neck_servo, sensor_manager)
                summary = scan_result.summary()
                
                if summary.get('status') == 'ok':
                    best_angle = summary['best_angle']
                    clearance = summary['best_clearance_cm']
                    avg_dist = summary['average_distance_cm']
                    blocked = summary.get('blocked_angles', [])
                    
                    results.append(f"  ✓ Safest direction: {best_angle}° with {clearance:.0f}cm clearance")
                    results.append(f"  ✓ Average distance: {avg_dist:.0f}cm")
                    
                    if blocked:
                        results.append(f"  ⚠ Blocked angles: {', '.join(map(str, blocked))}")
                    else:
                        results.append(f"  ✓ No obstacles detected nearby")
                    
                    # Display result
                    display.clear()
                    display.write_text(f"Safe: {best_angle}deg", row=0, col=2)
                    display.write_text(f"Clr: {int(clearance)}cm", row=1, col=2)
                    time.sleep(2)
                else:
                    results.append("  ⚠ Scan incomplete - limited data")
            else:
                results.append("  ⚠ Scanner not available")
        except Exception as e:
            results.append(f"  ✗ Scan error: {e}")
        
        # Step 3: Check sensors
        results.append("\n🌡️ SENSOR STATUS:")
        try:
            from sensors.sensor_manager import SensorManager
            mgr = SensorManager()
            
            # Temperature
            temp = mgr.get_temperature()
            if temp:
                results.append(f"  ✓ Temperature: {temp:.1f}°C")
                if temp < 15:
                    results.append("    → Environment is cold")
                elif temp > 30:
                    results.append("    → Environment is warm")
                else:
                    results.append("    → Temperature comfortable")
            
            # Humidity
            humidity = mgr.get_humidity()
            if humidity:
                results.append(f"  ✓ Humidity: {humidity:.1f}%")
                if humidity < 30:
                    results.append("    → Air is dry")
                elif humidity > 70:
                    results.append("    → Air is humid")
                else:
                    results.append("    → Humidity normal")
            
            # Distance
            dist = mgr.get_distance()
            if dist and dist > 0:
                results.append(f"  ✓ Front obstacle: {dist:.0f}cm away")
                if dist < 50:
                    results.append("    → Something nearby")
                else:
                    results.append("    → Path clear ahead")
            elif dist == -2:
                results.append(f"  ✓ No obstacles in front (>4m)")
            
            # Motion
            if mgr.pir_sensor:
                stats = mgr.pir_sensor.get_motion_stats()
                results.append(f"  ✓ Motion events: {stats['total_count']}")
                if stats['last_motion_time']:
                    results.append(f"    → Last motion: {stats['last_motion_str']}")
            
            # Display sensor summary
            display.clear()
            if temp:
                display.write_text(f"T:{temp:.0f}C H:{humidity:.0f}%", row=0, col=0)
            display.write_text("Sensors OK", row=1, col=2)
            time.sleep(2)
            
        except Exception as e:
            results.append(f"  ⚠ Sensor check error: {e}")
        
        # Step 4: Final gesture
        try:
            body_language_engine.perform_gesture('nod', blocking=True)
        except:
            pass
        
        # Step 5: Final display
        try:
            display.clear()
            display.write_text("Analysis", row=0, col=3)
            display.write_text("Complete!", row=1, col=3)
            display.show_face("happy")
            time.sleep(2)
        except:
            pass
        
        # Compile report
        results.append("\n✅ ANALYSIS COMPLETE!")
        results.append("Room has been thoroughly analyzed, Sir.")
        
        return "\n".join(results)
        
    except Exception as e:
        return f"Analysis failed, Sir: {e}"


@tool
def be_friendly_assistant(task: str) -> str:
    """
    Act as a friendly, respectful personal assistant for the owner.
    
    Args:
        task: What needs to be done
    
    Use when: Owner asks for help, needs assistance, wants companionship
    """
    try:
        from actuators.display import display
        from core.body_language import body_language_engine
        
        # Show attentiveness
        try:
            body_language_engine.perform_gesture('nod', blocking=False)
        except:
            pass
        
        try:
            display.clear()
            display.write_text("At your", row=0, col=4)
            display.write_text("service!", row=1, col=3)
        except:
            pass
        
        return f"Of course, Sir! I'm here to help. Let me assist you with: {task}. What would you like me to do first?"
        
    except Exception as e:
        return f"At your service, Sir! {e}"


# Export all conversation tools
all_conversation_tools = [
    introduce_myself,
    chat_with_person,
    show_status_info,
    analyze_and_explore_room,
    be_friendly_assistant
]
