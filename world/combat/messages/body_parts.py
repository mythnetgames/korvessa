"""
Body Part Combat Message System

Provides body-part-specific message fragments, consequences, and flavor text
for combat messages. This allows weapons to have contextually appropriate
descriptions based on WHERE they hit, not just THAT they hit.

Body locations are pulled from the medical/longdesc system:
- head, face, left_eye, right_eye
- chest, back, abdomen, groin
- left_arm, right_arm, left_hand, right_hand
- left_thigh, right_thigh, left_shin, right_shin
- left_foot, right_foot
"""

import random

# =============================================================================
# BODY PART CATEGORIES
# =============================================================================

# Group body parts by type for message selection
HEAD_PARTS = {"head", "face", "left_eye", "right_eye"}
TORSO_PARTS = {"chest", "back", "abdomen", "groin"}
ARM_PARTS = {"left_arm", "right_arm", "left_hand", "right_hand"}
LEG_PARTS = {"left_thigh", "right_thigh", "left_shin", "right_shin", "left_foot", "right_foot"}

# Vital areas for special messaging
VITAL_AREAS = {"head", "chest", "abdomen", "groin"}

# =============================================================================
# IMPACT DESCRIPTIONS BY BODY PART
# =============================================================================

# Generic impact descriptions that work with any weapon type
IMPACT_DESCRIPTIONS = {
    # Head region
    "head": [
        "snapping their head back violently",
        "rattling their skull",
        "sending stars across their vision",
        "making their ears ring",
        "nearly knocking them senseless",
    ],
    "face": [
        "crunching bone and cartilage",
        "splitting skin across cheekbone",
        "sending teeth flying",
        "crushing their nose flat",
        "leaving their face a bloody mess",
    ],
    "left_eye": [
        "threatening their vision",
        "making them see red - literally",
        "nearly blinding them",
    ],
    "right_eye": [
        "threatening their vision",
        "making them see red - literally",
        "nearly blinding them",
    ],
    
    # Torso region
    "chest": [
        "driving the air from their lungs",
        "cracking ribs with an audible snap",
        "making them double over",
        "leaving them gasping",
        "staggering them backward",
    ],
    "back": [
        "arching their spine in agony",
        "driving them to their knees",
        "making them stumble forward",
        "wrenching a cry from their throat",
    ],
    "abdomen": [
        "folding them like a cheap chair",
        "threatening to spill their guts",
        "making them retch",
        "leaving them clutching their midsection",
    ],
    "groin": [
        "dropping them to their knees instantly",
        "making them curl into a fetal position",
        "eliciting a high-pitched wheeze",
        "ending any thoughts of heroism",
    ],
    
    # Arm region
    "left_arm": [
        "numbing their grip",
        "making their arm hang useless",
        "threatening to break bone",
        "leaving the limb screaming in protest",
    ],
    "right_arm": [
        "numbing their grip",
        "making their arm hang useless",
        "threatening to break bone",
        "leaving the limb screaming in protest",
    ],
    "left_hand": [
        "crushing delicate bones",
        "making them drop what they were holding",
        "mangling their fingers",
    ],
    "right_hand": [
        "crushing delicate bones",
        "making them drop what they were holding",
        "mangling their fingers",
    ],
    
    # Leg region
    "left_thigh": [
        "buckling their leg",
        "threatening to drop them",
        "making them limp badly",
        "taking the strength from their stance",
    ],
    "right_thigh": [
        "buckling their leg",
        "threatening to drop them",
        "making them limp badly",
        "taking the strength from their stance",
    ],
    "left_shin": [
        "making them howl",
        "threatening to snap the bone",
        "leaving them hobbling",
    ],
    "right_shin": [
        "making them howl",
        "threatening to snap the bone",
        "leaving them hobbling",
    ],
    "left_foot": [
        "that will get them out of the army",
        "making every future step agony",
        "crushing small bones underfoot",
    ],
    "right_foot": [
        "that will get them out of the army",
        "making every future step agony",
        "crushing small bones underfoot",
    ],
}

