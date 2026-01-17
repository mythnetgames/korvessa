"""
Survival Core System

Implements hunger, thirst, intoxication tracking and effects.
"""

import time
import random
import re

# =============================================================================
# CONSTANTS
# =============================================================================

# Time constants (in seconds)
SECONDS_PER_DAY = 86400
MEAL_REQUIREMENT_HOURS = 24  # Need to eat once per 24 hours
DRINK_REQUIREMENT_HOURS = 12  # Need to drink twice per day (every 12 hours)
NUTRITION_BONUS_DURATION = 7200  # 2 hours in seconds
SOBERING_INTERVAL = 300  # Check sobering every 5 minutes
INTOXICATION_DECAY_RATE = 5  # Points of intoxication lost per interval

# Starvation kicks in after 3 consecutive login days without eating
STARVATION_DAYS_THRESHOLD = 3

# Intoxication tiers - each tier has threshold, speech effects, stat maluses
INTOXICATION_TIERS = {
    "sober": {
        "threshold": 0,
        "slur_chance": 0.0,
        "hiccup_chance": 0.0,
        "stat_malus": {},
        "description": "sober"
    },
    "tipsy": {
        "threshold": 20,
        "slur_chance": 0.1,
        "hiccup_chance": 0.05,
        "stat_malus": {},
        "description": "slightly tipsy"
    },
    "buzzed": {
        "threshold": 40,
        "slur_chance": 0.25,
        "hiccup_chance": 0.1,
        "stat_malus": {"dexterity": -1},
        "description": "buzzed"
    },
    "drunk": {
        "threshold": 60,
        "slur_chance": 0.5,
        "hiccup_chance": 0.2,
        "stat_malus": {"dexterity": -2, "intellect": -1},
        "description": "drunk"
    },
    "very_drunk": {
        "threshold": 80,
        "slur_chance": 0.75,
        "hiccup_chance": 0.3,
        "stat_malus": {"dexterity": -3, "intellect": -2, "strength": -1},
        "description": "very drunk"
    },
    "wasted": {
        "threshold": 100,
        "slur_chance": 0.9,
        "hiccup_chance": 0.4,
        "stat_malus": {"dexterity": -4, "intellect": -3, "strength": -2},
        "liver_damage": 2,  # HP damage to liver per sobering interval
        "description": "completely wasted"
    },
    "alcohol_poisoning": {
        "threshold": 150,
        "slur_chance": 1.0,
        "hiccup_chance": 0.5,
        "stat_malus": {"dexterity": -5, "intellect": -4, "strength": -3, "constitution": -2},
        "liver_damage": 5,  # Severe liver damage
        "description": "suffering from alcohol poisoning"
    }
}

# Hunger ambient messages
HUNGER_MESSAGES = [
    "Your stomach growls loudly.",
    "You feel a gnawing emptiness in your belly.",
    "Your thoughts keep drifting to food.",
    "A wave of hunger washes over you.",
    "You find yourself thinking about your last meal.",
    "Your stomach clenches with hunger pangs.",
    "The smell of food from somewhere nearby makes your mouth water.",
    "You feel lightheaded from lack of food.",
    "Your hands tremble slightly from hunger.",
    "You struggle to focus through the hunger.",
]

# Thirst ambient messages
THIRST_MESSAGES = [
    "Your throat feels dry and scratchy.",
    "You lick your parched lips.",
    "You could really use something to drink.",
    "A wave of thirst washes over you.",
    "Your mouth feels like sandpaper.",
    "You swallow, trying to moisten your dry throat.",
    "You find yourself thinking about cool, refreshing water.",
    "Your head pounds from dehydration.",
    "You feel sluggish from thirst.",
    "Your lips are cracked and dry.",
]

# Hiccup variations
HICCUP_MESSAGES = [
    "*hic*",
    "*HIC*",
    "-hic-",
    "...hic...",
    "*hiccup*",
]


# =============================================================================
# DEBUG MESSAGING
# =============================================================================

def _send_debug_message(msg):
    """Send a debug message to the 'feasting' channel."""
    try:
        from evennia.comms.models import ChannelDB
        channel = ChannelDB.objects.filter(db_key__iexact="feasting").first()
        if channel:
            channel.msg(f"|y[DEBUG]|n {msg}", keep_log=False)
    except Exception:
        pass  # Fail silently if channel doesn't exist

