# NPC Wandering System - Setup & Testing Guide

## Quick Start

### 1. Ensure Rooms Have Zones

First, your rooms need `zone` attributes. You can set them via:

```
@set <room> zone = market_district
```

Or programmatically in a room's code:
```python
zone = AttributeProperty(default="market_district", autocreate=True)
```

### 2. Create NPC Templates with Wandering Zones

Use the new builder system:

```
designnpc
```

Follow the menu:
1. Enter NPC name (e.g., "Street Vendor")
2. Enter description
3. **Enter wandering zone** (e.g., "market_district")
4. Configure stats and skills
5. Save

### 3. Spawn NPCs

```
spawnnpc [name or id]
```

Select the NPC template. If it has a wandering zone set, it will:
- Automatically start wandering
- Move between rooms in that zone only
- Never leave the zone

## Testing the System

### Test 1: Basic Wandering

1. **Create a test zone with 3 rooms:**
   ```
   @create room "Test Room 1" = typeclasses.rooms:Room
   @create room "Test Room 2" = typeclasses.rooms:Room
   @create room "Test Room 3" = typeclasses.rooms:Room
   ```

2. **Assign zones:**
   ```
   @set Test Room 1 zone = test_zone
   @set Test Room 2 zone = test_zone
   @set Test Room 3 zone = test_zone
   ```

3. **Connect with exits:**
   ```
   @open north from Test Room 1 to Test Room 2
   @open south from Test Room 2 to Test Room 1
   @open east from Test Room 1 to Test Room 3
   @open west from Test Room 3 to Test Room 1
   ```

4. **Create NPC template:**
   ```
   designnpc
   - Name: "Test Wanderer"
   - Description: "A test NPC"
   - Zone: "test_zone"
   - Stats/Skills: default values
   - Save
   ```

5. **Spawn NPC:**
   ```
   spawnnpc Test Wanderer
   ```

6. **Observe wandering:**
   - Stay in Test Room 1
   - Wait 10-30 seconds
   - You should see: "|r[NPC Name] wanders away.|n"
   - Go to other rooms and see the NPC appear
   - NPC will never leave the test_zone

### Test 2: Zone Boundary Enforcement

1. **Create a second zone:**
   ```
   @create room "Other Zone Room" = typeclasses.rooms:Room
   @set Other Zone Room zone = other_zone
   ```

2. **Connect to test zone (but verify zone mismatch):**
   ```
   @open north from Test Room 3 to Other Zone Room
   ```

3. **Spawn NPC and observe:**
   - Even though there's an exit to other_zone
   - NPC will NEVER use that exit
   - NPC stays entirely within test_zone

### Test 3: Management Commands

```
# Check wandering status
npcwander <npc_name> = status

# List zone rooms
npcwander zone market_district

# Disable wandering
npcwander <npc_name> = disable

# Change wandering zone
npcwander <npc_name> = zone different_zone

# Re-enable wandering
npcwander <npc_name> = enable test_zone
```

### Test 4: Puppeting Override

```
# Puppet an NPC (wandering stops)
puppet <npc_name>
```

While puppeting:
- NPC doesn't wander
- You have full control
- Movement messages still show

```
# Unpuppet (wandering resumes)
@puppet release
```

After unpuppeting:
- Wandering automatically resumes
- NPC continues its patrol

### Test 5: Combat Interaction

```
# Attack an NPC
attack <npc_name>
```

During combat:
- NPC stops wandering
- Combat proceeds normally
- After combat ends, wandering resumes

## Troubleshooting Tests

### NPC Not Wandering?

1. **Check if wandering is enabled:**
   ```
   npcwander vendor = status
   ```
   Look for `Wandering Enabled: Yes`

2. **Check zone is set:**
   ```
   npcwander vendor = status
   ```
   Look for `Wandering Zone: market_district` (not "None")

3. **Check zone has rooms:**
   ```
   npcwander zone market_district
   ```
   Should show at least 2 rooms

4. **Check NPC isn't puppeted:**
   ```
   npcwander vendor = status
   ```
   Look for `Currently Puppeted: No`

5. **Check NPC isn't in combat:**
   - If fighting, wait for combat to end
   - NPC should resume wandering after

### NPC Leaves Zone?

