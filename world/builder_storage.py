"""
Builder Storage System - Centralized storage for custom items created by builders

This module provides persistent storage for:
- Furniture designs
- NPC templates
- Weapon templates
- Clothing/armor templates
- Factions

Storage uses ScriptDB for persistence across server restarts.
"""

from evennia.scripts.models import ScriptDB
from evennia import create_script


def get_builder_storage():
    """Get or create the builder storage script."""
    try:
        storage = ScriptDB.objects.get(db_key="builder_storage")
    except ScriptDB.DoesNotExist:
        storage = create_script(
            "evennia.scripts.scripts.DefaultScript",
            key="builder_storage",
            persistent=True
        )
        # Initialize all storage containers
        storage.db.furniture = []
        storage.db.npcs = []
        storage.db.weapons = []
        storage.db.clothes = []
        storage.db.armor = []
        storage.db.factions = []
    
    return storage


def initialize_default_factions():
    """Initialize default factions if none exist."""
    storage = get_builder_storage()
    
    if not storage.db.factions:
        storage.db.factions = [
            {
                "id": "neutral",
                "name": "Neutral",
                "description": "No faction affiliation",
                "created_by": "System"
            },
            {
                "id": "kowloon_citizens",
                "name": "Kowloon Citizens",
                "description": "Local residents of Kowloon",
                "created_by": "System"
            },
            {
                "id": "kowloon_security",
                "name": "Kowloon Security",
                "description": "Security forces of Kowloon",
                "created_by": "System"
            },
        ]


# ============================================================================
# FURNITURE FUNCTIONS
# ============================================================================

def add_furniture(name, desc, movable=True, max_seats=0, can_recline=False, 
                  can_lie_down=False, sit_msg_first="", sit_msg_third="",
                  lie_msg_first="", lie_msg_third="", recline_msg_first="",
                  recline_msg_third="", created_by=""):
    """
    Add a new furniture design to storage.
    
    Args:
        name: Furniture name
        desc: Furniture description
        movable: Can the furniture be moved?
        max_seats: Maximum number of people who can sit (0 = can't sit)
        can_recline: Can furniture recline?
        can_lie_down: Can furniture be laid on?
        sit_msg_first: First-person sit message
        sit_msg_third: Third-person sit message
        lie_msg_first: First-person lie down message
        lie_msg_third: Third-person lie down message
        recline_msg_first: First-person recline message
        recline_msg_third: Third-person recline message
        created_by: Character who created this
    
    Returns:
        dict: The created furniture data or None on failure
    """
    storage = get_builder_storage()
    
    # Generate unique ID
    existing_ids = [f["id"] for f in storage.db.furniture]
    furniture_id = f"furniture_{len(existing_ids) + 1}"
    
    furniture_data = {
        "id": furniture_id,
        "name": name,
        "desc": desc,
        "movable": movable,
        "max_seats": max_seats,
        "can_recline": can_recline,
        "can_lie_down": can_lie_down,
        "sit_msg_first": sit_msg_first,
        "sit_msg_third": sit_msg_third,
        "lie_msg_first": lie_msg_first,
        "lie_msg_third": lie_msg_third,
        "recline_msg_first": recline_msg_first,
        "recline_msg_third": recline_msg_third,
        "created_by": created_by,
    }
    
    storage.db.furniture.append(furniture_data)
    return furniture_data


def get_furniture_by_id(furniture_id):
    """Get furniture design by ID."""
    storage = get_builder_storage()
    for furniture in storage.db.furniture:
        if furniture["id"] == furniture_id:
            return furniture
    return None


def search_furniture(keyword):
    """Search furniture by name or ID (case-insensitive)."""
    storage = get_builder_storage()
    keyword = keyword.lower()
    results = []
    
    for furniture in storage.db.furniture:
        if keyword in furniture["name"].lower() or keyword in furniture["id"].lower():
            results.append(furniture)
    
    return results


def get_all_furniture():
    """Get all furniture designs."""
    storage = get_builder_storage()
    return storage.db.furniture or []


def delete_furniture(furniture_id):
    """Delete a furniture design by ID."""
    storage = get_builder_storage()
    storage.db.furniture = [f for f in storage.db.furniture if f["id"] != furniture_id]


# ============================================================================
# NPC FUNCTIONS
# ============================================================================