# =============================================================================
# STATE MANAGEMENT
# =============================================================================

def get_survival_state(character):
    """
    Get or initialize the survival state for a character.
    
    Returns a dict with:
        - last_meal_time: timestamp of last meal
        - last_drink_time: timestamp of last drink
        - intoxication: current intoxication level (0-200)
        - nutrition_bonus_until: timestamp when nutrition bonus expires
        - login_days_without_food: consecutive login days without eating
        - last_login_date: date string of last login for tracking
    """
    if not hasattr(character, 'db'):
        return None
    
    # Initialize if not present
    if not character.db.survival_state:
        character.db.survival_state = {
            "last_meal_time": time.time(),  # Start fed
            "last_drink_time": time.time(),  # Start hydrated
            "intoxication": 0,
            "nutrition_bonus_until": 0,
            "login_days_without_food": 0,
            "last_login_date": None,
        }
    
    return character.db.survival_state


def save_survival_state(character, state):
    """Save survival state to character."""
    if hasattr(character, 'db'):
        character.db.survival_state = state


# =============================================================================
# CONSTITUTION MODIFIER
# =============================================================================

def _get_constitution_modifier(character):
    """
    Get a Constitution-based time modifier for hunger/thirst.
    Higher CON = can go longer without food/drink.
    Dwarves get an additional 0.5x multiplier on top of this.
    
    CON 0:   1.0x (normal - go hungry in 24h)
    CON 50:  1.0x (normal baseline)
    CON 100: 1.5x (50% longer between meals)
    
    Dwarf racial bonus: x0.5 (e.g., 1.0x becomes 0.5x, so they go hungry in 12h instead of 24h)
    
    Returns:
        float: multiplier for hunger/thirst timers
    """
    try:
        # Try to get Constitution stat
        con = getattr(character, 'con', None) or getattr(character.db, 'con', None) or 50
        con = max(0, min(100, con))  # Clamp to 0-100
        
        # Formula: 1.0 + (CON - 50) * 0.01 = 1.0 to 1.5
        modifier = 1.0 + ((con - 50) * 0.01)
        
        # Dwarf racial bonus: need hunger/thirst twice as often (0.5x multiplier)
        race = getattr(character, 'race', 'human').lower()
        if race == 'dwarf':
            modifier *= 0.5
        
        return modifier
    except Exception:
        return 1.0  # Default to normal


# =============================================================================
# HUNGER & THIRST TRACKING
# =============================================================================

def record_meal(character, nutritious=False):
    """
    Record that the character has eaten.
    
    Args:
        character: The character who ate
        nutritious: If True, grants 2-hour health bonus
        
    Returns:
        dict with meal info
    """
    state = get_survival_state(character)
    if not state:
        return {"error": "No survival state"}
    
    current_time = time.time()
    state["last_meal_time"] = current_time
    state["login_days_without_food"] = 0  # Reset starvation counter
    
    result = {"fed": True}
    
    # Send debug message to feasting channel
    con_modifier = _get_constitution_modifier(character)
    debug_msg = f"[MEAL] {character.name} ate (nutritious={nutritious}, CON_mod={con_modifier:.2f})"
    _send_debug_message(debug_msg)
    
    # Apply nutrition bonus for nutritious food
    if nutritious:
        state["nutrition_bonus_until"] = current_time + NUTRITION_BONUS_DURATION
        result["nutrition_bonus"] = True
        result["bonus_duration"] = NUTRITION_BONUS_DURATION
        
        # Nutritious food helps sober 2x faster
        if state["intoxication"] > 0:
            # Apply extra sobering
            state["intoxication"] = max(0, state["intoxication"] - INTOXICATION_DECAY_RATE)
            result["helped_sober"] = True
    
    save_survival_state(character, state)
    return result


