"""
Cube Housing Commands

Commands for interacting with cube housing units:
- ENTER <code> <direction> - Enter a cube with the correct code
- CHECK <direction> - Check a cube's cost and rental status
- CLOSE DOOR - Close and lock the door from inside
- PAY RENT <direction> - Pay rent for a cube
- CREATECUBE <direction> - Admin: Create a new cube
- SETCUBERENTER <direction> = <character> - Admin: Assign a renter
"""

import time
from evennia import Command, CmdSet
from evennia.utils import create
from evennia.utils.search import search_object
from typeclasses.cube_housing import (
    CubeDoor, CubeRoom, generate_unique_code, 
    CUBE_RENT_PER_DAY
)


class CmdEnter(Command):
    """
    Enter a cube using the door code.
    
    Usage:
        enter <code> <direction>
        
    Examples:
        enter ABC123 north
        enter XY7Z9K n
        
    The code is a 6-character alphanumeric code provided when you rent
    or are given access to a cube. The direction is the exit to the cube door.
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
        exit_obj = None
        for ex in caller.location.exits:
            ex_aliases = [a.lower() for a in ex.aliases.all()] if hasattr(ex.aliases, "all") else []
            if ex.key.lower() == direction or direction in ex_aliases:
                exit_obj = ex
                break
        
        if not exit_obj:
            caller.msg(f"There is no exit in that direction.")
            return
        
        # Check if it's a CubeDoor
        if not exit_obj.is_typeclass("typeclasses.cube_housing.CubeDoor"):
            caller.msg("That is not a cube door.")
            return
        
        # Check access
        can_enter, error_msg = exit_obj.can_traverse(code)
        
        if not can_enter:
            caller.msg(error_msg)
            return
        
        # Success - traverse with authorization
        destination = exit_obj.destination
        
        # Messages
        caller.msg("The keypad chirps once. The door swings open.")
        
        # Message to the room (others see them enter)
        caller.location.msg_contents(
            f"{caller.key} enters as the cube door swings open, then shuts behind them.",
            exclude=[caller]
        )
        
        # Perform the actual traversal
        caller.move_to(destination, quiet=True)
        
        # Show the new room
        caller.msg(caller.location.return_appearance(caller, force_display=True))
        
        # Message in destination room
        caller.location.msg_contents(
            f"{caller.key} enters through the cube door, which clicks shut behind them.",
            exclude=[caller]
        )


class CmdCheck(Command):
    """
    Check a cube door to see its cost and rental status.
    
    Usage:
        check <direction>
        
    Examples:
        check north
        check n
        
    Shows the nightly rate and either "Available for rent" or how long the rent is paid for.
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
        exit_obj = None
        for ex in caller.location.exits:
            ex_aliases = [a.lower() for a in ex.aliases.all()] if hasattr(ex.aliases, "all") else []
            if ex.key.lower() == direction or direction in ex_aliases:
                exit_obj = ex
                break
        
        if not exit_obj:
            caller.msg(f"There is no exit in that direction.")
            return
        
        # Check if it's a CubeDoor
        if not exit_obj.is_typeclass("typeclasses.cube_housing.CubeDoor"):
            caller.msg("That is not a cube door.")
            return
        
        from world.economy.constants import CUBE_RENT_PER_DAY
        
        # Show rental info
        caller.msg(f"|cCube {direction}|n")
        caller.msg(f"  Nightly Rate: ${CUBE_RENT_PER_DAY}")
        
        if exit_obj.current_door_code and exit_obj.is_rent_current():
            rent_remaining = exit_obj.get_rent_remaining()
            caller.msg(f"  Rental Status: Paid - {rent_remaining} remaining")
        else:
            caller.msg(f"  Rental Status: Available for rent")


class CmdCloseDoor(Command):
    """
    Close and lock the cube door from inside.
    
    Usage:
        close door
        
    When inside a cube, this closes the door and locks it automatically.
    """
    
    key = "close door"
    aliases = ["closedoor"]
    locks = "cmd:all()"
    help_category = "Housing"
    
    def func(self):
        caller = self.caller
        room = caller.location
        
        # Check if we're in a cube room
        if not room.tags.has("cube_room", category="housing"):
            caller.msg("There is no cube door here to close.")
            return
        
        # Find the exit out (the cube door or any exit)
        exit_out = None
        if hasattr(room, "get_exit_to_hallway"):
            exit_out = room.get_exit_to_hallway()
        else:
            # Fallback: find any exit
            if room.exits:
                exit_out = room.exits[0]
        
        if not exit_out:
            caller.msg("There is no door to close.")
            return
        
        # Success message
        caller.msg("You pull the door shut. The lock clicks and the red indicator steadies.")
        
        # Message to others in the room
        room.msg_contents(
            f"{caller.key} pulls the door shut.",
            exclude=[caller]
        )


