"""
Personality System Constants

Personalities are like classes taken only at chargen. They define thematic identity
and starting mechanical positioning - not profession.

Each personality provides:
- A stat bonus (choice of 2 in most cases)
- Skill bonuses (primary +10%, secondary +5%)
- A passive ability
- Social standing shifts with factions
"""

# =============================================================================
# PERSONALITY DEFINITIONS
# =============================================================================

PERSONALITIES = {
    'stalwart': {
        'name': 'Stalwart',
        'desc': 'You are dependable, enduring, and grounded. Work is your anchor, and you take pride in it. People count on you to see things through, and you rarely disappoint.',
        'stat_options': ['str', 'con'],  # Player picks one
        'skills': {
            'primary': {'skill': 'endurance', 'bonus': 10},
            'secondary': {'skill': 'athletics', 'bonus': 5}
        },
        'passive': {
            'name': 'Reduced Stamina Loss',
            'desc': 'Physical exertion drains you less than others.',
            'key': 'reduced_stamina_loss'
        },
        'standing_shifts': {
            'laborers': 200
        }
    },
    'sharp_eyed': {
        'name': 'Sharp-Eyed',
        'desc': 'You notice things others miss - the slight tremor in a voice, the scuff marks on a floor, the tension in a room. Your attention to detail has kept you alive.',
        'stat_options': ['wis', 'dex'],
        'skills': {
            'primary': {'skill': 'perception', 'bonus': 10},
            'secondary': {'skill': 'investigation', 'bonus': 5}
        },
        'passive': {
            'name': 'Detect Hidden',
            'desc': '+3% chance to notice hidden objects or creatures.',
            'key': 'detect_hidden_bonus'
        },
        'standing_shifts': {
            'civic_order': 150
        }
    },
    'artificer': {
        'name': 'Artificer',
        'desc': 'You understand how things work - and how to make them better. Whether fixing a broken hinge or appraising a relic, your hands and mind work in tandem.',
        'stat_options': ['int', 'dex'],
        'skills': {
            'primary': {'skill': 'crafting', 'bonus': 10},
            'secondary': {'skill': 'appraise', 'bonus': 5}
        },
        'passive': {
            'name': 'Faster Repairs',
            'desc': 'Repair actions take less time.',
            'key': 'faster_repairs'
        },
        'standing_shifts': {
            'merchants': 150
        }
    },
    'silver_tongued': {
        'name': 'Silver-Tongued',
        'desc': 'Words are your currency. You know when to speak and when to listen, how to flatter and how to deflect. Doors open for you that stay closed to others.',
        'stat_options': ['cha'],  # Only CHA for this one
        'skills': {
            'primary': {'skill': 'persuasion', 'bonus': 10},
            'secondary': {'skill': 'social', 'bonus': 5}
        },
        'passive': {
            'name': 'Start Friendlier',
            'desc': 'NPCs begin with a slightly better disposition toward you.',
            'key': 'friendlier_start'
        },
        'standing_shifts': {
            'nobility': 150,
            'merchants': 100
        }
    },
    'hidden': {
        'name': 'Hidden',
        'desc': 'You move through the world unseen when you wish to be. Shadows are friends, crowds are cover, and you have learned that those who are not seen cannot be stopped.',
        'stat_options': ['dex', 'wis'],
        'skills': {
            'primary': {'skill': 'stealth', 'bonus': 10},
            'secondary': {'skill': 'streetwise', 'bonus': 5}
        },
        'passive': {
            'name': 'Harder to Detect',
            'desc': 'Others have a harder time noticing you.',
            'key': 'harder_to_detect'
        },
        'standing_shifts': {
            'underbelly': 200,
            'civic_order': -100
        }
    },
    'devoted': {
        'name': 'Devoted',
        'desc': 'Faith guides your steps. Whether through prayer, meditation, or ritual, you have touched something beyond the mundane. Your conviction grants you resilience.',
        'stat_options': ['wis'],  # Only WIS for this one
        'skills': {
            'primary': {'skill': 'ritual', 'bonus': 10},
            'secondary': {'skill': 'sense_motive', 'bonus': 5}
        },
        'passive': {
            'name': 'Mental Resistance',
            'desc': '+1 to resist mental influences.',
            'key': 'mental_resist'
        },
        'standing_shifts': {
            'watcher_cult': 250
        }
    },
    'insightful': {
        'name': 'Insightful',
        'desc': 'Knowledge is power, and you pursue it relentlessly. Ancient texts, strange symbols, forgotten lore - you piece together what others overlook.',
        'stat_options': ['int'],  # Only INT for this one
        'skills': {
            'primary': {'skill': 'lore', 'bonus': 10},
            'secondary': {'skill': 'investigation', 'bonus': 5}
        },
        'passive': {
            'name': 'Auto-Insight',
            'desc': 'Automatically gain basic insight on runes and texts.',
            'key': 'auto_insight'
        },
        'standing_shifts': {
            'scholars': 200
        }
    },
    'freehands': {
        'name': 'Freehands',
        'desc': 'You belong to no one place, no one trade. Adaptability is your strength. Where others specialize, you improvise - and somehow, you always land on your feet.',
        'stat_options': ['dex', 'con'],
        'skills': {
            'primary': {'skill': 'adaptability', 'bonus': 10},
            'secondary': {'skill': 'any', 'bonus': 5}  # Player chooses
        },
        'passive': {
            'name': 'Environmental Resistance',
            'desc': 'Better tolerance for harsh environmental conditions.',
            'key': 'environmental_resist'
        },
        'standing_shifts': {}  # Neutral - no shifts
    }
}

