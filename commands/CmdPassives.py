"""
Passive Command

Shows active personality passives and their effects.
"""

from evennia import Command


class CmdPassives(Command):
    """
    View your active personality passive abilities.
    
    Usage:
        passives
        passive
    
    Shows what passive bonuses you have from your personality.
    """
    
    key = "passives"
    aliases = ["passive", "perks"]
    locks = "cmd:all()"
    help_category = "Character"
    
    def func(self):
        caller = self.caller
        
        personality = getattr(caller.db, 'personality', None)
        passive_key = getattr(caller.db, 'personality_passive', None)
        
        if not personality or not passive_key:
            caller.msg("|yYou have no personality passive abilities.|n")
            return
        
        from world.personality_system import PERSONALITIES
        from world.personality_passives import (
            get_stamina_modifiers,
            get_perception_bonus,
            get_repair_time_multiplier,
            get_initial_standing_bonus,
            get_stealth_bonus,
            get_disguise_slip_reduction,
            get_psychic_resistance,
            can_read_any_language,
            get_environmental_resistance
        )
        
        p = PERSONALITIES.get(personality, {})
        passive_info = p.get('passive', {})
        
        msg = f"|w=== Your Passive Abilities ===|n\n\n"
        msg += f"|wPersonality:|n |c{p.get('name', 'Unknown')}|n\n"
        msg += f"|wPassive:|n |y{passive_info.get('name', 'Unknown')}|n\n"
        msg += f"|wDescription:|n {passive_info.get('desc', 'No description')}\n\n"
        msg += f"|w=== Active Effects ===|n\n"
        
        # Show specific mechanical bonuses
        effects = []
        
        # Stalwart
        regen_mult, drain_mult = get_stamina_modifiers(caller)
        if regen_mult > 1.0:
            bonus_pct = int((regen_mult - 1.0) * 100)
            effects.append(f"|gStamina Regeneration:|n +{bonus_pct}%")
        if drain_mult < 1.0:
            reduction_pct = int((1.0 - drain_mult) * 100)
            effects.append(f"|gStamina Drain Reduction:|n -{reduction_pct}%")
        
        # Sharp-Eyed
        perception_bonus = get_perception_bonus(caller)
        if perception_bonus:
            effects.append(f"|gPerception Rolls:|n +{perception_bonus}")
            effects.append(f"|gAuto-Perception:|n 30% chance on room entry")
        
        # Artificer
        repair_mult = get_repair_time_multiplier(caller)
        if repair_mult < 1.0:
            speed_pct = int((1.0 - repair_mult) * 100)
            effects.append(f"|gRepair Speed:|n +{speed_pct}% faster")
        
        # Silver-Tongued
        standing_bonus = get_initial_standing_bonus(caller)
        if standing_bonus:
            effects.append(f"|gNPC First Meeting:|n +{standing_bonus} standing")
        
        # Hidden
        stealth_bonus = get_stealth_bonus(caller)
        if stealth_bonus:
            effects.append(f"|gStealth Skill:|n +{stealth_bonus}%")
        slip_mult = get_disguise_slip_reduction(caller)
        if slip_mult < 1.0:
            reduction_pct = int((1.0 - slip_mult) * 100)
            effects.append(f"|gDisguise Slip Chance:|n -{reduction_pct}%")
        
        # Devoted
        psychic_mult = get_psychic_resistance(caller)
        if psychic_mult < 1.0:
            resist_pct = int((1.0 - psychic_mult) * 100)
            effects.append(f"|gPsychic Damage Resistance:|n {resist_pct}%")
        
        # Insightful
        if can_read_any_language(caller):
            effects.append(f"|gLanguage Reading:|n Can read any language")
        
        # Freehands
        env_mult = get_environmental_resistance(caller)
        if env_mult < 1.0:
            resist_pct = int((1.0 - env_mult) * 100)
            race = getattr(caller.db, 'race', 'human')
            if race == 'dwarf':
                effects.append(f"|gEnvironmental Resistance:|n {resist_pct}% (Freehands + Dwarf stacked)")
            else:
                effects.append(f"|gEnvironmental Resistance:|n {resist_pct}%")
        
        if effects:
            for effect in effects:
                msg += f"  {effect}\n"
        else:
            msg += "  |xNo active mechanical effects (passive may affect roleplay)|n\n"
        
        caller.msg(msg)
