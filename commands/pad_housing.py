"""
Pad Housing Commands

Commands for interacting with pad housing units:
- ENTER <code> <direction> - Enter a pad with the correct code (also works for cubes)
- CLOSE DOOR - Close and lock the door from inside
- PAY RENT <direction> - Pay rent for a pad or cube
- CREATEPAD <direction> <name> - Admin: Create a new pad with its own zone
- SETRENT <direction> <amount> - Admin: Set weekly rent for a pad
- SETPADRENTER <direction> = <character> - Admin: Assign a renter to a pad
- PADINFO <direction> - Admin: View pad information
- CLEARPADRENTER <direction> - Admin: Remove renter from a pad
"""

import time
from evennia import Command, CmdSet
from evennia.utils import create
from evennia.utils.search import search_object
from evennia.objects.models import ObjectDB
from typeclasses.pad_housing import (
    PadDoor, PadRoom, generate_unique_pad_code,
    PAD_CODE_LENGTH, PAD_DEFAULT_WEEKLY_RENT, RENT_PERIOD_SECONDS
)


def find_exit_by_direction(room, direction):
    """
    Find an exit in the given direction from a room.
    
    Args:
        room: The room to search exits from
        direction: The direction to look for (handles aliases)
        
    Returns:
        Exit or None
    """
    direction = direction.lower()
    for ex in room.exits:
        ex_aliases = [a.lower() for a in ex.aliases.all()] if hasattr(ex.aliases, "all") else []
        if ex.key.lower() == direction or direction in ex_aliases:
            return ex
    return None


def is_pad_or_cube_door(exit_obj):
    """Check if an exit is a PadDoor or CubeDoor."""
    return (exit_obj.is_typeclass("typeclasses.pad_housing.PadDoor") or 
            exit_obj.is_typeclass("typeclasses.cube_housing.CubeDoor"))


def is_pad_door(exit_obj):
    """Check if an exit is a PadDoor."""
    return exit_obj.is_typeclass("typeclasses.pad_housing.PadDoor")


def is_cube_door(exit_obj):
    """Check if an exit is a CubeDoor."""
    return exit_obj.is_typeclass("typeclasses.cube_housing.CubeDoor")


class CmdEnterPad(Command):
    """
    Enter a pad or cube using the door code.
    
    Usage:
        enter <code> <direction>
        
    Examples:
        enter ABC123 north
        enter XY7Z9K n
        
    The code is a 6-character alphanumeric code provided when you rent
    or are given access to a pad/cube. The direction is the exit to the door.
    
    For pads: The door unlocks and swings open. You must then walk through.
    For cubes: You are moved inside automatically.
    """
    
    key = "enter"
    locks = "cmd:all()"
    help_category = "Housing"
    
    def func(self):
        caller = self.caller
        
        if not self.args:
            caller.msg("Usage: enter <code> <direction>")
            return
        
        args = self.args.strip().split()
        if len(args) < 2:
            caller.msg("Usage: enter <code> <direction>")
            return
        
        code = args[0].upper()
        direction = " ".join(args[1:]).lower()
        
        # Find the exit in the given direction
        exit_obj = find_exit_by_direction(caller.location, direction)
        
        if not exit_obj:
            caller.msg("There is no exit in that direction.")
            return
        
        # Check if it's a PadDoor or CubeDoor
        if is_pad_door(exit_obj):
            self._handle_pad_entry(caller, exit_obj, code, direction)
        elif is_cube_door(exit_obj):
            self._handle_cube_entry(caller, exit_obj, code, direction)
        else:
            caller.msg("That is not a housing door.")
    
    def _handle_pad_entry(self, caller, exit_obj, code, direction):
        """Handle entry through a pad door."""
        # Check access
        can_enter, error_msg = exit_obj.can_traverse(code)
        
        if not can_enter:
            caller.msg(error_msg)
            return
        
        # Success - unlock the door (player must walk through manually)
        exit_obj.unlock_door()
        
        # Messages - plain text only, no colors
        caller.msg("The keypad chirps once. The door swings open.")
        
        # Message to the room (others see them enter code)
        caller.location.msg_contents(
            f"{caller.key} pushes a code on the {direction} and the door swings open.",
            exclude=[caller]
        )
    
    def _handle_cube_entry(self, caller, exit_obj, code, direction):
        """Handle entry through a cube door (auto-traverse for cubes)."""
        # Check access
        can_enter, error_msg = exit_obj.can_traverse(code)
        
        if not can_enter:
            caller.msg(error_msg)
            return
        
        # Success - traverse with authorization (cubes auto-enter)
        destination = exit_obj.destination
        
        # Messages
        caller.msg("The keypad chirps once. The door swings open.")
        
        # Message to the room (others see them enter)
        caller.location.msg_contents(
            f"{caller.key} enters a code in the door and the cube door swings open before they head inside.",
            exclude=[caller]
        )
        
        # Temporarily unlock the door to allow traversal
        was_closed = getattr(exit_obj, 'is_closed', True)
        exit_obj.is_closed = False
        
        # Perform the actual traversal (quiet=False so room is shown)
        caller.move_to(destination, quiet=False)
        
        # Re-lock the door
        exit_obj.is_closed = was_closed
        
        # Message in destination room
        caller.location.msg_contents(
            f"{caller.key} enters through the cube door, which clicks shut behind them.",
            exclude=[caller]
        )