def record_drink(character, is_alcohol=False, alcohol_strength=0):
    """
    Record that the character has had a drink.
    
    Args:
        character: The character who drank
        is_alcohol: If True, adds intoxication
        alcohol_strength: Amount of intoxication to add (0-50 typical)
        
    Returns:
        dict with drink info
    """
    state = get_survival_state(character)
    if not state:
        return {"error": "No survival state"}
    
    current_time = time.time()
    state["last_drink_time"] = current_time
    
    result = {"hydrated": True}
    
    # Send debug message to feasting channel
    con_modifier = _get_constitution_modifier(character)
    debug_msg = f"[DRINK] {character.name} drank (alcohol={is_alcohol}, strength={alcohol_strength}, CON_mod={con_modifier:.2f})"
    _send_debug_message(debug_msg)
    
    # Handle alcohol
    if is_alcohol and alcohol_strength > 0:
        old_level = state["intoxication"]
        state["intoxication"] = min(200, state["intoxication"] + alcohol_strength)
        new_level = state["intoxication"]
        
        old_tier = get_intoxication_tier(old_level)
        new_tier = get_intoxication_tier(new_level)
        
        result["intoxication_added"] = alcohol_strength
        result["intoxication_level"] = new_level
        result["tier_changed"] = old_tier != new_tier
        result["new_tier"] = new_tier
    
    save_survival_state(character, state)
    return result


def is_hungry(character):
    """Check if character needs to eat (more than 24 hours since last meal)."""
    state = get_survival_state(character)
    if not state:
        return False
    
    con_modifier = _get_constitution_modifier(character)
    time_since_meal = time.time() - state.get("last_meal_time", time.time())
    return time_since_meal > (MEAL_REQUIREMENT_HOURS * 3600 * con_modifier)


def is_thirsty(character):
    """Check if character needs to drink (more than 12 hours since last drink)."""
    state = get_survival_state(character)
    if not state:
        return False
    
    con_modifier = _get_constitution_modifier(character)
    time_since_drink = time.time() - state.get("last_drink_time", time.time())
    return time_since_drink > (DRINK_REQUIREMENT_HOURS * 3600 * con_modifier)


def is_starving(character):
    """
    Check if character is starving (3+ consecutive login days without eating).
    """
    state = get_survival_state(character)
    if not state:
        return False
    
    return state.get("login_days_without_food", 0) >= STARVATION_DAYS_THRESHOLD


def is_dehydrated(character):
    """
    Check if character is severely dehydrated (more than 24 hours without drink).
    """
    state = get_survival_state(character)
    if not state:
        return False
    
    time_since_drink = time.time() - state.get("last_drink_time", time.time())
    return time_since_drink > (24 * 3600)  # 24 hours without drinking


def update_login_tracking(character):
    """
    Update login tracking for starvation system.
    Call this when a character logs in.
    """
    state = get_survival_state(character)
    if not state:
        return
    
    import datetime
    today = datetime.date.today().isoformat()
    last_login = state.get("last_login_date")
    
    if last_login != today:
        # New day login
        if is_hungry(character):
            # Increment days without food
            state["login_days_without_food"] = state.get("login_days_without_food", 0) + 1
        else:
            # They ate today (before this login check)
            state["login_days_without_food"] = 0
        
        state["last_login_date"] = today
        save_survival_state(character, state)


# =============================================================================
# INTOXICATION SYSTEM
# =============================================================================

def get_intoxication_level(character):
    """Get current intoxication level (0-200)."""
    state = get_survival_state(character)
    if not state:
        return 0
    return state.get("intoxication", 0)


def get_intoxication_tier(level):
    """
    Get the intoxication tier name for a given level.
    
    Returns tier name string.
    """
    if level >= INTOXICATION_TIERS["alcohol_poisoning"]["threshold"]:
        return "alcohol_poisoning"
    elif level >= INTOXICATION_TIERS["wasted"]["threshold"]:
        return "wasted"
    elif level >= INTOXICATION_TIERS["very_drunk"]["threshold"]:
        return "very_drunk"
    elif level >= INTOXICATION_TIERS["drunk"]["threshold"]:
        return "drunk"
    elif level >= INTOXICATION_TIERS["buzzed"]["threshold"]:
        return "buzzed"
    elif level >= INTOXICATION_TIERS["tipsy"]["threshold"]:
        return "tipsy"
    else:
        return "sober"


def add_intoxication(character, amount):
    """
    Add intoxication to a character.
    
    Args:
        character: The character
        amount: Amount to add (positive)
        
    Returns:
        dict with new level and tier info
    """
    state = get_survival_state(character)
    if not state:
        return {"error": "No survival state"}
    
    old_level = state.get("intoxication", 0)
    old_tier = get_intoxication_tier(old_level)
    
    new_level = min(200, old_level + amount)
    state["intoxication"] = new_level
    new_tier = get_intoxication_tier(new_level)
    
    save_survival_state(character, state)
    
    return {
        "old_level": old_level,
        "new_level": new_level,
        "old_tier": old_tier,
        "new_tier": new_tier,
        "tier_changed": old_tier != new_tier
    }