# =============================================================================
# BULLET/PROJECTILE WOUND DESCRIPTIONS
# =============================================================================

BULLET_WOUNDS = {
    "head": [
        "punching through skull",
        "tearing through scalp and bone",
        "leaving a ragged furrow across their skull",
        "nearly taking their head off",
    ],
    "face": [
        "shattering their jaw",
        "tearing through their cheek",
        "ripping through facial bone",
        "leaving a bloody crater where features used to be",
    ],
    "left_eye": [
        "destroying the eye in a spray of vitreous humor",
        "punching straight through the socket",
    ],
    "right_eye": [
        "destroying the eye in a spray of vitreous humor",
        "punching straight through the socket",
    ],
    "chest": [
        "punching clean through",
        "collapsing a lung",
        "spraying blood from the exit wound",
        "leaving a sucking chest wound",
        "embedding deep in muscle and bone",
    ],
    "back": [
        "exiting through the front in a spray of red",
        "severing something important",
        "punching through their spine",
    ],
    "abdomen": [
        "tearing through intestines",
        "leaving a ragged hole leaking blood",
        "ripping through their gut",
        "spilling blood and worse",
    ],
    "groin": [
        "in the worst possible place",
        "turning future plans into past tense",
        "hitting something that will never heal right",
    ],
    "left_arm": [
        "shattering the humerus",
        "tearing through muscle",
        "leaving the arm hanging by sinew",
        "spraying arterial red",
    ],
    "right_arm": [
        "shattering the humerus",
        "tearing through muscle",
        "leaving the arm hanging by sinew",
        "spraying arterial red",
    ],
    "left_hand": [
        "taking fingers with it",
        "shattering the palm",
        "leaving a mangled mess",
    ],
    "right_hand": [
        "taking fingers with it",
        "shattering the palm",
        "leaving a mangled mess",
    ],
    "left_thigh": [
        "shattering the femur",
        "clipping the femoral artery",
        "leaving a gaping wound",
        "dropping them instantly",
    ],
    "right_thigh": [
        "shattering the femur",
        "clipping the femoral artery",
        "leaving a gaping wound",
        "dropping them instantly",
    ],
    "left_shin": [
        "splintering the tibia",
        "tearing through the calf",
        "leaving them crippled",
    ],
    "right_shin": [
        "splintering the tibia",
        "tearing through the calf",
        "leaving them crippled",
    ],
    "left_foot": [
        "shattering small bones",
        "turning the boot into a bloody mess",
        "taking toes with it",
    ],
    "right_foot": [
        "shattering small bones",
        "turning the boot into a bloody mess",
        "taking toes with it",
    ],
}

# =============================================================================
# BLADE WOUND DESCRIPTIONS
# =============================================================================

BLADE_WOUNDS = {
    "head": [
        "carving a deep gash across their scalp",
        "splitting skin to the bone",
        "nearly scalping them",
        "opening their skull to daylight",
    ],
    "face": [
        "laying their cheek open to the teeth",
        "carving a permanent smile",
        "splitting their lip to the gum",
        "taking an ear clean off",
    ],
    "left_eye": [
        "slicing across the socket",
        "blinding them in a spray of fluid",
    ],
    "right_eye": [
        "slicing across the socket",
        "blinding them in a spray of fluid",
    ],
    "chest": [
        "parting flesh like water",
        "sliding between ribs",
        "opening them up like a fish",
        "leaving a wound that won't stop weeping red",
    ],
    "back": [
        "carving a furrow down their spine",
        "laying muscle bare to bone",
        "leaving a wound that will scar forever",
    ],
    "abdomen": [
        "threatening to spill their insides",
        "slicing through the belly wall",
        "gutting them like livestock",
        "opening a wound no surgeon can close clean",
    ],
    "groin": [
        "in a place that makes them scream",
        "cutting something that matters",
        "ending their lineage",
    ],
    "left_arm": [
        "slicing through muscle to bone",
        "nearly severing tendons",
        "leaving the arm streaming blood",
        "cutting deep enough to see white",
    ],
    "right_arm": [
        "slicing through muscle to bone",
        "nearly severing tendons",
        "leaving the arm streaming blood",
        "cutting deep enough to see white",
    ],
    "left_hand": [
        "taking fingers",
        "slicing through the palm",
        "severing tendons",
    ],
    "right_hand": [
        "taking fingers",
        "slicing through the palm",
        "severing tendons",
    ],
    "left_thigh": [
        "opening the femoral artery",
        "carving through the quad",
        "leaving them struggling to stand",
    ],
    "right_thigh": [
        "opening the femoral artery",
        "carving through the quad",
        "leaving them struggling to stand",
    ],
    "left_shin": [
        "scraping bone",
        "slicing through the calf",
        "hamstringing them",
    ],
    "right_shin": [
        "scraping bone",
        "slicing through the calf",
        "hamstringing them",
    ],
    "left_foot": [
        "slicing through the boot",
        "severing the Achilles",
        "crippling them",
    ],
    "right_foot": [
        "slicing through the boot",
        "severing the Achilles",
        "crippling them",
    ],
}

