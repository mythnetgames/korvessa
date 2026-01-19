#!/usr/bin/env python
"""
Quick check of language constants and functions.
"""

# Check imports work
try:
    from world.language.constants import RACE_LANGUAGES, LANGUAGES, LANGUAGE_ALIASES
    print("✓ Language constants imported successfully")
    print(f"RACE_LANGUAGES: {RACE_LANGUAGES}")
    print(f"LANGUAGES: {list(LANGUAGES.keys())}")
    print(f"LANGUAGE_ALIASES: {LANGUAGE_ALIASES}")
    
    # Check that RACE_LANGUAGES has the right structure
    assert 'dwarf' in RACE_LANGUAGES
    assert 'elf' in RACE_LANGUAGES
    assert 'human' in RACE_LANGUAGES
    
    assert RACE_LANGUAGES['dwarf'] == ['common', 'dwarvish']
    assert RACE_LANGUAGES['elf'] == ['common', 'elvish']
    assert RACE_LANGUAGES['human'] == ['common']
    
    print("\n✓ All race languages are correctly configured")
    
except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()
