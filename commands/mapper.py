"""
All mapping commands removed.
"""
from evennia import Command
import re

class CmdMapColor(Command):
    """
    Set the color of the map brackets for this room.
    Usage: @mapcolor <colorcode>
    Example: @mapcolor |r
    """
    key = "@mapcolor"
    locks = "cmd:all()"
    help_category = "Mapping"

    def func(self):
        caller = self.caller
        color = self.args.strip()
        if not color:
            caller.msg("Usage: @mapcolor <colorcode> (e.g. |r, |g, |b, |y, |c, |m, |w)")
            return
        room = caller.location
        room.db.map_color = color
        caller.msg(f"Map color for this room set to '{color}'.")
from evennia import Command

class CmdMapRoom(Command):
    """
    Set coordinates for the current room.
    Usage: @maproom x y z
    """
    key = "@maproom"
    locks = "cmd:all()"
    help_category = "Mapping"

    def func(self):
        args = self.args.strip().split()
        if len(args) != 3:
            self.caller.msg("Usage: @maproom x y z")
            return
        try:
            x, y, z = map(int, args)
        except ValueError:
            self.caller.msg("Coordinates must be integers.")
            return
        room = self.caller.location
        room.db.x = x
        room.db.y = y
        room.db.z = z
        self.caller.msg(f"Room '{room.key}' mapped to ({x},{y},{z}).")

class CmdMapOn(Command):
    """
    Turn on the mapper for this session.
    Usage: mapon
    """
    key = "mapon"
    locks = "cmd:all()"
    help_category = "Mapping"

    def func(self):
        room = self.caller.location
        if not (hasattr(room.db, "x") and hasattr(room.db, "y") and hasattr(room.db, "z")):
            self.caller.msg("You must be in a coordinate-assigned room to enable the mapper.")
            return
        # Set per-account variable for persistent toggle
        if self.caller.account and hasattr(self.caller.account, 'db'):
            self.caller.account.db.mapper_enabled = True
        # Also set session ndb for immediate effect
        self.caller.ndb.mapper_enabled = True
        self.caller.msg("Mapper enabled. Move to see the map.")

class CmdMapOff(Command):
    """
    Turn off the mapper for this session.
    Usage: mapoff
    """
    key = "mapoff"
    locks = "cmd:all()"
    help_category = "Mapping"

    def func(self):
        # Set per-account variable for persistent toggle
        if self.caller.account and hasattr(self.caller.account, 'db'):
            self.caller.account.db.mapper_enabled = False
        # Also set session ndb for immediate effect
        self.caller.ndb.mapper_enabled = False
        self.caller.msg("Mapper disabled. Room name and description will always be shown.")

class CmdMapIcon(Command):
    """
    Set the map icon for the current room.
    Usage: @mapicon <icon> [options]
    Example: @mapicon [black][bg_cyan]OD
    """
    key = "@mapicon"
    locks = "cmd:all()"
    help_category = "Mapping"

    def func(self):
        args = self.args.strip()
        if not args:
            self.caller.msg("Usage: @mapicon <icon> [options]")
            return
        room = self.caller.location
        room.db.map_icon = args
        self.caller.msg(f"Map icon for this room set to '{args}'.")

class CmdAreaIcon(Command):
    """
    Set the area background icon for the current area.
    Usage: @areaicon <icon> [options]
    """
    key = "@areaicon"
    locks = "cmd:all()"
    help_category = "Mapping"

    def func(self):
        args = self.args.strip()
        if not args:
            self.caller.msg("Usage: @areaicon <icon> [options]")
            return
        room = self.caller.location
        room.db.area_icon = args
        self.caller.msg(f"Area icon for this area set to '{args}'.")

