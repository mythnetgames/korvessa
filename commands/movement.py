"""
Movement Speed Commands

Commands for setting character movement tiers: stroll, walk, jog, run, sprint.
Integrates with the stamina system in world/stamina.py.
"""

from evennia import Command, CmdSet
from world.stamina import MovementTier, CharacterMovementStamina, TIER_NAMES


def invalidate_stamina_cache(character):
    """
    Clear the cached stamina component when stats change.
    This forces recalculation on next access to use updated stats.
    
    Args:
        character: The character whose stamina cache should be cleared
    """
    if hasattr(character.ndb, "stamina"):
        character.ndb.stamina = None


class CmdStroll(Command):
    """
    Move at a leisurely stroll - fastest stamina recovery.

    Usage:
        stroll

    Strolling is the slowest movement speed but provides the best
    stamina regeneration (+3.0/sec).
    """
    key = "stroll"
    locks = "cmd:all()"
    help_category = "Movement"

    def func(self):
        caller = self.caller
        _set_movement_tier(caller, MovementTier.STROLL)


class CmdWalk(Command):
    """
    Move at a normal walking pace - moderate stamina recovery.

    Usage:
        walk

    Walking is a comfortable pace that still allows stamina
    regeneration (+1.0/sec).
    """
    key = "walk"
    locks = "cmd:all()"
    help_category = "Movement"

    def func(self):
        caller = self.caller
        _set_movement_tier(caller, MovementTier.WALK)


class CmdJog(Command):
    """
    Move at a jogging pace - slight stamina drain.

    Usage:
        jog

    Jogging is a moderate speed that causes minor stamina
    drain (-0.2/sec). Sustainable for long periods.
    """
    key = "jog"
    locks = "cmd:all()"
    help_category = "Movement"

    def func(self):
        caller = self.caller
        _set_movement_tier(caller, MovementTier.JOG)


class CmdRun(Command):
    """
    Move at a running pace - moderate stamina drain.

    Usage:
        run

    Running is fast but drains stamina steadily (-2.0/sec).
    You cannot run when stamina falls below 10%.
    """
    key = "run"
    locks = "cmd:all()"
    help_category = "Movement"

    def func(self):
        caller = self.caller
        _set_movement_tier(caller, MovementTier.RUN)


class CmdSprint(Command):
    """
    Move at maximum speed - heavy stamina drain.

    Usage:
        sprint

    Sprinting is the fastest movement but drains stamina rapidly
    (-5.0/sec). Entering sprint costs burst stamina. After sprinting,
    you will be fatigued for several seconds with reduced recovery.
    You cannot sprint when stamina falls below 20%.
    """
    key = "sprint"
    locks = "cmd:all()"
    help_category = "Movement"

    def func(self):
        caller = self.caller
        _set_movement_tier(caller, MovementTier.SPRINT)