def add_npc(name, desc, faction="neutral", wandering_zone="", is_shopkeeper=False,
            stats=None, skills=None, created_by="", primary_language="common", known_languages=None, race="human"):
    """
    Add a new NPC template to storage.
    
    Common is the default primary language.
    
    Args:
        name: NPC name
        desc: NPC description
        faction: Faction ID this NPC belongs to
        wandering_zone: Zone ID for wandering, or empty string for static
        is_shopkeeper: Is this NPC a shopkeeper?
        stats: Dictionary of D&D 5e stats (str, dex, con, int, wis, cha)
        skills: Dictionary of skills (brawling, blades, ranged, grapple, dodge, stealth, etc.)
        created_by: Character who created this
        primary_language: Primary language code (defaults to Common)
        known_languages: List of language codes NPC knows
        race: NPC race (human, elf, dwarf)
    
    Returns:
        dict: The created NPC data or None on failure
    """
    storage = get_builder_storage()
    
    # Default D&D 5e stats
    if stats is None:
        stats = {
            "str": 10,
            "dex": 10,
            "con": 10,
            "int": 10,
            "wis": 10,
            "cha": 10,
        }
    
    if skills is None:
        skills = {
            # Combat
            "dodge": 0,
            "parry": 0,
            "blades": 0,
            "ranged": 0,
            "melee": 0,
            "brawling": 0,
            "martial_arts": 0,
            "grappling": 0,
            # Stealth/Subterfuge
            "snooping": 0,
            "stealing": 0,
            "hiding": 0,
            "sneaking": 0,
            "disguise": 0,
            # Social
            "mercantile": 0,
            "persuasion": 0,
            "streetwise": 0,
            # Crafting
            "carpentry": 0,
            "blacksmithing": 0,
            "herbalism": 0,
            "tailoring": 0,
            "cooking": 0,
            # Survival
            "tracking": 0,
            "foraging": 0,
            # Lore
            "investigation": 0,
            "lore": 0,
            "appraise": 0,
            # Medical
            "first_aid": 0,
            "chirurgy": 0,
            # Creative
            "paint_draw_sculpt": 0,
            "instrument": 0,
        }
    
    if known_languages is None:
        known_languages = ["common"]
    
    # Generate unique ID
    existing_ids = [n["id"] for n in storage.db.npcs]
    npc_id = f"npc_{len(existing_ids) + 1}"
    
    npc_data = {
        "id": npc_id,
        "name": name,
        "desc": desc,
        "faction": faction,
        "wandering_zone": wandering_zone,
        "is_shopkeeper": is_shopkeeper,
        "stats": stats,
        "skills": skills,
        "created_by": created_by,
        "primary_language": primary_language,
        "known_languages": known_languages,
        "race": race,
    }
    
    storage.db.npcs.append(npc_data)
    return npc_data


def get_npc_by_id(npc_id):
    """Get NPC template by ID."""
    storage = get_builder_storage()
    for npc in storage.db.npcs:
        if npc["id"] == npc_id:
            return npc
    return None


def search_npcs(keyword):
    """Search NPCs by name or ID (case-insensitive)."""
    storage = get_builder_storage()
    keyword = keyword.lower()
    results = []
    
    for npc in storage.db.npcs:
        if keyword in npc["name"].lower() or keyword in npc["id"].lower():
            results.append(npc)
    
    return results


def get_all_npcs():
    """Get all NPC templates."""
    storage = get_builder_storage()
    return storage.db.npcs or []


