# SafetyNet Device Spawning - Staff Quick Reference

## Quick Spawn Commands

Staff can quickly spawn SafetyNet access devices using these commands:

### Main Command: @spawnsn

```
@spawnsn wristpad           - Spawn a standard wristpad
@spawnsn wristpad/deluxe    - Spawn a deluxe wristpad (bonus features)
@spawnsn computer           - Spawn a desktop computer terminal
@spawnsn computer/personal  - Spawn a personal computer
@spawnsn computer/portable  - Spawn a portable laptop-style computer
```

### Quick Shortcuts

```
@wristpad           - Instantly spawn a wristpad
@computer           - Instantly spawn a computer terminal
@portablecomp       - Instantly spawn a portable computer
```

## Device Specifications

### Wristpads

| Model | Speed | Weight | Wearable | Cost (IC) |
|-------|-------|--------|----------|-----------|
| Standard | Slow (2-5s) | 0.3 lbs | Yes (wrist) | Budget |
| Deluxe | Slow (2-5s) | 0.4 lbs | Yes (wrist) | Premium |

**Use Case**: Mobile access for runners and street operators

### Computers

| Model | Speed | Weight | Portable | Cost (IC) |
|-------|-------|--------|----------|-----------|
| Terminal | Fast (0.3-1s) | 25 lbs | No | Corporate |
| Personal | Fast (0.3-1s) | 3.5 lbs | Yes | Mid-range |
| Portable | Fast (0.3-1s) | 3.5 lbs | Yes | Mid-range |

**Use Case**: Fixed-location fast access or mobile high-speed terminal

## Device Properties

### Wristpad

```
Location: Worn on wrist
Armor Layer: 5 (wrist slot)
Weight: 0.3-0.4 lbs
Connection Speed: Slow (dial-up atmosphere)
SafetyNet Access: YES (is_wristpad=True)
Locked: Not pickupable (removable)
```

### Computer Terminal

```
Location: Room (stationary)
Size: Large desk unit
Weight: 25 lbs
Connection Speed: Fast
SafetyNet Access: YES (is_computer=True)
Locked: NOT pickupable (@get returns failure)
Features: Multiple workstations possible
```

### Portable Computer

```
Location: Inventory
Size: Laptop-like
Weight: 3.5 lbs
Connection Speed: Fast
SafetyNet Access: YES (is_computer=True)
Locked: Pickupable and portable
Features: Mobile fast access
```

## Installation Locations

### For Corps/Businesses

- Computer Terminal in corporate office/workspace
- One per major room for accessibility
- Can be locked down by location builder

### For Street Level

- Wristpads scattered in various locations for player use
- Public computer terminals in cafes, bars, street markets
- Allows characters without access to use system

### For Personal Use

- Portable computers in player private rooms
- Wristpads as personal equipment
- Characters can carry their own access device

## Administrative Operations

### Checking Spawned Devices

```
@find typeclasses.items.Wristpad
@find typeclasses.items.ComputerTerminal
@find typeclasses.items.PortableComputer
```

### Modifying Device Properties

Access a spawned device directly:

```
@set <device>#db_weight = 0.3          # Change weight
@set <device>#db_desc = "Your description here"  # Change appearance
```

### Restricting Device Access

Make a device non-pickupable:

```
@lock <device> = get:false()
```

Allow picking up:

```
@lock <device> = get:true()
```

## Device Descriptions

Players see these when examining devices:

### Wristpad (Standard)

```
This sleek wrist-mounted computer displays a glowing screen. The interface
is intuitive but clearly designed for quick queries rather than extended
work sessions. You can feel the connection speed might be a bit sluggish,
typical of mobile devices on the network.
```

### Wristpad (Deluxe)

```
This premium wrist-mounted computer features a brighter display and more
responsive interface than the standard model. Despite its portable nature,
the connection quality is noticeably better. A status light pulses gently
on the edge of the display.
```

### Computer Terminal

```
A full-sized computer terminal sits on the desk or console. The screen is
bright and responsive, with a full keyboard and mouse setup. This is clearly
the kind of system that gives you fast, reliable network access - though
you'll need to be in this location to use it.
```

### Portable Computer

```
A compact but capable computer that looks like a refined laptop. Despite
its portability, it maintains good processing power and network connection
speed. It's light enough to carry but substantial enough to feel reliable.
```

## Player Impact

### Gameplay Implications

**Wristpad Players**:
- Can access SafetyNet from anywhere
- Experience 2-5 second delays (immersive slowness)
- Limited but sufficient for quick posts/messages
- Cost-effective access

**Computer Players**:
- Fast access (0.3-1 second response times)
- Need to be at a specific location
- Better for research and complex operations
- More "professional" feel

### IC Justification

- **Wristpad**: Ubiquitous street tech, available everywhere, limited but functional
- **Computer**: Premium fixed installation, corporate or private
- **Portable**: Balance of convenience and capability

## Troubleshooting Device Spawning

### Device Won't Spawn

Check prototype exists:
```
py from evennia.prototypes import prototypes; print([p for p in prototypes.ALL_PROTOS if 'WRISTPAD' in p.get('key', '').upper()])
```

Check spelling:
```
@spawnsn wristpad    # Correct
@spawnsn wristPad    # Wrong - case sensitive in command args
```

### Device Disappears

Devices may be cleaned up if location is deleted. Use `@find` to locate:
```
@find typeclasses.items.Wristpad
```

### Access Not Working

Verify device has correct attribute:
```
py obj = search("wristpad")[0]; print(obj.db_is_wristpad, obj.db_is_computer)
```

Should print: `True False` for wristpad, `False True` for computer

## Best Practices

1. **Public Access**: Place at least one device in major hubs (marketplace, cantina, corporate lobby)
2. **Personal Devices**: Allow characters to request personal devices for their rooms
3. **Mobile Access**: Encourage wristpad use for immersive "on-the-go" roleplaying
4. **Performance**: Don't spawn more than needed - each device adds minimal but measurable load
5. **Immersion**: Consider device placement as part of zone design:
   - Corporate zones: Computers
   - Street areas: Wristpads
   - Neutral zones: Both

## Documentation

- Player Guide: [SAFETYNET_PLAYER_GUIDE.md](SAFETYNET_PLAYER_GUIDE.md)
- Staff Guide: [SAFETYNET_STAFF_GUIDE.md](SAFETYNET_STAFF_GUIDE.md)

---

**Last Updated**: January 14, 2026
