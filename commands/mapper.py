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
    locks = "cmd:perm(Builder)"
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
    locks = "cmd:perm(Builder)"
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
    Usage: @mapon
    """
    key = "@mapon"
    locks = "cmd:perm(Builder)"
    help_category = "Mapping"

    def func(self):
        room = self.caller.location
        if not (hasattr(room.db, "x") and hasattr(room.db, "y") and hasattr(room.db, "z")):
            self.caller.msg("You must be in a coordinate-assigned room to enable the mapper.")
            return
        self.caller.ndb.mapper_enabled = True
        self.caller.msg("Mapper enabled. Move to see the map.")

class CmdMapOff(Command):
    """
    Turn off the mapper for this session.
    Usage: @mapoff
    """
    key = "@mapoff"
    locks = "cmd:perm(Builder)"
    help_category = "Mapping"

    def func(self):
        self.caller.ndb.mapper_enabled = False
        self.caller.msg("Mapper disabled.")

class CmdMapIcon(Command):
    """
    Set the map icon for the current room.
    Usage: @mapicon <icon> [options]
    Example: @mapicon [black][bg_cyan]OD
    """
    key = "@mapicon"
    locks = "cmd:perm(Builder)"
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
    locks = "cmd:perm(Builder)"
    help_category = "Mapping"

    def func(self):
        args = self.args.strip()
        if not args:
            self.caller.msg("Usage: @areaicon <icon> [options]")
            return
        room = self.caller.location
        room.db.area_icon = args
        self.caller.msg(f"Area icon for this area set to '{args}'.")


    # Register mapping commands for inclusion in command sets
    # (must be after all command classes are defined)

    # ...existing code...

    mapping_cmds = [
        CmdMapColor,
        CmdMapRoom,
        CmdMapOn,
        CmdMapOff,
        CmdMapIcon,
        CmdAreaIcon,
        CmdMapIconHelp,
        CmdMap,
        CmdHelpMapping,
    ]
class CmdMapIconHelp(Command):
    """
    Show help for map icon settings.
    Usage: mapicon help
    """
    key = "mapicon help"
    locks = "cmd:perm(Builder)"
    help_category = "Mapping"

    def func(self):
        help_text = (
            "[bold_on]/[bold_off] - Bolds a color, making it brighter. "
            "[underline_on]/[underline_off] - Underlines the characters. "
            "[strikethrough_on]/[strikethrough_off] - Strike through. "
            "[color] - Changes the color. Valid: black,white,red,blue,yellow,green,purple,cyan. "
            "[bg_color] - Background color. Valid: black,white,red,blue,yellow,green,purple,cyan. "
            "Icons must be two characters long. Example: mapicon [black][bg_cyan]OD"
        )
        self.caller.msg(help_text)

class CmdMap(Command):
    """
    Show a 5x5 map centered on your current room, using 2-character icons per room.
    Usage: map
    """
    key = "map"
    locks = "cmd:perm(Builder)"
    help_category = "Mapping"

    def func(self):
        room = self.caller.location
        x = getattr(room.db, "x", None)
        y = getattr(room.db, "y", None)
        z = getattr(room.db, "z", None)
        if x is None or y is None or z is None:
            self.caller.msg("This room does not have valid coordinates. The map cannot be displayed.")
            return
        from evennia.objects.models import ObjectDB
        rooms = [r for r in ObjectDB.objects.filter(db_typeclass_path="typeclasses.rooms.Room") if getattr(r.db, "z", None) == z]
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
                        import re
                        # Remove [tag]s, keep |color codes
                        icon_clean = re.sub(r"\[(\w+)]", "", icon)
                        # Extract all Evennia codes at the start (|c, |[c, |h, etc.)
                        codes = ""
                        i = 0
                        while i < len(icon_clean):
                            if icon_clean[i] == '|':
                                codes += icon_clean[i]
                                i += 1
                                if i < len(icon_clean) and icon_clean[i] == '[':
                                    codes += icon_clean[i]
                                    i += 1
                                if i < len(icon_clean):
                                    codes += icon_clean[i]
                                    i += 1
                            else:
                                break
                        # Now extract two visible chars, skipping any | codes
                        visible = ""
                        j = i
                        while len(visible) < 2 and j < len(icon_clean):
                            if icon_clean[j] == '|':
                                j += 1
                                if j < len(icon_clean) and icon_clean[j] == '[':
                                    j += 1
                                if j < len(icon_clean):
                                    j += 1
                            else:
                                visible += icon_clean[j]
                                j += 1
                        visible = visible.ljust(2)
                        row.append(f"{codes}{visible}|n")
                    else:
                        row.append("[]")
                else:
                    row.append("  ")
            grid.append("".join(row))

        # Get room description (appearance)
        appearance = ""
        # Always get room description, but only display it to the right of the map when @mapon is enabled
        try:
            appearance = room.return_appearance(self.caller)
        except Exception as e:
            appearance = f"[Error getting room description: {e}]"

        # If @mapon is enabled, suppress the default room description and name elsewhere
        suppress_room_text = getattr(self.caller.ndb, "mapper_enabled", False)
        if suppress_room_text:
            # Only show the room text to the right of the map, not in the default output
            # (This is handled by the map output below)
            pass

        # Always show the map and room description together, no @mapon logic
        # Indent room description so it never runs over the map (five spaces to the right)
        # Indent every line, including blank lines, five spaces to the right of the map
        # Indent every linebreak and line, so all lines are aligned
        # Move 'There are exits...' to the bottom of the right column
        import textwrap
        # Calculate map width dynamically for perfect alignment
        map_cells = 5
        map_cell_width = 2
        map_width = map_cells * map_cell_width
        # Dynamic indentation for perfect straightness, exactly two spaces to the right of the map
        indent = " " * (map_width + 2)
        column_width = 80  # Increased wrap width for longer lines
        if appearance:
            lines = appearance.split('\n')
            exit_line = None
            other_lines = []
            seen = set()
            for line in lines:
                # Remove duplicate lines
                if line in seen:
                    continue
                seen.add(line)
                if line.strip().lower().startswith("there are exits"):
                    exit_line = line
                else:
                    other_lines.append(line)
            # Wrap each line and indent all wrapped lines
            wrapped_lines = []
            for line in other_lines:
                wrapped = textwrap.fill(line, width=column_width, initial_indent=indent, subsequent_indent=indent)
                wrapped_lines.extend(wrapped.split('\n'))
            desc_lines = wrapped_lines
            if exit_line:
                wrapped = textwrap.fill(exit_line, width=column_width, initial_indent=indent, subsequent_indent=indent)
                desc_lines.extend(wrapped.split('\n'))
        else:
            desc_lines = [indent]


        # Strict columnar layout: map (top left), text (top right)
        map_width = 2 * 5 + 2  # 5 cells * 2 chars + 2 spaces for margin

        # Pad map and text so both have same number of lines
        max_lines = max(len(grid), len(desc_lines))
        map_lines = grid + ["  " * 5] * (max_lines - len(grid))
        desc_lines += [""] * (max_lines - len(desc_lines))

        # Render as two columns, never overlapping
        combined = []
        for m, d in zip(map_lines, desc_lines):
            combined.append(f"{m.ljust(map_width)}{d}")

        # Move coordinates directly under the map, and if there are more desc lines, show the next one in the right column
        # Always pad the right column to start after the map
        right_pad = indent
        coord_line = f"{' ' * (map_width // 2 - 6)}x={x}, y={y}, z={z}"
        if len(desc_lines) > len(grid):
            coord_line = f"{' ' * (map_width // 2 - 6)}x={x}, y={y}, z={z}{right_pad}{desc_lines[len(grid)].lstrip()}"
            desc_lines.pop(len(grid))
        combined.insert(len(grid), coord_line)

        # Suppress all other room output when @mapon is active
        self.caller.msg("\n".join(combined), parse=True)

class CmdHelpMapping(Command):
    """
    Show help for mapping commands and icon customization (builder+).
    Usage: help mapping
    """
    key = "help mapping"
    locks = "cmd:perm(Builder)"
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

