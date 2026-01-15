"""
Test script to verify grapple messages show disguised names correctly.
"""

from evennia.scripts.models import ScriptDB
from evennia.utils import evtable
from world.combat.handler import msg_contents_disguised, get_or_create_combat, CombatHandler
from world.combat.utils import get_display_name_safe
from world.disguise.core import get_display_identity


def test_grapple_messages():
    """Test that grapple messages use disguised names for observers."""
    from evennia import create_object
    from evennia.objects import ObjectDB
    from typeclasses.characters import Character
    from typeclasses.rooms import Room
    
    # Clean up any existing test objects
    test_objs = ObjectDB.objects.filter(db_key__istartswith="TestGrapple")
    for obj in test_objs:
        obj.delete()
    
    # Create test room
    room = create_object(Room, key="TestGrappleRoom")
    
    # Create two test characters
    attacker = create_object(Character, key="Dalao", location=room)
    victim = create_object(Character, key="TestDummy", location=room)
    
    # Give attacker a disguise
    attacker.db.disguise_name = "a masked individual"
    attacker.db.disguise_description = "A mysterious masked figure"
    attacker.db.is_disguised = True
    
    # Test 1: get_display_name_safe
    print("=" * 60)
    print("TEST 1: get_display_name_safe")
    print("=" * 60)
    
    # Attacker sees their own name
    attacker_view = get_display_name_safe(attacker, attacker)
    print(f"Attacker's view of self: {attacker_view}")
    
    # Victim sees disguised name
    victim_view = get_display_name_safe(attacker, victim)
    print(f"Victim's view of attacker: {victim_view}")
    
    # Test 2: msg_contents_disguised
    print("\n" + "=" * 60)
    print("TEST 2: msg_contents_disguised")
    print("=" * 60)
    
    # Set up test message handler
    test_messages = []
    original_msg = victim.msg
    
    def capture_msg(msg):
        test_messages.append(msg)
        original_msg(msg)
    
    victim.msg = capture_msg
    
    # Test the grapple message format
    msg_contents_disguised(
        room,
        "{char0_name} grapples {char1_name}!",
        [attacker, victim],
        exclude=[attacker, victim]
    )
    
    print(f"Observer messages captured: {len(test_messages)}")
    for msg in test_messages:
        print(f"  Message: {msg}")
    
    # Test 3: Check against observer outside combat
    print("\n" + "=" * 60)
    print("TEST 3: Observer verification")
    print("=" * 60)
    
    observer = create_object(Character, key="Observer", location=room)
    observer_messages = []
    
    def capture_observer_msg(msg):
        observer_messages.append(msg)
    
    observer.msg = capture_observer_msg
    
    msg_contents_disguised(
        room,
        "{char0_name} maintains a restraining hold on {char1_name}.",
        [attacker, victim],
        exclude=[attacker, victim]
    )
    
    if observer_messages:
        print(f"Observer saw: {observer_messages[0]}")
        # Should NOT contain "Dalao", should contain "a masked individual"
        if "Dalao" in observer_messages[0]:
            print("ERROR: Real name 'Dalao' visible to observer!")
        elif "masked individual" in observer_messages[0]:
            print("SUCCESS: Disguised name visible to observer!")
        else:
            print(f"UNKNOWN: Message was '{observer_messages[0]}'")
    else:
        print("ERROR: No messages captured!")
    
    # Clean up
    print("\n" + "=" * 60)
    print("CLEANUP")
    print("=" * 60)
    
    room.delete()
    attacker.delete()
    victim.delete()
    observer.delete()
    
    print("Test complete!")


if __name__ == "__main__":
    test_grapple_messages()
