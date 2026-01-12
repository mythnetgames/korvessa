# Builder Item Creation System

A comprehensive system for Builders+ to create custom furniture, NPCs, weapons, and clothing/armor items without needing to modify code.

## Overview

This system provides interactive menus and spawn commands that allow builders to:
- **Design and create** custom items through guided menus
- **Store designs** persistently in the database
- **Spawn instances** of designs with easy-to-use search commands
- **Manage factions** for NPC organization
- **List all designs** they've created

## Quick Start

### Creating Furniture
```
designfurniture              # Start the furniture design menu
spawnfurniture              # List all furniture (then select by number)
spawnfurniture table        # Search furniture by keyword
```

### Creating NPCs
```
designnpc                   # Start the NPC design menu
spawnnpc                    # List all NPCs (then select by number)
spawnnpc vendor             # Search NPCs by keyword
```

### Creating Weapons
```
designweapon                # Start the weapon design menu
spawnweapon                 # List all weapons (then select by number)
spawnweapon pistol          # Search weapons by keyword
```

### Creating Clothing/Armor
```
designclothing              # Start the clothing/armor design menu
spawnclothing               # List all clothing (then select by number)
spawnclothing shirt         # Search clothing by keyword
spawnarmor                  # List all armor (then select by number)
spawnarmor kevlar           # Search armor by keyword
```

### Managing Items
```
listdesigns                 # List all your designs
listdesigns furniture       # List all furniture
listdesigns all            # List everything
managefactions             # Manage NPC factions
managefactions list        # List all factions
```

---

## Detailed Command Reference

### Design Commands

#### designfurniture
Creates a new furniture template through an interactive menu.

