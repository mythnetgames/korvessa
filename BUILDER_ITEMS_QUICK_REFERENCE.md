# Builder Items System - Quick Reference

## 🎯 Quick Command List

### Design (Create New Templates)
| Command | Purpose |
|---------|---------|
| `designfurniture` | Create furniture template |
| `designnpc` | Create NPC template |
| `designweapon` | Create weapon template |
| `designclothing` | Create clothing/armor template |

### Spawn (Create Instances from Templates)
| Command | Purpose |
|---------|---------|
| `spawnfurniture [keyword]` | Spawn furniture instance |
| `spawnnpc [keyword]` | Spawn NPC instance |
| `spawnweapon [keyword]` | Spawn weapon instance |
| `spawnclothing [keyword]` | Spawn clothing instance |
| `spawnarmor [keyword]` | Spawn armor instance |

### Management
| Command | Purpose |
|---------|---------|
| `listdesigns [type]` | List all designs |
| `managefactions` | Manage NPC factions |

---

## 📝 Menu Workflows

### Creating Furniture
```
designfurniture
→ Enter name
→ Enter description
→ Set properties (movable, seats, recline, lie down)
→ Configure custom messages
→ Save
```

**Furniture Properties:**
- **Movable**: Can players pick it up?
- **Max Seats**: How many can sit? (0 = not sittable)
- **Recline**: Support reclining?
- **Lie Down**: Support lying down?

### Creating NPCs
```
designnpc
→ Enter name
→ Enter description
→ Choose faction
→ Set wandering zone (optional)
→ Shopkeeper? (yes/no)
→ Save
```

**NPC Properties:**
- **Faction**: Organization affiliation
- **Wandering Zone**: Zone ID to wander in (leave blank for static)
- **Shopkeeper**: Is this NPC a merchant?

### Creating Weapons
```
designweapon
→ Enter name
→ Enter description
→ Choose type (melee/ranged)
→ If ranged: enter ammo type
→ Set damage bonus (-5 to +5)
→ Set accuracy bonus (-5 to +5)
→ Save
```

### Creating Clothing/Armor
```
designclothing
→ Enter name
→ Enter description
→ Choose type (clothing/armor)
→ If armor: choose armor type and value
→ Choose rarity
→ Save
```

---

## 🔍 Spawn Command Patterns

### List All Items
```
spawnfurniture          # All furniture
spawnnpc               # All NPCs
spawnweapon            # All weapons
spawnclothing          # All clothing
spawnarmor             # All armor
```

### Search by Keyword
```
spawnfurniture table       # Find furniture with "table"
spawnnpc vendor           # Find NPCs with "vendor"
spawnweapon pistol        # Find weapons with "pistol"
spawnclothing shirt       # Find clothing with "shirt"
spawnarmor kevlar         # Find armor with "kevlar"
```

### Search by Type
```
spawnweapon melee         # Find all melee weapons
spawnarmor light          # Find all light armor
spawnweapon ranged        # Find all ranged weapons
spawnarmor heavy          # Find all heavy armor
```

### Spawn by Selection
```
spawnfurniture              # Lists items
1                          # Select item 1
```

---

## 📊 Item Criteria Checklist

### Furniture
- [ ] Name (e.g., "Oak Table")
- [ ] Description
- [ ] Movable? (yes/no)
- [ ] Max seats (0-infinite)
- [ ] Can recline? (yes/no)
- [ ] Can lie down? (yes/no)
- [ ] Sit messages (1st & 3rd person)
- [ ] Lie messages (if applicable)
- [ ] Recline messages (if applicable)

### NPC
- [ ] Name
- [ ] Description
- [ ] Faction (choose from list)
- [ ] Wandering zone (optional)
- [ ] Shopkeeper? (yes/no)

### Weapon
- [ ] Name
- [ ] Description
- [ ] Type (melee/ranged)
- [ ] Ammo type (if ranged)
- [ ] Damage bonus (-5 to +5)
- [ ] Accuracy bonus (-5 to +5)

### Clothing/Armor
- [ ] Name
- [ ] Description
- [ ] Type (clothing/armor)
- [ ] Armor value (1-10, if armor)
- [ ] Armor type (light/medium/heavy, if armor)
- [ ] Rarity (common/uncommon/rare/epic)

---

## 🔑 Default Factions

```
neutral              # No affiliation
kowloon_citizens     # Local residents
kowloon_security     # Security forces
```

### Add Custom Faction
```
managefactions add faction_id = Faction Name ; Description
```

Example:
```
managefactions add kowloon_gang = Kowloon Gang ; Street gang
managefactions add merchants = Merchant Guild ; Trading organization
```

---

## 💾 Storage & IDs

### How IDs Work
- Auto-generated: `furniture_1`, `furniture_2`, etc.
- Used to spawn specific items: `spawnfurniture furniture_1`
- Used in searches: included in keyword matching

### Listing All Designs
```
listdesigns                 # Everything
listdesigns furniture       # Furniture only
listdesigns npcs            # NPCs only
listdesigns weapons         # Weapons only
listdesigns clothing        # Clothing only
listdesigns armor           # Armor only
listdesigns all            # Everything
```

---

## ⚡ Common Tasks

### Setup a Bar
1. `designfurniture` → "Mahogany Bar"
2. `designfurniture` → "Bar Stool"
3. `designnpc` → "Bartender"
4. `spawnfurniture bar` → spawn 1 counter
5. `spawnfurniture stool` → spawn multiple stools
6. `spawnnpc bartender` → spawn bartender

### Create Weapon Variants
1. `designweapon` → "Standard 9mm" (damage 0, accuracy 0)
2. `designweapon` → "Custom 9mm" (damage +1, accuracy +1)
3. `designweapon` → "Overtuned 9mm" (damage +2, accuracy -1)
4. `spawnweapon 9mm` → choose variant

### Stock a Shop
1. `designnpc` → create shopkeeper
2. `designweapon`, `designarmor`, `designclothing` → items
3. `spawnnpc shopkeeper` → place NPC
4. `spawnweapon`, `spawnarmor`, `spawnclothing` → stock items
5. Place items near/with shopkeeper

---

## ⚠️ Tips & Tricks

### Message Placeholders
Available in furniture messages:
- `{name}` - Player name
- `{furniture}` - Furniture name

Examples:
- "You settle into the {furniture}."
- "{name} sits down on the {furniture}."

### Search Tips
- Search is case-insensitive
- Partial matches work: "table" finds "oak table"
- Can search by ID: "furniture_1"
- Search by weapon type: "melee", "ranged"
- Search by armor type: "light", "medium", "heavy"

### Organization
- Use faction system to organize NPCs
- Use naming conventions for related items
- Examples: "Weapon: 9mm Standard", "Weapon: 9mm Tactical"

---

## 🐛 Troubleshooting

| Problem | Solution |
|---------|----------|
| Items won't save | Check all required fields filled |
| Can't find item | Use `listdesigns` to verify it exists |
| Can't see spawn menu | Check Builder+ permissions |
| Wrong faction choice | Use `managefactions list` then create if needed |
| Item missing properties | Re-design or use `listdesigns` to verify |

---

## 📚 Learn More

See `BUILDER_ITEMS_SYSTEM.md` for:
- Detailed command documentation
- Workflow examples
- Technical details
- Extensibility guide
- Python API reference

---

*Quick Reference - Last Updated: January 11, 2026*
