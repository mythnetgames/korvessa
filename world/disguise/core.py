"""
Disguise System Core Module

Handles identity concealment, slip mechanics, and observer recognition.

Identity Display Priority (from highest to lowest):
1. True name (if a slip/break just occurred and not corrected)
2. Active disguise display name (if skill disguise intact)
3. Active disguise anonymity descriptor
4. Item-based anonymity descriptor (hood up, mask on, etc.)
5. True name (fallback)
"""

import random
from world.combat.constants import (
    ANONYMITY_KEYWORDS,
    ANONYMITY_DESCRIPTORS,
    DEFAULT_ANONYMITY_DESCRIPTOR,
    DISGUISE_STABILITY_MAX,
    DISGUISE_STABILITY_UNSTABLE,
    DISGUISE_STABILITY_BROKEN,
    SLIP_CHANCE_COMBAT,
    SLIP_CHANCE_SHOVE,
    SLIP_CHANCE_RUN,
    SLIP_CHANCE_SCRUTINY,
    SLIP_CHANCE_EMOTE_BASE,
    SLIP_CHANCE_EMOTE_INCREMENT,
    DISGUISE_SKILL_MODIFIER,
    STABILITY_DAMAGE_COMBAT,
    STABILITY_DAMAGE_HIT,
    STABILITY_DAMAGE_CRITICAL,
    STABILITY_DAMAGE_SCRUTINY,
    STABILITY_DAMAGE_ENVIRONMENT,
    RECOGNITION_BONUS_KNOWS_IDENTITY,
    RECOGNITION_BONUS_CLOSE_CONTACT,
    RECOGNITION_BONUS_VOICE,
    NDB_EMOTE_COUNT_SINCE_ADJUST,
    NDB_IDENTITY_SLIPPED,
    DB_ACTIVE_DISGUISE,
    DB_KNOWN_IDENTITIES,
    DB_DISGUISE_PROFILES,
    MSG_ITEM_SLIP_SELF,
    MSG_ITEM_SLIP_ROOM,
    MSG_ITEM_ADJUSTED,
    MSG_ITEM_ADJUSTED_ROOM,
    MSG_DISGUISE_PARTIAL_SELF,
    MSG_DISGUISE_PARTIAL_ROOM,
    MSG_DISGUISE_BREAK_SELF,
    MSG_DISGUISE_BREAK_ROOM,
    MSG_RECOGNIZED,
)


# ===================================================================
# DISGUISE CLOTHING DETECTION
# ===================================================================

DISGUISE_CLOTHING_KEYWORDS = {
    # Face masks and coverings
    "mask", "masks", "blindfold", "veil", "patch",
    
    # Eye wear
    "glasses", "shades", "sunglasses", "goggles", "contacts", "contact",
    
    # Head coverings
    "hood", "hoodie", "hoodies", "cowl", "cowls", "wig", "wigs", "hat",
    "helmet", "beret", "cap", "turban", "headwrap", "headscarf", "wimple",
    "bonnet", "fascinator", "snood", "coif", "pillbox", "fedora", "bowler",
    "tophat", "sombrero", "balaclava", "ski mask",
    
    # Face wrappings
    "bandage", "bandages", "wrap", "wraps", "scarf", "kerchief"
}


def count_disguise_clothing(character):
    """
    Count valid disguise clothing items worn by character.
    
    Disguise clothing includes items like hoods, masks, glasses, scarves, etc.
    Max 2 items per body location (head nakeds, torso nakeds, etc).
    
    Args:
        character: The character to check
        
    Returns:
        int: Number of valid disguise clothing items (capped at 2 per location)
    """
    if not hasattr(character, "db") or not hasattr(character.db, "worn_items"):
        return 0
    
    worn_items = character.db.worn_items or {}
    clothing_count_by_location = {}
    total_count = 0
    
    for location, items_at_location in worn_items.items():
        location_count = 0
        for item in items_at_location:
            if not item:
                continue
            
            # Check if item name contains disguise clothing keywords
            item_key_lower = item.key.lower()
            is_disguise_clothing = any(keyword in item_key_lower for keyword in DISGUISE_CLOTHING_KEYWORDS)
            
            if is_disguise_clothing and location_count < 2:
                location_count += 1
                total_count += 1
        
        if location_count > 0:
            clothing_count_by_location[location] = location_count
    
    return total_count