def _get_intoxication_decay_multiplier(character):
    """
    Get the intoxication decay multiplier for a character.
    Dwarves sober up more slowly (0.5x rate, so it takes 2x as long).
    
    Returns:
        float: multiplier for decay rate
    """
    try:
        race = getattr(character, 'race', 'human').lower()
        if race == 'dwarf':
            return 0.5  # 50% slower sobering
        return 1.0
    except Exception:
        return 1.0


def process_sobering(character):
    """
    Process sobering over time. Call periodically.
    Dwarves sober up more slowly (take 2x as long).
    
    Returns:
        dict with sobering info and any effects applied
    """
    state = get_survival_state(character)
    if not state:
        return {"error": "No survival state"}
    
    old_level = state.get("intoxication", 0)
    if old_level <= 0:
        return {"already_sober": True}
    
    old_tier = get_intoxication_tier(old_level)
    tier_data = INTOXICATION_TIERS.get(old_tier, {})
    
    result = {"old_level": old_level, "old_tier": old_tier}
    
    # Check for nutrition bonus (2x faster sobering)
    has_bonus = has_nutrition_bonus(character)
    decay_multiplier = 2 if has_bonus else 1
    
    # Apply dwarf modifier (0.5x = slower sobering)
    decay_multiplier *= _get_intoxication_decay_multiplier(character)
    
    decay_amount = INTOXICATION_DECAY_RATE * decay_multiplier
    
    # Apply decay
    new_level = max(0, old_level - decay_amount)
    state["intoxication"] = new_level
    new_tier = get_intoxication_tier(new_level)
    
    result["new_level"] = new_level
    result["new_tier"] = new_tier
    result["tier_changed"] = old_tier != new_tier
    result["decay_amount"] = decay_amount
    result["nutrition_bonus_active"] = has_bonus
    
    # Apply liver damage if at dangerous tiers
    liver_damage = tier_data.get("liver_damage", 0)
    if liver_damage > 0:
        result["liver_damage"] = _apply_liver_damage(character, liver_damage)
    
    save_survival_state(character, state)
    return result


def clear_intoxication(character):
    """
    Clear all intoxication (used by healing).
    """
    state = get_survival_state(character)
    if not state:
        return
    
    state["intoxication"] = 0
    save_survival_state(character, state)


def _apply_liver_damage(character, damage):
    """
    Apply damage to the character's liver organ.
    
    Returns:
        dict with damage info
    """
    try:
        if not hasattr(character, 'medical_state') or not character.medical_state:
            return {"error": "No medical state"}
        
        medical_state = character.medical_state
        if "liver" not in medical_state.organs:
            return {"error": "No liver organ"}
        
        liver = medical_state.organs["liver"]
        old_hp = liver.current_hp
        liver.current_hp = max(0, liver.current_hp - damage)
        new_hp = liver.current_hp
        
        character.save_medical_state()
        
        return {
            "damage_dealt": damage,
            "old_hp": old_hp,
            "new_hp": new_hp,
            "liver_destroyed": new_hp <= 0
        }
    except Exception as e:
        return {"error": str(e)}


# =============================================================================
# NUTRITION BONUS
# =============================================================================

def add_nutrition_bonus(character, duration=NUTRITION_BONUS_DURATION):
    """
    Add nutrition bonus (health regen) to character.
    
    Args:
        character: The character
        duration: Duration in seconds (default 2 hours)
    """
    state = get_survival_state(character)
    if not state:
        return
    
    state["nutrition_bonus_until"] = time.time() + duration
    save_survival_state(character, state)


def has_nutrition_bonus(character):
    """Check if character currently has nutrition bonus active."""
    state = get_survival_state(character)
    if not state:
        return False
    
    bonus_until = state.get("nutrition_bonus_until", 0)
    return time.time() < bonus_until


def get_nutrition_bonus_remaining(character):
    """Get remaining seconds of nutrition bonus."""
    state = get_survival_state(character)
    if not state:
        return 0
    
    bonus_until = state.get("nutrition_bonus_until", 0)
    remaining = bonus_until - time.time()
    return max(0, remaining)


# =============================================================================
# SPEECH PROCESSING (SLURRING)
# =============================================================================