class CmdPace(Command):
    """
    Check your current movement pace and stamina.

    Usage:
        pace

    Shows your current movement tier, stamina level, and any
    active effects like fatigue.
    """
    key = "pace"
    aliases = ["speed", "stamina"]
    locks = "cmd:all()"
    help_category = "Movement"

    def func(self):
        caller = self.caller
        stamina = _get_or_create_stamina(caller)
        status = stamina.get_debug_status()

        # Build status message
        tier_name = status["current_tier"].lower()
        current = status["stamina_current"]
        maximum = status["stamina_max"]
        ratio = status["stamina_ratio"] * 100
        move_cost = status["move_cost"]
        move_delay = status["move_delay"]

        msg = f"|wMovement:|n {tier_name.capitalize()}\n"
        msg += f"|wStamina:|n {current:.0f}/{maximum} ({ratio:.0f}%)\n"
        msg += f"|wMove Cost:|n {move_cost:.1f} stamina per room"

        # Show status effects
        if status["is_fatigued"]:
            msg += f"\n|yFatigued:|n {status['fatigue_timer']:.1f}s remaining (reduced recovery)"

        if status["is_regen_delayed"]:
            msg += f"\n|yRecovering:|n {status['regen_delay']:.1f}s until stamina regenerates"

        # Show stamina bar
        bar_width = 20
        filled = int(bar_width * status["stamina_ratio"])
        empty = bar_width - filled

        # Color based on stamina level
        if ratio > 50:
            bar_color = "|g"
        elif ratio > 20:
            bar_color = "|y"
        else:
            bar_color = "|r"

        bar = f"{bar_color}{'|' * filled}|n{'.' * empty}"
        msg += f"\n[{bar}]"

        caller.msg(msg)


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def _get_or_create_stamina(character):
    """
    Get the character's stamina component, creating it if needed.

    The stamina component is stored in character.ndb.stamina for the session.
    Stats are pulled from the character's D&D 5e attributes and converted to stamina scale.
    """
    # Always check if stamina exists AND is valid
    existing = getattr(character.ndb, "stamina", None)
    if existing is not None:
        return existing
    
    # Convert D&D 5e stats (8-15 range) to stamina system (0-100 scale)
    # Formula: (stat - 8) * (100 / 7) to map 8->0, 15->100
    # For personality-boosted stats (up to 16): 16->114
    def d5e_to_stamina_scale(d5e_stat):
        """Convert D&D 5e stat (8-16) to stamina scale (0-100+)."""
        return (d5e_stat - 8) * (100.0 / 7.0)

    # Get D&D 5e stats from character, with fallback to default of 10 (middle of range)
    str_val = getattr(character, "str", 10) or 10
    dex_val = getattr(character, "dex", 10) or 10
    con_val = getattr(character, "con", 10) or 10
    wis_val = getattr(character, "wis", 10) or 10
    
    # In stamina system:
    # body = CON (affects stamina pool and max capacity)
    # dex = DEX (affects movement efficiency and recovery)
    # will = WIS (provides subtle bonuses in low-stamina situations)
    body = int(d5e_to_stamina_scale(con_val))
    dex = int(d5e_to_stamina_scale(dex_val))
    will = int(d5e_to_stamina_scale(wis_val))

    # Create stamina component
    stamina = CharacterMovementStamina(
        body=body,
        dex=dex,
        will=will
    )
    character.ndb.stamina = stamina

    return stamina


def _set_movement_tier(character, desired_tier):
    """
    Set a character's movement tier and send appropriate feedback.

    Args:
        character: The character changing tiers
        desired_tier: The MovementTier they want to enter
    """
    stamina = _get_or_create_stamina(character)
    old_tier = stamina.current_tier
    actual_tier = stamina.set_tier(desired_tier)

    desired_name = TIER_NAMES[desired_tier].lower()
    actual_name = TIER_NAMES[actual_tier].lower()
    old_name = TIER_NAMES[old_tier].lower()

    # Check if already at this tier
    if old_tier == actual_tier and old_tier == desired_tier:
        character.msg(f"You are already {_tier_verb(actual_name)}.")
        return

    # Build response message
    if actual_tier == desired_tier:
        # Successfully changed to desired tier
        move_cost = stamina.get_move_cost(actual_tier)
        
        msg = f"You begin {_tier_verb(actual_name)}."
        msg += f" |y({move_cost:.1f} stamina per room)|n"

    else:
        # Forced to a lower tier due to stamina
        msg = f"|yYou try to {desired_name} but you are too exhausted.|n "
        msg += f"You {_tier_verb(actual_name)} instead."

    character.msg(msg)

    # Room message for others
    if actual_tier != old_tier:
        room_msg = f"{character.key} begins {_tier_verb(actual_name)}."
        character.location.msg_contents(room_msg, exclude=[character])


def _tier_verb(tier_name):
    """Convert tier name to present participle verb form."""
    verbs = {
        "stroll": "strolling",
        "walk": "walking",
        "jog": "jogging",
        "run": "running",
        "sprint": "sprinting",
    }
    return verbs.get(tier_name, f"moving at {tier_name} pace")


# =============================================================================
# COMMAND SET
# =============================================================================

class MovementCmdSet(CmdSet):
    """Command set for movement speed commands."""

    key = "movement_cmdset"

    def at_cmdset_creation(self):
        self.add(CmdStroll())
        self.add(CmdWalk())
        self.add(CmdJog())
        self.add(CmdRun())
        self.add(CmdSprint())
        self.add(CmdPace())
