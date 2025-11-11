"""Greeting manager for Jarvis.

Generates human-like greeting scripts that coordinate spoken lines,
LCD display text, body language gestures, and status prompts.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
import random
from typing import List, Optional, Callable


@dataclass
class GreetingScript:
    """Container describing what Jarvis should say, show, and do."""

    speech_lines: List[str] = field(default_factory=list)
    display_lines: List[str] = field(default_factory=list)
    gesture: Optional[str] = None  # Gesture to perform
    status_line: str = "Ready for your commands."
    log_line: Optional[str] = None

    def speech_text(self) -> str:
        """Join speech lines into a single utterance."""
        return " ".join(line.strip() for line in self.speech_lines if line.strip())


class GreetingManager:
    """Builds varied greetings based on time of day and persona hints."""

    def __init__(self, user_name: str = "Sir", location_hint: str = "control room") -> None:
        self.user_name = user_name or "Sir"
        self.location_hint = location_hint or "control room"

    def _time_bucket(self) -> str:
        hour = datetime.now().hour
        if 5 <= hour < 12:
            return "morning"
        if 12 <= hour < 17:
            return "afternoon"
        if 17 <= hour < 22:
            return "evening"
        return "night"

    def _intro_line(self) -> str:
        bucket = self._time_bucket()
        opening_options = [
            f"Good {bucket}, {self.user_name}.",
            f"Happy {bucket}, {self.user_name}.",
            f"Greetings this {bucket}, {self.user_name}.",
        ]
        return random.choice(opening_options)

    def _status_line(self, system_status: Optional[str]) -> str:
        if system_status:
            return f"Systems check: {system_status}."
        status_options = [
            "All diagnostics report green lights.",
            "Core modules are synchronised and ready.",
            "Power, sensors, and communications are nominal.",
        ]
        return random.choice(status_options)

    def _ready_prompt(self) -> str:
        prompts = [
            "How shall we begin?",
            "Ready when you are.",
            "Give me the first directive when you're set.",
            "Standing by for your command.",
        ]
        return random.choice(prompts)

    def _display_lines(self, bucket: str) -> List[str]:
        top = f"Jarvis Online"
        bottom_options = [
            f"Good {bucket.title()}!",
            f"Hello {self.user_name}",
            "Standing by",
        ]
        bottom = random.choice(bottom_options)
        # Ensure 16 character max per LCD row.
        return [top[:16], bottom[:16]]

    def build_startup_greeting(self, system_status: Optional[str] = None) -> GreetingScript:
        bucket = self._time_bucket()
        intro = self._intro_line()
        status_line = self._status_line(system_status)
        prompt = self._ready_prompt()

        speech_lines = [
            intro,
            status_line,
            f"We are in the {self.location_hint}. {prompt}",
        ]

        log_line = f"{intro} {status_line} {prompt}".strip()
        display_lines = self._display_lines(bucket)

        return GreetingScript(
            speech_lines=speech_lines,
            display_lines=display_lines,
            gesture="greeting_sir",  # Add gesture
            status_line=f"Ready for instructions ({bucket}).",
            log_line=log_line,
        )

    def build_interactive_greeting(self) -> GreetingScript:
        bucket = self._time_bucket()
        intro = self._intro_line()
        followups = [
            "Would you like a status briefing or shall we start patrol?",
            "Do you want me to scan the area or fetch today's schedule?",
            "Shall I prepare the room summary or go straight to tasks?",
        ]
        follow = random.choice(followups)

        speech_lines = [intro, follow]
        log_line = f"{intro} {follow}".strip()
        display_lines = self._display_lines(bucket)

        return GreetingScript(
            speech_lines=speech_lines,
            display_lines=display_lines,
            gesture="greeting_wave",  # Add gesture
            status_line=f"Awaiting direction ({bucket}).",
            log_line=log_line,
        )
    
    def build_person_greeting(self, person_name: str) -> GreetingScript:
        """
        Build a personalized greeting for a specific person with gesture.
        
        Args:
            person_name: Name of the person to greet
        """
        bucket = self._time_bucket()
        
        # Determine appropriate greeting based on person
        person_lower = person_name.lower()
        
        if "sachin" in person_lower or "sir" in person_lower:
            speech_lines = [
                f"Good {bucket}, {person_name}.",
                "It's an honor to assist you today.",
                "All systems are ready for your commands."
            ]
            gesture = "greeting_sir"
        elif "mam" in person_lower or "madam" in person_lower:
            speech_lines = [
                f"Namaste, {person_name}.",
                f"Good {bucket} to you.",
                "How may I assist you today?"
            ]
            gesture = "namaste"
        else:
            speech_lines = [
                f"Hello {person_name}!",
                f"Good {bucket}.",
                "Great to see you!"
            ]
            gesture = "greeting_wave"
        
        display_lines = [
            f"Hello {person_name[:12]}"[:16],  # Fit to LCD
            f"Good {bucket.title()}!"[:16]
        ]
        
        log_line = " ".join(speech_lines)
        
        return GreetingScript(
            speech_lines=speech_lines,
            display_lines=display_lines,
            gesture=gesture,
            status_line=f"Greeting {person_name}",
            log_line=log_line,
        )