class CmdCloseDoorPad(Command):
    """
    Close and lock the door from inside.
    
    Usage:
        close door
        close door <direction>
        
    Closes and locks the pad/cube door. When inside, this closes the door
    that leads into your pad/cube (preventing entry from outside).
    """
    
    key = "close door"
    aliases = ["closedoor"]
    locks = "cmd:all()"
    help_category = "Housing"
    
    def func(self):
        caller = self.caller
        room = caller.location
        
        # Parse optional direction argument
        direction = self.args.strip().lower() if self.args else None
        
        housing_door = None
        
        # First, check if any exit FROM this room is a PadDoor or CubeDoor
        if direction:
            exit_obj = find_exit_by_direction(room, direction)
            if exit_obj and is_pad_or_cube_door(exit_obj):
                housing_door = exit_obj
        else:
            # Check all exits from this room for housing doors
            for ex in room.exits:
                if is_pad_or_cube_door(ex):
                    housing_door = ex
                    break
        
        # If no housing door exit found, check for doors leading INTO this room
        # (for when you are INSIDE a pad/cube and want to close the door)
        if not housing_door:
            # Check for PadDoors leading into this room
            incoming_pad_doors = ObjectDB.objects.filter(
                db_typeclass_path__contains="PadDoor",
                db_destination=room
            )
            
            if incoming_pad_doors.count() == 1:
                housing_door = incoming_pad_doors.first()
                if housing_door:
                    housing_door = housing_door.typeclass
            elif incoming_pad_doors.count() > 1:
                # Multiple pad doors - need direction
                if not direction:
                    caller.msg("There are multiple doors here. Please specify a direction.")
                    return
            
            # Also check CubeDoors
            if not housing_door:
                incoming_cube_doors = ObjectDB.objects.filter(
                    db_typeclass_path__contains="CubeDoor",
                    db_destination=room
                )
                
                if incoming_cube_doors.count() == 1:
                    housing_door = incoming_cube_doors.first()
                    if housing_door:
                        housing_door = housing_door.typeclass
                elif incoming_cube_doors.count() > 1 and not direction:
                    caller.msg("There are multiple doors here. Please specify a direction.")
                    return
        
        if not housing_door:
            caller.msg("There is no housing door here to close.")
            return
        
        # Handle based on door type
        if is_pad_door(housing_door):
            # Lock the pad door
            housing_door.lock_door()
            caller.msg("You pull the door shut. The lock clicks.")
            room.msg_contents(
                f"{caller.key} pulls the door shut. The lock clicks.",
                exclude=[caller]
            )
        else:
            # CubeDoor behavior
            if hasattr(housing_door, 'is_closed') and housing_door.is_closed:
                caller.msg("The door is already closed.")
                return
            
            housing_door.is_closed = True
            
            # Also close paired door if it exists
            paired_door_id = housing_door.db.paired_door_id
            if paired_door_id:
                try:
                    paired = ObjectDB.objects.get(id=paired_door_id)
                    if paired and hasattr(paired, 'is_closed'):
                        paired.is_closed = True
                except ObjectDB.DoesNotExist:
                    pass
            
            caller.msg("You pull the door shut. The keypad beeps once and the red indicator steadies.")
            room.msg_contents(
                f"{caller.key} pulls the door shut. The keypad beeps once.",
                exclude=[caller]
            )