def migrate_npc_skills():
    """
    Migrate old skill names to new skill system.
    Maps old skills to new ones and normalizes the skill dictionary.
    """
    storage = get_builder_storage()
    
    # Mapping of old skill names to new ones
    old_to_new = {
        "brawling": "brawling",
        "blades": "blades",
        "blunt": "melee",  # Remap to melee
        "ranged": "ranged",
        "grapple": "grappling",
        "dodge": "dodge",
        "stealth": "sneaking",
        "intimidate": None,  # Remove
        "persuasion": "persuasion",
        "perception": "investigation",  # Remap to investigation
        "athletics": None,  # Remove
        "farming": "foraging",  # Remap to foraging
        "aeronautics": None,  # Remove
        "forgery": None,  # Remove
        # Old cyberpunk skills mapped to new fantasy equivalents
        "modern_medicine": "first_aid",
        "holistic_medicine": "herbalism",
        "surgery": "chirurgy",
        "chemical": "herbalism",
        "science": None,  # Remove
        "tinkering": "carpentry",
        "manufacturing": "blacksmithing",
        "forensics": "investigation",
        "decking": None,  # Remove
        "electronics": None,  # Remove
    }
    
    # New skill defaults
    new_skills = {
        # Combat
        "dodge": 0,
        "parry": 0,
        "blades": 0,
        "ranged": 0,
        "melee": 0,
        "brawling": 0,
        "martial_arts": 0,
        "grappling": 0,
        # Stealth/Subterfuge
        "snooping": 0,
        "stealing": 0,
        "hiding": 0,
        "sneaking": 0,
        "disguise": 0,
        # Social
        "mercantile": 0,
        "persuasion": 0,
        "streetwise": 0,
        # Crafting
        "carpentry": 0,
        "blacksmithing": 0,
        "herbalism": 0,
        "tailoring": 0,
        "cooking": 0,
        # Survival
        "tracking": 0,
        "foraging": 0,
        # Lore
        "investigation": 0,
        "lore": 0,
        "appraise": 0,
        # Medical
        "first_aid": 0,
        "chirurgy": 0,
        # Creative
        "paint_draw_sculpt": 0,
        "instrument": 0,
    }
    
    for npc in storage.db.npcs:
        if "skills" not in npc:
            npc["skills"] = new_skills.copy()
            continue
        
        old_skills = npc["skills"]
        new_npc_skills = new_skills.copy()
        
        # Migrate old skills to new ones
        for old_name, old_value in old_skills.items():
            if old_name in old_to_new:
                new_name = old_to_new[old_name]
                if new_name and old_value > 0:
                    new_npc_skills[new_name] = old_value
            elif old_name in new_npc_skills:
                # Already a new-style skill, keep it
                new_npc_skills[old_name] = old_value
        
        npc["skills"] = new_npc_skills
    
    storage.save()


def delete_npc(npc_id):
    """Delete an NPC template by ID."""
    storage = get_builder_storage()
    storage.db.npcs = [n for n in storage.db.npcs if n["id"] != npc_id]


# ============================================================================
# WEAPON FUNCTIONS
# ============================================================================

def add_weapon(name, desc, weapon_type="melee", ammo_type="", damage_bonus=0,
               accuracy_bonus=0, skill="brawling", created_by=""):
    """
    Add a new weapon template to storage.
    
    Args:
        name: Weapon name
        desc: Weapon description
        weapon_type: "melee" or "ranged"
        ammo_type: Type of ammo required (empty for melee, e.g., "9mm", "arrow")
        damage_bonus: Bonus damage
        accuracy_bonus: Bonus to accuracy rolls
        skill: Combat skill used with this weapon (blades, ranged, melee, brawling, martial_arts, dodge, athletics)
        created_by: Character who created this
    
    Returns:
        dict: The created weapon data or None on failure
    """
    storage = get_builder_storage()
    
    # Generate unique ID
    existing_ids = [w["id"] for w in storage.db.weapons]
    weapon_id = f"weapon_{len(existing_ids) + 1}"
    
    weapon_data = {
        "id": weapon_id,
        "name": name,
        "desc": desc,
        "weapon_type": weapon_type,
        "ammo_type": ammo_type,
        "damage_bonus": damage_bonus,
        "accuracy_bonus": accuracy_bonus,
        "skill": skill,
        "created_by": created_by,
    }
    
    storage.db.weapons.append(weapon_data)
    return weapon_data


def get_weapon_by_id(weapon_id):
    """Get weapon template by ID."""
    storage = get_builder_storage()
    for weapon in storage.db.weapons:
        if weapon["id"] == weapon_id:
            return weapon
    return None


def update_weapon_name(weapon_id, new_name):
    """Update weapon name by ID."""
    storage = get_builder_storage()
    for weapon in storage.db.weapons:
        if weapon["id"] == weapon_id:
            # Strip designweapon prefix if present
            if new_name.startswith('designweapon '):
                new_name = new_name[len('designweapon '):]
            weapon["name"] = new_name
            return True
    return False


def search_weapons(keyword):
    """Search weapons by name, type, or ID (case-insensitive)."""
    storage = get_builder_storage()
    keyword = keyword.lower()
    results = []
    
    for weapon in storage.db.weapons:
        if (keyword in weapon["name"].lower() or 
            keyword in weapon["id"].lower() or
            keyword in weapon["weapon_type"].lower()):
            results.append(weapon)
    
    return results


def get_all_weapons():
    """Get all weapon templates."""
    storage = get_builder_storage()
    return storage.db.weapons or []


def delete_weapon(weapon_id):
    """Delete a weapon template by ID."""
    storage = get_builder_storage()
    storage.db.weapons = [w for w in storage.db.weapons if w["id"] != weapon_id]


# ============================================================================
# CLOTHING/ARMOR FUNCTIONS
# ============================================================================