# ===================================================================
# ITEM-BASED ANONYMITY
# ===================================================================

def _item_covers_face(item):
    """
    Check if an item covers the face location.
    
    Args:
        item: The item to check
        
    Returns:
        bool: True if item covers face
    """
    # Check explicit coverage attribute
    coverage = getattr(item.db, "coverage", None)
    if coverage:
        if isinstance(coverage, (list, tuple, set)):
            return "face" in coverage
        # Handle AttributeProperty or other attribute types
        return "face" in str(coverage).lower()
    
    # Fallback to method if available
    if hasattr(item, "get_current_coverage"):
        try:
            coverage = item.get_current_coverage()
            return "face" in coverage
        except:
            pass
    
    return False


def get_anonymity_item(character):
    """
    Get the currently active anonymity-providing item on a character.
    
    Checks worn items for anonymity capability (hood up, mask on, etc.)
    Only items that cover the FACE can provide anonymity.
    
    Args:
        character: The character to check
        
    Returns:
        tuple: (item, descriptor) or (None, None) if no anonymity active
    """
    # Get all worn items from character's worn_items tracking
    worn_items = []
    
    # Method 1: Check character's worn_items database tracking (primary)
    if hasattr(character.db, "worn_items") and character.db.worn_items:
        for location, items_at_location in character.db.worn_items.items():
            for item in items_at_location:
                if item and item not in worn_items:
                    worn_items.append(item)
    
    # Method 2: Fallback to checking currently_worn attribute (legacy support)
    for obj in character.contents:
        if obj not in worn_items and hasattr(obj, "db") and getattr(obj.db, "currently_worn", False):
            worn_items.append(obj)
    
    # Check each item for anonymity capability
    for item in worn_items:
        # CRITICAL: Item must cover FACE to provide anonymity
        if not _item_covers_face(item):
            continue
        
        # Check if item explicitly provides anonymity
        if getattr(item.db, "provides_anonymity", False):
            # Check if anonymity is currently active (e.g., hood is up)
            if getattr(item.db, "anonymity_active", False):
                descriptor = getattr(item.db, "anonymity_descriptor", None)
                if not descriptor:
                    descriptor = _get_descriptor_from_name(item.key)
                return (item, descriptor)
        
        # Check by item name keywords if no explicit flag
        item_name_lower = item.key.lower()
        for keyword in ANONYMITY_KEYWORDS:
            if keyword in item_name_lower:
                # Check style properties for hood/mask state
                style_props = getattr(item.db, "style_properties", {})
                if style_props:
                    # Check if hood is up (adjustable: rolled means hood up for hoodies)
                    adj_state = style_props.get("adjustable", "normal")
                    if adj_state == "rolled" or getattr(item.db, "anonymity_active", False):
                        descriptor = _get_descriptor_from_name(item.key)
                        return (item, descriptor)
                # For items without style system, check explicit flag
                elif getattr(item.db, "anonymity_active", False):
                    descriptor = _get_descriptor_from_name(item.key)
                    return (item, descriptor)
    
    return (None, None)


def _get_descriptor_from_name(item_name):
    """
    Get anonymity descriptor based on item name keywords.
    
    Args:
        item_name: The item name to check
        
    Returns:
        str: Appropriate anonymity descriptor
    """
    item_lower = item_name.lower()
    for keyword, descriptor in ANONYMITY_DESCRIPTORS.items():
        if keyword in item_lower:
            return descriptor
    return DEFAULT_ANONYMITY_DESCRIPTOR


def check_item_anonymity(character):
    """
    Check if character has active item-based anonymity.
    
    Args:
        character: The character to check
        
    Returns:
        bool: True if anonymity is active
    """
    item, descriptor = get_anonymity_item(character)
    return item is not None


def get_anonymity_descriptor(character):
    """
    Get the anonymity descriptor for a character if any.
    
    Args:
        character: The character to check
        
    Returns:
        str or None: Descriptor like 'a hooded figure' or None
    """
    item, descriptor = get_anonymity_item(character)
    return descriptor


