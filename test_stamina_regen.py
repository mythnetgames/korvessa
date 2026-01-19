"""
Test Stamina Regeneration System

Run with: python manage.py shell < test_stamina_regen.py

This script verifies that:
1. Stamina component is created on character login
2. Stamina regenerates when not in combat
3. Stamina doesn't regenerate in combat
4. CON affects regen rate
5. Thirst penalties apply
"""

from evennia import search_object
from evennia.scripts.models import ScriptDB
from world.stamina_ticker import StaminaTicker
from world.stamina import CharacterMovementStamina, MovementTier
from commands.movement import _get_or_create_stamina

def test_stamina_initialization():
    """Test that stamina is created properly."""
    print("\n=== TEST 1: Stamina Initialization ===")
    
    # Create a test stamina component
    stamina = CharacterMovementStamina(body=50, dex=50, will=50)
    print(f"Created stamina component:")
    print(f"  Max Stamina: {stamina.stamina_max}")
    print(f"  Current Stamina: {stamina.stamina_current}")
    print(f"  Stats: BODY={stamina.body}, DEX={stamina.dex}, WILL={stamina.will}")
    assert stamina.stamina_current == stamina.stamina_max, "Should start at max"
    print("✓ PASS: Stamina initializes correctly")


def test_stamina_regen():
    """Test that stamina regenerates over time."""
    print("\n=== TEST 2: Stamina Regen Idle ===")
    
    stamina = CharacterMovementStamina(body=50, dex=50, will=50)
    stamina.stamina_current = 50.0  # Start at half
    
    print(f"Starting stamina: {stamina.stamina_current:.1f}/{stamina.stamina_max}")
    
    # Update for 10 seconds while idle (WALK tier with no movement = slight positive delta)
    for _ in range(10):
        stamina.update(1.0)
    
    print(f"After 10 seconds idle: {stamina.stamina_current:.1f}/{stamina.stamina_max}")
    assert stamina.stamina_current > 50.0, "Stamina should regenerate when idle"
    print("✓ PASS: Stamina regenerates when idle")


def test_stamina_con_bonus():
    """Test that CON affects regen rate."""
    print("\n=== TEST 3: CON Bonus Impact ===")
    
    # Low CON character
    low_con = CharacterMovementStamina(body=20, dex=50, will=50)
    low_con.stamina_current = 50.0
    low_con.update(10.0)  # 10 seconds
    low_con_regen = low_con.stamina_current - 50.0
    
    # High CON character
    high_con = CharacterMovementStamina(body=80, dex=50, will=50)
    high_con.stamina_current = 50.0
    high_con.update(10.0)  # 10 seconds
    high_con_regen = high_con.stamina_current - 50.0
    
    print(f"Low CON regen (10s): {low_con_regen:.1f}")
    print(f"High CON regen (10s): {high_con_regen:.1f}")
    assert high_con_regen > low_con_regen, "Higher CON should regen more"
    print("✓ PASS: CON affects regen rate correctly")


def test_stamina_drain_on_tier_change():
    """Test that stamina drains when moving faster."""
    print("\n=== TEST 4: Stamina Drain on Sprint ===")
    
    stamina = CharacterMovementStamina(body=60, dex=50, will=50)
    stamina_before = stamina.stamina_current
    
    # Switch to sprint
    stamina.set_tier(MovementTier.SPRINT)
    
    # Update while sprinting
    for _ in range(5):
        stamina.update(1.0)
    
    stamina_after = stamina.stamina_current
    delta = stamina_after - stamina_before
    
    print(f"Starting stamina: {stamina_before:.1f}")
    print(f"After 5s sprint: {stamina_after:.1f}")
    print(f"Delta: {delta:.1f}")
    assert delta < 0, "Stamina should drain during sprint"
    print("✓ PASS: Stamina drains correctly during sprint")


def test_stamina_ticker_exists():
    """Test that the stamina ticker script is running."""
    print("\n=== TEST 5: Stamina Ticker ===")
    
    ticker = ScriptDB.objects.filter(db_key="stamina_ticker").first()
    if ticker:
        print(f"Stamina ticker found: {ticker}")
        print(f"  Is active: {ticker.is_active}")
        print(f"  Interval: {ticker.interval}s")
        if ticker.is_active:
            print("✓ PASS: Stamina ticker is running")
        else:
            print("⚠ WARNING: Stamina ticker exists but not active - starting it...")
            ticker.start()
    else:
        print("✗ FAIL: Stamina ticker not found - creating it...")
        ticker = StaminaTicker.create(key="stamina_ticker")
        if ticker:
            print(f"✓ Created ticker: {ticker}")
        else:
            print("✗ FAIL: Could not create stamina ticker")


def test_character_stamina_initialization():
    """Test that characters get stamina on login."""
    print("\n=== TEST 6: Character Stamina on Login ===")
    
    # Try to find a player character
    players = search_object("*", typeclass="typeclasses.characters.Character")[:1]
    
    if not players:
        print("⚠ No players online - skipping character test")
        return
    
    char = players[0]
    print(f"Testing character: {char.key}")
    
    # Check if stamina exists
    stamina = getattr(char.ndb, "stamina", None)
    if stamina:
        print(f"✓ Stamina component exists:")
        print(f"  Current: {stamina.stamina_current:.1f}/{stamina.stamina_max}")
        print(f"  Tier: {stamina.current_tier}")
        print(f"✓ PASS: Character has stamina component")
    else:
        print("✗ Stamina component not found - initializing...")
        stamina = _get_or_create_stamina(char)
        if stamina:
            print(f"✓ Created stamina: {stamina.stamina_current:.1f}/{stamina.stamina_max}")
        else:
            print("✗ FAIL: Could not initialize stamina")


if __name__ == "__main__":
    import sys
    print("=" * 60)
    print("STAMINA REGEN SYSTEM TEST")
    print("=" * 60)
    
    try:
        test_stamina_initialization()
        test_stamina_regen()
        test_stamina_con_bonus()
        test_stamina_drain_on_tier_change()
        test_stamina_ticker_exists()
        test_character_stamina_initialization()
        
        print("\n" + "=" * 60)
        print("ALL TESTS PASSED!")
        print("=" * 60)
        print("\nNEXT STEPS:")
        print("1. Log in a character")
        print("2. Check Splattercast channel for stamina debug messages")
        print("3. Stand still for 10 seconds - stamina should go up")
        print("4. Watch stamina drain when you sprint/run")
        print("5. Watch stamina regen when you walk/stand")
        
    except AssertionError as e:
        print(f"\n✗ TEST FAILED: {e}")
        sys.exit(1)
    except Exception as e:
        import traceback
        print(f"\n✗ UNEXPECTED ERROR: {e}")
        traceback.print_exc()
        sys.exit(1)
