def node_npc_set_cloneable(caller, raw_string, **kwargs):
    data = _npc_data(caller)
    current = '|gYES|n' if data.get('cloneable') else '|rNO|n'
    text = (
        f"|c=== Set Cloneable Status ===|n\n\n"
        f"Current: {current}\n\n"
        "Should this NPC design be cloneable?\n"
        "If |gYES|n, you can use this design as a template to spawn new NPCs.\n"
        "If |rNO|n, this design is just a one-off.\n\n"
        "Type |g1|n or |gyes|n for YES, |r2|n or |rno|n for NO, or 'back' to return."
    )
    options = ( {"key": "_default", "goto": "node_npc_set_cloneable_handler"}, )
    return text, options

def node_npc_set_cloneable_handler(caller, raw_string, **kwargs):
    val = (raw_string or '').strip().lower()
    if val == 'back':
        return "node_npc_main"
    if val in ('1', 'yes', 'y', 'true'):
        _npc_data(caller)['cloneable'] = True
        caller.msg("|gCloneable set to YES.|n")
        return "node_npc_main"
    if val in ('2', 'no', 'n', 'false'):
        _npc_data(caller)['cloneable'] = False
        caller.msg("|rCloneable set to NO.|n")
        return "node_npc_main"
    caller.msg("|rPlease type 1/yes or 2/no, or 'back' to return.|n")
    return "node_npc_set_cloneable"
# =============================
# NPC SAVE NODE (re-added/fixed)
def node_npc_save(caller, raw_string, **kwargs):
    storage = get_admin_design_storage()
    npc_data = dict(_npc_data(caller))
    if not npc_data.get("name"):
        caller.msg("|rYou must set a name before saving!|n")
        return "node_npc_main"
    storage.db.npcs.append(npc_data)
    caller.msg(f"|gNPC '{npc_data.get('name')}' saved!|n")
    return "node_npc_main"
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
from evennia.scripts.scripts import DefaultScript

# Storage script key for admin designs
ADMIN_DESIGN_STORAGE_KEY = "admin_design_storage"

# Helper to get or create storage script
def get_admin_design_storage():
    storage = ScriptDB.objects.filter(db_key=ADMIN_DESIGN_STORAGE_KEY).first()
    if storage:
        return storage
    from evennia import create_script
    storage = create_script(DefaultScript, key=ADMIN_DESIGN_STORAGE_KEY)
    storage.persistent = True
    storage.db.npcs = []
    storage.db.furniture = []
    storage.db.weapons = []
    storage.db.clothes = []
    return storage

# =============================
# NPC DESIGN MENU (Expanded)
# =============================
def _npc_data(caller):
    if not hasattr(caller.ndb, '_npc_design') or caller.ndb._npc_design is None:
        caller.ndb._npc_design = {
            "name": "",
            "desc": "",
            "prototype_key": "",
            "wandering": False,
            "cloneable": False,
        }
    return caller.ndb._npc_design

def node_npc_main(caller, raw_string, **kwargs):
    data = _npc_data(caller)
    text = f"""
|c=== NPC Designer ===|n

|wName:|n {data.get('name', '(unnamed)')}
|wPrototype Key:|n {data.get('prototype_key', '(none)')}
|wDescription:|n {data.get('desc', '(none)')}
|wWandering:|n {'|g[ON]|n' if data.get('wandering') else '|r[OFF]|n'}
|wCloneable:|n {'|g[YES]|n' if data.get('cloneable') else '|r[NO]|n'}

[R] Review
[S] Save
[L] Load
[Q] Quit
"""
    options = [
        {"desc": "Set Name", "goto": "node_npc_set_name"},
        {"desc": "Set Prototype Key", "goto": "node_npc_set_prototype"},
        {"desc": "Set Description", "goto": "node_npc_set_desc"},
        {"desc": "Toggle Wandering", "goto": "node_npc_toggle_wandering"},
        {"desc": "Set Cloneable", "goto": "node_npc_set_cloneable"},
        {"desc": "Review", "goto": "node_npc_review"},
        {"desc": "Save", "goto": "node_npc_save"},
        {"desc": "Load", "goto": "node_npc_load"},
        {"desc": "Quit", "goto": "node_quit"},
    ]
    return text, options

