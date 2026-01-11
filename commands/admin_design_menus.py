"""
Admin Design Menus - Builder+ EvMenu tools for creating and saving NPCs, furniture, weapons, clothes, and armor.

Features:
- Unified EvMenu system for all object types
- Save/load similar to recipe system
- NPCs: name, save, clone, toggle wandering
- Furniture: name, seating count, sit/lie/recline toggles
- Weapons: name, ammo toggle, ammo type
- Clothes/Armor: tailoring menu, ask if armor
"""

from evennia.utils.evmenu import EvMenu
from evennia import create_object
from evennia.utils.search import search_object
from evennia.scripts.models import ScriptDB
from evennia import Command

# Storage script key for admin designs
ADMIN_DESIGN_STORAGE_KEY = "admin_design_storage"

# Helper to get or create storage script
def get_admin_design_storage():
    storage = ScriptDB.objects.filter(db_key=ADMIN_DESIGN_STORAGE_KEY).first()
    if storage:
        return storage
    from evennia.scripts.scripts import DefaultScript
    storage = create_object(DefaultScript, key=ADMIN_DESIGN_STORAGE_KEY, persistent=True, desc="Admin design storage")
    storage.db.npcs = []
    storage.db.furniture = []
    storage.db.weapons = []
    storage.db.clothes = []
    return storage

# =============================
# NPC DESIGN MENU
# =============================
def node_npc_main(caller, raw_string, **kwargs):
    data = caller.ndb._npc_design or {}
    text = f"""
|c=== NPC Designer ===|n

|wName:|n {data.get('name', '(unnamed)')}
|wWandering:|n {'|g[ON]|n' if data.get('wandering') else '|r[OFF]|n'}
|wCloneable:|n {'|g[YES]|n' if data.get('cloneable') else '|r[NO]|n'}

[R] Review
[S] Save
[Q] Quit
"""
    options = [
        {"desc": "Set Name", "goto": "node_npc_set_name"},
        {"desc": "Toggle Wandering", "goto": "node_npc_toggle_wandering"},
        {"desc": "Toggle Cloneable", "goto": "node_npc_toggle_cloneable"},
        {"desc": "Review", "goto": "node_npc_review"},
        {"desc": "Save", "goto": "node_npc_save"},
        {"desc": "Quit", "goto": "node_quit"},
    ]
    return text, options

def node_npc_set_name(caller, raw_string, **kwargs):
    caller.msg("Enter NPC name:")
    return "Enter NPC name:", [
        {"key": "_input", "goto": "node_npc_main", "exec": lambda c, s: c.ndb._npc_design.update({'name': s})}
    ]

def node_npc_toggle_wandering(caller, raw_string, **kwargs):
    data = caller.ndb._npc_design
    data['wandering'] = not data.get('wandering', False)
    return node_npc_main(caller, raw_string, **kwargs)

def node_npc_toggle_cloneable(caller, raw_string, **kwargs):
    data = caller.ndb._npc_design
    data['cloneable'] = not data.get('cloneable', False)
    return node_npc_main(caller, raw_string, **kwargs)

def node_npc_review(caller, raw_string, **kwargs):
    data = caller.ndb._npc_design
    text = f"Review NPC:\nName: {data.get('name')}\nWandering: {data.get('wandering')}\nCloneable: {data.get('cloneable')}"
    return text, [{"desc": "Back", "goto": "node_npc_main"}]

def node_npc_save(caller, raw_string, **kwargs):
    storage = get_admin_design_storage()
    npc_data = dict(caller.ndb._npc_design)
    storage.db.npcs.append(npc_data)
    caller.msg(f"|gNPC '{npc_data.get('name')}' saved!|n")
    return node_npc_main(caller, raw_string, **kwargs)