class CmdZoneIcon(Command):
    """
    Set the default icon for nonexistent rooms in this zone.
    Usage: zoneicon <icon>
    Example: zoneicon |#00d700!!|n
    This icon will be displayed for all empty coordinate spaces in the zone's map.
    """
    key = "zoneicon"
    locks = "cmd:perm(Builders)"
    help_category = "Mapping"

    def func(self):
        args = self.args.strip()
        if not args:
            self.caller.msg("Usage: zoneicon <icon>")
            self.caller.msg("Example: zoneicon |#00d700!!|n")
            return
        
        # Validate icon format - extract visible (non-color-code) characters
        import re
        
        # Extract all color codes from the input (only valid Evennia color codes)
        # Valid: |#RRGGBB, |[#RRGGBB, |a-z, |A-Z
        # NOT valid: |_, |0, etc.
        color_codes_pattern = r'\|(?:\[)?#[0-9a-fA-F]{6}|\|[a-zA-Z]'
        
        # First, handle escaped pipes || - replace with placeholder for counting
        # || represents a single visible | character
        temp_args = args.replace('||', '\x00')  # Use null byte as placeholder
        
        # Extract visible characters by removing all color codes from temp string
        visible_chars = re.sub(color_codes_pattern, '', temp_args)
        # Convert placeholder back to single | for display
        visible_chars_display = visible_chars.replace('\x00', '|')
        
        # Ensure exactly 2 visible characters
        if len(visible_chars) != 2:
            self.caller.msg(f"Icon must have exactly 2 visible characters (non-color-code characters). You have {len(visible_chars)}: '{visible_chars_display}'")
            self.caller.msg("Example: zoneicon |#00d700!! or zoneicon |#00d700|r!!")
            self.caller.msg("Use || to display a literal | character.")
            return
        
        room = self.caller.location
        zone = getattr(room, "zone", None)
        
        if not zone:
            self.caller.msg("You must be in a zone to set the zone icon.")
            return
        
        # Build the zone icon string
        # If visible chars end with |, we need to escape it as || before adding |n
        # Otherwise ||n is interpreted as "escaped pipe + n" not "pipe + color reset"
        # But if user already escaped it (ends with ||), don't double-escape
        zone_icon = args
        if not zone_icon.endswith('|n'):
            # Check if it ends with a visible | (not part of a color code)
            # visible_chars has \x00 for escaped pipes
            if visible_chars.endswith('\x00'):
                # Already ends with escaped pipe ||, just add |n
                zone_icon = zone_icon + '|n'
            elif visible_chars.endswith('|'):
                # Ends with unescaped visible |, need to escape it
                zone_icon = zone_icon + '|' + '|n'
            else:
                zone_icon = zone_icon + '|n'
        
        # Find all rooms in this zone and set zone_icon on each
        from evennia.objects.models import ObjectDB
        all_rooms = ObjectDB.objects.filter(
            db_typeclass_path__endswith='typeclasses.rooms.Room'
        )
        
        room_count = 0
        for zroom in all_rooms:
            if getattr(zroom, "zone", None) == zone:
                zroom.db.zone_icon = zone_icon
                room_count += 1
        
        self.caller.msg(f"Zone icon set to '{zone_icon}' for {room_count} room(s) in zone '{zone}'.")

class CmdMapIconHelp(Command):
    """
    Show help for map icon settings.
    Usage: mapicon help
    """
    key = "mapicon help"
    locks = "cmd:all()"
    help_category = "Mapping"

    def func(self):
        help_text = (
            "Map icons use Evennia color codes. Example (remove spaces): `| b`, `| r`, `| y`, `| g`, `| c`, `| m`, `| w`, `| x`. "
            "|NYou can combine codes, e.g. `| b | [y` for blue text on yellow background. "
            "|NIcons must be exactly two characters long. Example: 'mapicon | b OD' sets icon to blue 'OD'. "
            "|NSee Evennia color documentation for full code list: https://www.evennia.com/docs/latest/Color.html"
        )
        self.caller.msg(help_text, parse=False)