**Menu Steps:**
1. **Name** - Furniture name (e.g., "Oak Table", "Red Couch")
2. **Description** - What players see when they look at it
3. **Properties:**
   - Movable (can it be picked up?)
   - Max Seats (0 = can't sit)
   - Can Recline (furniture supports reclining)
   - Can Lie Down (furniture can be laid on)
4. **Messages** - Custom messages for each interaction type
   - First person: "You sit down on the..."
   - Third person: "{name} sits down on the..."

**Furniture Criteria:**
- **Movable**: Is the furniture portable?
- **Max Seats**: How many people can sit (0 = not sittable)
- **Recline**: Can users recline on it?
- **Lie Down**: Can users lie down on it?
- **Custom Messages**: Unique flavor text for interactions

**Example:**
```
designfurniture
Name: Leather Couch
Description: A plush leather couch, well-worn but comfortable.
Properties: Movable=Yes, Seats=3, Recline=Yes, LieDown=Yes
Messages: "You sink into the soft leather cushions..."
```

#### designnpc
Creates a new NPC template through an interactive menu.

**Menu Steps:**
1. **Name** - NPC name
2. **Description** - NPC appearance and description
3. **Properties:**
   - Faction (choose from existing or neutral)
   - Wandering Zone (leave empty for static)
   - Shopkeeper (is this NPC a merchant?)

**NPC Criteria:**
- **Name**: NPC identifier
- **Description**: Visual/narrative description
- **Faction**: Organizational affiliation
- **Wander Zone**: Zone ID for wandering behavior (optional)
- **Shopkeeper**: Does this NPC sell items?

**Example:**
```
designnpc
Name: Street Vendor
Description: A weathered merchant with a cart of goods.
Faction: Neutral
Wandering Zone: plaza_west
Shopkeeper: Yes
```

#### designweapon
Creates a new weapon template through an interactive menu.

**Menu Steps:**
1. **Name** - Weapon name
2. **Description** - Weapon appearance
3. **Type:**
   - Melee (knife, sword, club, etc.)
   - Ranged (gun, bow, etc.)
4. **Ammo Type** (if ranged) - e.g., "9mm", "arrow", "12gauge"
5. **Stats:**
   - Damage Bonus (-5 to +5)
   - Accuracy Bonus (-5 to +5)

**Weapon Criteria:**
- **Type**: Melee or Ranged
- **Ammo Type**: Required for ranged weapons
- **Damage Bonus**: How much extra damage does it deal?
- **Accuracy Bonus**: How much does it help with accuracy?

**Example:**
```
designweapon
Name: 9mm Pistol
Description: A worn but reliable pistol.
Type: Ranged
Ammo: 9mm
Damage: +1
Accuracy: +1
```

#### designclothing
Creates a new clothing or armor template through an interactive menu.

**Menu Steps:**
1. **Name** - Item name
2. **Description** - Item appearance
3. **Type:**
   - Clothing (no armor)
   - Armor (provides protection)
4. **If Armor:** Select armor type and value
   - Light (leather, cloth)
   - Medium (kevlar, composite)
   - Heavy (ballistic plates)
   - Armor Value (1-10)
5. **Rarity** - Common, Uncommon, Rare, Epic

**Clothing/Armor Criteria:**
- **Type**: Clothing or Armor
- **Armor Value**: Protection level (1-10, armor only)
- **Armor Type**: Light/Medium/Heavy (armor only)
- **Rarity**: Item rarity level

**Example - Clothing:**
```
designclothing
Name: Black T-Shirt
Description: A worn black cotton t-shirt.
Type: Clothing
Rarity: Common
```

**Example - Armor:**
```
designclothing
Name: Tactical Vest
Description: Military-grade body armor.
Type: Armor
Armor Type: Medium
Armor Value: 6
Rarity: Uncommon
```

### Spawn Commands

#### spawnfurniture [keyword]
Spawn furniture from templates.

```
spawnfurniture              # List all furniture
spawnfurniture table        # Search for furniture with "table" in name
spawnfurniture furniture_1  # Spawn specific design by ID
spawnfurniture 1            # Select first item from list
```

#### spawnnpc [keyword]
Spawn NPCs from templates.

```
spawnnpc                    # List all NPCs
spawnnpc vendor             # Search for NPCs with "vendor" in name
spawnnpc npc_1              # Spawn specific NPC by ID
spawnnpc 2                  # Select second item from list
```

#### spawnweapon [keyword]
Spawn weapons from templates.

```
spawnweapon                 # List all weapons
spawnweapon pistol          # Search for weapons with "pistol" in name
spawnweapon melee           # Search for melee weapons
spawnweapon weapon_1        # Spawn specific weapon by ID
```

#### spawnclothing [keyword]
Spawn clothing items from templates.

```
spawnclothing               # List all clothing
spawnclothing shirt         # Search for clothing with "shirt" in name
spawnclothing clothing_1    # Spawn specific clothing by ID
```

#### spawnarmor [keyword]
Spawn armor items from templates.

```
spawnarmor                  # List all armor
spawnarmor light            # Search for light armor
spawnarmor kevlar           # Search for armor with "kevlar" in name
spawnarmor armor_1          # Spawn specific armor by ID
```

### Management Commands

#### listdesigns [type]
List all designs created by builders.

```
listdesigns                 # List everything
listdesigns furniture       # List furniture only
listdesigns npcs            # List NPCs only
listdesigns weapons         # List weapons only
listdesigns clothing        # List clothing only
listdesigns armor           # List armor only
```

**Output shows:**
- Item name
- Item ID (used in spawn commands)
- Creator name
- Item type specific info

#### managefactions
Create and manage NPC factions.

**Subcommands:**
```
managefactions list                                    # List all factions
managefactions add <id> = <name> ; <description>      # Add new faction
managefactions delete <id>                            # Delete faction
```

**Example:**
```
managefactions list
managefactions add kowloon_gang = Kowloon Gang ; Street gang in Kowloon
managefactions add security = Kowloon Security ; Official security force
managefactions delete kowloon_gang
```

**Default Factions:**
- `neutral` - No faction affiliation
- `kowloon_citizens` - Local residents
- `kowloon_security` - Security forces

---

## Data Storage

All designs are stored persistently in the database using Evennia's ScriptDB system.

### Storage Structure

```
Builder Storage (ScriptDB: "builder_storage")
├── furniture[]          # Array of furniture designs
├── npcs[]               # Array of NPC templates
├── weapons[]            # Array of weapon templates
├── clothes[]            # Array of clothing items
├── armor[]              # Array of armor items
└── factions[]           # Array of factions
```

Each item contains:
- Unique ID (auto-generated)
- Name and description
- Type-specific properties
- Creator name
- Creation timestamp (optional)

### Spawned Object Attributes

When you spawn an item, it gets these database attributes:

**Furniture:**
```
obj.db.furniture_template_id    # Template ID
obj.db.max_seats                # Seating capacity
obj.db.is_movable               # Can be picked up
obj.db.can_lie_down             # Supports lying
obj.db.can_recline              # Supports reclining
```

**NPCs:**
```
npc.db.npc_template_id          # Template ID
npc.db.faction                  # Faction ID
npc.db.wandering_zone           # Zone for wandering
npc.db.is_shopkeeper            # Merchant flag
npc.db.is_npc                   # NPC flag
```

**Weapons:**
```
obj.db.weapon_template_id       # Template ID
obj.db.weapon_type              # "melee" or "ranged"
obj.db.ammo_type                # For ranged weapons
obj.db.damage_bonus             # Damage modifier
obj.db.accuracy_bonus           # Accuracy modifier
obj.db.is_weapon                # Weapon flag
```

**Clothing:**
```
obj.db.clothing_template_id     # Template ID
obj.db.rarity                   # Item rarity
obj.db.is_clothing              # Clothing flag
```

**Armor:**
```
obj.db.armor_template_id        # Template ID
obj.db.armor_type               # light/medium/heavy
obj.db.armor_value              # Protection rating
obj.db.rarity                   # Item rarity
obj.db.is_armor                 # Armor flag
```

---

## Workflow Examples

### Creating a Complete Bar Scene

1. **Create furniture:**
   ```
   designfurniture
   Name: Mahogany Bar Counter
   Description: A long, polished mahogany bar counter with brass rail.
   Movable: No, MaxSeats: 0
   
   designfurniture
   Name: Bar Stool
   Description: A worn leather bar stool.
   Movable: No, MaxSeats: 1
   ```

2. **Spawn furniture:**
   ```
   spawnfurniture bar
   1  # Select Mahogany Bar Counter
   
   spawnfurniture stool
   1  # Select Bar Stool (repeat as needed)
   ```

3. **Create bartender NPC:**
   ```
   designnpc
   Name: Bartender
   Description: A grizzled bartender with years of experience.
   Faction: neutral
   Wandering Zone: (empty - stays at bar)
   Shopkeeper: Yes
   ```

4. **Spawn bartender:**
   ```
   spawnnpc bartender
   1  # Select Bartender
   ```

### Creating Weapon Variants

1. **Design multiple weapons:**
   ```
   designweapon
   Name: Standard 9mm
   Type: Ranged
   Ammo: 9mm
   Damage: 0, Accuracy: 0
   
   designweapon
   Name: Custom 9mm
   Type: Ranged
   Ammo: 9mm
   Damage: +1, Accuracy: +1
   ```

2. **Spawn for testing:**
   ```
   spawnweapon 9mm
   # Lists both variants - choose as needed
   ```

### Setting Up Shop Stock

1. **Design clothing and armor:**
   ```
   designclothing → Leather Jacket, Common
   designclothing → Jeans, Common
   designarmor → Tactical Vest, Medium, Armor 6
   ```

2. **Create shopkeeper:**
   ```
   designnpc
   Name: Weapon Dealer
   Shopkeeper: Yes
   Faction: merchant_guild
   ```

3. **Spawn and configure:**
   ```
   spawnnpc weapon_dealer
   spawnweapon rifle
   spawnarmor vest
   ```

---

## Technical Details

### Python API

For programmers who want to interact with the storage programmatically:

```python
from world.builder_storage import (
    add_furniture, get_all_furniture, search_furniture,
    add_npc, get_all_npcs, search_npcs,
    add_weapon, get_all_weapons, search_weapons,
    add_clothing_item, get_all_clothing, search_clothing,
    get_all_armor, search_armor,
    add_faction, get_all_factions, search_factions
)

# Add furniture
furniture = add_furniture(
    name="Couch",
    desc="A comfortable couch",
    movable=False,
    max_seats=3,
    can_recline=True,
    can_lie_down=True,
    created_by="BuilderName"
)

# Search
results = search_furniture("table")

# Get specific item
item = get_furniture_by_id("furniture_1")
```

### Menu System

The menu system uses Evennia's `EvMenu` framework for interactive creation:

```python
# Start a furniture design menu
EvMenu(caller, "world.builder_menus", startnode="furniture_start")

# The menu system handles:
# - Input validation
# - Step progression
# - State management
# - Error recovery
# - Data persistence
```

---

## Troubleshooting

### Design Won't Save
- Check all required fields are filled
- Look for error messages in the menu
- Verify you have Builder+ permissions

### Can't Find Items to Spawn
- Use keyword search: `spawnfurniture table`
- Check exact ID: `spawnfurniture furniture_1`
- Use `listdesigns` to see all available items

### Spawned Items Don't Have Expected Properties
- Items are based on template attributes
- Ensure template was saved with correct properties
- Use `listdesigns` to verify template settings

### Faction Not Available When Creating NPC
- Use `managefactions list` to see available factions
- Create faction if needed: `managefactions add faction_id = Name ; Description`
- Factions are case-sensitive in storage

---

## System Capabilities

### What Can Be Customized

**Furniture:**
- Visual appearance (description)
- Interaction capacity (seats, lying, reclining)
- Custom flavor text for all interactions
- Mobility (movable/static)

**NPCs:**
- Appearance and personality (description)
- Organizational affiliation (faction)
- Behavior (wandering/static)
- Role (shopkeeper flag)

**Weapons:**
- Type (melee/ranged)
- Ammo type (for ranged)
- Combat bonuses (damage, accuracy)
- Appearance (description)

**Clothing/Armor:**
- Type (cosmetic or protective)
- Armor properties (type, value)
- Rarity (for shop stocking)
- Appearance (description)

### Extensibility

The system is designed to be extended. Additional item types can be added by:
1. Adding storage functions to `world/builder_storage.py`
2. Creating menu nodes in `world/builder_menus.py`
3. Creating spawn commands in `commands/builder_spawners.py`
4. Creating design commands in `commands/builder_designs.py`

---

## File Structure

```
world/
├── builder_storage.py       # Storage functions and database access
└── builder_menus.py         # EvMenu nodes for design interfaces

commands/
├── builder_designs.py       # Design command entry points
├── builder_spawners.py      # Spawn command implementations
└── default_cmdsets.py       # Command set integration
```

---

## Permissions

All builder item creation commands require:
- `Builder` permission level or higher
- Standard builder locks apply

Commands are protected by Evennia's permission system.

---

*Last Updated: January 11, 2026*
*System Version: 1.0*