class CmdOpenDoorPad(Command):
    """
    Open a closed door from inside (cubes only - pads use ENTER).
    
    Usage:
        open door
        open door <direction>
        
    Opens a cube door you previously closed. When inside a cube, this opens
    the door that leads into your cube.
    
    Note: Pad doors require using ENTER <code> <direction> to unlock.
    """
    
    key = "open door"
    aliases = ["opendoor"]
    locks = "cmd:all()"
    help_category = "Housing"
    
    def func(self):
        caller = self.caller
        room = caller.location
        
        # Parse optional direction argument
        direction = self.args.strip().lower() if self.args else None
        
        housing_door = None
        
        # First, check if any exit FROM this room is a CubeDoor (pads dont use open door)
        if direction:
            exit_obj = find_exit_by_direction(room, direction)
            if exit_obj and is_cube_door(exit_obj):
                housing_door = exit_obj
        else:
            # Check all exits from this room for cube doors
            for ex in room.exits:
                if is_cube_door(ex):
                    housing_door = ex
                    break
        
        # If no CubeDoor exit found, check for CubeDoors leading INTO this room
        if not housing_door:
            incoming_cube_doors = ObjectDB.objects.filter(
                db_typeclass_path__contains="CubeDoor",
                db_destination=room
            )
            
            if incoming_cube_doors.count() == 1:
                housing_door = incoming_cube_doors.first()
                if housing_door:
                    housing_door = housing_door.typeclass
            elif incoming_cube_doors.count() > 1 and not direction:
                caller.msg("There are multiple doors here. Please specify a direction.")
                return
        
        # Check for pad doors - inform user they need to use ENTER
        if not housing_door:
            # Check if there's a pad door
            for ex in room.exits:
                if is_pad_door(ex):
                    caller.msg("Pad doors require using ENTER <code> <direction> to unlock.")
                    return
            
            incoming_pad_doors = ObjectDB.objects.filter(
                db_typeclass_path__contains="PadDoor",
                db_destination=room
            )
            if incoming_pad_doors.exists():
                caller.msg("Pad doors require using ENTER <code> <direction> to unlock.")
                return
            
            caller.msg("There is no door here to open.")
            return
        
        # Open the cube door
        if hasattr(housing_door, 'is_closed') and housing_door.is_closed:
            housing_door.is_closed = False
            
            # Also open paired door if it exists
            paired_door_id = housing_door.db.paired_door_id
            if paired_door_id:
                try:
                    paired = ObjectDB.objects.get(id=paired_door_id)
                    if paired and hasattr(paired, 'is_closed'):
                        paired.is_closed = False
                except ObjectDB.DoesNotExist:
                    pass
            
            caller.msg("You push the door open. The keypad beeps softly and the indicator dims.")
            room.msg_contents(
                f"{caller.key} pushes the door open. The keypad beeps softly.",
                exclude=[caller]
            )
        else:
            caller.msg("The door is already open.")