# =============================================================================
# FACTION DEFINITIONS
# =============================================================================

FACTIONS = {
    'laborers': {
        'name': 'Laborers',
        'desc': 'Common workers, builders, and craftsmen who keep the city running.'
    },
    'civic_order': {
        'name': 'Civic Order',
        'desc': 'Guards, officials, and those who uphold law and governance.'
    },
    'merchants': {
        'name': 'Merchants',
        'desc': 'Traders, shopkeepers, and those who deal in goods and coin.'
    },
    'nobility': {
        'name': 'Nobility',
        'desc': 'The landed elite, those with titles and inherited power.'
    },
    'underbelly': {
        'name': 'Underbelly',
        'desc': 'Criminals, outcasts, and those who work in the shadows.'
    },
    'watcher_cult': {
        'name': 'Watcher Cult',
        'desc': 'Devotees of the Watcher, seekers of divine truth.'
    },
    'scholars': {
        'name': 'Scholars',
        'desc': 'Academics, researchers, and keepers of knowledge.'
    }
}

# =============================================================================
# SKILL CATEGORIES
# =============================================================================

# Skills organized by category for skill group purchasing
SKILL_GROUPS = {
    'physical': {
        'name': 'Physical',
        'skills': ['athletics', 'endurance', 'acrobatics', 'climbing', 'swimming']
    },
    'combat': {
        'name': 'Combat',
        'skills': ['melee', 'ranged', 'unarmed', 'defense', 'tactics']
    },
    'stealth': {
        'name': 'Stealth',
        'skills': ['stealth', 'sleight_of_hand', 'disguise', 'lockpicking']
    },
    'social': {
        'name': 'Social',
        'skills': ['persuasion', 'intimidation', 'deception', 'social', 'performance']
    },
    'knowledge': {
        'name': 'Knowledge',
        'skills': ['lore', 'history', 'religion', 'nature', 'arcana']
    },
    'perception': {
        'name': 'Perception',
        'skills': ['perception', 'investigation', 'sense_motive', 'tracking']
    },
    'craft': {
        'name': 'Craft',
        'skills': ['crafting', 'appraise', 'repair', 'cooking', 'alchemy']
    },
    'survival': {
        'name': 'Survival',
        'skills': ['survival', 'medicine', 'animal_handling', 'navigation']
    },
    'subterfuge': {
        'name': 'Subterfuge',
        'skills': ['streetwise', 'gambling', 'forgery', 'smuggling']
    }
}

# All individual skills for reference
ALL_SKILLS = [
    'athletics', 'endurance', 'acrobatics', 'climbing', 'swimming',
    'melee', 'ranged', 'unarmed', 'defense', 'tactics',
    'stealth', 'sleight_of_hand', 'disguise', 'lockpicking',
    'persuasion', 'intimidation', 'deception', 'social', 'performance',
    'lore', 'history', 'religion', 'nature', 'arcana',
    'perception', 'investigation', 'sense_motive', 'tracking',
    'crafting', 'appraise', 'repair', 'cooking', 'alchemy',
    'survival', 'medicine', 'animal_handling', 'navigation',
    'streetwise', 'gambling', 'forgery', 'smuggling',
    'ritual', 'meditation', 'adaptability'
]

# =============================================================================
# REPUTATION TIERS
# =============================================================================

REPUTATION_TIERS = {
    'minor': {
        'name': 'Minor',
        'desc': 'Few have heard of you. Your name might ring a bell in specific circles.',
        'dc_modifier': 0
    },
    'moderate': {
        'name': 'Moderate',
        'desc': 'Your reputation precedes you in relevant communities.',
        'dc_modifier': -2
    },
    'strong': {
        'name': 'Strong',
        'desc': 'You are well-known. Your deeds are spoken of widely.',
        'dc_modifier': -5
    }
}