# =============================================================================
# BLUNT TRAUMA DESCRIPTIONS
# =============================================================================

BLUNT_WOUNDS = {
    "head": [
        "with a skull-rattling crack",
        "leaving them seeing double",
        "with a sound like a melon dropped on concrete",
        "cratering their temple",
    ],
    "face": [
        "shattering their nose in a spray of blood",
        "caving in their cheekbone",
        "rearranging their features",
        "knocking teeth loose",
    ],
    "left_eye": [
        "swelling the socket shut instantly",
        "bursting blood vessels",
    ],
    "right_eye": [
        "swelling the socket shut instantly",
        "bursting blood vessels",
    ],
    "chest": [
        "with a rib-cracking impact",
        "driving the wind from their lungs",
        "with enough force to stop their heart",
        "caving in their sternum",
    ],
    "back": [
        "bruising the kidneys",
        "threatening the spine",
        "with a vertebrae-threatening crack",
    ],
    "abdomen": [
        "rupturing something internal",
        "making them vomit blood",
        "folding them in half",
    ],
    "groin": [
        "ending any chance of a good day",
        "with fight-ending precision",
        "making them wish for death",
    ],
    "left_arm": [
        "snapping bone audibly",
        "leaving the limb hanging wrong",
        "with a compound-fracture crack",
    ],
    "right_arm": [
        "snapping bone audibly",
        "leaving the limb hanging wrong",
        "with a compound-fracture crack",
    ],
    "left_hand": [
        "crushing small bones to powder",
        "shattering knuckles",
        "pulping the palm",
    ],
    "right_hand": [
        "crushing small bones to powder",
        "shattering knuckles",
        "pulping the palm",
    ],
    "left_thigh": [
        "dead-legging them instantly",
        "with a femur-threatening impact",
        "charley-horsing the muscle to uselessness",
    ],
    "right_thigh": [
        "dead-legging them instantly",
        "with a femur-threatening impact",
        "charley-horsing the muscle to uselessness",
    ],
    "left_shin": [
        "with a shin-splitting crack",
        "shattering the tibia",
        "making them collapse",
    ],
    "right_shin": [
        "with a shin-splitting crack",
        "shattering the tibia",
        "making them collapse",
    ],
    "left_foot": [
        "crushing metatarsals",
        "stomping through the boot",
        "shattering the ankle",
    ],
    "right_foot": [
        "crushing metatarsals",
        "stomping through the boot",
        "shattering the ankle",
    ],
}

# =============================================================================
# KILL DESCRIPTIONS BY BODY PART
# =============================================================================