# ===================================================================
# SKILL-BASED DISGUISES
# ===================================================================

def get_active_disguise(character):
    """
    Get the currently active skill-based disguise profile.
    
    Args:
        character: The character to check
        
    Returns:
        dict or None: Active disguise profile or None
    """
    return getattr(character.db, DB_ACTIVE_DISGUISE, None)


def get_disguise_stability(character):
    """
    Get the current stability of a skill-based disguise.
    
    Args:
        character: The character to check
        
    Returns:
        int: Stability value (0-100) or None if no disguise
    """
    disguise = get_active_disguise(character)
    if disguise:
        stability = disguise.get("stability", DISGUISE_STABILITY_MAX)
        # Handle None values - treat as max stability
        return stability if stability is not None else DISGUISE_STABILITY_MAX
    return None


def damage_disguise_stability(character, amount, reason="unknown"):
    """
    Damage the stability of an active disguise.
    
    Args:
        character: The character with the disguise
        amount: Amount of stability to remove
        reason: Reason for the damage (for logging)
        
    Returns:
        tuple: (new_stability, broke_disguise, partial_slip)
    """
    disguise = get_active_disguise(character)
    if not disguise:
        return (None, False, False)
    
    current = disguise.get("stability", DISGUISE_STABILITY_MAX)
    # Handle None values - treat as max stability
    if current is None:
        current = DISGUISE_STABILITY_MAX
    
    new_stability = max(0, current - amount)
    disguise["stability"] = new_stability
    character.db.active_disguise = disguise
    
    broke = new_stability <= DISGUISE_STABILITY_BROKEN
    partial = not broke and new_stability < DISGUISE_STABILITY_UNSTABLE and current >= DISGUISE_STABILITY_UNSTABLE
    
    return (new_stability, broke, partial)


def apply_disguise(character, profile_id):
    """
    Apply a disguise profile to a character.
    
    When a disguise is applied, clear this character's identity from all observers'
    known_identities so they see the new disguise, not the true name.
    
    Also applies stability boost based on disguise clothing worn (max 2 items per body part).
    Each valid clothing item adds +10 stability (e.g., hoodie + mask = +20).

    Args:
        character: The character to disguise
        profile_id: ID of the disguise profile to apply
        
    Returns:
        bool: True if successful
    """
    profiles = getattr(character.db, DB_DISGUISE_PROFILES, {})
    if profile_id not in profiles:
        return False
    
    profile = dict(profiles[profile_id])
    profile["stability"] = DISGUISE_STABILITY_MAX
    profile["profile_id"] = profile_id
    
    # Add stability boost from disguise clothing
    clothing_count = count_disguise_clothing(character)
    clothing_bonus = clothing_count * 10
    profile["stability"] = min(100, profile["stability"] + clothing_bonus)
    
    # DEBUG: Log before and after
    try:
        from evennia.comms.models import ChannelDB
        splat = ChannelDB.objects.get_channel("Splattercast")
        splat.msg(f"DEBUG apply_disguise: Setting active_disguise for {character.key}")
        splat.msg(f"  Profile: {profile}")
    except:
        pass
    
    character.db.active_disguise = profile
    
    # DEBUG: Verify it was set
    try:
        from evennia.comms.models import ChannelDB
        splat = ChannelDB.objects.get_channel("Splattercast")
        verify = getattr(character.db, DB_ACTIVE_DISGUISE, None)
        splat.msg(f"DEBUG apply_disguise: Verified active_disguise = {verify}")
    except:
        pass
    
    # Clear any slip state
    if hasattr(character.ndb, NDB_IDENTITY_SLIPPED):
        delattr(character.ndb, NDB_IDENTITY_SLIPPED)
    if hasattr(character.ndb, NDB_EMOTE_COUNT_SINCE_ADJUST):
        delattr(character.ndb, NDB_EMOTE_COUNT_SINCE_ADJUST)
    
    # Clear this character's identity from all observers' known_identities
    # so they see the new disguise instead of the true name
    from evennia.objects.models import ObjectDB
    char_dbref = str(character.dbref)
    all_chars = ObjectDB.objects.filter(db_typeclass_path="typeclasses.characters.Character")
    for observer in all_chars:
        if hasattr(observer, "db"):
            known = getattr(observer.db, DB_KNOWN_IDENTITIES, {})
            if known and char_dbref in known:
                del known[char_dbref]
                observer.db.known_identities = known
    
    return True


