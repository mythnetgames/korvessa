"""
Stamina-based Movement System

A movement stamina system where BODY determines capacity, DEX affects efficiency
and recovery, and WILL provides subtle bonuses when pushing through exhaustion.

All stats are on a 0-100 scale.
"""

from enum import IntEnum
import math

# =============================================================================
# CONSTANTS - Easy to tune
# =============================================================================

# --- Stamina Pool ---
STAMINA_BASE = 100              # Base stamina everyone starts with
STAMINA_BODY_MULT = 0.7         # How much BODY adds to max stamina
STAMINA_SYNERGY_MULT = 0.3      # How much BODY+DEX synergy adds to max stamina

# --- Base Stamina Delta per Second by Tier ---
# Positive = regeneration, Negative = drain (when standing still)
BASE_DELTA = {
    "STROLL": 3.0,
    "WALK": 1.0,
    "JOG": -0.2,
    "RUN": -2.0,
    "SPRINT": -5.0,
}

# --- Movement Costs (stamina per room move) ---
MOVE_COST = {
    "STROLL": 2.0,      # Very light exertion
    "WALK": 3.0,        # Light exertion
    "JOG": 5.0,         # Moderate exertion
    "RUN": 8.0,         # Heavy exertion
    "SPRINT": 12.0,     # Very heavy exertion
}

# --- Movement Delay (seconds per room move) ---
MOVE_DELAY = {
    "STROLL": 2.0,      # Slow
    "WALK": 1.0,        # Normal
    "JOG": 0.5,         # Quick
    "RUN": 0.25,        # Fast
    "SPRINT": 0.0,      # Instant
}

# --- DEX Modifiers ---
DEX_REGEN_BONUS = 0.03          # Regen multiplier bonus per DEX point (scaled)
DEX_DRAIN_REDUCTION = 0.04      # Drain reduction factor from DEX+BODY synergy

# --- Movement Cost Modifiers ---
DEX_MOVE_COST_REDUCTION = 0.03  # How much DEX reduces movement costs

# --- Fatigue System ---
FATIGUE_BASE_SECONDS = 7.0      # Base fatigue duration after leaving sprint
FATIGUE_REGEN_MULT = 0.5        # Regen multiplier during fatigue
FATIGUE_WILL_FACTOR = 0.6       # How much WILL reduces fatigue duration
FATIGUE_MIN_SECONDS = 3.0       # Minimum fatigue duration
FATIGUE_MAX_SECONDS = 7.0       # Maximum fatigue duration

# --- WILL Low Stamina Grace ---
LOW_STAMINA_THRESHOLD = 0.30    # Stamina ratio below which grace kicks in
WILL_GRACE_MAX = 0.20           # Maximum drain reduction from WILL grace
WILL_GRACE_FACTOR = 0.25        # How much WILL contributes to grace

# --- Speed Downgrade Thresholds ---
SPRINT_MIN_RATIO = 0.20         # Below this, cannot sprint
RUN_MIN_RATIO = 0.10            # Below this, cannot run
JOG_MIN_STAMINA = 0             # At zero stamina, cannot jog (must walk)

# --- Regen Delay ---
REGEN_DELAY_SECONDS = 1.5       # Delay before regen starts after draining


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def clamp(value, min_val, max_val):
    """Clamp a value between min and max bounds."""
    return max(min_val, min(max_val, value))


def safe_div(numerator, denominator, default=0):
    """Safe division that returns default if denominator is zero."""
    if denominator == 0:
        return default
    return numerator / denominator


# =============================================================================
# MOVEMENT TIER ENUM
# =============================================================================

class MovementTier(IntEnum):
    """
    Movement speed tiers, ordered from slowest to fastest.
    Integer values allow easy comparison (higher = faster).
    """
    STROLL = 0
    WALK = 1
    JOG = 2
    RUN = 3
    SPRINT = 4


# Mapping from tier to base delta key
TIER_NAMES = {
    MovementTier.STROLL: "STROLL",
    MovementTier.WALK: "WALK",
    MovementTier.JOG: "JOG",
    MovementTier.RUN: "RUN",
    MovementTier.SPRINT: "SPRINT",
}


# =============================================================================
# CHARACTER MOVEMENT STAMINA COMPONENT
# =============================================================================

