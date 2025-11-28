"""
All mapping commands removed.
"""
from evennia import Command

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
        # Fix: Use attribute filter for db.z
        rooms = [r for r in ObjectDB.objects.filter(db_typeclass_path="typeclasses.rooms.Room") if getattr(r.db, "z", None) == z]
        coords = {(r.db.x, r.db.y): r for r in rooms if r.db.x is not None and r.db.y is not None}
        grid = []
        for dy in range(2, -3, -1):
            row = []
            for dx in range(-2, 3):
                cx, cy = x + dx, y + dy
                room_obj = coords.get((cx, cy))
                # Fix: Show '@' for current room, not map_icon
                if (cx, cy) == (x, y):
                    row.append("@ ")
                elif room_obj:
                    icon = getattr(room_obj.db, 'map_icon', None)
                    if icon and len(icon) >= 2:
                        row.append(icon[:2])
                    else:
                        row.append("[]")
                else:
                    row.append("  ")
            # Join row and send with Evennia color parsing
            grid.append("".join(row))
        # Send the whole grid with Evennia color parsing
        map_output = "\n".join(grid) + f"\nCurrent coordinates: x={x}, y={y}, z={z}"
        self.caller.msg(map_output, raw=True)

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
            "- Each room is shown as a 2-character icon.\n"
            "- Set a room's icon with: @mapicon <icon> [options]\n"
            "- Set area background icon with: @areaicon <icon> [options]\n"
            "- Icons must be exactly two characters.\n"
            "- Icon options: [bold_on]/[bold_off], [underline_on]/[underline_off], [strikethrough_on]/[strikethrough_off], [color], [bg_color]\n"
            "  Valid colors: black, white, red, blue, yellow, green, purple, cyan\n"
            "- Example: @mapicon [black][bg_cyan]OD\n"
            "- For icon customization help, use: mapicon help\n"
            "- Coordinates are set with: @maproom x y z\n"
            "- Map color for brackets: @mapcolor <colorcode>\n"
            "- Only builder+ can use these commands.\n"
        )
        self.caller.msg(help_text)