def break_disguise(character, notify=True):
    """
    Fully break a character's active disguise.
    
    Args:
        character: The character whose disguise breaks
        notify: Whether to send messages
        
    Returns:
        bool: True if a disguise was broken
    """
    disguise = get_active_disguise(character)
    if not disguise:
        return False
    
    # Get display name before breaking for message
    display_name = disguise.get("display_name", "someone")
    
    # Clear the disguise
    character.db.active_disguise = None
    
    # Set slip state
    character.ndb.identity_slipped = True
    
    if notify:
        character.msg(MSG_DISGUISE_BREAK_SELF)
        if character.location:
            character.location.msg_contents(
                MSG_DISGUISE_BREAK_ROOM.format(name=display_name),
                exclude=[character]
            )
    
    # Mark all observers as knowing true identity
    if character.location:
        for observer in character.location.contents:
            if observer != character and hasattr(observer, "db"):
                mark_identity_known(observer, character)
    
    return True


def create_disguise_profile(character, profile_id, display_name, description=None, 
                            voice_override=None, anonymity_descriptor=None):
    """
    Create or update a disguise profile for a character.
    
    Args:
        character: The character creating the profile
        profile_id: Unique identifier for this profile
        display_name: Name to display when disguised
        description: Optional custom description
        voice_override: Optional voice description override
        anonymity_descriptor: Optional descriptor (e.g., 'a grizzled man')
        
    Returns:
        dict: The created profile
    """
    profiles = getattr(character.db, DB_DISGUISE_PROFILES, None)
    if profiles is None:
        profiles = {}
    
    profile = {
        "display_name": display_name,
        "description": description,
        "voice_override": voice_override,
        "anonymity_descriptor": anonymity_descriptor,
        "created_at": None,  # Could add timestamp
    }
    
    profiles[profile_id] = profile
    character.db.disguise_profiles = profiles
    
    return profile


def delete_disguise_profile(character, profile_id):
    """
    Delete a disguise profile.
    
    Args:
        character: The character
        profile_id: ID of profile to delete
        
    Returns:
        bool: True if deleted
    """
    profiles = getattr(character.db, DB_DISGUISE_PROFILES, {})
    if profile_id in profiles:
        del profiles[profile_id]
        character.db.disguise_profiles = profiles
        
        # If this was the active disguise, clear it
        active = get_active_disguise(character)
        if active and active.get("profile_id") == profile_id:
            character.db.active_disguise = None
        
        return True
    return False


# ===================================================================
# IDENTITY RESOLUTION
# ===================================================================

def get_display_identity(character, looker):
    """
    Get the appropriate display identity for a character.
    
    Follows priority:
    1. True name (if slip occurred and not corrected)
    2. Active disguise display name (if intact)
    3. Active disguise anonymity descriptor
    4. Item-based anonymity descriptor
    5. True name (fallback)
    
    Args:
        character: The character being looked at
        looker: The character doing the looking
        
    Returns:
        tuple: (display_name, is_true_identity)
    """
    true_name = character.key
    
    # Priority 1: Check if identity has slipped
    if getattr(character.ndb, NDB_IDENTITY_SLIPPED, False):
        return (true_name, True)
    
    # Priority 2 & 3: Check skill-based disguise
    disguise = get_active_disguise(character)
    if disguise:
        stability = disguise.get("stability", DISGUISE_STABILITY_MAX)
        if stability > DISGUISE_STABILITY_BROKEN:
            display_name = disguise.get("display_name")
            if display_name:
                return (display_name, False)
            # Fall back to disguise anonymity descriptor
            descriptor = disguise.get("anonymity_descriptor")
            if descriptor:
                return (descriptor, False)
    
    # Priority 4: Check item-based anonymity
    item, descriptor = get_anonymity_item(character)
    if item and descriptor:
        return (descriptor, False)
    
    # Priority 5: True name fallback
    return (true_name, True)