class CmdPayRent(Command):
    """
    Pay rent for a cube you are renting.
    
    Usage:
        pay rent <direction>
        pay rent <direction> = <amount>
        
    Examples:
        pay rent north
        pay rent n = 700
        
    Payment is taken from your cash on hand. The rate is 100 dollars per day.
    Partial payments are accepted: 700 dollars = 7 days, remainders become
    hours and minutes.
    
    You must be the registered renter of the cube to pay rent.
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
        exit_obj = None
        for ex in caller.location.exits:
            ex_aliases = [a.lower() for a in ex.aliases.all()] if hasattr(ex.aliases, "all") else []
            if ex.key.lower() == direction or direction in ex_aliases:
                exit_obj = ex
                break
        
        if not exit_obj:
            caller.msg(f"There is no exit in that direction.")
            return
        
        # Check if it's a CubeDoor
        if not exit_obj.is_typeclass("typeclasses.cube_housing.CubeDoor"):
            caller.msg("That is not a cube door.")
            return
        
        # Check if caller is the renter, or if cube is unrented
        if exit_obj.current_renter_id and exit_obj.current_renter_id != caller.id:
            caller.msg("You are not the registered renter of this cube.")
            return
        
        # If unrented, set caller as the renter and generate a code
        if not exit_obj.current_renter_id:
            exit_obj.current_renter = caller
            exit_obj.current_door_code = generate_unique_code()
            caller.msg(f"You have claimed the cube! Your access code is: {exit_obj.current_door_code}")
        
        # Get caller's cash
        cash = getattr(caller.db, "cash_on_hand", 0) or 0
        
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
        
        # Process payment
        caller.db.cash_on_hand = cash - amount
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


class CmdCreateCube(Command):
    """
    Create a new cube housing unit.
    
    Usage:
        createcube <direction> <name>
        
    Examples:
        createcube north Cube 101 - Dao Lane Motel
        createcube e Room 5B
        
    This creates:
    - A new cube room in the specified direction with the given name
    - A CubeDoor exit to the cube
    - A return exit back to this room
    - A bed inside the cube
    
    The cube starts unassigned with no renter and no active code.
    """
    
    key = "createcube"
    locks = "cmd:perm(Builder)"
    help_category = "Building"
    
    def func(self):
        caller = self.caller
        
        if not self.args:
            caller.msg("Usage: createcube <direction> <name>")
            return
        
        args = self.args.strip().split(None, 1)  # Split into direction and rest
        if len(args) < 2:
            caller.msg("Usage: createcube <direction> <name>")
            return
        
        direction = args[0].lower()
        room_name = args[1]
        
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
        for ex in caller.location.exits:
            ex_aliases = [a.lower() for a in ex.aliases.all()] if hasattr(ex.aliases, "all") else []
            if ex.key.lower() == direction or direction in ex_aliases:
                caller.msg(f"An exit already exists in that direction.")
                return
        
        # Get current room's zone and coordinates
        current_room = caller.location
        src_zone = getattr(current_room, 'zone', None)
        src_x = getattr(current_room.db, 'x', 0) or 0
        src_y = getattr(current_room.db, 'y', 0) or 0
        src_z = getattr(current_room.db, 'z', 0) or 0
        
        # Calculate new coordinates based on direction
        direction_offsets = {
            "north": (0, 1, 0), "n": (0, 1, 0),
            "south": (0, -1, 0), "s": (0, -1, 0),
            "east": (1, 0, 0), "e": (1, 0, 0),
            "west": (-1, 0, 0), "w": (-1, 0, 0),
            "northeast": (1, 1, 0), "ne": (1, 1, 0),
            "northwest": (-1, 1, 0), "nw": (-1, 1, 0),
            "southeast": (1, -1, 0), "se": (1, -1, 0),
            "southwest": (-1, -1, 0), "sw": (-1, -1, 0),
            "up": (0, 0, 1), "u": (0, 0, 1),
            "down": (0, 0, -1), "d": (0, 0, -1),
        }
        
        offset = direction_offsets.get(direction)
        if not offset:
            caller.msg(f"Unknown direction: {direction}")
            return
        
        new_x = src_x + offset[0]
        new_y = src_y + offset[1]
        new_z = src_z + offset[2]
        
        # Normalize direction to full name for exit key
        direction_names = {
            "n": "north", "s": "south", "e": "east", "w": "west",
            "ne": "northeast", "nw": "northwest", "se": "southeast", "sw": "southwest",
            "u": "up", "d": "down"
        }
        exit_name = direction_names.get(direction, direction)
        
        # Create the cube room using standard Room typeclass so it shows on map
        cube_room = create.create_object(
            typeclass="typeclasses.rooms.Room",
            key=room_name
        )
        
        # Set zone and coordinates EXPLICITLY (same as zdig)
        if src_zone:
            cube_room.zone = src_zone
        cube_room.db.x = new_x
        cube_room.db.y = new_y
        cube_room.db.z = new_z
        cube_room.db.desc = "A cramped cube, barely large enough for a bed and a small space to stand. The walls are bare metal with a faint industrial smell. A red indicator light glows by the door."
        
        # Create the door from hallway to cube
        door_to_cube = create.create_object(
            typeclass="typeclasses.cube_housing.CubeDoor",
            key=exit_name,
            location=caller.location,
            destination=cube_room
        )
        
        # Add short alias
        alias_map = {
            "north": "n", "south": "s", "east": "e", "west": "w",
            "northeast": "ne", "northwest": "nw", "southeast": "se", "southwest": "sw",
            "up": "u", "down": "d"
        }
        if exit_name in alias_map:
            door_to_cube.aliases.add(alias_map[exit_name])
        
        # Get reverse direction for return exit
        reverse_map = {
            "north": "south", "south": "north", "east": "west", "west": "east",
            "northeast": "southwest", "southwest": "northeast",
            "northwest": "southeast", "southeast": "northwest",
            "up": "down", "down": "up"
        }
        reverse_dir = reverse_map.get(exit_name, "out")
        
        # Create return exit (regular exit, not cube door - exiting is always allowed)
        door_to_hallway = create.create_object(
            typeclass="typeclasses.exits.Exit",
            key=reverse_dir,
            location=cube_room,
            destination=caller.location
        )
        if reverse_dir in alias_map:
            door_to_hallway.aliases.add(alias_map[reverse_dir])
        
        # Create the bed
        bed = create.create_object(
            typeclass="typeclasses.objects.Object",
            key="two person bed",
            location=cube_room
        )
        bed.db.desc = "A thin mattress on a metal frame, barely wide enough for two people to lie uncomfortably close. The sheets are clean but threadbare."
        bed.db.get_err_msg = "The bed is bolted to the floor."
        bed.locks.add("get:false()")
        
        zone_info = f" in zone '{src_zone}'" if src_zone else ""
        caller.msg(f"Created cube room '{cube_room.key}' ({cube_room.dbref}) at ({new_x}, {new_y}, {new_z}){zone_info}.")
        caller.msg(f"Created CubeDoor '{exit_name}' to the {direction_display}.")
        caller.msg(f"Cube is unassigned. Use 'setcuberenter {exit_name} = <character>' to assign a renter.")


class CmdSetCubeRenter(Command):
    """
    Assign a renter to a cube and generate their access code.
    
    Usage:
        setcuberenter <direction> = <character>
        
    Examples:
        setcuberenter north = Bob
        setcuberenter e = Alice
        
    This assigns the character as the cube's renter, generates a new unique
    6-character access code, and initializes their rent period.
    
    The new renter will be messaged their access code.
    """
    
    key = "setcuberenter"
    aliases = ["setcuberenter", "cuberenter"]
    locks = "cmd:perm(Builder)"
    help_category = "Building"
    
    def func(self):
        caller = self.caller
        
        if not self.args or "=" not in self.args:
            caller.msg("Usage: setcuberenter <direction> = <character>")
            return
        
        direction, char_name = self.args.split("=", 1)
        direction = direction.strip().lower()
        char_name = char_name.strip()
        
        # Find the exit
        exit_obj = None
        for ex in caller.location.exits:
            ex_aliases = [a.lower() for a in ex.aliases.all()] if hasattr(ex.aliases, "all") else []
            if ex.key.lower() == direction or direction in ex_aliases:
                exit_obj = ex
                break
        
        if not exit_obj:
            caller.msg(f"There is no exit in that direction.")
            return
        
        # Check if it's a CubeDoor
        if not exit_obj.is_typeclass("typeclasses.cube_housing.CubeDoor"):
            caller.msg("That is not a cube door.")
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
        new_code = generate_unique_code()
        
        # Assign renter and code
        old_renter = exit_obj.current_renter
        exit_obj.current_renter = char
        exit_obj.current_door_code = new_code
        
        # Initialize rent (start from now with a small grace period)
        if not exit_obj.rent_paid_until_ts or exit_obj.rent_paid_until_ts < time.time():
            # Give 1 hour grace period for new renters
            exit_obj.rent_paid_until_ts = time.time() + 3600
        
        caller.msg(f"Assigned {char.key} as renter of cube to the {direction}.")
        caller.msg(f"New access code: {new_code}")
        caller.msg(f"Rent grace period: 1 hour. Renter should pay rent to extend.")
        
        # Message the renter
        if char.has_account:
            char.msg(f"You have been assigned a cube. Your access code is: {new_code}")
            char.msg(f"Use 'enter {new_code} <direction>' to enter your cube.")
            char.msg(f"Use 'pay rent <direction>' to pay rent (100 dollars per day).")


class CmdCubeInfo(Command):
    """
    View information about a cube door.
    
    Usage:
        cubeinfo <direction>
        
    Shows the cube's current renter, rent status, and other details.
    Builder+ only.
    """
    
    key = "cubeinfo"
    locks = "cmd:perm(Builder)"
    help_category = "Building"
    
    def func(self):
        caller = self.caller
        
        if not self.args:
            caller.msg("Usage: cubeinfo <direction>")
            return
        
        direction = self.args.strip().lower()
        
        # Find the exit
        exit_obj = None
        for ex in caller.location.exits:
            ex_aliases = [a.lower() for a in ex.aliases.all()] if hasattr(ex.aliases, "all") else []
            if ex.key.lower() == direction or direction in ex_aliases:
                exit_obj = ex
                break
        
        if not exit_obj:
            caller.msg(f"There is no exit in that direction.")
            return
        
        # Check if it's a CubeDoor
        if not exit_obj.is_typeclass("typeclasses.cube_housing.CubeDoor"):
            caller.msg("That is not a cube door.")
            return
        
        # Display info
        lines = [f"Cube Door: {exit_obj.key} (#{exit_obj.id})"]
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
        
        if exit_obj.rent_paid_until_ts:
            if exit_obj.is_rent_current():
                lines.append(f"Rent Status: PAID ({exit_obj.get_rent_remaining()} remaining)")
            else:
                lines.append("Rent Status: EXPIRED")
        else:
            lines.append("Rent Status: Never paid")
        
        lines.append(f"Destination: {exit_obj.destination.key if exit_obj.destination else 'None'}")
        
        caller.msg("\n".join(lines))


class CmdClearCubeRenter(Command):
    """
    Remove a renter from a cube.
    
    Usage:
        clearcuberenter <direction>
        
    This removes the renter assignment and deactivates the access code.
    The cube returns to an unassigned state.
    """
    
    key = "clearcuberenter"
    aliases = ["removecuberenter"]
    locks = "cmd:perm(Builder)"
    help_category = "Building"
    
    def func(self):
        caller = self.caller
        
        if not self.args:
            caller.msg("Usage: clearcuberenter <direction>")
            return
        
        direction = self.args.strip().lower()
        
        # Find the exit
        exit_obj = None
        for ex in caller.location.exits:
            ex_aliases = [a.lower() for a in ex.aliases.all()] if hasattr(ex.aliases, "all") else []
            if ex.key.lower() == direction or direction in ex_aliases:
                exit_obj = ex
                break
        
        if not exit_obj:
            caller.msg(f"There is no exit in that direction.")
            return
        
        # Check if it's a CubeDoor
        if not exit_obj.is_typeclass("typeclasses.cube_housing.CubeDoor"):
            caller.msg("That is not a cube door.")
            return
        
        old_renter = exit_obj.current_renter
        
        # Clear renter and code
        exit_obj.current_renter = None
        exit_obj.current_door_code = None
        exit_obj.rent_paid_until_ts = 0
        
        if old_renter:
            caller.msg(f"Removed {old_renter.key} as renter. Cube is now unassigned.")
        else:
            caller.msg("Cube was already unassigned.")


class CubeHousingCmdSet(CmdSet):
    """Command set for cube housing commands."""
    
    key = "cube_housing"
    
    def at_cmdset_creation(self):
        self.add(CmdEnter())
        self.add(CmdCheck())
        self.add(CmdCloseDoor())
        self.add(CmdPayRent())
        self.add(CmdCreateCube())
        self.add(CmdSetCubeRenter())
        self.add(CmdCubeInfo())
        self.add(CmdClearCubeRenter())
