# NPC Storage Data Structure Documentation

## Database Schema

NPCs are stored in the builder storage system with complete stat and skill information.

### NPC Data Structure

```python
{
    "id": "npc_42",                    # Unique identifier
    "name": "Gang Boss",               # Display name
    "desc": "A scarred man with cold eyes", # Description
    "faction": "kowloon_gang",         # Faction ID
    "wandering_zone": "kowloon_01",   # Zone for wandering or empty string
    "is_shopkeeper": False,            # Whether NPC sells items
    "created_by": "BuilderName",       # Creator's character name
    
    # Stats (1-10 scale)
    "stats": {
        "body": 5,      # Physical toughness
        "ref": 5,       # Reaction speed
        "dex": 5,       # Dexterity
        "tech": 4,      # Technical aptitude
        "smrt": 5,      # Intelligence
        "will": 5,      # Mental fortitude
        "edge": 4,      # Luck
        "emp": 6,       # Empathy/Social
    },
    
    # Skills (0-100 scale)
    "skills": {
        "brawling": 50,
        "blades": 45,
        "blunt": 0,
        "ranged": 40,
        "grapple": 45,
        "dodge": 40,
        "stealth": 30,
        "intimidate": 60,
        "persuasion": 55,
        "perception": 45,
    }
}
```

## Accessing NPCs

### From Builder Commands

```python
from world.builder_storage import (
    add_npc, get_npc_by_id, search_npcs, 
    get_all_npcs, delete_npc
)

# Create a new NPC with stats and skills
npc = add_npc(
    name="Street Vendor",
    desc="An old man selling street food",
    faction="neutral",
    wandering_zone="market_district",
    is_shopkeeper=True,
    stats={
        "body": 2, "ref": 2, "dex": 3, "tech": 1,
        "smrt": 3, "will": 3, "edge": 2, "emp": 4
    },
    skills={
        "persuasion": 40,
        "perception": 30,
        "intimidate": 5,
    },
    created_by="Builder"
)

# Get NPC by ID
npc = get_npc_by_id("npc_42")

# Search for NPCs
results = search_npcs("gang")

# Get all NPCs
all_npcs = get_all_npcs()

# Delete an NPC
delete_npc("npc_42")
```

### From Spawn Commands

```python
# When spawning, stats and skills are applied to the NPC object

if 'stats' in npc_data:
    for stat_name, stat_value in npc_data['stats'].items():
        setattr(npc.db, stat_name, stat_value)

if 'skills' in npc_data:
    for skill_name, skill_value in npc_data['skills'].items():
        setattr(npc.db, skill_name, skill_value)

# Result: NPC has db.body, db.ref, db.dex, etc.
# And also: db.brawling, db.blades, db.dodge, etc.
```

## Storage Location

NPCs are stored in the ScriptDB under the key `"builder_storage"`:

```python
from world.builder_storage import get_builder_storage

storage = get_builder_storage()
all_npcs = storage.db.npcs  # List of NPC dictionaries
```

## Migration from Old Format

If you have older NPCs without stats/skills:

```python
def migrate_npc_data(old_npc):
    """Convert old NPC format to new format with stats/skills."""
    
    # Old NPCs will have default stats/skills
    return {
        **old_npc,
        "stats": {
            "body": 1,
            "ref": 1,
            "dex": 1,
            "tech": 1,
            "smrt": 1,
            "will": 1,
            "edge": 1,
            "emp": 1,
        },
        "skills": {
            "brawling": 0,
            "blades": 0,
            "blunt": 0,
            "ranged": 0,
            "grapple": 0,
            "dodge": 0,
            "stealth": 0,
            "intimidate": 0,
            "persuasion": 0,
            "perception": 0,
        }
    }
```

## Integration with Combat System

When an NPC is spawned with stats and skills:

### Stats Integration
Stats are stored as database attributes and used by the combat system:

```python
# Combat system accesses stats
from world.combat.utils import get_character_stat

stat_value = get_character_stat(npc, "body", default=1)
roll = roll_stat(npc, "ref", default=1)
```

### Skills Integration
Skills are stored as database attributes and used by the combat system:

```python
# Combat system accesses skills
from world.combat.utils import get_combat_skill_value

skill_value = get_combat_skill_value(npc, "brawling")
combined_skill = get_combat_skill_value(npc, "dodge", stat_name="ref")
```

## Example: Creating Combat-Ready NPC Templates

### Weak Enemy
```python
weak_npc = add_npc(
    name="Weak Thug",
    desc="A scrawny street punk",
    faction="neutral",
    stats={
        "body": 2, "ref": 2, "dex": 2, "tech": 1,
        "smrt": 1, "will": 1, "edge": 1, "emp": 1
    },
    skills={
        "brawling": 10, "dodge": 5, "intimidate": 15
    },
    created_by="Builder"
)
```

### Medium Enemy
```python
medium_npc = add_npc(
    name="Gang Member",
    desc="A street-hardened fighter",
    faction="kowloon_gang",
    stats={
        "body": 4, "ref": 3, "dex": 3, "tech": 1,
        "smrt": 2, "will": 2, "edge": 2, "emp": 1
    },
    skills={
        "brawling": 25, "blades": 15, "blunt": 20,
        "dodge": 10, "intimidate": 30, "perception": 15
    },
    created_by="Builder"
)
```

### Strong Enemy
```python
strong_npc = add_npc(
    name="Gang Leader",
    desc="A commanding presence, scarred and dangerous",
    faction="kowloon_gang",
    stats={
        "body": 5, "ref": 5, "dex": 5, "tech": 4,
        "smrt": 5, "will": 5, "edge": 4, "emp": 6
    },
    skills={
        "brawling": 50, "blades": 45, "ranged": 40,
        "grapple": 45, "dodge": 40, "intimidate": 60,
        "persuasion": 55, "perception": 45, "stealth": 30
    },
    created_by="Builder"
)
```

## Data Persistence

All NPC data is automatically saved to the database via Evennia's ScriptDB:

- Changes are persisted across server restarts
- No manual save required (Evennia handles it)
- Data is automatically validated on load

## Backward Compatibility

The system gracefully handles NPCs without stats/skills:

```python
# In spawning code
if 'stats' in npc_data:
    # Apply stats
    for stat_name, stat_value in npc_data['stats'].items():
        setattr(npc.db, stat_name, stat_value)
else:
    # NPC has no template stats, use defaults
    pass

if 'skills' in npc_data:
    # Apply skills
    for skill_name, skill_value in npc_data['skills'].items():
        setattr(npc.db, skill_name, skill_value)
else:
    # NPC has no template skills, use defaults
    pass
```

---

**Note:** All NPCs created with `/designnpc` will include stats and skills. Older templates without these fields will still work but won't use the stat/skill system.