# ===================================================================
# SLIP MECHANICS
# ===================================================================

def check_disguise_slip(character, trigger_type, **kwargs):
    """
    Check if a disguise or anonymity should slip.
    
    Args:
        character: The character to check
        trigger_type: Type of trigger ('combat', 'shove', 'run', 'scrutiny', 'emote')
        **kwargs: Additional context (round_num for combat escalation, etc.)
        
    Returns:
        tuple: (slipped, slip_type) where slip_type is 'item', 'partial', or 'full'
    """
    # Debug logging
    try:
        from evennia.comms.models import ChannelDB
        splattercast = ChannelDB.objects.get_channel("Splattercast")
    except Exception:
        splattercast = None
    
    # Get character's disguise skill to reduce slip chance
    disguise_skill = getattr(character.db, "disguise", 0) or 0
    
    # Determine base slip chance based on trigger
    if trigger_type == "combat":
        # Combat slip is much more aggressive
        # With 0 disguise, you're almost guaranteed to slip
        # With high disguise, you're well protected
        base_chance = SLIP_CHANCE_COMBAT
        # Escalate chance as combat rounds progress (1% increase per round starting at round 1)
        round_num = kwargs.get('round_num', 0) or 0
        if round_num > 0:
            base_chance = base_chance + (round_num * 1.0)  # 1% per round
    elif trigger_type == "shove":
        base_chance = SLIP_CHANCE_SHOVE
    elif trigger_type == "run":
        base_chance = SLIP_CHANCE_RUN
    elif trigger_type == "scrutiny":
        base_chance = SLIP_CHANCE_SCRUTINY
    elif trigger_type == "emote":
        # Escalating chance based on emotes since last adjust
        emote_count = getattr(character.ndb, NDB_EMOTE_COUNT_SINCE_ADJUST, 0) or 0
        emote_increment = SLIP_CHANCE_EMOTE_INCREMENT or 1
        base_chance = (SLIP_CHANCE_EMOTE_BASE or 5) + (emote_count * emote_increment)
        character.ndb.emote_count_since_adjust = emote_count + 1
    else:
        base_chance = 5  # Default small chance
    
    # Apply disguise skill modifier - reduce slip chance by skill points
    # At skill 0: no reduction (30% base in combat)
    # At skill 20: -20% reduction (10% in combat, harder to slip)
    # At skill 50: -50% reduction (very safe in combat)
    # At skill 80: -80% reduction (extremely safe in combat)
    # But with combat escalation, low skill characters will eventually slip
    if disguise_skill < 10:
        # Very low skill is extremely risky in combat
        # With 0 skill: base_chance stays high (30% per round)
        # With 5 skill: 30-5 = 25%
        skill_reduction = disguise_skill * 1.0
    else:
        # Normal skill scaling after 10
        skill_reduction = disguise_skill * 0.5
    
    base_chance = max(1, base_chance - skill_reduction)  # Never go below 1% chance
    
    # Check item-based anonymity first
    item, descriptor = get_anonymity_item(character)
    if splattercast:
        splattercast.msg(f"DISGUISE_CHECK: {character.key} trigger={trigger_type}, has_item={item is not None}, base_chance={base_chance}")
    if item:
        # Item anonymity has no resistance roll - just chance
        roll = random.randint(1, 100)
        if roll <= base_chance:
            # Use a slip counter for combat so it takes multiple hits to fully reveal
            if trigger_type == "combat":
                slip_count = getattr(character.ndb, "combat_slip_count", 0) + 1
                character.ndb.combat_slip_count = slip_count
                SLIP_THRESHOLD = 3  # Number of slips before full item reveal
                if slip_count < SLIP_THRESHOLD:
                    # Count toward threshold but don't message
                    return (False, None)
                else:
                    # Reset counter and actually slip
                    character.ndb.combat_slip_count = 0
                    return (True, "item")
            else:
                return (True, "item")
    
    # Check skill-based disguise
    disguise = get_active_disguise(character)
    if splattercast:
        splattercast.msg(f"DISGUISE_CHECK: active_disguise={disguise}")
    if disguise:
        # Get disguise skill for resistance
        disguise_skill = getattr(character.db, "disguise", 0)
        edge_stat = getattr(character.db, "edge", 1)
        # Skill reduces slip chance
        skill_reduction = (disguise_skill // 10) * DISGUISE_SKILL_MODIFIER
        adjusted_chance = max(1, base_chance - skill_reduction)
        roll = random.randint(1, 100)
        if roll <= adjusted_chance:
            # Use a partial slip counter for combat
            if trigger_type == "combat":
                partial_count = getattr(character.ndb, "combat_partial_slip_count", 0) + 1
                character.ndb.combat_partial_slip_count = partial_count
                PARTIAL_THRESHOLD = 2  # Number of partials before full slip
                stability = disguise.get("stability", DISGUISE_STABILITY_MAX)
                if partial_count < PARTIAL_THRESHOLD:
                    return (True, "partial")
                else:
                    character.ndb.combat_partial_slip_count = 0
                    # If already unstable, more likely to fully break
                    if stability < DISGUISE_STABILITY_UNSTABLE:
                        if random.randint(1, 100) <= 50:
                            return (True, "full")
                        return (True, "partial")
                    return (True, "full")
            else:
                # Non-combat triggers use original logic
                stability = disguise.get("stability", DISGUISE_STABILITY_MAX)
                if stability < DISGUISE_STABILITY_UNSTABLE:
                    if random.randint(1, 100) <= 50:
                        return (True, "full")
                    return (True, "partial")
                return (True, "partial")
    # No item or skill disguise found
    if splattercast:
        splattercast.msg(f"DISGUISE_CHECK: {character.key} has no active disguise or anonymity item - skipping slip check")
    return (False, None)


def trigger_slip_event(character, slip_type, item=None):
    """
    Process a slip event, revealing identity.
    
    Args:
        character: The character whose identity slips
        slip_type: 'item', 'partial', or 'full'
        item: The anonymity item if item slip
        
    Returns:
        bool: True if slip occurred
    """
    if slip_type == "item":
        # Item-based slip - simple reveal
        character.ndb.identity_slipped = True
        item_name = item.key if item else "hood"
        character.msg(MSG_ITEM_SLIP_SELF.format(item=item_name))
        if character.location:
            # Get current descriptor for the message
            _, descriptor = get_anonymity_item(character)
            name_to_use = descriptor if descriptor else character.key
            character.location.msg_contents(
                MSG_ITEM_SLIP_ROOM.format(name=name_to_use, item=item_name),
                exclude=[character]
            )
        # Deactivate the anonymity
        if item:
            item.db.anonymity_active = False
        # Mark observers as knowing identity
        if character.location:
            for observer in character.location.contents:
                if observer != character and hasattr(observer, "db"):
                    mark_identity_known(observer, character)
        return True
    
    elif slip_type == "partial":
        # Partial disguise slip - brief exposure
        character.ndb.identity_slipped = True
        
        disguise = get_active_disguise(character)
        display_name = disguise.get("display_name", "someone") if disguise else "someone"
        
        character.msg(MSG_DISGUISE_PARTIAL_SELF)
        if character.location:
            character.location.msg_contents(
                MSG_DISGUISE_PARTIAL_ROOM.format(name=display_name),
                exclude=[character]
            )
        
        # Mark current observers
        if character.location:
            for observer in character.location.contents:
                if observer != character and hasattr(observer, "db"):
                    mark_identity_known(observer, character)
        
        return True
    
    elif slip_type == "full":
        # Full disguise break
        return break_disguise(character, notify=True)
    
    return False


def adjust_anonymity_item(character, item=None):
    """
    Adjust an anonymity item to restore concealment after a slip.
    
    Items must cover the FACE location to provide anonymity.
    
    Args:
        character: The character adjusting
        item: Specific item to adjust, or None to find automatically
        
    Returns:
        bool: True if adjustment successful
    """
    if not item:
        # Find the anonymity item
        item, _ = get_anonymity_item(character)
        if not item:
            # Try to find any worn item that could provide anonymity
            worn_items = []
            
            # Get worn items from character tracking
            if hasattr(character.db, "worn_items") and character.db.worn_items:
                for location, items_at_location in character.db.worn_items.items():
                    for worn_obj in items_at_location:
                        if worn_obj and worn_obj not in worn_items:
                            worn_items.append(worn_obj)
            
            # Fallback to currently_worn attribute
            for obj in character.contents:
                if obj not in worn_items and hasattr(obj, "db") and getattr(obj.db, "currently_worn", False):
                    worn_items.append(obj)
            
            # Find anonymity-capable item that covers FACE
            for obj in worn_items:
                # CRITICAL: Item must cover FACE to provide anonymity
                if not _item_covers_face(obj):
                    continue
                
                item_name_lower = obj.key.lower()
                for keyword in ANONYMITY_KEYWORDS:
                    if keyword in item_name_lower:
                        item = obj
                        break
                if item:
                    break
    
    if not item:
        return False
    
    # CRITICAL: Verify item covers FACE
    if not _item_covers_face(item):
        return False
    
    # Reactivate anonymity
    item.db.anonymity_active = True
    
    # Clear slip state
    if hasattr(character.ndb, NDB_IDENTITY_SLIPPED):
        delattr(character.ndb, NDB_IDENTITY_SLIPPED)
    
    # Reset emote and combat slip counters
    character.ndb.emote_count_since_adjust = 0
    character.ndb.combat_slip_count = 0
    character.ndb.combat_partial_slip_count = 0
    
    # Send messages
    character.msg(MSG_ITEM_ADJUSTED.format(item=item.key))
    if character.location:
        # Show disguised name to each observer, plain text only
        for observer in character.location.contents:
            if observer != character:
                display_name, _ = get_display_identity(character, observer)
                # Remove any color codes from the message
                msg = MSG_ITEM_ADJUSTED_ROOM.format(name=display_name, item=item.key)
                # Strip Evennia color codes (|y, |n, etc.) if present
                import re
                msg_plain = re.sub(r'\|[a-zA-Z]', '', msg)
                observer.msg(msg_plain)
    
    return True


# ===================================================================
# OBSERVER MEMORY
# ===================================================================

def mark_identity_known(observer, target):
    """
    Mark that an observer now knows a target's true identity.
    
    Args:
        observer: The character who witnessed the reveal
        target: The character whose identity was revealed
    """
    if not hasattr(observer, "db"):
        return
    
    known = getattr(observer.db, DB_KNOWN_IDENTITIES, None)
    if known is None:
        known = {}
    
    # Store by dbref for persistence
    target_dbref = target.dbref if hasattr(target, "dbref") else str(target.id)
    known[target_dbref] = {
        "true_name": target.key,
        "witnessed_at": None,  # Could add timestamp
    }
    
    observer.db.known_identities = known
    
    # Notify the observer
    descriptor = get_anonymity_descriptor(target)
    if descriptor:
        observer.msg(MSG_RECOGNIZED.format(descriptor=descriptor, true_name=target.key))


def knows_identity(observer, target):
    """
    Check if an observer knows a target's true identity.
    
    Args:
        observer: The observer to check
        target: The target character
        
    Returns:
        bool: True if observer knows target's identity
    """
    if not hasattr(observer, "db"):
        return False
    
    known = getattr(observer.db, DB_KNOWN_IDENTITIES, {})
    if not known:
        return False
    
    target_dbref = target.dbref if hasattr(target, "dbref") else str(target.id)
    return target_dbref in known


def clear_known_identity(observer, target):
    """
    Clear knowledge of a target's identity (for time passage, new disguise, etc.)
    
    Args:
        observer: The observer
        target: The target to forget
        
    Returns:
        bool: True if cleared
    """
    if not hasattr(observer, "db"):
        return False
    
    known = getattr(observer.db, DB_KNOWN_IDENTITIES, {})
    target_dbref = target.dbref if hasattr(target, "dbref") else str(target.id)
    
    if target_dbref in known:
        del known[target_dbref]
        observer.db.known_identities = known
        return True
    return False


# ===================================================================
# RECOGNITION CHECKS (Opposed Rolls)
# ===================================================================

def recognition_check(observer, target):
    """
    Perform a recognition check - observer trying to see through disguise.
    
    This is a DIFFICULT SMARTS check. The observer's own Disguise skill helps
    them understand and pick apart disguise work (takes one to know one).

    Observer Roll: SMRT * d10 + snooping + (disguise_skill / 2) + bonuses
    Target Roll: EDGE * d10 + disguise_skill + stability_bonus + clothing_bonus
    
    Target receives +5 defense per disguise clothing item worn (e.g., hoodie + mask = +10).
    Max 2 items per body location.
    
    Base difficulty is HIGH - disguises are meant to work most of the time.
    
    Args:
        observer: Character trying to recognize
        target: Character being scrutinized
        
    Returns:
        tuple: (recognized, margin) where margin is how much observer won/lost by
    """
    # Observer uses SMRT (primary) + snooping + THEIR OWN disguise skill
    # "Takes one to know one" - experts at disguise can spot flaws
    observer_smrt = getattr(observer.db, "smrt", 1)
    observer_snooping = getattr(observer.db, "snooping", 0)
    observer_disguise = getattr(observer.db, "disguise", 0)
    
    # Base roll: SMRT * d10 (makes SMARTS the key stat)
    base_roll = random.randint(1, 10) * observer_smrt
    
    # Add snooping skill
    skill_bonus = observer_snooping
    
    # Add half their own disguise skill (expertise bonus)
    expertise_bonus = observer_disguise // 2
    
    observer_roll = base_roll + skill_bonus + expertise_bonus
    
    # Bonuses for observer
    if knows_identity(observer, target):
        observer_roll += RECOGNITION_BONUS_KNOWS_IDENTITY
    
    # Check proximity (close contact helps spot details)
    proximity = getattr(observer.ndb, "in_proximity_with", set())
    if target in proximity:
        observer_roll += RECOGNITION_BONUS_CLOSE_CONTACT
    
    # Target uses EDGE * d10 + disguise skill (full skill for defense)
    target_disguise = getattr(target.db, "disguise", 0)
    target_edge = getattr(target.db, "edge", 1)
    
    # Target base roll with a BONUS to make scrutiny difficult
    # This is the "difficulty" factor - disguises should be hard to pierce
    difficulty_bonus = 30  # Significant base difficulty
    
    target_roll = random.randint(1, 10) * target_edge + target_disguise + difficulty_bonus
    
    # Stability affects target defense (unstable disguises are easier to spot)
    disguise = get_active_disguise(target)
    if disguise:
        stability = disguise.get("stability", DISGUISE_STABILITY_MAX)
        # Lower stability means worse defense (penalty scales with instability)
        stability_penalty = ((DISGUISE_STABILITY_MAX - stability) * 2) // 10
        target_roll -= stability_penalty
    
    # Add disguise clothing bonus to target defense
    clothing_count = count_disguise_clothing(target)
    clothing_bonus = clothing_count * 5  # +5 per item, max 2 per location = +10 max
    target_roll += clothing_bonus
    
    margin = observer_roll - target_roll
    recognized = margin > 0
    
    return (recognized, margin)


def scrutinize(observer, target):
    """
    Actively scrutinize a target to try to see through their disguise.
    
    Args:
        observer: Character scrutinizing
        target: Target being scrutinized
        
    Returns:
        tuple: (success, message)
    """
    # Perform recognition check
    recognized, margin = recognition_check(observer, target)
    
    # Damage target's disguise stability from scrutiny
    damage_disguise_stability(target, STABILITY_DAMAGE_SCRUTINY, reason="scrutiny")
    
    # Check for slip from scrutiny
    slipped, slip_type = check_disguise_slip(target, "scrutiny")
    if slipped:
        trigger_slip_event(target, slip_type)
        recognized = True
    
    if recognized:
        mark_identity_known(observer, target)
        return (True, f"You see through the disguise - it is {target.key}!")
    else:
        display_name, _ = get_display_identity(target, observer)
        return (False, f"You study {display_name} carefully but cannot determine their true identity.")
