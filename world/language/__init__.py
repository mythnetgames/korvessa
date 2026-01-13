"""
Language System

Comprehensive language system for Kowloon MUD.
Allows characters to speak multiple languages based on stats and choices.
"""

from .constants import LANGUAGES, DEFAULT_LANGUAGE
from .utils import get_character_languages, add_language, remove_language, set_primary_language

__all__ = [
    'LANGUAGES',
    'DEFAULT_LANGUAGE',
    'get_character_languages',
    'add_language',
    'remove_language',
    'set_primary_language',
]