class CmdMap(Command):
    """
    Show a 5x5 map centered on your current room, using 2-character icons per room.
    Usage: map
    """
    key = "map"
    locks = "cmd:all()"
    help_category = "Mapping"

    def func(self):
        room = self.caller.location
        x = getattr(room.db, "x", None)
        y = getattr(room.db, "y", None)
        z = getattr(room.db, "z", None)
        zone = getattr(room, "zone", None)
        
        if x is None or y is None or z is None:
            self.caller.msg("This room does not have valid coordinates. The map cannot be displayed.")
            return
        # Get room description (appearance)
        try:
            appearance = room.return_appearance(self.caller)
        except Exception as e:
            appearance = f"[Error getting room description: {e}]"

        # Always show the map when called, regardless of toggle
        from evennia.objects.models import ObjectDB
        # Filter rooms by both zone AND z-level for zone-aware mapping
        rooms = [r for r in ObjectDB.objects.filter(db_typeclass_path="typeclasses.rooms.Room") 
                 if getattr(r.db, "z", None) == z and getattr(r, "zone", None) == zone]
        coords = {(r.db.x, r.db.y): r for r in rooms if r.db.x is not None and r.db.y is not None}
        grid = []
        for dy in range(2, -3, -1):
            row = []
            for dx in range(-2, 3):
                cx, cy = x + dx, y + dy
                room_obj = coords.get((cx, cy))
                # Current room always '@'
                if (cx, cy) == (x, y):
                    row.append("@ ")
                elif room_obj:
                    icon = getattr(room_obj.db, 'map_icon', None)
                    if icon:
                        # Use icon as-is, ensure it ends with |n
                        if not icon.endswith('|n'):
                            icon = icon + '|n'
                        row.append(icon)
                    else:
                        row.append("[]")
                else:
                    # Use zone icon for empty spaces, default to ". "
                    zone_icon = getattr(room.db, 'zone_icon', None)
                    if zone_icon:
                        # Use zone_icon directly - already validated to have 2 visible chars
                        row.append(zone_icon)
                    else:
                        row.append(". ")
            grid.append("".join(row))

        import textwrap
        # Map grid: 5 rooms x 2 chars = 10 visual chars per line
        # Total left column: 10 (grid) + 5 (padding) = 15 chars
        map_grid_width = 10  # Always exactly 10 visual characters
        padding_width = 5    # 5 spaces padding
        left_column_width = map_grid_width + padding_width  # 15 total
        
        # Description column width (80 - 15 = 65)
        column_width = 65
        
        if appearance:
            lines = appearance.split('\n')
            exit_line = None
            other_lines = []
            seen = set()
            for line in lines:
                if line in seen:
                    continue
                seen.add(line)
                if line.strip().lower().startswith("there are exits"):
                    exit_line = line
                else:
                    other_lines.append(line)
            wrapped_lines = []
            for i, line in enumerate(other_lines):
                # Don't wrap the first line (room name with tags) - let it overflow
                if i == 0 and line.startswith('|c'):
                    wrapped_lines.append(line)
                else:
                    # Wrap to column width
                    wrapped = textwrap.fill(line.strip(), width=column_width)
                    wrapped_lines.extend(wrapped.split('\n'))
            desc_lines = wrapped_lines
            if exit_line:
                wrapped = textwrap.fill(exit_line.strip(), width=column_width)
                desc_lines.extend(wrapped.split('\n'))
        else:
            desc_lines = []

        map_grid_height = 5
        
        # Build map grid - always 5 rows, always 10 VISUAL characters per line
        base_map_lines = []
        for map_row in grid:
            base_map_lines.append(map_row)
        
        # Fill empty rows with spaces if grid has fewer than 5 rows
        while len(base_map_lines) < map_grid_height:
            base_map_lines.append("          ")  # 10 spaces for empty row
        
        # Coordinate string (displayed on its own line, not paired with description)
        coord_str = f"x={x}, y={y}, z={z}"
        
        # Helper to calculate visual width (excluding ALL Evennia color codes)
        def visual_len(s):
            # Remove all Evennia color codes:
            # |x, |X (single letter colors)
            # |[x, |[X (background colors)  
            # |#RRGGBB (hex colors)
            # |[#RRGGBB (hex background)
            # |n, |h, |u, |s (reset/formatting)
            # || (escaped pipe = 1 visible character)
            import re
            # First replace escaped pipes || with placeholder
            temp = s.replace('||', '\x00')
            # Remove color codes (only valid letter-based codes)
            stripped = re.sub(r'\|(?:\[)?(?:#[0-9a-fA-F]{6}|[a-zA-Z])', '', temp)
            # Convert placeholder back to single character for counting
            stripped = stripped.replace('\x00', '|')
            return len(stripped)
        
        def pad_to_visual_width(s, target_width):
            # Pad string so visual width equals target_width
            vis_len = visual_len(s)
            padding = max(0, target_width - vis_len)
            return s + " " * padding
        
        # Build output - map on left, descriptions on right and bottom
        output = []
        
        # Rows 0-4: map grid (padded to 25 visual chars) + description
        for i in range(map_grid_height):
            left = pad_to_visual_width(base_map_lines[i], left_column_width)
            right = desc_lines[i] if i < len(desc_lines) else ""
            output.append(f"{left}{right}")
        
        # Row 5: coordinates (padded to 25 chars) + description continues
        coord_left = pad_to_visual_width(coord_str, left_column_width)
        coord_right = desc_lines[map_grid_height] if map_grid_height < len(desc_lines) else ""
        output.append(f"{coord_left}{coord_right}")
        
        # Remaining description lines (row 6+) - full width, no indent
        for i in range(map_grid_height + 1, len(desc_lines)):
            output.append(desc_lines[i])
        
        self.caller.msg("\n".join(output), parse=True)