KILL_DESCRIPTIONS = {
    "head": [
        "Their skull caves in and they drop like a puppet with cut strings.",
        "The light leaves their eyes before they hit the ground.",
        "Brain matter paints the wall behind them.",
        "They collapse, twitching, as life abandons the wreckage of their head.",
    ],
    "face": [
        "What's left of their face slides off the bone as they crumple.",
        "They fall with a wet gurgle, face unrecognizable.",
        "The ruin that was their face hits the ground first.",
    ],
    "left_eye": [
        "The blow penetrates deep into the brain. They're dead before they know it.",
    ],
    "right_eye": [
        "The blow penetrates deep into the brain. They're dead before they know it.",
    ],
    "chest": [
        "Their heart explodes in their chest. They look surprised as they fall.",
        "A wet, sucking sound, then silence. They don't get back up.",
        "Ribs pierce lungs. They drown in their own blood before hitting the floor.",
        "The light fades from their eyes as their chest stops moving.",
    ],
    "back": [
        "Their spine severs. They fold backward at an impossible angle.",
        "They drop face-first, paralyzed and dying.",
    ],
    "abdomen": [
        "Their guts spill in a steaming pile. They die screaming.",
        "Something ruptures inside. They bleed out in seconds.",
        "They collapse clutching their ruined midsection, life pooling around them.",
    ],
    "groin": [
        "The femoral artery opens like a faucet. They're dead in seconds.",
        "They bleed out from the worst possible wound, whimpering until they stop.",
    ],
    "left_arm": [
        "The brachial artery sprays like a fountain. They're pale in seconds, dead in moments.",
    ],
    "right_arm": [
        "The brachial artery sprays like a fountain. They're pale in seconds, dead in moments.",
    ],
    "left_hand": [
        "Shock takes them - an inglorious end to an unremarkable life.",
    ],
    "right_hand": [
        "Shock takes them - an inglorious end to an unremarkable life.",
    ],
    "left_thigh": [
        "The femoral artery opens. They're dead before they understand what happened.",
        "They bleed out in a spreading pool, life leaving with every heartbeat.",
    ],
    "right_thigh": [
        "The femoral artery opens. They're dead before they understand what happened.",
        "They bleed out in a spreading pool, life leaving with every heartbeat.",
    ],
    "left_shin": [
        "Shock and blood loss take them. They die confused and cold.",
    ],
    "right_shin": [
        "Shock and blood loss take them. They die confused and cold.",
    ],
    "left_foot": [
        "Shock claims them. An undignified end.",
    ],
    "right_foot": [
        "Shock claims them. An undignified end.",
    ],
}

# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def get_body_part_category(location):
    """
    Get the category a body part belongs to.
    
    Args:
        location (str): Body location
        
    Returns:
        str: Category name (head, torso, arm, leg) or 'torso' as default
    """
    location = location.lower().replace(" ", "_")
    
    if location in HEAD_PARTS:
        return "head"
    elif location in TORSO_PARTS:
        return "torso"
    elif location in ARM_PARTS:
        return "arm"
    elif location in LEG_PARTS:
        return "leg"
    return "torso"  # Default


def get_impact_description(location):
    """
    Get a random impact description for a body part.
    
    Args:
        location (str): Body location
        
    Returns:
        str: Impact description or empty string
    """
    location = location.lower().replace(" ", "_")
    descriptions = IMPACT_DESCRIPTIONS.get(location, [])
    return random.choice(descriptions) if descriptions else ""


def get_wound_description(location, wound_type="blunt"):
    """
    Get a random wound description for a specific body part and wound type.
    
    Args:
        location (str): Body location
        wound_type (str): Type of wound (bullet, blade, blunt)
        
    Returns:
        str: Wound description
    """
    location = location.lower().replace(" ", "_")
    
    if wound_type in ("bullet", "projectile", "shot", "gunshot"):
        wounds = BULLET_WOUNDS
    elif wound_type in ("blade", "cut", "slash", "stab"):
        wounds = BLADE_WOUNDS
    else:
        wounds = BLUNT_WOUNDS
    
    descriptions = wounds.get(location, wounds.get("chest", []))
    return random.choice(descriptions) if descriptions else ""


def get_kill_description(location):
    """
    Get a random kill description for a body part.
    
    Args:
        location (str): Body location
        
    Returns:
        str: Kill description
    """
    location = location.lower().replace(" ", "_")
    descriptions = KILL_DESCRIPTIONS.get(location, KILL_DESCRIPTIONS.get("chest", []))
    return random.choice(descriptions) if descriptions else "They fall and don't get back up."


