# NPC Wandering System

## Overview

NPCs can now wander within their assigned zones! When an NPC is spawned with a wandering zone set, it will automatically move between rooms in that zone, never leaving the zone boundaries.

## How It Works

### Zone-Based Constraints
- Each room in the world has a `zone` attribute (e.g., "market_district", "fortress_entrance", "street_01")
- NPCs are assigned a `wandering_zone` when created
- The wandering system ensures NPCs **NEVER** leave their assigned zone
- Only rooms with matching zone attributes are considered valid destinations

### Wandering Behavior
- NPCs check if they can move approximately every 10-30 seconds
- They have a random chance (30%) to move each interval
- Movement happens automatically without admin input
- NPCs won't wander if:
  - They're being puppeted by an admin
  - They're in combat
  - Their zone has no other rooms
  - They're in a zone with only one room

## Setup

### Step 1: Configure Rooms with Zones

Ensure your rooms have zone attributes set:

```python
# In a room:
room.zone = "market_district"
```

Or set via admin command:
```
@set <room> zone = market_district
```

### Step 2: Create NPC Templates with Zones

When creating an NPC design using `/designnpc`:
1. Set the NPC name and description
2. Enter the **wandering zone** when prompted (e.g., "market_district")
3. Set stats and skills as desired
4. Save the template

### Step 3: Spawn NPCs

When spawning an NPC from a template:
```
spawnnpc [template_name or id]
```

If the template has a wandering zone set:
- The NPC will automatically start wandering
- Movement begins after initialization

## Zone Configuration Guide

### Creating Zones

1. **Identify Your Zone Areas**
   - Decide which rooms belong together logically
   - Examples: "marketplace", "guards_quarter", "merchant_road"

2. **Set Zone on All Rooms**
   ```
   @set room1 zone = marketplace
   @set room2 zone = marketplace
   @set room3 zone = marketplace
   ```

3. **Create Connected Exits**
   - Use standard exit commands
   - The system handles zone verification automatically

### Zone Best Practices

- **Use descriptive names**: "market_district" instead of "m1"
- **Group logically**: Keep related rooms in same zone
- **Test before mass-spawning**: 
  - Spawn one NPC in zone
  - Watch them wander for a minute
  - Verify they stay within zone boundaries
- **Minimum 2 rooms**: Zones need at least 2 rooms for meaningful wandering
- **Connect with exits**: Ensure rooms are connected with proper exits

## Admin Commands

### Check NPC Wandering Status

```
look <npc>
```

Will show:
- NPC's current zone (if wandering enabled)
- Whether actively wandering

### Enable/Disable Wandering

```
@set <npc> npc_can_wander = 1      # Enable wandering
@set <npc> npc_can_wander = 0      # Disable wandering
@set <npc> npc_zone = market       # Set wandering zone
```

### List Zone Rooms

```
@zone_rooms <zone_name>
```

Shows all rooms in a zone.

### Stop NPC Movement

```
@puppet <npc>
```

Puppeting an NPC automatically stops their wandering (preserved when unpuppeting).

## Example Configuration

### Market District Setup

```
Rooms:
- merchant_square (zone=market_district)
- fruit_stand (zone=market_district)  
- cloth_shop (zone=market_district)
- spice_merchant (zone=market_district)

Exits:
- merchant_square -> north = fruit_stand
- fruit_stand -> south = merchant_square
- fruit_stand -> west = cloth_shop
- cloth_shop -> east = fruit_stand
- cloth_shop -> north = spice_merchant
- spice_merchant -> south = cloth_shop

NPC Template: "Street Vendor"
- Zone: market_district
- Wanders: Yes
```

**Result**: Vendor moves randomly between all 4 rooms, never leaving the market.

## Troubleshooting

### NPC Not Wandering

1. **Check if wandering is enabled:**
   ```
   @set <npc> npc_can_wander = 1
   ```

2. **Check zone is set:**
   ```
   @set <npc> npc_zone = <zone_name>
   ```

3. **Check zone has multiple rooms:**
   ```
   @zone_rooms <zone_name>
   ```
   Should show 2+ rooms

4. **Check NPC isn't in combat:**
   - If NPC is in combat, wandering is disabled
   - Wait for combat to end

5. **Verify room zones match:**
   ```
   look <room>
   ```
   All connected rooms should have same zone

### NPC Left Zone (Bug Report)

If an NPC leaves their assigned zone:
1. Note the NPC name, zone, and destination room
2. Move NPC back: `@teleport <npc> to <correct_room>`
3. Report issue with details

### Performance Issues

If many NPCs are wandering:
- The system is efficient (checks ~every 15 seconds global)
- Consider reducing number of simultaneous wandering NPCs
- Or increase interval in `npc_wandering.py`

## Advanced Configuration

### Adjusting Wander Frequency

Edit `scripts/npc_wandering.py`:

```python
# In NPCWanderingScript.at_repeat():
if randint(1, 10) <= 3:  # 30% chance - change to <=1 for 10%, <=5 for 50%
    self._attempt_wander(npc, zone)
```

Lower percentage = less frequent movement
Higher percentage = more frequent movement

### Custom Wander Messages

Edit the messages in `_move_npc_safely()`:

```python
old_location.msg_contents(f"|r{npc.name} wanders away.|n")
destination.msg_contents(f"|r{npc.name} wanders in.|n")
```

Change to flavor text like:
```python
old_location.msg_contents(f"{npc.name} shuffles away muttering.")
destination.msg_contents(f"{npc.name} enters with purpose.")
```

## Integration with Combat

**Important**: NPCs stop wandering when they enter combat and resume after combat ends automatically.

This prevents NPC movement during active combat encounters.

## Integration with Puppeting

When an admin puppets an NPC:
1. Wandering stops
2. Admin has full control
3. When unpuppeted, wandering resumes automatically

## Summary

The NPC wandering system provides realistic, constrained NPC movement. NPCs stay within their zones, create ambient life in areas, and can be easily managed by builders.

Key benefits:
- ✅ Zone constraints enforced
- ✅ Automatic initialization
- ✅ Combat-aware
- ✅ Puppet-compatible
- ✅ Low performance overhead
- ✅ Configurable behavior