def slur_speech(character, text):
    """
    Process speech text to add slurring based on intoxication level.
    
    Args:
        character: The speaking character
        text: Original speech text
        
    Returns:
        str: Potentially slurred text
    """
    level = get_intoxication_level(character)
    if level <= 0:
        return text
    
    tier = get_intoxication_tier(level)
    tier_data = INTOXICATION_TIERS.get(tier, {})
    
    slur_chance = tier_data.get("slur_chance", 0)
    hiccup_chance = tier_data.get("hiccup_chance", 0)
    
    if slur_chance <= 0 and hiccup_chance <= 0:
        return text
    
    # Process the text
    result = []
    words = text.split()
    
    for i, word in enumerate(words):
        processed_word = word
        
        # Apply slurring to individual words
        if random.random() < slur_chance:
            processed_word = _slur_word(word, slur_chance)
        
        # Potentially insert hiccup
        if random.random() < hiccup_chance:
            hiccup = random.choice(HICCUP_MESSAGES)
            # Insert hiccup before or after word
            if random.random() < 0.5:
                processed_word = f"{hiccup} {processed_word}"
            else:
                processed_word = f"{processed_word} {hiccup}"
        
        result.append(processed_word)
    
    return ' '.join(result)


def _slur_word(word, intensity):
    """
    Apply slurring effects to a single word.
    
    Effects based on intensity:
    - Letter duplication (sssso)
    - Letter swapping
    - Dropped letters
    - s -> sh transformation
    """
    if len(word) < 2:
        return word
    
    # Don't slur short common words
    if word.lower() in ["i", "a", "an", "the", "to", "of", "is", "it"]:
        return word
    
    result = list(word)
    
    # s -> sh transformation (common drunk slur)
    if random.random() < intensity * 0.5:
        for i, char in enumerate(result):
            if char.lower() == 's' and random.random() < 0.5:
                result[i] = 'sh' if char == 's' else 'Sh'
    
    # Letter duplication
    if random.random() < intensity * 0.3 and len(result) > 2:
        idx = random.randint(0, len(result) - 1)
        if result[idx].isalpha():
            result[idx] = result[idx] * random.randint(2, 3)
    
    # Dropped letters (only at high intensity)
    if intensity > 0.5 and random.random() < intensity * 0.2 and len(result) > 3:
        idx = random.randint(1, len(result) - 2)
        result[idx] = ''
    
    return ''.join(result)


# =============================================================================
# SURVIVAL EFFECTS CHECK
# =============================================================================

def check_survival_effects(character):
    """
    Check and return current survival effects on the character.
    
    Returns:
        dict with all current effects
    """
    effects = {
        "hungry": is_hungry(character),
        "thirsty": is_thirsty(character),
        "starving": is_starving(character),
        "dehydrated": is_dehydrated(character),
        "intoxication_level": get_intoxication_level(character),
        "intoxication_tier": get_intoxication_tier(get_intoxication_level(character)),
        "has_nutrition_bonus": has_nutrition_bonus(character),
        "stat_maluses": {},
        "health_effects": [],
        "stamina_effects": [],
    }
    
    # Get intoxication stat maluses
    tier = effects["intoxication_tier"]
    tier_data = INTOXICATION_TIERS.get(tier, {})
    effects["stat_maluses"] = tier_data.get("stat_malus", {}).copy()
    
    # Starvation effects
    if effects["starving"]:
        effects["health_effects"].append("lowered_max_health")
        effects["stat_maluses"]["constitution"] = effects["stat_maluses"].get("constitution", 0) - 2
    
    # Dehydration effects
    if effects["dehydrated"]:
        effects["stamina_effects"].append("lowered_stamina_regen")
        effects["stamina_effects"].append("lowered_stamina_pool")
    
    # Thirst effects (milder)
    if effects["thirsty"] and not effects["dehydrated"]:
        effects["stamina_effects"].append("reduced_stamina_regen")
    
    return effects


def get_random_hunger_message():
    """Get a random hunger ambient message."""
    return random.choice(HUNGER_MESSAGES)


def get_random_thirst_message():
    """Get a random thirst ambient message."""
    return random.choice(THIRST_MESSAGES)


# =============================================================================
# HEALING INTEGRATION
# =============================================================================

def on_character_healed(character):
    """
    Called when a character is healed by admin or medical treatment.
    Clears intoxication effects.
    """
    clear_intoxication(character)
