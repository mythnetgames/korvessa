"""
RelayNode and RelayViewer typeclasses for remote room viewing.
Includes builder/admin commands to create, link, and manage relays and viewers.
"""
from evennia import DefaultObject, create_object, search_object, CmdSet
from evennia.utils.utils import inherits_from

class RelayNode(DefaultObject):
    """Invisible relay object that stores a reference to a remote room."""
    def at_object_creation(self):
        self.db.remote_room = None
        self.locks.add("get:false();call:false()")
        self.db.desc = ""
        self.tags.add("invisible_relay", category="system")

    def set_remote_room(self, room):
        """Set the remote room this relay transmits from."""
        self.db.remote_room = room

    def return_appearance(self, looker, **kwargs):
        return ""  # Invisible

class RelayViewer(DefaultObject):
    """Viewer object that displays the remote room's description via a relay."""
    def at_object_creation(self):
        self.db.relay = None
        self.locks.add("view:true()")

    def set_relay(self, relay):
        """Link this viewer to a relay node."""
        self.db.relay = relay

    def return_appearance(self, looker, **kwargs):
        relay = self.db.relay
        if not relay or not relay.db.remote_room:
            return "|rNo active relay or remote room.|n"
        remote_room = relay.db.remote_room
        result = f"|w[Remote View: {remote_room.key}]|n\n"
        result += remote_room.return_appearance(looker)
        return result

# Builder/admin commands for relay system
from evennia import Command

class CmdCreateRelay(Command):
    """
    create_relay [room dbref or name]
    
    Create an invisible relay node in your current room, targeting the given room.
    """
    key = "create_relay"
    locks = "cmd:perm(Builder)"
    help_category = "Building"

    def func(self):
        caller = self.caller
        if not self.args:
            caller.msg("Usage: create_relay [room dbref or name]")
            return
        arg = self.args.strip()
        # Accept both #31 and 31
        if arg.isdigit():
            arg = f"#{arg}"
        target_room = search_object(arg)
        if not target_room:
            caller.msg("Target room not found.")
            return
        room_obj = target_room[0]
        # Accept any object whose typeclass path ends with 'rooms.Room'
        if not room_obj.typeclass_path.endswith("rooms.Room"):
            caller.msg("Target is not a valid room object.")
            return
        relay = create_object(key="relay", location=caller.location, typeclass="typeclasses.relay.RelayNode")
        relay.set_remote_room(room_obj)
        caller.msg(f"Relay created in this room, transmitting from {room_obj.key}.")

class CmdCreateViewer(Command):
    """
    create_viewer [relay dbref or name]
    
    Create a viewer object in your current room, linked to the given relay.
    """
    key = "create_viewer"
    locks = "cmd:perm(Builder)"
    help_category = "Building"

    def func(self):
        caller = self.caller
        if not self.args:
            caller.msg("Usage: create_viewer [relay dbref or name]")
            return
        relay = search_object(self.args.strip())
        if not relay or not inherits_from(relay[0], "typeclasses.relay.RelayNode"):
            caller.msg("Relay not found or not a valid relay node.")
            return
        viewer = create_object(key="viewer", location=caller.location, typeclass="typeclasses.relay.RelayViewer")
        viewer.set_relay(relay[0])
        caller.msg(f"Viewer created in this room, linked to relay {relay[0].key}.")

class CmdLinkRelay(Command):
    """
    link_relay [relay dbref or name] = [room dbref or name]
    
    Set the remote room for an existing relay node.
    """
    key = "link_relay"
    locks = "cmd:perm(Builder)"
    help_category = "Building"

    def func(self):
        caller = self.caller
        if not self.args or "=" not in self.args:
            caller.msg("Usage: link_relay [relay] = [room]")
            return
        relay_str, room_str = [part.strip() for part in self.args.split("=", 1)]
        relay = search_object(relay_str)
        room = search_object(room_str)
        if not relay or not inherits_from(relay[0], "typeclasses.relay.RelayNode"):
            caller.msg("Relay not found or not a valid relay node.")
            return
        if not room or not inherits_from(room[0], "typeclasses.rooms.Room"):
            caller.msg("Room not found or not a valid room.")
            return
        relay[0].set_remote_room(room[0])
        caller.msg(f"Relay {relay[0].key} now transmits from room {room[0].key}.")

class CmdLinkViewer(Command):
    """
    link_viewer [viewer dbref or name] = [relay dbref or name]
    
    Link an existing viewer to a relay node.
    """
    key = "link_viewer"
    locks = "cmd:perm(Builder)"
    help_category = "Building"

    def func(self):
        caller = self.caller
        if not self.args or "=" not in self.args:
            caller.msg("Usage: link_viewer [viewer] = [relay]")
            return
        viewer_str, relay_str = [part.strip() for part in self.args.split("=", 1)]
        viewer = search_object(viewer_str)
        relay = search_object(relay_str)
        if not viewer or not inherits_from(viewer[0], "typeclasses.relay.RelayViewer"):
            caller.msg("Viewer not found or not a valid viewer object.")
            return
        if not relay or not inherits_from(relay[0], "typeclasses.relay.RelayNode"):
            caller.msg("Relay not found or not a valid relay node.")
            return
        viewer[0].set_relay(relay[0])
        caller.msg(f"Viewer {viewer[0].key} now linked to relay {relay[0].key}.")

class RelayCmdSet(CmdSet):
    """CmdSet for relay system builder commands."""
    key = "RelayCmdSet"
    priority = 1
    def at_cmdset_creation(self):
        self.add(CmdCreateRelay())
        self.add(CmdCreateViewer())
        self.add(CmdLinkRelay())
        self.add(CmdLinkViewer())

# To use: add RelayCmdSet to your builder/admin cmdsets, or import commands as needed.