class CmdPayRentPad(Command):
    """
    Pay rent for a pad or cube you are renting.
    
    Usage:
        pay rent <direction>
        pay rent <direction> = <amount>
        
    Examples:
        pay rent north
        pay rent n = 10
        
    Payment is taken from your cash on hand.
    - For pads: Rate is set per-pad (weekly rent). Payment converts to time.
    - For cubes: Rate is 100 dollars per day.
    
    Partial payments are accepted and convert to rental time.
    Anyone can pay rent on a pad/cube, but only the assigned renter gets the code.
    """
    
    key = "pay rent"
    aliases = ["payrent"]
    locks = "cmd:all()"
    help_category = "Housing"
    
    def func(self):
        caller = self.caller
        
        if not self.args:
            caller.msg("Usage: pay rent <direction> [= <amount>]")
            return
        
        # Parse args
        if "=" in self.args:
            direction, amount_str = self.args.split("=", 1)
            direction = direction.strip().lower()
            try:
                amount = int(amount_str.strip())
            except ValueError:
                caller.msg("Amount must be a number.")
                return
        else:
            direction = self.args.strip().lower()
            amount = None  # Will pay all available cash
        
        # Find the exit
        exit_obj = find_exit_by_direction(caller.location, direction)
        
        if not exit_obj:
            caller.msg("There is no exit in that direction.")
            return
        
        # Check if it's a PadDoor or CubeDoor
        if is_pad_door(exit_obj):
            self._handle_pad_payment(caller, exit_obj, direction, amount)
        elif is_cube_door(exit_obj):
            self._handle_cube_payment(caller, exit_obj, direction, amount)
        else:
            caller.msg("That is not a housing door.")
    
    def _handle_pad_payment(self, caller, exit_obj, direction, amount):
        """Handle rent payment for a pad."""
        # Get caller's cash
        cash = caller.cash_on_hand or 0
        
        if cash <= 0:
            caller.msg("You have no cash on hand.")
            return
        
        # Determine payment amount
        if amount is None:
            amount = cash
        
        if amount > cash:
            caller.msg(f"You only have {cash} dollars on hand.")
            return
        
        if amount <= 0:
            caller.msg("You must pay a positive amount.")
            return
        
        # If unrented, set caller as the renter and generate a code
        if not exit_obj.current_renter_id:
            exit_obj.current_renter = caller
            exit_obj.current_door_code = generate_unique_pad_code()
            caller.msg(f"You have claimed the pad! Your access code is: {exit_obj.current_door_code}")
            
            # Set character housing attributes
            caller.db.housing_tier = "pad"
            caller.db.pad_id = exit_obj.id
            caller.db.pad_code = exit_obj.current_door_code
        
        # Process payment
        caller.cash_on_hand = cash - amount
        seconds_added = exit_obj.add_rent_time(amount)
        
        # Calculate time added for display
        days = int(seconds_added // 86400)
        hours = int((seconds_added % 86400) // 3600)
        minutes = int((seconds_added % 3600) // 60)
        
        time_parts = []
        if days:
            time_parts.append(f"{days} day{'s' if days != 1 else ''}")
        if hours:
            time_parts.append(f"{hours} hour{'s' if hours != 1 else ''}")
        if minutes:
            time_parts.append(f"{minutes} minute{'s' if minutes != 1 else ''}")
        
        time_str = ", ".join(time_parts) if time_parts else "less than a minute"
        
        caller.msg(f"You pay {amount} dollars. Rent extended by {time_str}.")
        caller.msg(f"Rent paid until: {exit_obj.get_rent_remaining()} remaining.")
    
    def _handle_cube_payment(self, caller, exit_obj, direction, amount):
        """Handle rent payment for a cube (reuses existing cube logic)."""
        from typeclasses.cube_housing import generate_unique_code
        
        # Get caller's cash
        cash = caller.cash_on_hand or 0
        
        if cash <= 0:
            caller.msg("You have no cash on hand.")
            return
        
        # Determine payment amount
        if amount is None:
            amount = cash
        
        if amount > cash:
            caller.msg(f"You only have {cash} dollars on hand.")
            return
        
        if amount <= 0:
            caller.msg("You must pay a positive amount.")
            return
        
        # If unrented, set caller as the renter and generate a code
        if not exit_obj.current_renter_id:
            exit_obj.current_renter = caller
            exit_obj.current_door_code = generate_unique_code()
            caller.msg(f"You have claimed the cube! Your access code is: {exit_obj.current_door_code}")
        
        # Process payment
        caller.cash_on_hand = cash - amount
        seconds_added = exit_obj.add_rent_time(amount)
        
        # Calculate time added for display
        days = int(seconds_added // 86400)
        hours = int((seconds_added % 86400) // 3600)
        minutes = int((seconds_added % 3600) // 60)
        
        time_parts = []
        if days:
            time_parts.append(f"{days} day{'s' if days != 1 else ''}")
        if hours:
            time_parts.append(f"{hours} hour{'s' if hours != 1 else ''}")
        if minutes:
            time_parts.append(f"{minutes} minute{'s' if minutes != 1 else ''}")
        
        time_str = ", ".join(time_parts) if time_parts else "less than a minute"
        
        caller.msg(f"You pay {amount} dollars. Rent extended by {time_str}.")
        caller.msg(f"Rent paid until: {exit_obj.get_rent_remaining()} remaining.")


class CmdCreatePad(Command):
    """
    Create a new pad housing unit with its own zone.
    
    Usage:
        createpad <direction> <name>
        
    Examples:
        createpad north Luxury Pad 1A
        createpad e Riverside Suite
        
    This creates:
    - A new Zone for the pad (named "Pad: <name>")
    - A pad interior entry room inside that zone
    - A PadDoor exit from the current room to the pad entry
    - A return exit from the pad back to the hallway (also requires code)
    
    The pad starts unassigned with no renter and no active code.
    Default weekly rent is $1 (use SETRENT to change).
    """
    
    key = "createpad"
    locks = "cmd:perm(Builder)"
    help_category = "Building"
    
    def func(self):
        caller = self.caller
        
        if not self.args:
            caller.msg("Usage: createpad <direction> <name>")
            return
        
        args = self.args.strip().split(None, 1)  # Split into direction and rest
        if len(args) < 2:
            caller.msg("Usage: createpad <direction> <name>")
            return
        
        direction = args[0].lower()
        pad_name = args[1]
        
        # Map direction to display name
        direction_display_map = {
            "north": "north (n)", "south": "south (s)", "east": "east (e)", "west": "west (w)",
            "northeast": "northeast (ne)", "northwest": "northwest (nw)", 
            "southeast": "southeast (se)", "southwest": "southwest (sw)",
            "up": "up (u)", "down": "down (d)", "n": "north (n)", "s": "south (s)",
            "e": "east (e)", "w": "west (w)", "ne": "northeast (ne)", "nw": "northwest (nw)",
            "se": "southeast (se)", "sw": "southwest (sw)", "u": "up (u)", "d": "down (d)"
        }
        direction_display = direction_display_map.get(direction, direction)
        
        # Check if exit already exists in that direction
        existing_exit = find_exit_by_direction(caller.location, direction)
        if existing_exit:
            caller.msg("An exit already exists in that direction.")
            return
        
        # Normalize direction to full name for exit key
        direction_names = {
            "n": "north", "s": "south", "e": "east", "w": "west",
            "ne": "northeast", "nw": "northwest", "se": "southeast", "sw": "southwest",
            "u": "up", "d": "down"
        }
        exit_name = direction_names.get(direction, direction)
        
        # Validate direction
        valid_directions = list(direction_names.keys()) + list(direction_names.values())
        if direction not in valid_directions:
            caller.msg(f"Unknown direction: {direction}")
            return
        
        # Find the highest zone number to create a unique zone
        from typeclasses.rooms import Room
        rooms = [obj for obj in ObjectDB.objects.all() 
                 if obj.is_typeclass(Room, exact=False) and getattr(obj, 'zone', None) is not None]
        zone_numbers = []
        for room in rooms:
            try:
                zone_num = int(room.zone)
                zone_numbers.append(zone_num)
            except (ValueError, TypeError):
                continue
        next_zone = max(zone_numbers) + 1 if zone_numbers else 0
        zone_id = str(next_zone)
        zone_name = f"Pad: {pad_name}"
        
        # Create the pad entry room using PadRoom typeclass
        pad_room = create.create_object(
            typeclass="typeclasses.pad_housing.PadRoom",
            key=f"{pad_name} - Entry"
        )
        
        # Set zone and coordinates for the pad room
        pad_room.zone = zone_id
        pad_room.db.x = 0
        pad_room.db.y = 0
        pad_room.db.z = 0
        pad_room.db.desc = "This is a room."
        pad_room.pad_zone_id = zone_id
        pad_room.is_pad_entry = True
        
        # Create the door from hallway to pad
        door_to_pad = create.create_object(
            typeclass="typeclasses.pad_housing.PadDoor",
            key=exit_name,
            location=caller.location,
            destination=pad_room
        )
        
        # Add short alias for direction
        alias_map = {
            "north": "n", "south": "s", "east": "e", "west": "w",
            "northeast": "ne", "northwest": "nw", "southeast": "se", "southwest": "sw",
            "up": "u", "down": "d"
        }
        if exit_name in alias_map:
            door_to_pad.aliases.add(alias_map[exit_name])
        
        # Get reverse direction for return exit
        reverse_map = {
            "north": "south", "south": "north", "east": "west", "west": "east",
            "northeast": "southwest", "southwest": "northeast",
            "northwest": "southeast", "southeast": "northwest",
            "up": "down", "down": "up"
        }
        reverse_dir = reverse_map.get(exit_name, "out")
        
        # Create return exit as a PadDoor too (requires code to leave for security)
        door_to_hallway = create.create_object(
            typeclass="typeclasses.pad_housing.PadDoor",
            key=reverse_dir,
            location=pad_room,
            destination=caller.location
        )
        if reverse_dir in alias_map:
            door_to_hallway.aliases.add(alias_map[reverse_dir])
        
        # Configure the entry door (from hallway)
        door_to_pad.zone_id = zone_id
        door_to_pad.hallway_room_id = caller.location.id
        door_to_pad.is_entry_door = True
        door_to_pad.paired_door_id = door_to_hallway.id
        door_to_pad.weekly_rent = PAD_DEFAULT_WEEKLY_RENT
        
        # Configure the exit door (from pad to hallway)
        door_to_hallway.zone_id = zone_id
        door_to_hallway.hallway_room_id = caller.location.id
        door_to_hallway.is_entry_door = False
        door_to_hallway.paired_door_id = door_to_pad.id
        door_to_hallway.weekly_rent = PAD_DEFAULT_WEEKLY_RENT
        
        # Tag both doors
        door_to_pad.tags.add("pad_door", category="housing")
        door_to_hallway.tags.add("pad_door", category="housing")
        
        # Output summary to admin
        caller.msg("-" * 50)
        caller.msg("PAD CREATED")
        caller.msg("-" * 50)
        caller.msg(f"Direction: {direction_display}")
        caller.msg(f"Pad Name: {pad_name}")
        caller.msg(f"Zone Created: {zone_id} ({zone_name})")
        caller.msg(f"Entry Room: {pad_room.key} ({pad_room.dbref})")
        caller.msg(f"Entry Door: {door_to_pad.key} ({door_to_pad.dbref})")
        caller.msg(f"Exit Door: {door_to_hallway.key} ({door_to_hallway.dbref})")
        caller.msg(f"Weekly Rent: ${PAD_DEFAULT_WEEKLY_RENT}")
        caller.msg(f"State: UNASSIGNED (no renter, no code)")
        caller.msg("-" * 50)
        caller.msg(f"Use 'setrent {exit_name} <amount>' to set weekly rent.")
        caller.msg(f"Use 'setpadrenter {exit_name} = <character>' to assign a renter.")


class CmdSetRent(Command):
    """
    Set the weekly rent for a pad.
    
    Usage:
        setrent <direction> <amount>
        
    Examples:
        setrent north 50
        setrent e 100
        
    Sets the pad's weekly rent to the specified amount (must be > 0).
    """
    
    key = "setrent"
    locks = "cmd:perm(Builder)"
    help_category = "Building"
    
    def func(self):
        caller = self.caller
        
        if not self.args:
            caller.msg("Usage: setrent <direction> <amount>")
            return
        
        args = self.args.strip().split()
        if len(args) < 2:
            caller.msg("Usage: setrent <direction> <amount>")
            return
        
        direction = args[0].lower()
        try:
            amount = int(args[1])
        except ValueError:
            caller.msg("Amount must be a number.")
            return
        
        if amount <= 0:
            caller.msg("Rent amount must be greater than 0.")
            return
        
        # Find the exit
        exit_obj = find_exit_by_direction(caller.location, direction)
        
        if not exit_obj:
            caller.msg("There is no exit in that direction.")
            return
        
        # Check if it's a PadDoor
        if not is_pad_door(exit_obj):
            caller.msg("That is not a pad door.")
            return
        
        # Set the weekly rent
        exit_obj.weekly_rent = amount
        
        # Also set on paired door if it exists
        if exit_obj.paired_door_id:
            try:
                paired = ObjectDB.objects.get(id=exit_obj.paired_door_id)
                if paired and hasattr(paired, 'weekly_rent'):
                    paired.weekly_rent = amount
            except ObjectDB.DoesNotExist:
                pass
        
        caller.msg(f"Pad rent set to ${amount}/week.")


class CmdSetPadRenter(Command):
    """
    Assign a renter to a pad and generate their access code.
    
    Usage:
        setpadrenter <direction> = <character>
        
    Examples:
        setpadrenter north = Bob
        setpadrenter e = Alice
        
    This assigns the character as the pad's renter, generates a new unique
    6-character access code, and initializes their rent period.
    
    The new renter will be messaged their access code.
    """
    
    key = "setpadrenter"
    aliases = ["padrenter"]
    locks = "cmd:perm(Builder)"
    help_category = "Building"
    
    def func(self):
        caller = self.caller
        
        if not self.args or "=" not in self.args:
            caller.msg("Usage: setpadrenter <direction> = <character>")
            return
        
        direction, char_name = self.args.split("=", 1)
        direction = direction.strip().lower()
        char_name = char_name.strip()
        
        # Find the exit
        exit_obj = find_exit_by_direction(caller.location, direction)
        
        if not exit_obj:
            caller.msg("There is no exit in that direction.")
            return
        
        # Check if it's a PadDoor
        if not is_pad_door(exit_obj):
            caller.msg("That is not a pad door.")
            return
        
        # Find the character
        char_matches = search_object(char_name)
        if not char_matches:
            caller.msg(f"Character '{char_name}' not found.")
            return
        
        # Filter to actual characters
        char = None
        for match in char_matches:
            if match.is_typeclass("typeclasses.characters.Character"):
                char = match
                break
        
        if not char:
            caller.msg(f"'{char_name}' is not a valid character.")
            return
        
        # Generate new unique code
        new_code = generate_unique_pad_code()
        
        # Assign renter and code
        old_renter = exit_obj.current_renter
        exit_obj.current_renter = char
        exit_obj.current_door_code = new_code
        
        # Also set on paired door
        if exit_obj.paired_door_id:
            try:
                paired = ObjectDB.objects.get(id=exit_obj.paired_door_id)
                if paired:
                    paired.current_renter_id = char.id
                    paired.current_door_code = new_code
            except ObjectDB.DoesNotExist:
                pass
        
        # Initialize rent (start from now with a small grace period)
        if not exit_obj.rent_paid_until_ts or exit_obj.rent_paid_until_ts < time.time():
            # Give 1 hour grace period for new renters
            exit_obj.rent_paid_until_ts = time.time() + 3600
            if exit_obj.paired_door_id:
                try:
                    paired = ObjectDB.objects.get(id=exit_obj.paired_door_id)
                    if paired:
                        paired.rent_paid_until_ts = exit_obj.rent_paid_until_ts
                except ObjectDB.DoesNotExist:
                    pass
        
        # Set character housing attributes
        char.db.housing_tier = "pad"
        char.db.pad_id = exit_obj.id
        char.db.pad_code = new_code
        char.db.rent_paid_until_ts = exit_obj.rent_paid_until_ts
        
        caller.msg(f"Assigned {char.key} as renter of pad to the {direction}.")
        caller.msg(f"New access code: {new_code}")
        caller.msg(f"Rent grace period: 1 hour. Renter should pay rent to extend.")
        
        # Message the renter (plain text only)
        if char.has_account:
            char.msg(f"You have been assigned a pad. Your access code is: {new_code}")
            char.msg(f"Use 'enter {new_code} <direction>' to unlock the door, then walk through.")
            char.msg(f"Use 'pay rent <direction>' to pay rent (${exit_obj.weekly_rent} per week).")


class CmdPadInfo(Command):
    """
    View information about a pad door.
    
    Usage:
        padinfo <direction>
        
    Shows the pad's current renter, rent status, weekly rent, and other details.
    Builder+ only.
    """
    
    key = "padinfo"
    locks = "cmd:perm(Builder)"
    help_category = "Building"
    
    def func(self):
        caller = self.caller
        
        if not self.args:
            caller.msg("Usage: padinfo <direction>")
            return
        
        direction = self.args.strip().lower()
        
        # Find the exit
        exit_obj = find_exit_by_direction(caller.location, direction)
        
        if not exit_obj:
            caller.msg("There is no exit in that direction.")
            return
        
        # Check if it's a PadDoor
        if not is_pad_door(exit_obj):
            caller.msg("That is not a pad door.")
            return
        
        # Display info
        lines = [f"Pad Door: {exit_obj.key} (#{exit_obj.id})"]
        lines.append("-" * 40)
        
        renter = exit_obj.current_renter
        if renter:
            lines.append(f"Current Renter: {renter.key} (#{renter.id})")
        else:
            lines.append("Current Renter: None (unassigned)")
        
        if exit_obj.current_door_code:
            lines.append(f"Access Code: {exit_obj.current_door_code}")
        else:
            lines.append("Access Code: None")
        
        lines.append(f"Weekly Rent: ${exit_obj.weekly_rent}")
        
        if exit_obj.rent_paid_until_ts:
            if exit_obj.is_rent_current():
                lines.append(f"Rent Status: PAID ({exit_obj.get_rent_remaining()} remaining)")
            else:
                lines.append("Rent Status: EXPIRED")
        else:
            lines.append("Rent Status: Never paid")
        
        lines.append(f"Zone ID: {exit_obj.zone_id}")
        lines.append(f"Is Entry Door: {exit_obj.is_entry_door}")
        lines.append(f"Destination: {exit_obj.destination.key if exit_obj.destination else 'None'}")
        lines.append(f"Paired Door ID: {exit_obj.paired_door_id}")
        
        caller.msg("\n".join(lines))


class CmdClearPadRenter(Command):
    """
    Remove a renter from a pad.
    
    Usage:
        clearpadrenter <direction>
        
    This removes the renter assignment and deactivates the access code.
    The pad returns to an unassigned state.
    """
    
    key = "clearpadrenter"
    aliases = ["removepadrenter"]
    locks = "cmd:perm(Builder)"
    help_category = "Building"
    
    def func(self):
        caller = self.caller
        
        if not self.args:
            caller.msg("Usage: clearpadrenter <direction>")
            return
        
        direction = self.args.strip().lower()
        
        # Find the exit
        exit_obj = find_exit_by_direction(caller.location, direction)
        
        if not exit_obj:
            caller.msg("There is no exit in that direction.")
            return
        
        # Check if it's a PadDoor
        if not is_pad_door(exit_obj):
            caller.msg("That is not a pad door.")
            return
        
        old_renter = exit_obj.current_renter
        
        # Clear renter data from character if they exist
        if old_renter:
            if old_renter.db.housing_tier == "pad" and old_renter.db.pad_id == exit_obj.id:
                old_renter.db.housing_tier = None
                old_renter.db.pad_id = None
                old_renter.db.pad_code = None
                old_renter.db.rent_paid_until_ts = None
        
        # Clear renter and code from door
        exit_obj.current_renter = None
        exit_obj.current_door_code = None
        exit_obj.rent_paid_until_ts = 0
        
        # Also clear on paired door
        if exit_obj.paired_door_id:
            try:
                paired = ObjectDB.objects.get(id=exit_obj.paired_door_id)
                if paired:
                    paired.current_renter_id = None
                    paired.current_door_code = None
                    paired.rent_paid_until_ts = 0
            except ObjectDB.DoesNotExist:
                pass
        
        if old_renter:
            caller.msg(f"Removed {old_renter.key} as renter. Pad is now unassigned.")
        else:
            caller.msg("Pad was already unassigned.")


class CmdCheckPad(Command):
    """
    Check a pad door to see its cost and rental status.
    
    Usage:
        check <direction>
        
    Examples:
        check north
        check n
        
    Shows the weekly rate and either "Available for rent" or how long the rent is paid for.
    Works for both pad doors and cube doors.
    """
    
    key = "check"
    locks = "cmd:all()"
    help_category = "Housing"
    
    def func(self):
        caller = self.caller
        
        if not self.args:
            caller.msg("Usage: check <direction>")
            return
        
        direction = self.args.strip().lower()
        
        # Find the exit in the given direction
        exit_obj = find_exit_by_direction(caller.location, direction)
        
        if not exit_obj:
            caller.msg("There is no exit in that direction.")
            return
        
        # Check if it's a PadDoor
        if is_pad_door(exit_obj):
            caller.msg(f"Pad {direction}")
            caller.msg(f"  Weekly Rate: ${exit_obj.weekly_rent}")
            
            if exit_obj.current_door_code and exit_obj.is_rent_current():
                rent_remaining = exit_obj.get_rent_remaining()
                caller.msg(f"  Rental Status: Paid - {rent_remaining} remaining")
            else:
                caller.msg("  Rental Status: Available for rent")
        elif is_cube_door(exit_obj):
            from world.economy.constants import CUBE_RENT_PER_DAY
            
            caller.msg(f"Cube {direction}")
            caller.msg(f"  Nightly Rate: ${CUBE_RENT_PER_DAY}")
            
            if exit_obj.current_door_code and exit_obj.is_rent_current():
                rent_remaining = exit_obj.get_rent_remaining()
                caller.msg(f"  Rental Status: Paid - {rent_remaining} remaining")
            else:
                caller.msg("  Rental Status: Available for rent")
        else:
            caller.msg("That is not a housing door.")


class PadHousingCmdSet(CmdSet):
    """Command set for pad housing commands."""
    
    key = "pad_housing"
    
    def at_cmdset_creation(self):
        # Player commands
        self.add(CmdEnterPad())      # Replaces cube enter, handles both
        self.add(CmdCheckPad())      # Replaces cube check, handles both
        self.add(CmdCloseDoorPad())  # Replaces cube close door, handles both
        self.add(CmdOpenDoorPad())   # Open door (cubes only, pads use ENTER)
        self.add(CmdPayRentPad())    # Replaces cube pay rent, handles both
        
        # Admin commands
        self.add(CmdCreatePad())
        self.add(CmdSetRent())
        self.add(CmdSetPadRenter())
        self.add(CmdPadInfo())
        self.add(CmdClearPadRenter())