# =============================================================================
# CHARACTER FACTS TEMPLATE
# =============================================================================

CHARACTER_FACTS_TEMPLATE = {
    'name_as_known': '',        # "Anea the Smith's Daughter" - street/common name
    'apparent_age': '',         # "Mid 20s" - helps perception-based rolls
    'appearance_notes': '',     # "Walks with a limp" - visible traits only
    'common_rumors': '',        # "Works odd hours near the mines" - everyday gossip
    'known_affiliations': '',   # "Often seen at laborer taverns" - based on Standing
    'reputation_tier': 'minor'  # minor, moderate, strong
}

# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def get_personality_display(personality_key):
    """Get formatted display text for a personality."""
    if personality_key not in PERSONALITIES:
        return None
    
    p = PERSONALITIES[personality_key]
    
    # Format stat options
    if len(p['stat_options']) == 1:
        stat_text = f"+1 {p['stat_options'][0].upper()}"
    else:
        stat_text = f"+1 {' or '.join(s.upper() for s in p['stat_options'])}"
    
    # Format skills
    primary = p['skills']['primary']
    secondary = p['skills']['secondary']
    skill_text = f"{primary['skill'].replace('_', ' ').title()} 5%, {secondary['skill'].replace('_', ' ').title()} 5%"
    
    # Format standing shifts
    if p['standing_shifts']:
        shifts = []
        for faction, amount in p['standing_shifts'].items():
            faction_name = FACTIONS.get(faction, {}).get('name', faction.title())
            sign = '+' if amount > 0 else ''
            shifts.append(f"{faction_name} {sign}{amount}")
        standing_text = ', '.join(shifts)
    else:
        standing_text = 'Neutral (no shifts)'
    
    return {
        'name': p['name'],
        'desc': p['desc'],
        'stat_bonus': stat_text,
        'skill_bonus': skill_text,
        'passive': p['passive']['desc'],
        'standing': standing_text
    }


def apply_personality_to_character(character, personality_key, chosen_stat, secondary_skill=None):
    """
    Apply a personality's bonuses to a character.
    
    Args:
        character: The character object
        personality_key: The personality chosen
        chosen_stat: Which stat bonus they picked (from stat_options)
        secondary_skill: For Freehands, which skill they pick for +5%
    """
    if personality_key not in PERSONALITIES:
        return False
    
    p = PERSONALITIES[personality_key]
    
    # Store personality
    character.db.personality = personality_key
    character.db.personality_stat_choice = chosen_stat
    
    # Apply stat bonus
    if chosen_stat in p['stat_options']:
        current_val = getattr(character, chosen_stat, 10)
        setattr(character, chosen_stat, current_val + 1)
    
    # Initialize skills dict if needed
    if not character.db.skills:
        character.db.skills = {}
    
    # Apply skill bonuses - grant 5% starting proficiency
    primary = p['skills']['primary']
    secondary = p['skills']['secondary']
    
    # Primary skill starts at 5%
    current_primary = character.db.skills.get(primary['skill'], 0)
    character.db.skills[primary['skill']] = max(current_primary, 5.0)
    
    # Handle secondary skill (Freehands can choose) - also starts at 5%
    if secondary['skill'] == 'any' and secondary_skill:
        character.db.personality_secondary_skill = secondary_skill
        current_secondary = character.db.skills.get(secondary_skill, 0)
        character.db.skills[secondary_skill] = max(current_secondary, 5.0)
    else:
        current_secondary = character.db.skills.get(secondary['skill'], 0)
        character.db.skills[secondary['skill']] = max(current_secondary, 5.0)
    
    # Store passive key
    character.db.personality_passive = p['passive']['key']
    
    # Apply passive skill bonuses (like Hidden's stealth bonus)
    from world.personality_passives import apply_personality_skill_bonuses
    apply_personality_skill_bonuses(character)
    
    # Apply standing shifts
    if not character.db.faction_standing:
        character.db.faction_standing = {}
    
    for faction, shift in p['standing_shifts'].items():
        current = character.db.faction_standing.get(faction, 0)
        character.db.faction_standing[faction] = current + shift
    
    return True


def apply_character_facts(character, facts):
    """
    Apply character facts to a character object.
    
    Args:
        character: The character object
        facts: Dict with character fact fields
    """
    character.db.character_facts = {
        'name_as_known': facts.get('name_as_known', character.key),
        'apparent_age': facts.get('apparent_age', 'Unknown'),
        'appearance_notes': facts.get('appearance_notes', ''),
        'common_rumors': facts.get('common_rumors', ''),
        'known_affiliations': facts.get('known_affiliations', ''),
        'reputation_tier': facts.get('reputation_tier', 'minor')
    }
