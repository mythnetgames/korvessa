#!/usr/bin/env python
"""
Test language system initialization and proficiency.

This test verifies:
1. Dwarves get common + dwarvish
2. Elves get common + elvish
3. Humans get common only
4. Language proficiency is properly initialized
5. Proficiency check respects known languages
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

django.setup()

from world.language.constants import RACE_LANGUAGES, LANGUAGES
from world.language.utils import (
    initialize_language_proficiency,
    get_language_proficiency,
    get_character_languages
)
from typeclasses.characters import Character
from evennia.utils.utils import create_script
from evennia import search_object


def test_race_languages():
    """Test that RACE_LANGUAGES is properly configured."""
    print("\n=== Testing RACE_LANGUAGES Configuration ===")
    
    print(f"Dwarf languages: {RACE_LANGUAGES['dwarf']}")
    assert RACE_LANGUAGES['dwarf'] == ['common', 'dwarvish'], "Dwarves should get common + dwarvish"
    print("✓ Dwarves have correct languages")
    
    print(f"Elf languages: {RACE_LANGUAGES['elf']}")
    assert RACE_LANGUAGES['elf'] == ['common', 'elvish'], "Elves should get common + elvish"
    print("✓ Elves have correct languages")
    
    print(f"Human languages: {RACE_LANGUAGES['human']}")
    assert RACE_LANGUAGES['human'] == ['common'], "Humans should get common only"
    print("✓ Humans have correct languages")


def test_language_initialization():
    """Test that language proficiency initializes correctly."""
    print("\n=== Testing Language Initialization ===")
    
    # Create a test character
    char = Character.objects.create(key="TestDwarf")
    char.race = "dwarf"
    
    try:
        # Set known languages as if from chargen
        known_langs = RACE_LANGUAGES['dwarf']
        char.db.known_languages = set(known_langs)
        char.db.primary_language = known_langs[0]
        
        print(f"Set character known_languages to: {char.db.known_languages}")
        
        # Initialize proficiency
        initialize_language_proficiency(char)
        
        print(f"Language proficiency dict: {char.db.language_proficiency}")
        
        # Verify all known languages are in proficiency dict
        proficiency = char.db.language_proficiency
        for lang in known_langs:
            assert lang in proficiency, f"Language {lang} not in proficiency dict"
            assert proficiency[lang] == 100.0, f"Language {lang} should be 100% proficient"
            print(f"✓ {lang}: 100.0% proficiency")
        
    finally:
        char.delete()


def test_proficiency_checks():
    """Test that proficiency checks work correctly."""
    print("\n=== Testing Proficiency Checks ===")
    
    # Create a test character (dwarf)
    char = Character.objects.create(key="TestDwarf2")
    char.race = "dwarf"
    
    try:
        # Initialize as dwarf with dwarvish
        known_langs = RACE_LANGUAGES['dwarf']
        char.db.known_languages = set(known_langs)
        char.db.primary_language = 'common'
        initialize_language_proficiency(char)
        
        # Check proficiency for known languages
        common_prof = get_language_proficiency(char, 'common')
        print(f"Common proficiency: {common_prof}%")
        assert common_prof == 100.0, "Should be fluent in common"
        print("✓ Common proficiency is 100%")
        
        dwarvish_prof = get_language_proficiency(char, 'dwarvish')
        print(f"Dwarvish proficiency: {dwarvish_prof}%")
        assert dwarvish_prof == 100.0, "Should be fluent in dwarvish"
        print("✓ Dwarvish proficiency is 100%")
        
        # Check proficiency for unknown language (elvish)
        elvish_prof = get_language_proficiency(char, 'elvish')
        print(f"Elvish proficiency: {elvish_prof}%")
        assert elvish_prof == 0.0, "Should not understand elvish"
        print("✓ Elvish proficiency is 0%")
        
    finally:
        char.delete()


def test_character_languages_function():
    """Test the get_character_languages helper function."""
    print("\n=== Testing get_character_languages Function ===")
    
    # Create a test character (elf)
    char = Character.objects.create(key="TestElf")
    char.race = "elf"
    
    try:
        # Initialize as elf
        known_langs = RACE_LANGUAGES['elf']
        char.db.known_languages = set(known_langs)
        char.db.primary_language = 'common'
        initialize_language_proficiency(char)
        
        # Get character languages
        langs = get_character_languages(char)
        print(f"Character languages result: {langs}")
        
        # Should be a dict with 'known', 'primary', 'proficiency'
        assert 'known' in langs, "Should have 'known' key"
        assert 'primary' in langs, "Should have 'primary' key"
        assert 'proficiency' in langs, "Should have 'proficiency' key"
        
        print(f"Known languages: {langs['known']}")
        print(f"Primary language: {langs['primary']}")
        print(f"Proficiencies: {langs['proficiency']}")
        
        # Verify contents
        assert set(langs['known']) == set(known_langs), "Known languages should match"
        print("✓ Character languages helper function works correctly")
        
    finally:
        char.delete()


def main():
    """Run all tests."""
    print("=" * 60)
    print("Language System Test Suite")
    print("=" * 60)
    
    try:
        test_race_languages()
        test_language_initialization()
        test_proficiency_checks()
        test_character_languages_function()
        
        print("\n" + "=" * 60)
        print("✓ All tests passed!")
        print("=" * 60)
        
    except AssertionError as e:
        print(f"\n✗ Test failed: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