class CharacterMovementStamina:
    """
    Manages stamina for a character's movement system.
    
    Attributes:
        body (int): BODY stat (0-100), affects stamina pool
        dex (int): DEX stat (0-100), affects recovery and efficiency
        will (int): WILL stat (0-100), provides subtle low-stamina bonuses
        stamina_current (float): Current stamina level
        stamina_max (int): Maximum stamina capacity
        current_tier (MovementTier): Current movement speed tier
        fatigue_timer (float): Remaining fatigue duration in seconds
        regen_delay (float): Remaining regen delay in seconds
    """
    
    def __init__(self, body=50, dex=50, will=50):
        """
        Initialize the stamina component with character stats.
        
        Args:
            body: BODY stat (0-100)
            dex: DEX stat (0-100)
            will: WILL stat (0-100)
        """
        # Core stats (clamped to valid range)
        self.body = clamp(body, 0, 100)
        self.dex = clamp(dex, 0, 100)
        self.will = clamp(will, 0, 100)
        
        # Stamina state
        self.stamina_max = 100  # Will be recalculated
        self.stamina_current = 0.0
        
        # Timers
        self.fatigue_timer = 0.0
        self.regen_delay = 0.0
        
        # Current movement tier
        self.current_tier = MovementTier.WALK
        
        # Track if we just entered sprint (to avoid repeated burst cost)
        self._was_sprinting = False
        
        # Initialize stamina to max
        self.recalc_stamina_max()
        self.stamina_current = float(self.stamina_max)
    
    def recalc_stamina_max(self):
        """
        Recalculate maximum stamina based on BODY and DEX.
        
        Formula: S_max = 100 + 0.7*BODY + 0.3*sqrt(BODY*DEX)
        """
        # Calculate BODY+DEX synergy factor
        synergy = math.sqrt(self.body * self.dex) if (self.body > 0 and self.dex > 0) else 0
        
        # Calculate max stamina
        raw_max = STAMINA_BASE + (STAMINA_BODY_MULT * self.body) + (STAMINA_SYNERGY_MULT * synergy)
        self.stamina_max = round(raw_max)
        
        # Ensure current stamina does not exceed new max
        self.stamina_current = min(self.stamina_current, float(self.stamina_max))
    
    def _get_synergy(self):
        """Calculate the BODY+DEX synergy value (A = sqrt(BODY*DEX))."""
        if self.body > 0 and self.dex > 0:
            return math.sqrt(self.body * self.dex)
        return 0
    
    def _get_regen_multiplier(self):
        """
        Calculate the regen multiplier based on DEX.
        
        Formula: regen_mult = 1 + 0.03 * DEX/100
        """
        return 1.0 + (DEX_REGEN_BONUS * self.dex / 100.0)
    
    def _get_drain_multiplier(self):
        """
        Calculate the drain multiplier based on BODY+DEX synergy.
        
        Formula: drain_mult = 1 / (1 + 0.04 * A/100)
        Lower is better (less drain).
        """
        synergy = self._get_synergy()
        return 1.0 / (1.0 + (DEX_DRAIN_REDUCTION * synergy / 100.0))
    
    def _get_will_grace(self):
        """
        Calculate WILL grace factor for low stamina situations.
        
        Formula: will_grace = clamp(0, 0.20, 0.25 * WILL/(WILL+50))
        """
        if self.will <= 0:
            return 0.0
        raw_grace = WILL_GRACE_FACTOR * self.will / (self.will + 50)
        return clamp(raw_grace, 0.0, WILL_GRACE_MAX)
    
    def _get_move_cost_multiplier(self):
        """
        Calculate the movement cost multiplier based on DEX.
        Higher DEX = lower movement costs.
        
        Formula: cost_mult = 1 / (1 + 0.03 * DEX/100)
        """
        return 1.0 / (1.0 + (DEX_MOVE_COST_REDUCTION * self.dex / 100.0))
    
    def get_move_cost(self, tier=None):
        """
        Get the stamina cost for moving one room at the given tier.
        
        Args:
            tier: MovementTier to get cost for (defaults to current tier)
            
        Returns:
            Stamina cost as a float
        """
        if tier is None:
            tier = self.current_tier
        
        tier_name = TIER_NAMES[tier]
        base_cost = MOVE_COST[tier_name]
        
        # Apply DEX reduction
        cost_mult = self._get_move_cost_multiplier()
        final_cost = base_cost * cost_mult
        
        # Apply WILL grace at low stamina (small reduction)
        ratio = self._get_stamina_ratio()
        if ratio < LOW_STAMINA_THRESHOLD:
            will_grace = self._get_will_grace()
            final_cost *= (1.0 - will_grace * 0.3)  # 30% of grace applies to movement
        
        return max(0, final_cost)
    
    def get_move_delay(self, tier=None):
        """
        Get the delay in seconds before moving at the given tier.
        
        Args:
            tier: MovementTier to get delay for (defaults to current tier)
            
        Returns:
            Delay in seconds as a float
        """
        if tier is None:
            tier = self.current_tier
        
        tier_name = TIER_NAMES[tier]
        return MOVE_DELAY[tier_name]
    
    def can_afford_move(self, tier=None):
        """
        Check if character has enough stamina to move at the given tier.
        
        Args:
            tier: MovementTier to check (defaults to current tier)
            
        Returns:
            True if can afford the move, False otherwise
        """
        cost = self.get_move_cost(tier)
        return self.stamina_current >= cost
    
    def pay_move_cost(self, tier=None):
        """
        Deduct stamina for moving one room at the given tier.
        
        Args:
            tier: MovementTier for the move (defaults to current tier)
            
        Returns:
            Actual cost paid (may be 0 if insufficient stamina)
        """
        if tier is None:
            tier = self.current_tier
        
        cost = self.get_move_cost(tier)
        
        if self.stamina_current >= cost:
            self.stamina_current -= cost
            self.stamina_current = max(0, self.stamina_current)
            
            # Set regen delay after movement
            self.regen_delay = REGEN_DELAY_SECONDS
            
            # Check if we need to auto-downgrade after the cost
            new_tier = self._get_allowed_tier(self.current_tier)
            if new_tier != self.current_tier:
                self.set_tier(new_tier)
            
            return cost
        else:
            # Not enough stamina - auto-downgrade and try again
            lower_tier = self._get_allowed_tier(self.current_tier)
            if lower_tier != self.current_tier:
                self.set_tier(lower_tier)
                return self.pay_move_cost(lower_tier)
            return 0
    
    def _get_fatigue_duration(self):
        """
        Calculate fatigue duration based on WILL.
        
        Formula: fatigue_seconds = 7 / (1 + 0.6 * WILL/(WILL+50))
        Clamped to [3, 7], rounded to 0.1s.
        """
        will_factor = self.will / (self.will + 50) if self.will > 0 else 0
        raw_duration = FATIGUE_BASE_SECONDS / (1.0 + FATIGUE_WILL_FACTOR * will_factor)
        clamped = clamp(raw_duration, FATIGUE_MIN_SECONDS, FATIGUE_MAX_SECONDS)
        return round(clamped, 1)
    
    def _get_stamina_ratio(self):
        """Get current stamina as a ratio of max (0.0 to 1.0)."""
        return safe_div(self.stamina_current, self.stamina_max, default=0.0)
    
    def _get_allowed_tier(self, desired_tier):
        """
        Determine the highest allowed tier based on current stamina.
        
        Rules:
        - stamina <= 20% of max: cannot SPRINT (drop to RUN)
        - stamina <= 10% of max: cannot RUN (drop to JOG)
        - stamina <= 0: cannot JOG (drop to WALK)
        
        Args:
            desired_tier: The tier the character wants to move at
            
        Returns:
            The highest tier actually allowed
        """
        ratio = self._get_stamina_ratio()
        allowed = desired_tier
        
        # Check sprint threshold
        if allowed >= MovementTier.SPRINT and ratio <= SPRINT_MIN_RATIO:
            allowed = MovementTier.RUN
        
        # Check run threshold
        if allowed >= MovementTier.RUN and ratio <= RUN_MIN_RATIO:
            allowed = MovementTier.JOG
        
        # Check jog threshold (at zero stamina)
        if allowed >= MovementTier.JOG and self.stamina_current <= JOG_MIN_STAMINA:
            allowed = MovementTier.WALK
        
        return allowed
    
    def set_tier(self, desired_tier):
        """
        Attempt to set the movement tier.
        
        Handles:
        - Automatic downgrade if stamina is too low
        - Fatigue application when leaving sprint
        
        Args:
            desired_tier: MovementTier or int representing desired speed
            
        Returns:
            The actual tier set (may be lower than desired)
        """
        # Convert int to enum if needed
        if isinstance(desired_tier, int) and not isinstance(desired_tier, MovementTier):
            desired_tier = MovementTier(clamp(desired_tier, 0, 4))
        
        old_tier = self.current_tier
        
        # Determine what tier we can actually use
        actual_tier = self._get_allowed_tier(desired_tier)
        
        # Handle leaving sprint - apply fatigue
        if old_tier == MovementTier.SPRINT and actual_tier != MovementTier.SPRINT:
            if self._was_sprinting:
                self.fatigue_timer = self._get_fatigue_duration()
                self._was_sprinting = False
        
        # Handle entering sprint - no burst cost, just track state
        if actual_tier == MovementTier.SPRINT and old_tier != MovementTier.SPRINT:
            self._was_sprinting = True
        
        self.current_tier = actual_tier
        return actual_tier
    
    def update(self, dt):
        """
        Update stamina and timers for the given time delta.
        
        This should be called every game tick/frame.
        
        Args:
            dt: Time delta in seconds
        """
        if dt <= 0:
            return
        
        # --- Update stamina buff timer ---
        if hasattr(self, 'ndb') and hasattr(self.ndb, 'stamina_buff_timer'):
            self.ndb.stamina_buff_timer = max(0, self.ndb.stamina_buff_timer - dt)
        
        # --- Get effective max stamina (with buff if active) ---
        effective_max = self.stamina_max
        if hasattr(self, 'ndb') and hasattr(self.ndb, 'stamina_buff_timer') and self.ndb.stamina_buff_timer > 0:
            effective_max = self.stamina_max * 1.4  # 40% buff
        
        # --- Get base delta for current tier ---
        tier_name = TIER_NAMES[self.current_tier]
        base_delta = BASE_DELTA[tier_name]
        
        # --- Calculate final delta ---
        final_delta = 0.0
        
        if base_delta > 0:
            # Regenerating stamina
            final_delta = base_delta * self._get_regen_multiplier()
            
            # Apply fatigue penalty to regen
            if self.fatigue_timer > 0:
                final_delta *= FATIGUE_REGEN_MULT
            
            # Apply regen delay - no regen while delay is active
            if self.regen_delay > 0:
                final_delta = 0.0
                
        elif base_delta < 0:
            # Draining stamina
            final_delta = base_delta * self._get_drain_multiplier()
            
            # Apply WILL grace at low stamina
            ratio = self._get_stamina_ratio()
            if ratio < LOW_STAMINA_THRESHOLD:
                will_grace = self._get_will_grace()
                # Reduce drain by will_grace (remember delta is negative)
                final_delta *= (1.0 - will_grace)
            
            # Reset regen delay when draining
            self.regen_delay = REGEN_DELAY_SECONDS
        
        # --- Apply stamina change ---
        self.stamina_current += final_delta * dt
        self.stamina_current = clamp(self.stamina_current, 0, effective_max)
        
        # --- Update timers ---
        if self.fatigue_timer > 0:
            self.fatigue_timer = max(0, self.fatigue_timer - dt)
        
        if self.regen_delay > 0:
            self.regen_delay = max(0, self.regen_delay - dt)
        
        # --- Auto-downgrade tier if stamina too low ---
        new_tier = self._get_allowed_tier(self.current_tier)
        if new_tier != self.current_tier:
            self.set_tier(new_tier)
    
    def get_debug_status(self):
        """
        Get a dictionary of current state for debugging.
        
        Returns:
            dict with stamina values, timers, multipliers, and tier info
        """
        tier_name = TIER_NAMES[self.current_tier]
        base_delta = BASE_DELTA[tier_name]
        
        return {
            # Stamina
            "stamina_current": round(self.stamina_current, 2),
            "stamina_max": self.stamina_max,
            "stamina_ratio": round(self._get_stamina_ratio(), 3),
            
            # Tier
            "current_tier": tier_name,
            "tier_base_delta": base_delta,
            "move_cost": round(self.get_move_cost(), 2),
            "move_delay": self.get_move_delay(),
            
            # Stats
            "body": self.body,
            "dex": self.dex,
            "will": self.will,
            "synergy": round(self._get_synergy(), 2),
            
            # Multipliers
            "regen_mult": round(self._get_regen_multiplier(), 3),
            "drain_mult": round(self._get_drain_multiplier(), 3),
            "move_cost_mult": round(self._get_move_cost_multiplier(), 3),
            "will_grace": round(self._get_will_grace(), 3),
            
            # Timers
            "fatigue_timer": round(self.fatigue_timer, 2),
            "regen_delay": round(self.regen_delay, 2),
            "is_fatigued": self.fatigue_timer > 0,
            "is_regen_delayed": self.regen_delay > 0,
            
            # Durations
            "fatigue_duration": self._get_fatigue_duration(),
        }