# =============================
# FURNITURE DESIGN MENU
# =============================
def node_furniture_main(caller, raw_string, **kwargs):
    data = caller.ndb._furniture_design or {}
    text = f"""
|c=== Furniture Designer ===|n

|wName:|n {data.get('name', '(unnamed)')}
|wSeats:|n {data.get('seats', 1)}
|wSit:|n {'|g[YES]|n' if data.get('can_sit') else '|r[NO]|n'}
|wLie:|n {'|g[YES]|n' if data.get('can_lie') else '|r[NO]|n'}
|wRecline:|n {'|g[YES]|n' if data.get('can_recline') else '|r[NO]|n'}

[R] Review
[S] Save
[Q] Quit
"""
    options = [
        {"desc": "Set Name", "goto": "node_furniture_set_name"},
        {"desc": "Set Seats", "goto": "node_furniture_set_seats"},
        {"desc": "Toggle Sit", "goto": "node_furniture_toggle_sit"},
        {"desc": "Toggle Lie", "goto": "node_furniture_toggle_lie"},
        {"desc": "Toggle Recline", "goto": "node_furniture_toggle_recline"},
        {"desc": "Review", "goto": "node_furniture_review"},
        {"desc": "Save", "goto": "node_furniture_save"},
        {"desc": "Quit", "goto": "node_quit"},
    ]
    return text, options

def node_furniture_set_name(caller, raw_string, **kwargs):
    caller.msg("Enter furniture name:")
    return "Enter furniture name:", [
        {"key": "_input", "goto": "node_furniture_main", "exec": lambda c, s: c.ndb._furniture_design.update({'name': s})}
    ]

def node_furniture_set_seats(caller, raw_string, **kwargs):
    caller.msg("Enter number of seats:")
    return "Enter number of seats:", [
        {"key": "_input", "goto": "node_furniture_main", "exec": lambda c, s: c.ndb._furniture_design.update({'seats': int(s)})}
    ]

def node_furniture_toggle_sit(caller, raw_string, **kwargs):
    data = caller.ndb._furniture_design
    data['can_sit'] = not data.get('can_sit', False)
    return node_furniture_main(caller, raw_string, **kwargs)

def node_furniture_toggle_lie(caller, raw_string, **kwargs):
    data = caller.ndb._furniture_design
    data['can_lie'] = not data.get('can_lie', False)
    return node_furniture_main(caller, raw_string, **kwargs)

def node_furniture_toggle_recline(caller, raw_string, **kwargs):
    data = caller.ndb._furniture_design
    data['can_recline'] = not data.get('can_recline', False)
    return node_furniture_main(caller, raw_string, **kwargs)

def node_furniture_review(caller, raw_string, **kwargs):
    data = caller.ndb._furniture_design
    text = f"Review Furniture:\nName: {data.get('name')}\nSeats: {data.get('seats')}\nSit: {data.get('can_sit')}\nLie: {data.get('can_lie')}\nRecline: {data.get('can_recline')}"
    return text, [{"desc": "Back", "goto": "node_furniture_main"}]

def node_furniture_save(caller, raw_string, **kwargs):
    storage = get_admin_design_storage()
    furniture_data = dict(caller.ndb._furniture_design)
    storage.db.furniture.append(furniture_data)
    caller.msg(f"|gFurniture '{furniture_data.get('name')}' saved!|n")
    return node_furniture_main(caller, raw_string, **kwargs)

# =============================
# WEAPON DESIGN MENU
# =============================
def node_weapon_main(caller, raw_string, **kwargs):
    data = caller.ndb._weapon_design or {}
    text = f"""
|c=== Weapon Designer ===|n

|wName:|n {data.get('name', '(unnamed)')}
|wAmmo:|n {'|g[YES]|n' if data.get('uses_ammo') else '|r[NO]|n'}
|wAmmo Type:|n {data.get('ammo_type', '(none)')}

[R] Review
[S] Save
[Q] Quit
"""
    options = [
        {"desc": "Set Name", "goto": "node_weapon_set_name"},
        {"desc": "Toggle Uses Ammo", "goto": "node_weapon_toggle_ammo"},
        {"desc": "Set Ammo Type", "goto": "node_weapon_set_ammo_type"},
        {"desc": "Review", "goto": "node_weapon_review"},
        {"desc": "Save", "goto": "node_weapon_save"},
        {"desc": "Quit", "goto": "node_quit"},
    ]
    return text, options

def node_weapon_set_name(caller, raw_string, **kwargs):
    caller.msg("Enter weapon name:")
    return "Enter weapon name:", [
        {"key": "_input", "goto": "node_weapon_main", "exec": lambda c, s: c.ndb._weapon_design.update({'name': s})}
    ]

def node_weapon_toggle_ammo(caller, raw_string, **kwargs):
    data = caller.ndb._weapon_design
    data['uses_ammo'] = not data.get('uses_ammo', False)
    return node_weapon_main(caller, raw_string, **kwargs)

