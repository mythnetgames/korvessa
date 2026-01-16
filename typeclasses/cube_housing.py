"""
Cube Housing System

Implements the cube door access system for rentable housing units.
Cubes are small rooms with keypad-locked doors that require a code to enter.
"""

import time
import random
import string
from evennia.objects.objects import DefaultExit, DefaultRoom
from evennia.typeclasses.attributes import AttributeProperty
from .exits import Exit
from .rooms import Room
from world.economy.constants import CUBE_RENT_PER_DAY


# Cube-specific constants
CUBE_CODE_LENGTH = 6


def generate_unique_code():
    """
    Generate a unique 6-character alphanumeric code (A-Z, 0-9).
    Checks against all active cube codes to ensure uniqueness.
    """
    from evennia.objects.models import ObjectDB
    
    # Get all active cube door codes
    active_codes = set()
    cube_doors = ObjectDB.objects.filter(
        db_typeclass_path__contains="CubeDoor"
    )
    
    now = time.time()
    for door in cube_doors:
        # Only count codes from cubes with active rent
        rent_until = door.db.rent_paid_until_ts or 0
        if rent_until > now and door.db.current_door_code:
            active_codes.add(door.db.current_door_code.upper())
    
    # Generate unique code
    chars = string.ascii_uppercase + string.digits
    for _ in range(100):  # Max attempts
        code = ''.join(random.choice(chars) for _ in range(CUBE_CODE_LENGTH))
        if code not in active_codes:
            return code
    
    # Fallback - should never happen with 36^6 possibilities
    return ''.join(random.choice(chars) for _ in range(CUBE_CODE_LENGTH))


class CubeDoor(Exit):
    """
    A keypad-locked door for cube housing units.
    
    Requires a valid code and current rent to traverse.
    Access is granted via the ENTER <code> <direction> command.
    
    Attributes:
        current_door_code: 6-character A-Z0-9 code
        rent_paid_until_ts: Unix timestamp when rent expires
        current_renter: Character dbref of current renter (optional)
    """
    
    # Door properties
    current_door_code = AttributeProperty(None, category="housing", autocreate=True)
    rent_paid_until_ts = AttributeProperty(0, category="housing", autocreate=True)
    current_renter_id = AttributeProperty(None, category="housing", autocreate=True)
    
    def at_object_creation(self):
        """Called when the cube door is first created."""
        super().at_object_creation()
        # Tag as cube door for easy lookup
        self.tags.add("cube_door", category="housing")
    
    @property
    def current_renter(self):
        """Get the current renter character object."""
        if self.current_renter_id:
            from evennia.objects.models import ObjectDB
            try:
                return ObjectDB.objects.get(id=self.current_renter_id)
            except ObjectDB.DoesNotExist:
                return None
        return None
    
    @current_renter.setter
    def current_renter(self, char):
        """Set the current renter."""
        if char:
            self.current_renter_id = char.id
        else:
            self.current_renter_id = None
    
    def is_rent_current(self):
        """Check if rent is paid up."""
        if not self.rent_paid_until_ts:
            return False
        return time.time() <= self.rent_paid_until_ts
    
    def is_assigned(self):
        """Check if cube has an active renter and code."""
        return bool(self.current_door_code and self.current_renter_id)
    
    def check_code(self, code):
        """Check if the provided code matches."""
        if not self.current_door_code:
            return False
        return code.upper() == self.current_door_code.upper()
    
    def can_traverse(self, code):
        """
        Check if traversal is allowed with the given code.
        
        Returns:
            tuple: (allowed: bool, error_message: str or None)
        """
        if not self.current_door_code:
            return (False, "The keypad is dark. This unit is unassigned.")
        
        if not self.is_rent_current():
            return (False, "The keypad buzzes. Payment required. A red indicator flashes.")
        
        if not self.check_code(code):
            return (False, "The keypad beeps angrily. A red indicator flashes.")
        
        return (True, None)
    
    def at_traverse(self, traversing_object, target_location, **kwargs):
        """
        Override default traversal - cube doors cannot be traversed normally.
        They require the ENTER command with the correct code.
        """
        # Check if this is an authorized traversal (set by ENTER command)
        if kwargs.get("cube_authorized"):
            return super().at_traverse(traversing_object, target_location, **kwargs)
        
        # Block normal traversal
        traversing_object.msg("The door is locked. A red indicator light glows steadily.")
        return False
    
    def at_failed_traverse(self, traversing_object, **kwargs):
        """Called when traversal fails."""
        traversing_object.msg("The door is locked. A red indicator light glows steadily.")
    
    def get_rent_remaining(self):
        """Get human-readable time until rent expires."""
        if not self.rent_paid_until_ts:
            return "No rent paid"
        
        remaining = self.rent_paid_until_ts - time.time()
        if remaining <= 0:
            return "Expired"
        
        days = int(remaining // 86400)
        hours = int((remaining % 86400) // 3600)
        minutes = int((remaining % 3600) // 60)
        
        parts = []
        if days:
            parts.append(f"{days} day{'s' if days != 1 else ''}")
        if hours:
            parts.append(f"{hours} hour{'s' if hours != 1 else ''}")
        if minutes and not days:  # Only show minutes if less than a day
            parts.append(f"{minutes} minute{'s' if minutes != 1 else ''}")
        
        return ", ".join(parts) if parts else "Less than a minute"
    
    def add_rent_time(self, dollars):
        """
        Add rent time based on payment amount.
        
        Args:
            dollars: Amount paid in dollars
            
        Returns:
            float: Seconds of rent time added
        """
        # 100 dollars = 1 day (86400 seconds)
        seconds_per_dollar = 86400 / CUBE_RENT_PER_DAY
        seconds_added = dollars * seconds_per_dollar
        
        # If rent has expired, start from now
        now = time.time()
        if not self.rent_paid_until_ts or self.rent_paid_until_ts < now:
            self.rent_paid_until_ts = now + seconds_added
        else:
            self.rent_paid_until_ts = self.rent_paid_until_ts + seconds_added
        
        return seconds_added


class CubeRoom(Room):
    """
    A small rentable housing unit (cube).
    
    Contains a bed and has a linked CubeDoor exit.
    """
    
    def at_object_creation(self):
        """Called when the cube room is first created."""
        super().at_object_creation()
        # Tag as cube room for easy lookup
        self.tags.add("cube_room", category="housing")
    
    def get_cube_door(self):
        """
        Find the CubeDoor exit that leads out of this cube.
        
        Returns:
            CubeDoor or None
        """
        for exit_obj in self.exits:
            if exit_obj.is_typeclass("typeclasses.cube_housing.CubeDoor"):
                return exit_obj
        return None
    
    def get_exit_to_hallway(self):
        """
        Find any exit that leads out of the cube (to the hallway).
        
        Returns:
            Exit or None
        """
        # First try to find a CubeDoor
        cube_door = self.get_cube_door()
        if cube_door:
            return cube_door
        
        # Otherwise find any exit (there should only be one way out)
        if self.exits:
            return self.exits[0]
        
        return None