def add_clothing_item(name, desc, item_type="clothing", armor_value=0, 
                      armor_type="", rarity="common", created_by=""):
    """
    Add a new clothing/armor item to storage.
    
    Args:
        name: Item name
        desc: Item description
        item_type: "clothing" or "armor"
        armor_value: Armor rating (0 for clothing)
        armor_type: Type of armor ("light", "medium", "heavy")
        rarity: Item rarity ("common", "uncommon", "rare", "epic")
        created_by: Character who created this
    
    Returns:
        dict: The created item data or None on failure
    """
    storage = get_builder_storage()
    
    # Generate unique ID
    all_clothes = storage.db.clothes or []
    all_armor = storage.db.armor or []
    total = len(all_clothes) + len(all_armor)
    item_id = f"{item_type}_{total + 1}"
    
    item_data = {
        "id": item_id,
        "name": name,
        "desc": desc,
        "item_type": item_type,
        "armor_value": armor_value,
        "armor_type": armor_type,
        "rarity": rarity,
        "created_by": created_by,
    }
    
    if item_type == "clothing":
        storage.db.clothes.append(item_data)
    else:
        storage.db.armor.append(item_data)
    
    return item_data


def get_clothing_by_id(item_id):
    """Get clothing item by ID."""
    storage = get_builder_storage()
    for item in storage.db.clothes or []:
        if item["id"] == item_id:
            return item
    return None


def get_armor_by_id(item_id):
    """Get armor item by ID."""
    storage = get_builder_storage()
    for item in storage.db.armor or []:
        if item["id"] == item_id:
            return item
    return None


def search_clothing(keyword):
    """Search clothing by name or ID (case-insensitive)."""
    storage = get_builder_storage()
    keyword = keyword.lower()
    results = []
    
    for item in storage.db.clothes or []:
        if keyword in item["name"].lower() or keyword in item["id"].lower():
            results.append(item)
    
    return results


def search_armor(keyword):
    """Search armor by name, type, or ID (case-insensitive)."""
    storage = get_builder_storage()
    keyword = keyword.lower()
    results = []
    
    for item in storage.db.armor or []:
        if (keyword in item["name"].lower() or 
            keyword in item["id"].lower() or
            keyword in item.get("armor_type", "").lower()):
            results.append(item)
    
    return results


def get_all_clothing():
    """Get all clothing items."""
    storage = get_builder_storage()
    return storage.db.clothes or []


def get_all_armor():
    """Get all armor items."""
    storage = get_builder_storage()
    return storage.db.armor or []


def delete_clothing(item_id):
    """Delete a clothing item by ID."""
    storage = get_builder_storage()
    storage.db.clothes = [i for i in (storage.db.clothes or []) if i["id"] != item_id]


def delete_armor(item_id):
    """Delete an armor item by ID."""
    storage = get_builder_storage()
    storage.db.armor = [i for i in (storage.db.armor or []) if i["id"] != item_id]


# ============================================================================
# FACTION FUNCTIONS
# ============================================================================

def add_faction(faction_id, name, description, created_by=""):
    """
    Add a new faction.
    
    Args:
        faction_id: Unique faction ID (lowercase, no spaces)
        name: Faction name
        description: Faction description
        created_by: Character who created this
    
    Returns:
        dict: The created faction data or None if ID already exists
    """
    storage = get_builder_storage()
    
    # Check if faction ID already exists
    if any(f["id"] == faction_id for f in storage.db.factions):
        return None
    
    faction_data = {
        "id": faction_id,
        "name": name,
        "description": description,
        "created_by": created_by,
    }
    
    storage.db.factions.append(faction_data)
    return faction_data


def get_faction(faction_id):
    """Get faction by ID."""
    storage = get_builder_storage()
    for faction in storage.db.factions:
        if faction["id"] == faction_id:
            return faction
    return None


def get_faction_by_name(faction_name):
    """Get faction by name (case-insensitive)."""
    storage = get_builder_storage()
    name_lower = faction_name.lower()
    
    for faction in storage.db.factions:
        if faction["name"].lower() == name_lower:
            return faction
    return None


def search_factions(keyword):
    """Search factions by name or ID (case-insensitive)."""
    storage = get_builder_storage()
    keyword = keyword.lower()
    results = []
    
    for faction in storage.db.factions:
        if (keyword in faction["name"].lower() or 
            keyword in faction["id"].lower()):
            results.append(faction)
    
    return results


def get_all_factions():
    """Get all factions."""
    storage = get_builder_storage()
    return storage.db.factions or []


def delete_faction(faction_id):
    """Delete a faction by ID."""
    storage = get_builder_storage()
    storage.db.factions = [f for f in storage.db.factions if f["id"] != faction_id]