def is_vital_hit(location):
    """
    Check if a hit location is a vital area.
    
    Args:
        location (str): Body location
        
    Returns:
        bool: True if vital area
    """
    location = location.lower().replace(" ", "_")
    return location in VITAL_AREAS


def format_location_for_display(location):
    """
    Format a body location for display in messages.
    
    Args:
        location (str): Body location (e.g., 'left_arm')
        
    Returns:
        str: Formatted location (e.g., 'left arm')
    """
    return location.replace("_", " ").lower()


# =============================================================================
# DAMAGE TYPE MAPPINGS
# =============================================================================

# Map weapon types to wound categories
WEAPON_TO_WOUND_TYPE = {
    # Ranged - bullets
    "light_pistol": "bullet",
    "heavy_pistol": "bullet",
    "pump-action_shotgun": "bullet",
    "break-action_shotgun": "bullet",
    "assault_rifle": "bullet",
    "bolt-action_rifle": "bullet",
    "smg": "bullet",
    "submachine_gun": "bullet",
    "heavy_revolver": "bullet",
    "light_revolver": "bullet",
    "machine_pistol": "bullet",
    "semi-auto_rifle": "bullet",
    "semi-auto_shotgun": "bullet",
    "lever-action_rifle": "bullet",
    "lever-action_shotgun": "bullet",
    "heavy_machine_gun": "bullet",
    "anti-material_rifle": "bullet",
    "sniper_rifle": "bullet",
    "nail_gun": "bullet",
    
    # Blades
    "katana": "blade",
    "knife": "blade",
    "combat_knife": "blade",
    "machete": "blade",
    "sword": "blade",
    "long_sword": "blade",
    "kukri": "blade",
    "gladius": "blade",
    "rapier": "blade",
    "cutlass": "blade",
    "scimitar": "blade",
    "falchion": "blade",
    "claymore": "blade",
    "small_knife": "blade",
    "box_cutter": "blade",
    "straight_razor": "blade",
    "scalpel": "blade",
    "meat_cleaver": "blade",
    "shiv": "blade",
    "glass_shard": "blade",
    "mirror_shard": "blade",
    "broken_bottle": "blade",
    "ice_pick": "blade",
    "garden_shears": "blade",
    
    # Axes (hybrid blade/blunt)
    "hatchet": "blade",
    "fire_axe": "blade",
    "small_axe": "blade",
    "large_axe": "blade",
    "battle_axe": "blade",
    "throwing_axe": "blade",
    
    # Blunt
    "unarmed": "blunt",
    "baseball_bat": "blunt",
    "cricket_bat": "blunt",
    "baton": "blunt",
    "nightstick": "blunt",
    "crowbar": "blunt",
    "pipe": "blunt",
    "pipe_wrench": "blunt",
    "tire_iron": "blunt",
    "hammer": "blunt",
    "sledgehammer": "blunt",
    "metal_club": "blunt",
    "brass_knuckles": "blunt",
    "nunchaku": "blunt",
    "staff": "blunt",
    "pool_cue": "blunt",
    "brick": "blunt",
    "rock": "blunt",
    "rebar": "blunt",
    "shovel": "blunt",
    "bokken": "blunt",
    "nail_bat": "blunt",
    "nailed_board": "blunt",
    "chain": "blunt",
    "whip": "blunt",
    "phonebook": "blunt",
    "cellphone": "blunt",
    "tennis_racket": "blunt",
    
    # Special
    "flamethrower": "blunt",  # Burns treated as blunt trauma for messages
    "stun_gun": "blunt",
    "spraycan": "blunt",
}


def get_wound_type_for_weapon(weapon_type):
    """
    Get the wound type category for a weapon type.
    
    Args:
        weapon_type (str): Weapon type identifier
        
    Returns:
        str: Wound type (bullet, blade, blunt)
    """
    return WEAPON_TO_WOUND_TYPE.get(weapon_type, "blunt")
