"""
Stamina System

A simple, robust stamina system for movement and combat.

Key features:
- CON determines max stamina pool
- DEX affects recovery rate
- Stamina regenerates automatically when not sprinting/running
- Combat and sprinting drain stamina
"""

from enum import IntEnum

# =============================================================================
# CONSTANTS
# =============================================================================

# --- Stamina Pool ---
STAMINA_BASE = 100              # Base stamina for everyone
STAMINA_CON_MULT = 5.0          # Each CON point above 8 adds this much

# --- Regeneration ---
REGEN_BASE = 2.0                # Base regen per second when idle
REGEN_DEX_MULT = 0.3            # Each DEX point above 8 adds this much regen/sec
REGEN_DELAY = 2.0               # Seconds after exertion before regen starts

# --- Movement Costs (per room moved) ---
COST_STROLL = 0                 # No cost
COST_WALK = 0                   # No cost
COST_JOG = 1                    # Light cost per room
COST_RUN = 3                    # Moderate cost per room
COST_SPRINT = 6                 # Heavy cost per room

# --- Movement Drain (per second while moving at that speed) ---
DRAIN_STROLL = 0                # No drain
DRAIN_WALK = 0                  # No drain
DRAIN_JOG = 0.5                 # Light drain
DRAIN_RUN = 2.0                 # Moderate drain
DRAIN_SPRINT = 5.0              # Heavy drain

# --- Movement Delays (seconds per room) ---
DELAY_STROLL = 2.0
DELAY_WALK = 1.0
DELAY_JOG = 0.5
DELAY_RUN = 0.25
DELAY_SPRINT = 0.1

# --- Thresholds ---
SPRINT_MIN_PERCENT = 20         # Need 20% stamina to sprint
RUN_MIN_PERCENT = 10            # Need 10% stamina to run
JOG_MIN_PERCENT = 5             # Need 5% stamina to jog


# =============================================================================
# MOVEMENT TIER ENUM
# =============================================================================

class MovementTier(IntEnum):
    """Movement speed tiers, slowest to fastest."""
    STROLL = 0
    WALK = 1
    JOG = 2
    RUN = 3
    SPRINT = 4


TIER_NAMES = {
    MovementTier.STROLL: "STROLL",
    MovementTier.WALK: "WALK",
    MovementTier.JOG: "JOG",
    MovementTier.RUN: "RUN",
    MovementTier.SPRINT: "SPRINT",
}

TIER_COSTS = {
    MovementTier.STROLL: COST_STROLL,
    MovementTier.WALK: COST_WALK,
    MovementTier.JOG: COST_JOG,
    MovementTier.RUN: COST_RUN,
    MovementTier.SPRINT: COST_SPRINT,
}

TIER_DRAINS = {
    MovementTier.STROLL: DRAIN_STROLL,
    MovementTier.WALK: DRAIN_WALK,
    MovementTier.JOG: DRAIN_JOG,
    MovementTier.RUN: DRAIN_RUN,
    MovementTier.SPRINT: DRAIN_SPRINT,
}

TIER_DELAYS = {
    MovementTier.STROLL: DELAY_STROLL,
    MovementTier.WALK: DELAY_WALK,
    MovementTier.JOG: DELAY_JOG,
    MovementTier.RUN: DELAY_RUN,
    MovementTier.SPRINT: DELAY_SPRINT,
}


# =============================================================================
# STAMINA COMPONENT
# =============================================================================