def node_npc_set_name(caller, raw_string, **kwargs):

    # Step 1: Prompt for name





    # --- Canonical EvMenu input pattern ---
    def node_npc_set_name(caller, raw_string, **kwargs):
        text = (
            "|c=== Set NPC Name ===|n\n\n"
            "Enter the name for your NPC. This is what the NPC will be called.\n\n"
            "Examples: |wLu Bu|n, |wStreet Vendor|n, |wCybernetic Guard|n\n\n"
            "|wType your name and press Enter, or type 'back' to return.|n"
        )
        options = ( {"key": "_default", "goto": "node_npc_set_name_handler"}, )
        return text, options

    def node_npc_set_name_handler(caller, raw_string, **kwargs):
        name = (raw_string or '').strip()
        if name.lower() == 'back':
            return "node_npc_main"
        if len(name) < 3:
            caller.msg("|rName must be at least 3 characters.|n")
            return "node_npc_set_name"
        if len(name) > 80:
            caller.msg("|rName must be 80 characters or less.|n")
            return "node_npc_set_name"
        if name.isdigit():
            caller.msg("|rPlease enter a non-numeric name.|n")
            return "node_npc_set_name"
        _npc_data(caller)["name"] = name
        caller.msg(f"|gNPC name set to:|n {name}")
        return "node_npc_main"

def node_npc_set_prototype(caller, raw_string, **kwargs):
    caller.msg("Enter prototype key (for cloning):")
    return "Enter prototype key:", [
        {"key": "_input", "goto": "node_npc_main", "exec": lambda c, s: _npc_data(c).update({'prototype_key': s})}
    ]

def node_npc_set_desc(caller, raw_string, **kwargs):
    text = (
        "|c=== Set NPC Description ===|n\n\n"
        "Enter a description for your NPC. This will be shown when someone examines the NPC.\n\n"
        "|wType your description and press Enter, or type 'back' to return.|n"
    )
    options = ( {"key": "_default", "goto": "node_npc_set_desc_handler"}, )
    return text, options

def node_npc_set_desc_handler(caller, raw_string, **kwargs):
    desc = (raw_string or '').strip()
    if desc.lower() == 'back':
        return "node_npc_main"
    if len(desc) < 5:
        caller.msg("|rDescription must be at least 5 characters.|n")
        return "node_npc_set_desc"
    if len(desc) > 2000:
        caller.msg("|rDescription must be 2000 characters or less.|n")
        return "node_npc_set_desc"
    _npc_data(caller)["desc"] = desc
    caller.msg(f"|gNPC description set.|n")
    return "node_npc_main"

def node_npc_toggle_wandering(caller, raw_string, **kwargs):
    data = _npc_data(caller)
    data['wandering'] = not data.get('wandering', False)
    return node_npc_main(caller, raw_string, **kwargs)


# --- Canonical EvMenu input pattern ---
def node_npc_set_name(caller, raw_string, **kwargs):
    text = (
        "|c=== Set NPC Name ===|n\n\n"
        "Enter the name for your NPC. This is what the NPC will be called.\n\n"
        "Examples: |wLu Bu|n, |wStreet Vendor|n, |wCybernetic Guard|n\n\n"
        "|wType your name and press Enter, or type 'back' to return.|n"
    )
    options = ( {"key": "_default", "goto": "node_npc_set_name_handler"}, )
    return text, options

def node_npc_set_name_handler(caller, raw_string, **kwargs):
    name = (raw_string or '').strip()
    if name.lower() == 'back':
        return "node_npc_main"
    if len(name) < 3:
        caller.msg("|rName must be at least 3 characters.|n")
        return "node_npc_set_name"
    if len(name) > 80:
        caller.msg("|rName must be 80 characters or less.|n")
        return "node_npc_set_name"
    if name.isdigit():
        caller.msg("|rPlease enter a non-numeric name.|n")
        return "node_npc_set_name"
    _npc_data(caller)["name"] = name
    caller.msg(f"|gNPC name set to:|n {name}")
    return "node_npc_main"
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
|wCoverage:|n {', '.join(data.get('coverage', [])) or '(none)'}
|wColor:|n {data.get('color', '(none)')}
|wSee-Thru:|n {'|g[YES]|n' if data.get('see_thru') else '|r[NO]|n'}
|wDescription:|n {data.get('desc', '(none)')}
|wWear Msg:|n {data.get('wear_msg', '(default)')}
|wRemove Msg:|n {data.get('remove_msg', '(default)')}
|wWorn Msg:|n {data.get('worn_msg', '(default)')}