def node_weapon_set_ammo_type(caller, raw_string, **kwargs):
    caller.msg("Enter ammo type (e.g. 9mm, 257, etc):")
    return "Enter ammo type:", [
        {"key": "_input", "goto": "node_weapon_main", "exec": lambda c, s: c.ndb._weapon_design.update({'ammo_type': s})}
    ]

def node_weapon_review(caller, raw_string, **kwargs):
    data = caller.ndb._weapon_design
    text = f"Review Weapon:\nName: {data.get('name')}\nUses Ammo: {data.get('uses_ammo')}\nAmmo Type: {data.get('ammo_type')}"
    return text, [{"desc": "Back", "goto": "node_weapon_main"}]

def node_weapon_save(caller, raw_string, **kwargs):
    storage = get_admin_design_storage()
    weapon_data = dict(caller.ndb._weapon_design)
    storage.db.weapons.append(weapon_data)
    caller.msg(f"|gWeapon '{weapon_data.get('name')}' saved!|n")
    return node_weapon_main(caller, raw_string, **kwargs)

# =============================
# CLOTHES/ARMOR DESIGN MENU
# =============================
def node_clothes_main(caller, raw_string, **kwargs):
    data = caller.ndb._clothes_design or {}
    text = f"""
|c=== Clothes/Armor Designer ===|n

|wName:|n {data.get('name', '(unnamed)')}
|wIs Armor:|n {'|g[YES]|n' if data.get('is_armor') else '|r[NO]|n'}

[R] Review
[S] Save
[Q] Quit
"""
    options = [
        {"desc": "Set Name", "goto": "node_clothes_set_name"},
        {"desc": "Toggle Is Armor", "goto": "node_clothes_toggle_armor"},
        {"desc": "Review", "goto": "node_clothes_review"},
        {"desc": "Save", "goto": "node_clothes_save"},
        {"desc": "Quit", "goto": "node_quit"},
    ]
    return text, options

def node_clothes_set_name(caller, raw_string, **kwargs):
    caller.msg("Enter clothing name:")
    return "Enter clothing name:", [
        {"key": "_input", "goto": "node_clothes_main", "exec": lambda c, s: c.ndb._clothes_design.update({'name': s})}
    ]

def node_clothes_toggle_armor(caller, raw_string, **kwargs):
    data = caller.ndb._clothes_design
    data['is_armor'] = not data.get('is_armor', False)
    return node_clothes_main(caller, raw_string, **kwargs)

def node_clothes_review(caller, raw_string, **kwargs):
    data = caller.ndb._clothes_design
    text = f"Review Clothes/Armor:\nName: {data.get('name')}\nIs Armor: {data.get('is_armor')}"
    return text, [{"desc": "Back", "goto": "node_clothes_main"}]

def node_clothes_save(caller, raw_string, **kwargs):
    storage = get_admin_design_storage()
    clothes_data = dict(caller.ndb._clothes_design)
    storage.db.clothes.append(clothes_data)
    caller.msg(f"|gClothes/Armor '{clothes_data.get('name')}' saved!|n")
    return node_clothes_main(caller, raw_string, **kwargs)

# =============================
# QUIT NODE
# =============================
def node_quit(caller, raw_string, **kwargs):
    caller.msg("|yExited admin design menu.|n")
    return "Exited.", []

# =============================
# MENU LAUNCHERS
# =============================
class CmdAdminDesignMenu(Command):
    """
    Launch the admin design menu for builders/admins.
    Usage:
        admindesign
    """
    key = "admindesign"
    locks = "cmd:perm(Builder)"
    help_category = "Building"

    def func(self):
        EvMenu(self.caller, "commands.admin_design_menus", startnode="node_npc_main")

class CmdFurnitureDesignMenu(Command):
    key = "furnituredesign"
    locks = "cmd:perm(Builder)"
    help_category = "Building"
    def func(self):
        EvMenu(self.caller, "commands.admin_design_menus", startnode="node_furniture_main")

class CmdWeaponDesignMenu(Command):
    key = "weapondesign"
    locks = "cmd:perm(Builder)"
    help_category = "Building"
    def func(self):
        EvMenu(self.caller, "commands.admin_design_menus", startnode="node_weapon_main")

class CmdClothesDesignMenu(Command):
    key = "clothesdesign"
    locks = "cmd:perm(Builder)"
    help_category = "Building"
    def func(self):
        EvMenu(self.caller, "commands.admin_design_menus", startnode="node_clothes_main")