class CharacterMovementStamina:
    """
    Manages stamina for a character.
    
    Attributes:
        stamina_max: Maximum stamina capacity
        stamina_current: Current stamina level
        current_tier: Current movement speed tier
        regen_delay: Seconds until regen starts
        con: Constitution stat (8-16)
        dex: Dexterity stat (8-16)
    """
    
    def __init__(self, con=10, dex=10, **kwargs):
        """
        Initialize stamina component.
        
        Args:
            con: Constitution stat (8-16, default 10)
            dex: Dexterity stat (8-16, default 10)
            **kwargs: Ignored (for backward compatibility with old body/will params)
        """
        self.con = max(8, min(20, con))
        self.dex = max(8, min(20, dex))
        
        # Backward compatibility - if 'body' was passed, use it as con
        if 'body' in kwargs and kwargs['body']:
            # Old system used 0-100 scale, convert back
            old_body = kwargs['body']
            self.con = max(8, min(16, int(8 + old_body * 7 / 100)))
        
        # Calculate max stamina from CON
        self.stamina_max = self._calc_max_stamina()
        self.stamina_current = float(self.stamina_max)
        
        # State
        self.current_tier = MovementTier.WALK
        self.regen_delay = 0.0
        
        # For backward compatibility
        self.body = self.con
        self.will = 10
    
    def _calc_max_stamina(self):
        """Calculate max stamina from CON."""
        # CON 8 = 100, CON 10 = 110, CON 15 = 135, CON 16 = 140
        return int(STAMINA_BASE + (self.con - 8) * STAMINA_CON_MULT)
    
    def _calc_regen_rate(self):
        """Calculate regen rate from DEX."""
        # DEX 8 = 2.0/s, DEX 10 = 2.6/s, DEX 15 = 4.1/s, DEX 16 = 4.4/s
        return REGEN_BASE + (self.dex - 8) * REGEN_DEX_MULT
    
    def recalc_stamina_max(self):
        """Recalculate max stamina (for compatibility)."""
        self.stamina_max = self._calc_max_stamina()
        self.stamina_current = min(self.stamina_current, float(self.stamina_max))
    
    def update_stats(self, con=None, dex=None, body=None, will=None):
        """Update stats and recalculate max stamina."""
        if con is not None:
            self.con = max(8, min(20, con))
        if dex is not None:
            self.dex = max(8, min(20, dex))
        
        # Backward compatibility
        if body is not None:
            self.con = max(8, min(16, int(8 + body * 7 / 100)))
        
        self.body = self.con
        
        old_max = self.stamina_max
        self.stamina_max = self._calc_max_stamina()
        
        # Scale current stamina proportionally
        if old_max > 0:
            ratio = self.stamina_current / old_max
            self.stamina_current = ratio * self.stamina_max
    
    def get_stamina_percent(self):
        """Get current stamina as a percentage."""
        if self.stamina_max <= 0:
            return 0
        return (self.stamina_current / self.stamina_max) * 100
    
    def _get_stamina_ratio(self):
        """Get current stamina as a ratio (0.0 to 1.0). For compatibility."""
        if self.stamina_max <= 0:
            return 0.0
        return self.stamina_current / self.stamina_max
    
    def can_use_tier(self, tier):
        """Check if stamina is high enough for a given tier."""
        percent = self.get_stamina_percent()
        
        if tier >= MovementTier.SPRINT:
            return percent >= SPRINT_MIN_PERCENT
        elif tier >= MovementTier.RUN:
            return percent >= RUN_MIN_PERCENT
        elif tier >= MovementTier.JOG:
            return percent >= JOG_MIN_PERCENT
        return True  # Walk and stroll always allowed
    
    def _get_allowed_tier(self, desired_tier):
        """Get the highest tier allowed based on current stamina."""
        for tier in range(int(desired_tier), -1, -1):
            if self.can_use_tier(MovementTier(tier)):
                return MovementTier(tier)
        return MovementTier.WALK
    
    def get_allowed_tier(self, desired_tier):
        """Alias for _get_allowed_tier for compatibility."""
        return self._get_allowed_tier(desired_tier)
    
    def set_tier(self, desired_tier):
        """
        Set movement tier. Returns actual tier (may be lower if stamina too low).
        """
        # Convert int to MovementTier if needed
        if isinstance(desired_tier, int) and not isinstance(desired_tier, MovementTier):
            desired_tier = MovementTier(max(0, min(4, desired_tier)))
        
        actual_tier = self._get_allowed_tier(desired_tier)
        self.current_tier = actual_tier
        return actual_tier
    
    def get_move_cost(self, tier=None):
        """Get stamina cost for moving one room."""
        if tier is None:
            tier = self.current_tier
        return TIER_COSTS.get(tier, 0)
    
    def get_move_delay(self, tier=None):
        """Get delay in seconds for moving one room."""
        if tier is None:
            tier = self.current_tier
        return TIER_DELAYS.get(tier, 1.0)
    
    def can_afford_move(self, tier=None):
        """Check if character has enough stamina for a move."""
        cost = self.get_move_cost(tier)
        return self.stamina_current >= cost
    
    def pay_move_cost(self, tier=None):
        """
        Pay stamina cost for moving one room.
        Returns actual cost paid.
        """
        if tier is None:
            tier = self.current_tier
        
        cost = TIER_COSTS.get(tier, 0)
        if cost > 0:
            self.stamina_current = max(0, self.stamina_current - cost)
            self.regen_delay = REGEN_DELAY
            
            # Auto-downgrade if needed
            new_tier = self._get_allowed_tier(self.current_tier)
            if new_tier != self.current_tier:
                self.current_tier = new_tier
        
        return cost
    
    def drain(self, amount):
        """
        Drain stamina by a given amount (for combat, etc).
        Returns actual amount drained.
        """
        actual = min(amount, self.stamina_current)
        self.stamina_current = max(0, self.stamina_current - actual)
        self.regen_delay = REGEN_DELAY
        return actual
    
    def restore(self, amount):
        """
        Restore stamina by a given amount.
        Returns actual amount restored.
        """
        old = self.stamina_current
        self.stamina_current = min(self.stamina_max, self.stamina_current + amount)
        return self.stamina_current - old
    
    def update(self, dt, character=None):
        """
        Update stamina for time passing.
        
        Args:
            dt: Time delta in seconds
            character: Character object (optional, ignored - for compatibility)
        """
        if dt <= 0:
            return
        
        # Get drain rate for current tier
        drain_rate = TIER_DRAINS.get(self.current_tier, 0)
        
        if drain_rate > 0:
            # Draining (jogging, running, sprinting)
            self.stamina_current = max(0, self.stamina_current - drain_rate * dt)
            self.regen_delay = REGEN_DELAY
            
            # Auto-downgrade if needed
            new_tier = self._get_allowed_tier(self.current_tier)
            if new_tier != self.current_tier:
                self.current_tier = new_tier
        else:
            # Regenerating (walking, strolling, standing)
            if self.regen_delay > 0:
                # Still in delay period
                self.regen_delay = max(0, self.regen_delay - dt)
            else:
                # Can regenerate
                regen_rate = self._calc_regen_rate()
                self.stamina_current = min(self.stamina_max, self.stamina_current + regen_rate * dt)
    
    def get_debug_status(self):
        """Get debug info dictionary."""
        return {
            "stamina_current": round(self.stamina_current, 1),
            "stamina_max": self.stamina_max,
            "stamina_ratio": round(self._get_stamina_ratio(), 3),
            "current_tier": TIER_NAMES.get(self.current_tier, "WALK"),
            "move_cost": self.get_move_cost(),
            "move_delay": self.get_move_delay(),
            "regen_delay": round(self.regen_delay, 1),
            "regen_rate": round(self._calc_regen_rate(), 2),
            "is_regen_delayed": self.regen_delay > 0,
            "is_fatigued": False,  # Removed fatigue system for simplicity
            "fatigue_timer": 0,    # Compatibility
            "con": self.con,
            "dex": self.dex,
            "body": self.con,      # Compatibility
            "will": 10,            # Compatibility
        }


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def get_or_create_stamina(character):
    """
    Get or create a stamina component for a character.
    
    Args:
        character: The character object
        
    Returns:
        CharacterMovementStamina instance
    """
    # Check for existing stamina component
    stamina = getattr(character.ndb, "stamina", None)
    if stamina is not None:
        return stamina
    
    # Get stats from character
    con = getattr(character, "con", 10) or 10
    dex = getattr(character, "dex", 10) or 10
    
    # Create new component
    stamina = CharacterMovementStamina(con=con, dex=dex)
    character.ndb.stamina = stamina
    
    return stamina


def invalidate_stamina_cache(character):
    """
    Clear cached stamina when stats change.
    """
    if hasattr(character, 'ndb') and hasattr(character.ndb, 'stamina'):
        character.ndb.stamina = None


# Backward compatibility aliases
def _get_or_create_stamina(character):
    """Alias for get_or_create_stamina."""
    return get_or_create_stamina(character)


# For imports that expect these
BASE_DELTA = {
    "STROLL": 0,
    "WALK": 0,
    "JOG": -DRAIN_JOG,
    "RUN": -DRAIN_RUN,
    "SPRINT": -DRAIN_SPRINT,
}

MOVE_COST = {
    "STROLL": COST_STROLL,
    "WALK": COST_WALK,
    "JOG": COST_JOG,
    "RUN": COST_RUN,
    "SPRINT": COST_SPRINT,
}

MOVE_DELAY = {
    "STROLL": DELAY_STROLL,
    "WALK": DELAY_WALK,
    "JOG": DELAY_JOG,
    "RUN": DELAY_RUN,
    "SPRINT": DELAY_SPRINT,
}
