"""
Characters

Characters are (by default) Objects setup to be puppeted by Accounts.
They are what you "see" in game. The Character class in this module
is setup to be the "default" character type created by the default
creation commands.

"""

from evennia.objects.objects import DefaultCharacter

from .objects import ObjectParent


class Character(ObjectParent, DefaultCharacter):
    def at_pre_puppet(self, account, session=None):
        """Block entry if character creation is incomplete or not approved."""
        if not self.is_chargen_complete():
            account.msg("Your character creation is not complete. Please finish all stages before entering the game.")
            return False
        if not self.is_approved():
            account.msg("Your character has not been approved by staff yet.")
            return False
        return True

    # --- Modular Character Creation Pipeline ---
    CHARGEN_STAGES = [
        'name',
        'concept',
        'stats',
        'personality',
        'skills',
        'background',
        'appearance',
        'review',
    ]

    def get_chargen_stage(self):
        """Return current chargen stage name."""
        idx = getattr(self.db, 'chargen_stage', 0)
        if 0 <= idx < len(self.CHARGEN_STAGES):
            return self.CHARGEN_STAGES[idx]
        return None

    def advance_chargen_stage(self, data=None):
        """Advance to next chargen stage, store data."""
        idx = getattr(self.db, 'chargen_stage', 0)
        if data:
            if not hasattr(self.db, 'chargen_data') or not self.db.chargen_data:
                self.db.chargen_data = {}
            self.db.chargen_data[self.get_chargen_stage()] = data
        if idx + 1 < len(self.CHARGEN_STAGES):
            self.db.chargen_stage = idx + 1
            return self.get_chargen_stage()
        else:
            self.at_chargen_complete()
            return None

    def validate_chargen_stage(self, stage, data):
        """Validation hook for each chargen stage. Extend as needed."""
        # Example: require non-empty name
        if stage == 'name':
            return bool(data and isinstance(data, str) and len(data) > 2)
        # Add more validation logic per stage as needed
        return True

    def get_chargen_data(self, stage=None):
        """Get stored chargen data for a stage or all."""
        if not hasattr(self.db, 'chargen_data') or not self.db.chargen_data:
            return None
        if stage:
            return self.db.chargen_data.get(stage)
        return self.db.chargen_data

    # --- Reputation & Rumor System Scaffolding ---
    def at_object_creation_reputation(self):
        """Initialize reputation and rumor attributes."""
        self.db.reputation_tier = 'Unknown'
        self.db.rumors = []

    def set_reputation_tier(self, tier):
        """Set the character's reputation tier."""
        self.db.reputation_tier = tier

    def get_reputation_tier(self):
        return self.db.reputation_tier

    def add_rumor(self, rumor):
        """Add a new rumor to the character's public knowledge."""
        if not self.db.rumors:
            self.db.rumors = []
        self.db.rumors.append(rumor)

    def get_rumors(self):
        return self.db.rumors if self.db.rumors else []

    def clear_rumors(self):
        self.db.rumors = []

    # --- Advanced Healing & Downtime Scaffolding ---
    def at_object_creation_healing(self):
        """Initialize downtime and advanced healing attributes."""
        self.db.downtime_hours = 0
        self.db.recovery_mod = 1.0  # Modifier for healing speed

    def add_downtime(self, hours):
        """Add downtime hours for healing/recovery."""
        self.db.downtime_hours = self.db.downtime_hours + hours if self.db.downtime_hours else hours

    def spend_downtime(self, hours):
        """Spend downtime hours, returns True if enough downtime."""
        if self.db.downtime_hours and self.db.downtime_hours >= hours:
            self.db.downtime_hours -= hours
            return True
        return False

    def heal_with_downtime(self):
        """Heal injury using downtime and recovery modifier."""
        if self.db.injury and self.db.injury.get('healing_time', 0) > 0:
            heal_amount = int(1 * self.db.recovery_mod)
            self.heal_injury(heal_amount)
            return heal_amount
        return 0

    # --- Character Creation & Staff Tools Scaffolding ---
    def at_chargen_start(self):
        """Hook for start of character creation."""
        self.db.chargen_stage = 0
        self.db.chargen_data = {}

    def at_chargen_advance(self, stage, data=None):
        """Advance chargen stage and store data."""
        self.db.chargen_stage = stage
        if data:
            self.db.chargen_data.update(data)

    def at_chargen_complete(self):
        """Finalize character creation."""
        self.db.chargen_complete = True
        self.db.approved = False  # Staff must approve

    def is_chargen_complete(self):
        return bool(self.db.chargen_complete)

    def is_approved(self):
        return bool(self.db.approved)

    def approve_character(self):
        self.db.approved = True

    def deny_character(self):
        self.db.approved = False
    """
    The Character just re-implements some of the Object's methods and hooks
    to represent a Character entity in-game.

    See mygame/typeclasses/objects.py for a list of
    properties and methods available on all Object child classes like this.

    """

    # --- Korvessa Stat, Personality, and Standing Scaffolding ---

    def at_object_creation(self):
        """
        Initialize character stats, personality, standing, skills, and XP.
        Extend this method as new systems are implemented.
        """
        super().at_object_creation()
        # Core stats
        self.db.stats = {
            'STR': 0,  # Strength
            'DEX': 0,  # Dexterity
            'CON': 0,  # Constitution
            'INT': 0,  # Intelligence
            'WIS': 0,  # Wisdom
            'CHA': 0,  # Charisma
        }
        # Personality (class-like)
        self.db.personality = None  # e.g., 'Stalwart', 'Sharp-Eyed', etc.
        # Social Standing (faction values)
        self.db.standing = {
            'Civic_Order': 0,
            'Laborers': 0,
            'Merchants': 0,
            'Nobility': 0,
            'Underbelly': 0,
            'Watcher_Cult': 0,
            'Scholars': 0,
            'Feyliks_Freefolk': 0,
        }
        # Character Facts / Public Knowledge
        self.db.public_knowledge = {
            'Name as Known': '',
            'Apparent Age': '',
            'Appearance Notes': '',
            'Common Rumors': '',
            'Known Affiliations': '',
            'Reputation Tier': '',
        }
        # --- Skill System Scaffolding ---
        self.db.skills = {
            'Combat': {},
            'Stealth': {},
            'Social': {},
            'Crafting': {},
            'Survival': {},
            'Lore': {},
            'Medical': {},
        }
        # --- XP & Economy Scaffolding ---
        self.db.xp = 0
        self.db.xp_daily = 0
        self.db.xp_daily_cap = 200
        self.db.training_points = 0
        # --- Mark as player character for menu visibility ---
        self.db.is_player = True
        self.db_is_player = True
        # --- Set default starting location ---
        from evennia.objects.models import ObjectDB
        start_room = ObjectDB.objects.filter(db_key__iexact="Limbo").first()
        if start_room:
            self.location = start_room

    def add_xp(self, amount):
        """Add XP, respecting daily cap."""
        if self.db.xp_daily + amount > self.db.xp_daily_cap:
            amount = max(0, self.db.xp_daily_cap - self.db.xp_daily)
        self.db.xp += amount
        self.db.xp_daily += amount
        return amount

    def spend_xp(self, amount):
        """Spend XP if available."""
        if self.db.xp >= amount:
            self.db.xp -= amount
            return True
        return False

    def reset_daily_xp(self):
        """Reset daily XP gain (call at rollover)."""
        self.db.xp_daily = 0

    def add_training_point(self):
        """Convert XP to training point if enough XP."""
        if self.spend_xp(200):
            self.db.training_points += 1
            return True
        return False

    # --- Combat & Injury System Scaffolding ---
    def at_object_creation_combat(self):
        """Initialize combat and injury system attributes."""
        self.db.stamina = 100  # Default stamina
        self.db.max_stamina = 100
        self.db.injury = {
            'tier': 0,  # 0 = healthy, 1 = bruised, 2 = wounded, 3 = critical
            'description': '',
            'healing_time': 0,  # in hours
        }

    def get_stamina(self):
        return self.db.stamina

    def set_stamina(self, value):
        self.db.stamina = max(0, min(value, self.db.max_stamina))

    def apply_injury(self, tier, description, healing_time):
        """Apply an injury to the character."""
        self.db.injury['tier'] = tier
        self.db.injury['description'] = description
        self.db.injury['healing_time'] = healing_time

    def heal_injury(self, amount):
        """Heal injury by reducing healing_time. If healing_time <= 0, clear injury."""
        self.db.injury['healing_time'] = max(0, self.db.injury['healing_time'] - amount)
        if self.db.injury['healing_time'] == 0:
            self.db.injury['tier'] = 0
            self.db.injury['description'] = ''

    def is_critically_injured(self):
        return self.db.injury.get('tier', 0) >= 3

    def resolve_combat(self, opponent, skill='Combat', stamina_cost=10):
        """Basic combat resolution stub."""
        # Example: compare skill proficiency and stats
        my_skill = self.get_skill_proficiency(skill)
        opp_skill = opponent.get_skill_proficiency(skill) if hasattr(opponent, 'get_skill_proficiency') else 0
        my_stat = self.db.stats.get('STR', 0)
        opp_stat = getattr(opponent, 'db', {}).get('stats', {}).get('STR', 0)
        self.set_stamina(self.get_stamina() - stamina_cost)
        if my_skill + my_stat > opp_skill + opp_stat:
            return 'win'
        elif my_skill + my_stat < opp_skill + opp_stat:
            self.apply_injury(1, 'Bruised in combat', 2)
            return 'lose'
        else:
            return 'draw'

    def get_skill(self, domain, skill):
        """Get a skill's proficiency and learning rate."""
        return self.db.skills.get(domain, {}).get(skill, {'proficiency': 0, 'learning_rate': 1.0})

    def set_skill(self, domain, skill, proficiency, learning_rate=1.0):
        """Set a skill's proficiency and learning rate."""
        if domain not in self.db.skills:
            self.db.skills[domain] = {}
        self.db.skills[domain][skill] = {'proficiency': proficiency, 'learning_rate': learning_rate}

    def get_skills_by_domain(self, domain):
        """Return all skills and proficiencies for a domain."""
        return self.db.skills.get(domain, {})

    def improve_skill(self, domain, skill, amount=1):
        """Increase a skill's proficiency, applying learning rate."""
        skill_data = self.get_skill(domain, skill)
        skill_data['proficiency'] += int(amount * skill_data.get('learning_rate', 1.0))
        self.set_skill(domain, skill, skill_data['proficiency'], skill_data['learning_rate'])

    def get_stat(self, stat):
        """Get a stat value by key (e.g., 'STR')."""
        return self.db.stats.get(stat, 0)

    def set_stat(self, stat, value):
        """Set a stat value by key."""
        self.db.stats[stat] = value

    def get_standing(self, group):
        """Get social standing for a faction group."""
        return self.db.standing.get(group, 0)

    def set_standing(self, group, value):
        """Set social standing for a faction group."""
        self.db.standing[group] = value

    def get_personality(self):
        """Get the character's personality/class."""
        return self.db.personality

    def set_personality(self, personality):
        """Set the character's personality/class."""
        self.db.personality = personality

    def get_public_knowledge(self):
        """Return the character's public knowledge dict."""
        return self.db.public_knowledge

    def set_public_knowledge(self, field, value):
        """Set a field in the public knowledge dict."""
        self.db.public_knowledge[field] = value
