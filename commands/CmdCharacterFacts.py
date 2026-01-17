"""
Commands for viewing character facts (public knowledge).

Character Facts are pieces of information that other characters can discover
in the relatively small city. They can be viewed directly by anyone.

Facts include:
- Name as Known
- Apparent Age
- Appearance Notes
- Common Rumors
- Known Affiliations
- Reputation Tier
"""

from evennia import Command


class CmdMyFacts(Command):
    """
    View your character's public knowledge facts.
    
    Usage:
        myfacts
        
    This shows the information about you that others can discover
    simply by living in the same city and hearing rumors or seeing you around.
    """
    
    key = "myfacts"
    aliases = ["characterfacts", "publicknowledge", "myinfo"]
    locks = "cmd:all()"
    help_category = "Character"
    
    def func(self):
        caller = self.caller
        
        facts = caller.db.character_facts
        if not facts:
            caller.msg("|rYou have no character facts set.|n")
            caller.msg("|yThese are normally set during character creation.|n")
            return
        
        from world.personality_system import REPUTATION_TIERS
        
        tier = facts.get('reputation_tier', 'minor')
        tier_info = REPUTATION_TIERS.get(tier, REPUTATION_TIERS['minor'])
        
        personality = caller.db.personality or 'unknown'
        from world.personality_system import PERSONALITIES
        p = PERSONALITIES.get(personality, {})
        personality_name = p.get('name', personality.title()) if p else personality.title()
        
        msg = f"""
|w=== Your Character Facts ===|n

|wPersonality:|n |c{personality_name}|n

|wName as Known:|n |c{facts.get('name_as_known', 'Unknown')}|n
|wApparent Age:|n |c{facts.get('apparent_age', 'Unknown')}|n
|wAppearance:|n |c{facts.get('appearance_notes', 'Nothing notable')}|n
|wRumors:|n |c{facts.get('common_rumors', 'None')}|n
|wAffiliations:|n |c{facts.get('known_affiliations', 'None')}|n
|wReputation:|n |c{tier_info['name']}|n - {tier_info['desc']}

|y----------------------------------------------------------------------|n
|yOthers in the city know these things about you.|n
"""
        caller.msg(msg)


class CmdFacts(Command):
    """
    View public information about another character.
    
    Usage:
        facts <character>
        
    Shows the publicly known facts about someone in the city.
    In a relatively small place, people know things about each other -
    your appearance, rumors about you, known affiliations, etc.
    """
    
    key = "facts"
    aliases = ["whois", "info"]
    locks = "cmd:all()"
    help_category = "Character"
    
    def func(self):
        caller = self.caller
        
        if not self.args:
            caller.msg("|rUsage: facts <character>|n")
            return
        
        # Find the target
        target_name = self.args.strip()
        target = caller.search(target_name, location=None)
        if not target:
            return
        
        # Check if it's a character with facts
        facts = target.db.character_facts
        if not facts:
            caller.msg(f"|y{target.key} has no publicly known information.|n")
            return
        
        from world.personality_system import REPUTATION_TIERS
        
        # Get target's reputation tier
        tier = facts.get('reputation_tier', 'minor')
        tier_info = REPUTATION_TIERS.get(tier, REPUTATION_TIERS['minor'])
        
        personality = target.db.personality or 'unknown'
        from world.personality_system import PERSONALITIES
        p = PERSONALITIES.get(personality, {})
        personality_name = p.get('name', personality.title()) if p else personality.title()
        
        msg = f"""
|w=== About {target.key} ===|n

|wPersonality:|n |c{personality_name}|n

|wName as Known:|n |c{facts.get('name_as_known', target.key)}|n
|wApparent Age:|n |c{facts.get('apparent_age', 'Unknown')}|n
|wAppearance:|n |c{facts.get('appearance_notes', 'Nothing remarkable')}|n
|wRumors:|n |c{facts.get('common_rumors', 'None you know of')}|n
|wAffiliations:|n |c{facts.get('known_affiliations', 'Unknown')}|n
|wReputation:|n |c{tier_info['name']}|n - {tier_info['desc']}
"""
        caller.msg(msg)


