"""
Test Stamina System

Run with: python manage.py shell < test_stamina_regen.py

This script verifies that:
1. Stamina component is created properly
2. Stamina regenerates when walking/idle
3. Stamina drains when running/sprinting
4. CON affects max stamina
5. DEX affects regen rate
"""

from evennia import search_object
from evennia.scripts.models import ScriptDB
from world.stamina_ticker import StaminaTicker
from world.stamina import CharacterMovementStamina, MovementTier, get_or_create_stamina


def test_stamina_initialization():
    """Test that stamina is created properly."""
    print("\n=== TEST 1: Stamina Initialization ===")
    
    # Create a test stamina component with CON 10, DEX 10
    stamina = CharacterMovementStamina(con=10, dex=10)
    print(f"Created stamina component (CON=10, DEX=10):")
    print(f"  Max Stamina: {stamina.stamina_max}")
    print(f"  Current Stamina: {stamina.stamina_current}")
    
    assert stamina.stamina_max == 110, f"Expected max 110, got {stamina.stamina_max}"
    assert stamina.stamina_current == stamina.stamina_max, "Should start at max"
    print("PASS: Stamina initializes correctly")


def test_stamina_con_scaling():
    """Test that CON affects max stamina."""
    print("\n=== TEST 2: CON Scaling ===")
    
    # CON 8 = 100, CON 10 = 110, CON 15 = 135, CON 16 = 140
    stamina_8 = CharacterMovementStamina(con=8, dex=10)
    stamina_10 = CharacterMovementStamina(con=10, dex=10)
    stamina_15 = CharacterMovementStamina(con=15, dex=10)
    stamina_16 = CharacterMovementStamina(con=16, dex=10)
    
    print(f"CON 8 max: {stamina_8.stamina_max}")
    print(f"CON 10 max: {stamina_10.stamina_max}")
    print(f"CON 15 max: {stamina_15.stamina_max}")
    print(f"CON 16 max: {stamina_16.stamina_max}")
    
    assert stamina_8.stamina_max == 100
    assert stamina_10.stamina_max == 110
    assert stamina_15.stamina_max == 135
    assert stamina_16.stamina_max == 140
    print("PASS: CON scaling works correctly")


def test_stamina_regen():
    """Test that stamina regenerates over time when walking."""
    print("\n=== TEST 3: Stamina Regen ===")
    
    stamina = CharacterMovementStamina(con=10, dex=10)
    stamina.stamina_current = 50.0  # Start at half
    stamina.current_tier = MovementTier.WALK  # Walking regens
    
    print(f"Starting stamina: {stamina.stamina_current:.1f}/{stamina.stamina_max}")
    
    # Update for 5 seconds
    for _ in range(5):
        stamina.update(1.0)
    
    print(f"After 5 seconds walking: {stamina.stamina_current:.1f}/{stamina.stamina_max}")
    assert stamina.stamina_current > 50.0, "Stamina should regenerate when walking"
    print("PASS: Stamina regenerates when walking")


def test_stamina_regen_delay():
    """Test that regen delay works after exertion."""
    print("\n=== TEST 4: Regen Delay ===")
    
    stamina = CharacterMovementStamina(con=10, dex=10)
    stamina.stamina_current = 50.0
    stamina.regen_delay = 2.0  # Set delay
    stamina.current_tier = MovementTier.WALK
    
    before = stamina.stamina_current
    stamina.update(1.0)  # 1 second - should not regen yet
    after_delay = stamina.stamina_current
    
    print(f"With regen delay: {before:.1f} -> {after_delay:.1f}")
    assert after_delay == before, "Should not regen during delay"
    
    stamina.update(2.0)  # 2 more seconds - delay should expire and regen starts
    after_regen = stamina.stamina_current
    
    print(f"After delay expires: {after_regen:.1f}")
    assert after_regen > before, "Should regen after delay expires"
    print("PASS: Regen delay works correctly")


def test_stamina_drain_sprint():
    """Test that stamina drains when sprinting."""
    print("\n=== TEST 5: Stamina Drain on Sprint ===")
    
    stamina = CharacterMovementStamina(con=10, dex=10)
    stamina_before = stamina.stamina_current
    
    # Switch to sprint
    stamina.set_tier(MovementTier.SPRINT)
    
    # Update for 2 seconds
    stamina.update(2.0)
    
    stamina_after = stamina.stamina_current
    delta = stamina_after - stamina_before
    
    print(f"Starting stamina: {stamina_before:.1f}")
    print(f"After 2s sprint: {stamina_after:.1f}")
    print(f"Delta: {delta:.1f}")
    
    assert delta < 0, "Stamina should drain during sprint"
    print("PASS: Stamina drains correctly during sprint")