# =============================================================================
# DEMO / TEST
# =============================================================================

if __name__ == "__main__":
    import time
    
    print("=" * 60)
    print("STAMINA MOVEMENT SYSTEM DEMO")
    print("=" * 60)
    
    # Create a character with moderate stats
    char = CharacterMovementStamina(body=60, dex=50, will=40)
    
    print(f"\nCharacter Stats: BODY={char.body}, DEX={char.dex}, WILL={char.will}")
    print(f"Max Stamina: {char.stamina_max}")
    print(f"Sprint Burst Cost: {char._get_sprint_burst_cost()}")
    print(f"Fatigue Duration: {char._get_fatigue_duration()}s")
    print()
    
    # Simulation parameters
    dt = 0.5  # Half-second ticks
    sim_time = 0.0
    
    # Scenario: Walk -> Sprint -> exhaustion -> recovery
    scenarios = [
        (0, MovementTier.WALK, "Starting at WALK"),
        (2, MovementTier.SPRINT, "Switching to SPRINT"),
        (8, MovementTier.RUN, "Dropping to RUN"),
        (12, MovementTier.WALK, "Slowing to WALK to recover"),
        (25, MovementTier.SPRINT, "Attempting SPRINT again"),
        (35, MovementTier.STROLL, "Slowing to STROLL"),
    ]
    scenario_idx = 0
    
    print("-" * 60)
    print(f"{'Time':>6} | {'Tier':>7} | {'Stamina':>12} | {'Fatigue':>7} | {'Delay':>5} | Notes")
    print("-" * 60)
    
    while sim_time <= 45:
        # Check if we should change tier
        if scenario_idx < len(scenarios):
            trigger_time, new_tier, note = scenarios[scenario_idx]
            if sim_time >= trigger_time:
                actual = char.set_tier(new_tier)
                tier_name = TIER_NAMES[new_tier]
                actual_name = TIER_NAMES[actual]
                if actual != new_tier:
                    note += f" (downgraded to {actual_name})"
                scenario_idx += 1
                
                # Print tier change
                status = char.get_debug_status()
                print(f"{sim_time:6.1f} | {status['current_tier']:>7} | "
                      f"{status['stamina_current']:>5.1f}/{status['stamina_max']:<5} | "
                      f"{status['fatigue_timer']:>5.1f}s | "
                      f"{status['regen_delay']:>3.1f}s | "
                      f"** {note}")
        
        # Update simulation
        char.update(dt)
        
        # Print status every 2 seconds
        if sim_time % 2 < dt:
            status = char.get_debug_status()
            print(f"{sim_time:6.1f} | {status['current_tier']:>7} | "
                  f"{status['stamina_current']:>5.1f}/{status['stamina_max']:<5} | "
                  f"{status['fatigue_timer']:>5.1f}s | "
                  f"{status['regen_delay']:>3.1f}s |")
        
        sim_time += dt
    
    print("-" * 60)
    print("\nFinal Debug Status:")
    for key, value in char.get_debug_status().items():
        print(f"  {key}: {value}")
    
    # Test edge case: very low stats
    print("\n" + "=" * 60)
    print("EDGE CASE: Low-stat character (BODY=10, DEX=10, WILL=5)")
    print("=" * 60)
    
    weak_char = CharacterMovementStamina(body=10, dex=10, will=5)
    print(f"Max Stamina: {weak_char.stamina_max}")
    print(f"Sprint Burst Cost: {weak_char._get_sprint_burst_cost()}")
    print(f"Fatigue Duration: {weak_char._get_fatigue_duration()}s")
    
    # Test edge case: maxed stats
    print("\n" + "=" * 60)
    print("EDGE CASE: High-stat character (BODY=100, DEX=100, WILL=100)")
    print("=" * 60)
    
    strong_char = CharacterMovementStamina(body=100, dex=100, will=100)
    print(f"Max Stamina: {strong_char.stamina_max}")
    print(f"Sprint Burst Cost: {strong_char._get_sprint_burst_cost()}")
    print(f"Fatigue Duration: {strong_char._get_fatigue_duration()}s")
    print(f"Regen Multiplier: {strong_char._get_regen_multiplier():.3f}")
    print(f"Drain Multiplier: {strong_char._get_drain_multiplier():.3f}")
    print(f"Will Grace: {strong_char._get_will_grace():.3f}")