class CmdEditFacts(Command):
    """
    Staff command to edit character facts.
    
    Usage:
        editfacts <character>/<field> = <value>
        
    Fields:
        name_as_known
        apparent_age
        appearance_notes
        common_rumors
        known_affiliations
        reputation_tier (minor, moderate, strong)
        
    Example:
        editfacts John/common_rumors = They say he killed a man in Eastport.
    """
    
    key = "editfacts"
    aliases = ["setfacts"]
    locks = "cmd:perm(Admin) or perm(Builder)"
    help_category = "Admin"
    
    def func(self):
        caller = self.caller
        
        if not self.args or "=" not in self.args:
            caller.msg("|rUsage: editfacts <character>/<field> = <value>|n")
            caller.msg("|yFields: name_as_known, apparent_age, appearance_notes,")
            caller.msg("|y        common_rumors, known_affiliations, reputation_tier|n")
            return
        
        lhs, rhs = self.args.split("=", 1)
        lhs = lhs.strip()
        value = rhs.strip()
        
        if "/" not in lhs:
            caller.msg("|rUsage: editfacts <character>/<field> = <value>|n")
            return
        
        char_name, field = lhs.rsplit("/", 1)
        char_name = char_name.strip()
        field = field.strip().lower()
        
        # Valid fields
        valid_fields = [
            'name_as_known', 'apparent_age', 'appearance_notes',
            'common_rumors', 'known_affiliations', 'reputation_tier'
        ]
        
        if field not in valid_fields:
            caller.msg(f"|rInvalid field '{field}'.|n")
            caller.msg(f"|yValid fields: {', '.join(valid_fields)}|n")
            return
        
        # Find the character
        from evennia.objects.models import ObjectDB
        targets = ObjectDB.objects.filter(db_key__iexact=char_name)
        if not targets:
            caller.msg(f"|rCharacter '{char_name}' not found.|n")
            return
        
        target = targets[0]
        
        # Validate reputation tier
        if field == 'reputation_tier':
            if value.lower() not in ['minor', 'moderate', 'strong']:
                caller.msg("|rReputation tier must be: minor, moderate, or strong|n")
                return
            value = value.lower()
        
        # Update facts
        if not target.db.character_facts:
            target.db.character_facts = {}
        
        target.db.character_facts[field] = value
        
        caller.msg(f"|gUpdated {target.key}'s {field} to:|n {value}")


class CmdViewFacts(Command):
    """
    Staff command to view another character's facts.
    
    Usage:
        viewfacts <character>
    """
    
    key = "viewfacts"
    locks = "cmd:perm(Admin) or perm(Builder)"
    help_category = "Admin"
    
    def func(self):
        caller = self.caller
        
        if not self.args:
            caller.msg("|rUsage: viewfacts <character>|n")
            return
        
        char_name = self.args.strip()
        
        # Find the character
        from evennia.objects.models import ObjectDB
        targets = ObjectDB.objects.filter(db_key__iexact=char_name)
        if not targets:
            caller.msg(f"|rCharacter '{char_name}' not found.|n")
            return
        
        target = targets[0]
        facts = target.db.character_facts
        
        if not facts:
            caller.msg(f"|y{target.key} has no character facts set.|n")
            return
        
        from world.personality_system import REPUTATION_TIERS
        
        tier = facts.get('reputation_tier', 'minor')
        tier_info = REPUTATION_TIERS.get(tier, REPUTATION_TIERS['minor'])
        
        personality = target.db.personality or 'unknown'
        from world.personality_system import PERSONALITIES
        p = PERSONALITIES.get(personality, {})
        personality_name = p.get('name', personality.title()) if p else personality.title()
        
        msg = f"""
|w=== Character Facts for {target.key} ===|n

|wPersonality:|n |c{personality_name}|n

|wName as Known:|n |c{facts.get('name_as_known', 'Unknown')}|n
|wApparent Age:|n |c{facts.get('apparent_age', 'Unknown')}|n
|wAppearance:|n |c{facts.get('appearance_notes', 'Nothing notable')}|n
|wRumors:|n |c{facts.get('common_rumors', 'None')}|n
|wAffiliations:|n |c{facts.get('known_affiliations', 'None')}|n
|wReputation:|n |c{tier_info['name']}|n - {tier_info['desc']}
|wDiscovery DC:|n |y{tier_info['discovery_dc']}|n
"""
        caller.msg(msg)