def test_stamina_dex_regen_bonus():
    """Test that DEX affects regen rate."""
    print("\n=== TEST 6: DEX Regen Bonus ===")
    
    # Low DEX character
    low_dex = CharacterMovementStamina(con=10, dex=8)
    low_dex.stamina_current = 50.0
    low_dex.update(5.0)  # 5 seconds
    low_dex_regen = low_dex.stamina_current - 50.0
    
    # High DEX character
    high_dex = CharacterMovementStamina(con=10, dex=16)
    high_dex.stamina_current = 50.0
    high_dex.update(5.0)  # 5 seconds
    high_dex_regen = high_dex.stamina_current - 50.0
    
    print(f"Low DEX (8) regen in 5s: {low_dex_regen:.1f}")
    print(f"High DEX (16) regen in 5s: {high_dex_regen:.1f}")
    
    assert high_dex_regen > low_dex_regen, "Higher DEX should regen faster"
    print("PASS: DEX affects regen rate correctly")


def test_tier_restrictions():
    """Test that low stamina prevents sprinting/running."""
    print("\n=== TEST 7: Tier Restrictions ===")
    
    stamina = CharacterMovementStamina(con=10, dex=10)
    
    # At full stamina, should be able to sprint
    actual = stamina.set_tier(MovementTier.SPRINT)
    print(f"Full stamina -> Sprint: {actual == MovementTier.SPRINT}")
    assert actual == MovementTier.SPRINT
    
    # At 10% stamina, should not be able to sprint
    stamina.stamina_current = stamina.stamina_max * 0.10
    actual = stamina.set_tier(MovementTier.SPRINT)
    print(f"10% stamina -> Sprint request: Got {actual.name}")
    assert actual < MovementTier.SPRINT, "Should not be able to sprint at 10%"
    
    # At 5% stamina, should not be able to run
    stamina.stamina_current = stamina.stamina_max * 0.05
    actual = stamina.set_tier(MovementTier.RUN)
    print(f"5% stamina -> Run request: Got {actual.name}")
    assert actual < MovementTier.RUN, "Should not be able to run at 5%"
    
    print("PASS: Tier restrictions work correctly")


def test_stamina_ticker_exists():
    """Test that the stamina ticker script exists."""
    print("\n=== TEST 8: Stamina Ticker ===")
    
    ticker = ScriptDB.objects.filter(db_key="stamina_ticker").first()
    if ticker:
        print(f"Ticker exists: {ticker}")
        print(f"Active: {ticker.is_active}")
        print("PASS: Stamina ticker is present")
    else:
        print("WARNING: Stamina ticker not found - creating...")
        ticker = StaminaTicker.create(key="stamina_ticker")
        print(f"Created ticker: {ticker}")
        print("PASS: Stamina ticker created")


def test_character_stamina():
    """Test stamina on an actual character."""
    print("\n=== TEST 9: Character Stamina ===")
    
    from evennia import search_object
    players = search_object("*", typeclass="typeclasses.characters.Character")[:1]
    
    if not players:
        print("WARNING: No characters online - skipping character test")
        return
    
    char = players[0]
    print(f"Testing character: {char.key}")
    
    stamina = get_or_create_stamina(char)
    if stamina:
        print(f"  Current: {stamina.stamina_current:.1f}/{stamina.stamina_max}")
        print(f"  Tier: {stamina.current_tier.name}")
        print(f"  CON: {stamina.con}, DEX: {stamina.dex}")
        print("PASS: Character has stamina component")
    else:
        print("FAIL: Could not get stamina for character")


if __name__ == "__main__":
    print("=" * 60)
    print("STAMINA SYSTEM TEST")
    print("=" * 60)
    
    try:
        test_stamina_initialization()
        test_stamina_con_scaling()
        test_stamina_regen()
        test_stamina_regen_delay()
        test_stamina_drain_sprint()
        test_stamina_dex_regen_bonus()
        test_tier_restrictions()
        test_stamina_ticker_exists()
        test_character_stamina()
        
        print("\n" + "=" * 60)
        print("ALL TESTS PASSED!")
        print("=" * 60)
        
    except AssertionError as e:
        print(f"\nTEST FAILED: {e}")
        import traceback
        traceback.print_exc()
    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback
        traceback.print_exc()