If an NPC somehow leaves their zone (shouldn't happen):

1. **Check exit configuration:**
   - Verify exit destination rooms have correct zone
   ```
   look <destination_room>
   ```

2. **Check room zone is set:**
   ```
   @set <room> zone = correct_zone
   ```

3. **Teleport NPC back:**
   ```
   @teleport <npc> to <correct_room>
   ```

4. **Report bug with:**
   - NPC name and ID
   - Source room and destination
   - Expected zone

### Performance Issues

If too many NPCs are wandering:

1. **Check active NPCs:**
   ```
   npcwander zone market_district
   ```

2. **Reduce number of wandering NPCs:**
   ```
   npcwander <npc_name> = disable
   ```

3. **Or increase check interval** in `scripts/npc_wandering.py`:
   ```python
   self.interval = 30  # Check every 30 seconds instead of 15
   ```

## Configuration Examples

### Market with Multiple Vendors

```
Zones:
- main_square (zone: market_main)
- fruit_stand (zone: market_main)
- spice_vendor (zone: market_main)
- fish_market (zone: market_main)

NPCs to Create:
1. "Fruit Vendor" → zone: market_main
2. "Spice Merchant" → zone: market_main
3. "Fish Seller" → zone: market_main
```

All three will wander between the 4 rooms, creating a lively market.

### Guard Patrol Route

```
Zones:
- guard_post (zone: fortress_guard)
- north_tower (zone: fortress_guard)
- south_tower (zone: fortress_guard)
- main_gate (zone: fortress_guard)

NPC to Create:
1. "Guard Captain" → zone: fortress_guard

Result: Guard patrols all fortress areas
```

### Street Level Bums

```
Zones:
- alley_north (zone: slums_alley)
- alley_central (zone: slums_alley)
- alley_south (zone: slums_alley)

NPCs to Create:
1. "Drunk Vagrant" → zone: slums_alley
2. "Street Beggar" → zone: slums_alley
3. "Alley Cat" → zone: slums_alley

Result: Multiple low-level NPCs wander alley areas
```

## Verification Checklist

Before using NPCs in a zone:

- [ ] Zone name is descriptive (e.g., "market_main" not "z1")
- [ ] All rooms have matching zone attributes
- [ ] At least 2 rooms in each zone
- [ ] Rooms are connected with proper exits
- [ ] NPC templates created with correct zones
- [ ] NPCs spawn successfully
- [ ] NPCs wander within zone boundaries
- [ ] Management commands work
- [ ] Puppeting works
- [ ] Combat integration works

## Advanced Testing

### Load Testing

Create many NPCs to test performance:

```python
# Via Python shell or script
from commands.builder_spawners import *
from world.builder_storage import search_npcs

npc_template = search_npcs("Test Wanderer")[0]
for i in range(20):
    # Spawn 20 copies
    # Monitor system performance
```

### Zone Boundary Testing

Create complex zone maps:

```
Z1: Rooms A, B, C
Z2: Rooms D, E (adjacent to Z1)
Z3: Rooms F, G, H (surrounded by Z2)

Spawn NPCs in Z3, verify they:
- Never enter Z1 or Z2
- Only move within Z3
```

### State Persistence Testing

```
1. Spawn NPC (npcwander = enable market_zone)
2. Reload server
3. Verify NPC still wandering in same zone
```

NPCs should remember their wandering state across reboots.

## Reporting Issues

If you find bugs, report with:

1. **NPC Name/ID**
2. **Zone Name**
3. **Rooms in Zone**
4. **Expected Behavior**
5. **Actual Behavior**
6. **Steps to Reproduce**
7. **Error Messages** (from logs if any)

Example:
```
Bug: Vendor left market_zone
- NPC: Street Vendor (#123)
- Zone: market_district
- Expected: Stay in market_district only
- Actual: Found in outer_district
- Steps:
  1. Spawn Street Vendor in merchant_square
  2. Wait 2 minutes
  3. Check other zones
- Notes: This happened 3 times during testing
```

## Performance Notes

- ✅ System checks every 15 seconds
- ✅ Each NPC has 30% chance to move per check
- ✅ Multiple NPCs don't stack performance
- ✅ Compatible with combat system
- ✅ Compatible with puppeting system
- ✅ Survives server reloads

Expected performance overhead: Minimal
- ~10 NPCs wandering: negligible impact
- ~50 NPCs wandering: <1% CPU overhead
- ~200+ NPCs wandering: consider spreading zones

## Success Indicators

You'll know the system is working when:

1. ✅ NPCs move between rooms in their zone
2. ✅ Movement happens automatically (no admin input)
3. ✅ NPCs never leave assigned zone
4. ✅ Puppeting stops wandering
5. ✅ Combat stops wandering
6. ✅ Wandering resumes after interruptions
7. ✅ Management commands work
8. ✅ State persists through reloads
