# NPC CREATION SYSTEM - EXPANSION SUMMARY

## What Was Added

The NPC creation system has been expanded with comprehensive stats and skills support, allowing builders to create fully-customized NPCs that can be mass-produced.

### Key Features

✅ **Stats System** - 8 core attributes (Body, Ref, Dex, Tech, Smrt, Will, Edge, Emp)
✅ **Skills System** - 10 combat and social skills (Brawling, Blades, Dodge, Stealth, Persuasion, etc.)
✅ **Interactive Menus** - Full EvMenu support for configuring all NPC attributes
✅ **Mass Production** - Create one template, spawn infinite copies with identical stats/skills
✅ **Combat Integration** - Stats and skills automatically apply to spawned NPCs
✅ **Database Persistence** - All NPC templates saved permanently
✅ **Search and List** - Easy filtering of NPCs by keyword or ID

---

## System Components

### 1. Storage Layer (`world/builder_storage.py`)

**Updated `add_npc()` function:**
- Now accepts `stats` and `skills` parameters
- Stores complete NPC definition including stats/skills
- Provides default values for unspecified stats/skills

```python
npc = add_npc(
    name="Gang Boss",
    desc="A scarred man with cold eyes",
    faction="kowloon_gang",
    stats={"body": 5, "ref": 5, ...},
    skills={"brawling": 50, "dodge": 40, ...},
    created_by="Builder"
)
```

### 2. Menu System (`commands/builder_menus.py`)

**New menu functions:**
- `npc_stats_menu()` - Browse and edit all 8 stats
- `npc_edit_stat()` - Edit individual stat (1-10 scale)
- `npc_skills_menu()` - Browse and edit all 10 skills
- `npc_edit_skill()` - Edit individual skill (0-100 scale)

**Updated flow:**
1. Name and Description (existing)
2. Faction, Wandering Zone, Shopkeeper (existing)
3. **NEW: Configure Stats** (interactive menu)
4. **NEW: Configure Skills** (interactive menu)
5. Save and confirm

### 3. Spawn Command (`commands/builder_spawners.py`)

**Enhanced NPC listing:**
- Shows all 8 stats for each NPC
- Shows non-zero skills for each NPC
- Better formatted output with color coding

**Updated NPC application:**
- Automatically applies all stats to spawned NPC
- Automatically applies all skills to spawned NPC
- Stats stored as `db.body`, `db.ref`, `db.dex`, etc.
- Skills stored as `db.brawling`, `db.blades`, `db.dodge`, etc.

---

## Usage Workflow

### Creating an NPC

```
Step 1: /designnpc
        Enter NPC name

Step 2: Enter description

Step 3: Set faction, wandering zone, shopkeeper flag

Step 4: Configure Stats (1-10 scale)
        - Browse all 8 stats
        - Edit each individually
        - Save changes

Step 5: Configure Skills (0-100 scale)
        - Browse all 10 skills
        - Edit each individually
        - Save changes

Step 6: Save NPC template
        Get ID like "npc_42"
```

### Spawning NPCs

```
/spawnnpc                    # List all NPCs
/spawnnpc gang              # Search by keyword
/spawnnpc npc_42            # Spawn by ID
/spawnnpc 1                 # Select from list
```

### Mass Production

```
# Create template once
/designnpc
→ Create "Street Thug" (npc_100)

# Spawn multiple copies
/spawnnpc npc_100
/spawnnpc npc_100
/spawnnpc npc_100
→ Creates 3 identical Street Thugs
```

---

## Stats Reference

| Stat | Range | Purpose |
|------|-------|---------|
| body | 1-10 | Physical toughness, HP modifier |
| ref | 1-10 | Reaction speed, initiative |
| dex | 1-10 | Dexterity, accuracy |
| tech | 1-10 | Technical abilities |
| smrt | 1-10 | Intelligence, reasoning |
| will | 1-10 | Mental resistance |
| edge | 1-10 | Luck, chance events |
| emp | 1-10 | Empathy, social skills |

**Scale:** 5 = average human, 1-4 = below average, 6-10 = above average

---

## Skills Reference

