"""
Language System Constants

Centralized language definitions for the Kowloon MUD language system.

LANGUAGE HIERARCHY:

Core Everyday Languages (street-level reality):
- Cantonese: The primary spoken language. Default oral language of daily life,
  markets, gangs, families, neighborhoods. If people talk, they talk Cantonese.
- English: Corporate + technical lingua franca. Used by corporations, hackers,
  engineers. Signals education, money, or outside power.

Secondary but Powerful Languages:
- Mandarin: Political + mainland power language. Used by state officials, corporate
  envoys, mainland migrants. Using Mandarin in Kowloon can imply authority, surveillance,
  or outsider status.

Underground & Subcultural Layers:
- Street Cant: Mixed spoken register with Cantonese base, English tech verbs, Mandarin
  bureaucratic nouns, Japanese/Korean slang fragments. Where Kowloon flavor shines.
- Japanese: Corporate influence, yakuza, media, design culture.
- Korean: Entertainment, biotech, pop-tech crossover.

Minority & Legacy Languages:
- Vietnamese: Migrant labor, refugees, dock workers.
- Russian: Organized crime, black market, underworld.
- Arabic: Middle Eastern districts and markets.
- Hindi: Indian immigrants and communities.

Builder+ Permission:
- Builders with Builder+ permission gain access to all languages for NPC creation.
- Standard builders see a curated set of common languages.
"""

# ===================================================================
# LANGUAGE DEFINITIONS
# ===================================================================

LANGUAGES = {
    'cantonese': {
        'name': 'Cantonese',
        'description': 'The primary oral language of Kowloon. Sharp, staccato, streetwise. Daily life language of markets, gangs, families. If people talk, they talk Cantonese.',
        'native': False,
        'common': True,  # Default language
    },
    'english': {
        'name': 'English',
        'description': 'Corporate + technical lingua franca. Used by corporations, hackers, engineers, contracts, academia. Signals education, money, or outside power.',
        'native': False,
        'common': True,
    },
    'mandarin': {
        'name': 'Mandarin Chinese',
        'description': 'Political + mainland power language. Used by state officials, corporate envoys, mainland migrants. Using Mandarin can imply authority, surveillance, or outsider status.',
        'native': False,
        'common': True,
    },
    'street_cant': {
        'name': 'Street Cant',
        'description': 'Mixed spoken register: Cantonese base + English tech verbs + Mandarin bureaucratic nouns + Japanese/Korean slang. Code-speech and argot for hackers, runners, and triads. Where Kowloon flavor shines.',
        'native': False,
        'common': True,
    },
    'japanese': {
        'name': 'Japanese',
        'description': 'Corporate influence, yakuza, media, design culture. Industrial and corpo dialect. Used by suits, corpos, and organized crime.',
        'native': False,
        'common': False,
    },
    'korean': {
        'name': 'Korean',
        'description': 'Entertainment, biotech, pop-tech crossover. Industrial dialect. Common among tech workers and mechanics.',
        'native': False,
        'common': False,
    },
    'vietnamese': {
        'name': 'Vietnamese',
        'description': 'Migrant labor, refugees, dock workers. Street dialect of refugee and working communities.',
        'native': False,
        'common': False,
    },
    'russian': {
        'name': 'Russian',
        'description': 'Organized crime, black market, underworld. Associated with organized crime and black market deals.',
        'native': False,
        'common': False,
    },
    'arabic': {
        'name': 'Arabic',
        'description': 'Middle Eastern districts and markets. Used in certain enclaves and trading communities.',
        'native': False,
        'common': False,
    },
    'hindi': {
        'name': 'Hindi',
        'description': 'Indian immigrant communities. Used by Indian laborers, merchants, and cultural enclaves.',
        'native': False,
        'common': False,
    },
}

# ===================================================================
# LANGUAGE SYSTEM CONSTANTS
# ===================================================================

DEFAULT_LANGUAGE = 'cantonese'
MAX_LANGUAGES = 10
SMARTS_THRESHOLD_FOR_SECOND_LANGUAGE = 4  # Characters with Smarts > 4 get a second language choice

# Common languages available to all builders
COMMON_LANGUAGES = [code for code, info in LANGUAGES.items() if info.get('common', False)]

# All languages available only to Builder+ users
ALL_LANGUAGES = list(LANGUAGES.keys())


# ===================================================================
# DATABASE AND NDB FIELD NAMES
# ===================================================================

DB_PRIMARY_LANGUAGE = 'primary_language'
DB_LANGUAGES = 'known_languages'
NDB_LAST_SPOKEN = 'last_spoken_language'

# ===================================================================
# MESSAGE TEMPLATES
# ===================================================================

MSG_LANGUAGE_SET = "|g{char_name}'s primary language is now set to {language}.|n"
MSG_LANGUAGE_ADDED = "|g{language} added to {char_name}'s known languages.|n"
MSG_LANGUAGE_REMOVED = "|g{language} removed from {char_name}'s known languages.|n"
MSG_LANGUAGE_ALREADY_KNOWN = "|y{char_name} already speaks {language}.|n"
MSG_LANGUAGE_NOT_KNOWN = "|r{char_name} does not speak {language}.|n"
MSG_LANGUAGE_INVALID = "|rInvalid language: {language}|n"
MSG_LANGUAGE_LIST = "|yKnown Languages:|n {languages}"
MSG_PRIMARY_LANGUAGE = "|yPrimary Language:|n {language}"
MSG_SPEAK_IN = "speaks in {language}"
MSG_LANGUAGE_CANNOT_REMOVE_PRIMARY = "|rCannot remove primary language. Set a new primary language first.|n"