[R] Review
[S] Save
[Q] Quit
"""
    options = [
        {"desc": "Set Name", "goto": "node_clothes_set_name"},
        {"desc": "Toggle Is Armor", "goto": "node_clothes_toggle_armor"},
        {"desc": "Set Coverage", "goto": "node_clothes_set_coverage"},
        {"desc": "Set Color", "goto": "node_clothes_set_color"},
        {"desc": "Toggle See-Thru", "goto": "node_clothes_toggle_see_thru"},
        {"desc": "Set Description", "goto": "node_clothes_set_desc"},
        {"desc": "Set Wear Msg", "goto": "node_clothes_set_wear_msg"},
        {"desc": "Set Remove Msg", "goto": "node_clothes_set_remove_msg"},
        {"desc": "Set Worn Msg", "goto": "node_clothes_set_worn_msg"},
        {"desc": "Review", "goto": "node_clothes_review"},
        {"desc": "Save", "goto": "node_clothes_save"},
        {"desc": "Quit", "goto": "node_quit"},
    ]
    return text, options
def node_clothes_set_coverage(caller, raw_string, **kwargs):
    caller.msg("Enter comma-separated body locations for coverage (e.g. chest, arms, legs):")
    return "Enter coverage:", [
        {"key": "_input", "goto": "node_clothes_main", "exec": lambda c, s: c.ndb._clothes_design.update({'coverage': [loc.strip() for loc in s.split(',') if loc.strip()]})}
    ]

def node_clothes_set_color(caller, raw_string, **kwargs):
    caller.msg("Enter color:")
    return "Enter color:", [
        {"key": "_input", "goto": "node_clothes_main", "exec": lambda c, s: c.ndb._clothes_design.update({'color': s.strip()})}
    ]

def node_clothes_toggle_see_thru(caller, raw_string, **kwargs):
    data = caller.ndb._clothes_design
    data['see_thru'] = not data.get('see_thru', False)
    return node_clothes_main(caller, raw_string, **kwargs)

def node_clothes_set_desc(caller, raw_string, **kwargs):
    caller.msg("Enter description:")
    return "Enter description:", [
        {"key": "_input", "goto": "node_clothes_main", "exec": lambda c, s: c.ndb._clothes_design.update({'desc': s.strip()})}
    ]

def node_clothes_set_wear_msg(caller, raw_string, **kwargs):
    caller.msg("Enter wear message:")
    return "Enter wear message:", [
        {"key": "_input", "goto": "node_clothes_main", "exec": lambda c, s: c.ndb._clothes_design.update({'wear_msg': s.strip()})}
    ]

def node_clothes_set_remove_msg(caller, raw_string, **kwargs):
    caller.msg("Enter remove message:")
    return "Enter remove message:", [
        {"key": "_input", "goto": "node_clothes_main", "exec": lambda c, s: c.ndb._clothes_design.update({'remove_msg': s.strip()})}
    ]

def node_clothes_set_worn_msg(caller, raw_string, **kwargs):
    caller.msg("Enter worn message:")
    return "Enter worn message:", [
        {"key": "_input", "goto": "node_clothes_main", "exec": lambda c, s: c.ndb._clothes_design.update({'worn_msg': s.strip()})}
    ]

def node_clothes_set_name(caller, raw_string, **kwargs):
    caller.msg("Enter clothing name:")
    return "Enter clothing name:", [
        {"key": "_input", "goto": "node_clothes_main", "exec": lambda c, s: c.ndb._clothes_design.update({'name': s})}
    ]

def node_clothes_toggle_armor(caller, raw_string, **kwargs):
    data = caller.ndb._clothes_design
    data['is_armor'] = not data.get('is_armor', False)
    return node_clothes_main(caller, raw_string, **kwargs)

def node_clothes_toggle_see_thru(caller, raw_string, **kwargs):
    data = caller.ndb._clothes_design
    data['see_thru'] = not data.get('see_thru', False)
    return node_clothes_main(caller, raw_string, **kwargs)

def node_clothes_review(caller, raw_string, **kwargs):
    data = caller.ndb._clothes_design
    text = f"""