| Skill | Range | Purpose |
|-------|-------|---------|
| brawling | 0-100 | Unarmed combat |
| blades | 0-100 | Edged weapons |
| blunt | 0-100 | Blunt weapons |
| ranged | 0-100 | Ranged weapons |
| grapple | 0-100 | Wrestling/holds |
| dodge | 0-100 | Evasion |
| stealth | 0-100 | Sneaking/hiding |
| intimidate | 0-100 | Threatening |
| persuasion | 0-100 | Talking/charming |
| perception | 0-100 | Awareness |

**Scale:** 0 = untrained, 50 = veteran, 100 = master

---

## Example NPC Templates

### Standard Street Thug
```
Stats:  body:4 ref:3 dex:3 tech:1 smrt:2 will:2 edge:2 emp:1
Skills: brawling:25 blades:15 blunt:20 dodge:10 intimidate:30 perception:15
```

### Elite Gang Leader
```
Stats:  body:5 ref:5 dex:5 tech:4 smrt:5 will:5 edge:4 emp:6
Skills: brawling:50 blades:45 ranged:40 grapple:45 dodge:40 
        intimidate:60 persuasion:55 perception:45 stealth:30
```

### Stealth/Assassin
```
Stats:  body:4 ref:6 dex:7 tech:3 smrt:4 will:5 edge:3 emp:2
Skills: blades:70 ranged:65 grapple:50 dodge:60 stealth:85 
        perception:60 intimidate:35
```

---

## Data Persistence

- All NPC templates stored in ScriptDB
- Automatically saved across server restarts
- No manual save required
- Can be modified by updating template and respawning

---

## Integration with Combat System

When an NPC is spawned:

1. **Stats Applied** - All 8 stats become NPC database attributes
2. **Skills Applied** - All 10 skills become NPC database attributes
3. **Combat Ready** - NPC can immediately participate in combat
4. **Skill Checks** - Combat system uses skills for attacks/defense
5. **Stat Modifiers** - Stats modify skill rolls in combat

Example:
```
Spawned "Gang Boss" with:
- body:5 → npc.db.body = 5
- brawling:50 → npc.db.brawling = 50
- dodge:40 → npc.db.dodge = 40

Combat System:
- Uses body stat for HP calculation
- Uses brawling+body for melee attack rolls
- Uses dodge+ref for defensive rolls
```

---

## Files Modified

### Code Changes
- `world/builder_storage.py` - Updated `add_npc()` function
- `commands/builder_menus.py` - Added 4 new menu functions, updated NPC flow
- `commands/builder_spawners.py` - Enhanced NPC display and stat/skill application

### Documentation Added
- `NPC_STATS_SKILLS_GUIDE.md` - Comprehensive builder's guide
- `NPC_STATS_SKILLS_QUICK_REF.md` - Quick reference card with templates
- `NPC_STORAGE_SCHEMA.md` - Database structure and integration docs

---

## Commands

### Admin Commands (Builders+)
- `/designnpc` - Start NPC designer with stats/skills support
- `/spawnnpc` - List, search, and spawn NPCs with full stat/skill info
- `/listdesigns` - See all created designs

### Interactive Menus
- Configure Stats menu - Edit 8 stats (1-10)
- Configure Skills menu - Edit 10 skills (0-100)
- Faction selection menu (existing)
- Zone selection menu (existing)

---

## Quick Start for Builders

1. **Design** one NPC with `/designnpc`
   - Set name, description
   - Configure stats (aim for 3-5 average)
   - Configure skills (0-40 for regular NPCs)
   - Save and get ID

2. **Spawn** copies with `/spawnnpc <id>`
   - All spawns are identical
   - Change individual copy names if desired

3. **Use in Combat**
   - Stats and skills automatically apply
   - NPCs are combat-ready immediately

---

## Best Practices

- Create **3 versions**: weak (stats 2-3), medium (stats 3-5), strong (stats 5-7)
- Set **realistic skills**: Most NPCs should have 0-40 in combat skills
- Use **appropriate stats**: Leaders get higher Empathy, fighters get higher Body
- **Reuse templates**: Don't make new NPC for every spawn, use same template
- **Name variants**: Same stats/skills but different names for variety

---

## Future Expansion Points

The system is designed to support:
- Equipment templates
- Spell/ability templates
- Inventory associations
- Dialog/reaction templates
- AI behavior patterns
- Faction loyalty modifiers
- Loot tables
- Quest giver status

All can be added to the NPC data dictionary without breaking existing system.

---

**Documentation:** See NPC_STATS_SKILLS_GUIDE.md for complete usage guide.