class CmdHelpMapping(Command):
    """
    Show help for mapping commands and icon customization (builder+).
    Usage: help mapping
    """
    key = "help mapping"
    locks = "cmd:all()"
    help_category = "Mapping"

    def func(self):
        help_text = (
            "Mapping System Help (Builder+)\n"
            "--------------------------------\n"
            "- Use @mapon/@mapoff to toggle automatic map display on movement.\n"
            "- Use 'map' to view the map centered on your current room.\n"
            "- Set a room's icon with: @mapicon <icon> [options]\n"
            "- Set area background icon with: @areaicon <icon> [options]\n"
            "- Icons must be exactly two characters.\n"
            "- Icon options: [bold_on]/[bold_off], [underline_on]/[underline_off], [strikethrough_on]/[strikethrough_off], [color], [bg_color]\n"
            "  Valid colors: black, white, red, blue, yellow, green, purple, cyan\n"
            "  Effects: bold_on (|h), underline_on (|u), strikethrough_on (|s), bold_off/underline_off/strikethrough_off (|n)\n"
            "  You can also use Evennia codes directly: |c (cyan), |[c (cyan background), |h (bold), |u (underline), |s (strikethrough), |n (reset)\n"
            "- Example: @mapicon |x|[c|hOD|n\n"
            "- For icon customization help, use: mapicon help\n"
            "- Coordinates are set with: @maproom x y z\n"
            "- Map color for brackets: @mapcolor <colorcode>\n"
            "- Only builder+ can use these commands.\n"
        )
        self.caller.msg(help_text)

# Register mapping commands for inclusion in command sets (must be after all command classes are defined)
mapping_cmds = [
    CmdMapColor,
    CmdMapRoom,
    CmdMapOn,
    CmdMapOff,
    CmdMapIcon,
    CmdAreaIcon,
    CmdZoneIcon,
    CmdMapIconHelp,
    CmdMap,
    CmdHelpMapping,
]