|c=== Review Clothes/Armor ===|n
Name: {data.get('name')}
Is Armor: {data.get('is_armor')}
Coverage: {', '.join(data.get('coverage', []))}
Color: {data.get('color')}
See-Thru: {data.get('see_thru')}
Description: {data.get('desc')}
Wear Msg: {data.get('wear_msg')}
Remove Msg: {data.get('remove_msg')}
Worn Msg: {data.get('worn_msg')}
"""
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

# NPC Design Command
class CmdNPCDesignMenu(Command):
    """
    Launch the NPC design menu for builders/admins.
    Usage:
        npcdesign
    """
    key = "npcdesign"
    locks = "cmd:perm(Builder)"
    help_category = "Building"

    def func(self):
        EvMenu(self.caller, "commands.admin_design_menus", startnode="node_npc_main")

# Furniture Design Command
class CmdFurnitureDesignMenu(Command):
    key = "furnituredesign"
    locks = "cmd:perm(Builder)"
    help_category = "Building"
    def func(self):
        EvMenu(self.caller, "commands.admin_design_menus", startnode="node_furniture_main")

# Weapon Design Command
class CmdWeaponDesignMenu(Command):
    key = "weapondesign"
    locks = "cmd:perm(Builder)"
    help_category = "Building"
    def func(self):
        EvMenu(self.caller, "commands.admin_design_menus", startnode="node_weapon_main")

# Armor/Clothes Design Command (alias: armordesign)
class CmdArmorDesignMenu(Command):
    key = "armordesign"
    aliases = ["clothesdesign", "clothdesign"]
    locks = "cmd:perm(Builder)"
    help_category = "Building"
    def func(self):
        EvMenu(self.caller, "commands.admin_design_menus", startnode="node_clothes_main")

# Spawn Clothing Design Command
class CmdSpawnClothingDesign(Command):
    """
    Spawn a clothing/armor item from a saved design.
    Usage:
        spawnclothing <name> [to <character>]
    """
    key = "spawnclothing"
    locks = "cmd:perm(Builder)"
    help_category = "Building"

    def func(self):
        args = self.args.strip()
        if not args:
            self.caller.msg("Usage: spawnclothing <name> [to <character>]")
            return
        parts = args.split(" to ", 1)
        name = parts[0].strip()
        target = self.caller
        if len(parts) > 1:
            from evennia.utils.search import search_object
            targets = search_object(parts[1].strip())
            if not targets:
                self.caller.msg(f"Target '{parts[1].strip()}' not found.")
                return
            target = targets[0]
        storage = get_admin_design_storage()
        designs = storage.db.clothes or []
        design = next((d for d in designs if d.get('name', '').lower() == name.lower()), None)
        if not design:
            self.caller.msg(f"No saved clothing/armor design named '{name}'.")
            return
        # Create the clothing/armor object (replace with your typeclass as needed)
        from evennia import create_object
        obj = create_object("typeclasses.clothing.Clothing", key=design.get('name'), location=target)
        obj.db.is_armor = design.get('is_armor', False)
        obj.db.coverage = design.get('coverage', [])
        obj.db.color = design.get('color', '')
        obj.db.see_thru = design.get('see_thru', False)
        obj.db.desc = design.get('desc', '')
        obj.db.wear_msg = design.get('wear_msg', '')
        obj.db.remove_msg = design.get('remove_msg', '')
        obj.db.worn_msg = design.get('worn_msg', '')
        self.caller.msg(f"|gSpawned '{obj.key}' for {target.key}.|n")
        if target != self.caller:
            target.msg(f"|y{self.caller.key} has given you '{obj.key}'.|n")
