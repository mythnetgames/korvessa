# NPC Stats and Skills System - Builder's Guide

## Overview

The expanded NPC creation system now allows builders to create fully-customized NPCs with stats and skills that define their combat capabilities and social interactions.

## Quick Start

1. Use `/designnpc` to start the NPC designer
2. Enter NPC name and description
3. Set faction, wandering zone, and shopkeeper status
4. Configure stats (scales 1-10)
5. Configure skills (scales 0-100)
6. Save and spawn with `/spawnnpc <id>`

## Stats System

Stats represent the core attributes of an NPC. Each stat ranges from **1-10**, with 5 being average human level.

### Available Stats

| Stat | Full Name | Purpose |
|------|-----------|---------|
| `body` | Body | Physical toughness, damage resistance, carrying capacity |
| `ref` | Reflexes | Reaction speed, initiative, evasion ability |
| `dex` | Dexterity | Manual dexterity, fine motor control, climbing |
| `tech` | Technical | Technical aptitude, hacking, repair, device usage |
| `smrt` | Smart | Intelligence, reasoning, puzzle-solving |
| `will` | Willpower | Mental fortitude, resistance to mental effects |
| `edge` | Edge | Luck, chance occurrences, critical moments |
| `emp` | Empathy | Social awareness, reading emotions, rapport |

### Stat Guidelines

**For Weak NPCs (Stats 1-2):**
- Street thugs, homeless people
- Untrained civilians
- Fleeing or panicked NPCs

**For Average NPCs (Stats 3-5):**
- Common street people
- Average gang members
- Trained workers
- Most NPCs should be here

**For Strong NPCs (Stats 6-8):**
- Veteran fighters
- Professional soldiers
- Skilled specialists
- Gang leaders

**For Exceptional NPCs (Stats 9-10):**
- Master-level fighters
- Elite soldiers
- Legendary performers
- Use sparingly!

## Skills System

Skills represent trained abilities and experience. Each skill ranges from **0-100**.

### Available Skills

| Skill | Description |
|-------|-------------|
| `brawling` | Unarmed combat, fist fighting, kicks, grappling (without tools) |
| `blades` | Edged weapons like knives, swords, machetes |
| `blunt` | Heavy blunt weapons like clubs, hammers, pipes |
| `ranged` | Firearms, bows, throwing weapons, accuracy with distance weapons |
| `grapple` | Wrestling, holds, joint locks, submission techniques |
| `dodge` | Evasion, defensive movement, blocking |
| `stealth` | Sneaking, hiding, moving silently, ambush tactics |
| `intimidate` | Threatening, coercion, fear-based influence |
| `persuasion` | Talking people into things, charm, negotiation |
| `perception` | Noticing details, awareness, sight/hearing |

### Skill Guidelines

**0-20 (Untrained to Novice)**
- Most civilians won't have combat skills above 0
- Minimal training or experience
- Guards might have 10-15

**20-40 (Trained)**
- Regular gang members: 20-30
- Trained security: 25-35
- Street fighters: 30-40

**40-60 (Experienced)**
- Veteran gang members: 45-55
- Professional soldiers: 50-65
- Specialists in their field: 50-70

**60-80 (Expert)**
- Elite fighters: 65-80
- Master assassins: 75-90
- Gang leaders: 70-85

**80-100 (Master)**
- Legendary fighters: 85-100
- Used very sparingly
- Legendary assassins or warriors

## Example NPC Builds

### Street Thug
```
Stats:
  body: 4, ref: 3, dex: 3, tech: 1, smrt: 2, will: 2, edge: 2, emp: 1

Skills:
  brawling: 25, blades: 15, blunt: 20, dodge: 10, intimidate: 30, 
  perception: 15, stealth: 5
```

### Professional Bodyguard
```
Stats:
  body: 6, ref: 5, dex: 5, tech: 3, smrt: 4, will: 4, edge: 3, emp: 3

Skills:
  brawling: 45, blades: 40, ranged: 50, dodge: 45, perception: 50,
  intimidate: 40, stealth: 25
```

### Charming Merchant/Shopkeeper
```
Stats:
  body: 2, ref: 2, dex: 2, tech: 2, smrt: 5, will: 4, edge: 3, emp: 6

Skills:
  persuasion: 60, perception: 35, stealth: 10, intimidate: 15
```

### Gang Leader / Fixer
```
Stats:
  body: 5, ref: 5, dex: 5, tech: 4, smrt: 5, will: 5, edge: 4, emp: 6

Skills:
  brawling: 50, blades: 45, ranged: 40, grapple: 45, dodge: 40,
  intimidate: 60, persuasion: 55, perception: 45, stealth: 30
```

### Hacker/Tech Specialist
```
Stats:
  body: 2, ref: 4, dex: 4, tech: 8, smrt: 7, will: 4, edge: 2, emp: 2

Skills:
  dodge: 20, perception: 40, stealth: 35
```

### Stealthy Assassin
```
Stats:
  body: 4, ref: 6, dex: 7, tech: 3, smrt: 4, will: 5, edge: 3, emp: 2

Skills:
  blades: 70, ranged: 65, grapple: 50, dodge: 60, stealth: 85,
  perception: 60, intimidate: 35
```

## Using the NPC Designer

### Step-by-Step Walkthrough

1. **Start the Designer**
   ```
   /designnpc
   ```
   
2. **Enter Name**
   - Simple, memorable names work best
   - Examples: "Street Vendor", "Gang Boss", "Security Guard"
   
3. **Enter Description**
   - What does the NPC look like?
   - What's their demeanor?
   - Keep it brief but vivid
   
4. **Set Properties**
   - **Faction**: Choose which faction this NPC belongs to
   - **Wandering Zone**: Leave empty for static, or enter zone ID for wandering
   - **Shopkeeper**: Mark if this NPC sells items
   
5. **Configure Stats**
   - Menu shows all 8 stats with current values
   - Select each stat to adjust (1-10)
   - Default is 1 for all
   
6. **Configure Skills**
   - Menu shows all 10 skills with current values
   - Select each skill to adjust (0-100)
   - Default is 0 (untrained)
   
7. **Save**
   - Review all settings
   - Confirm save
   - Gets a unique ID (e.g., `npc_42`)

## Spawning NPCs

### List All NPCs
```
/spawnnpc
```

### Search by Keyword
```
/spawnnpc gang
/spawnnpc vendor
/spawnnpc npc_1
```

### View NPC Details

When listing NPCs, you'll see:
- Name and ID
- Faction affiliation
- Shopkeeper status
- Wandering status
- **All stats** (Body, Ref, Dex, Tech, Smrt, Will, Edge, Emp)
- **All non-zero skills** displayed

Example output:
```
1. Gang Boss (ID: npc_42)
   Faction: kowloon_gang, Shopkeeper: No, Wanders: Yes
   Stats: Body:5 Ref:5 Dex:5 Tech:4 Smrt:5 Will:5 Edge:4 Emp:6
   Skills: brawling:50, blades:45, ranged:40, grapple:45, dodge:40, 
           intimidate:60, persuasion:55, perception:45, stealth:30
```

### Spawn an NPC
```
/spawnnpc 1
```
(or select from the numbered list)

## Mass Production of NPCs

Once you've created a template:

1. **Create the Template** once with `/designnpc`
2. **Spawn Multiple Copies** with `/spawnnpc <id>`
3. **Customize Individual Copies** in-game if needed

### Example: Creating 5 Street Thugs

1. Create template "Street Thug" (ID: `npc_100`)
   - Stats: body:4, ref:3, dex:3, tech:1, smrt:2, will:2, edge:2, emp:1
   - Skills: brawling:25, blades:15, blunt:20, dodge:10, etc.

2. Spawn 5 copies:
   ```
   /spawnnpc npc_100
   /spawnnpc npc_100
   /spawnnpc npc_100
   /spawnnpc npc_100
   /spawnnpc npc_100
   ```

3. Each spawn gets the exact same stats and skills

### Tips for Mass Production

- **Create Base Templates**: One weak, one medium, one strong for each NPC type
- **Reuse Templates**: Don't create a new template for every NPC
- **Variant Names**: Give spawned copies slightly different names if desired
- **Consistency**: All spawns of same template have identical stats

## Integration with Combat System

When an NPC spawns with stats and skills:

- **Stats** are used for:
  - Initiative rolls (Ref stat)
  - Damage resistance (Body stat)
  - Attack rolls (various stats + skills)
  - Movement and evasion (Dex, Ref)
  
- **Skills** are used for:
  - Attack accuracy and effectiveness
  - Defense and dodging
  - Determining combat success/failure
  - Scaling damage output

Stronger stats + higher skills = tougher NPC in combat!

## Faction Integration

When you set a faction for an NPC:

- NPCs with same faction may have loyalty interactions
- Factions can be expanded later for faction-based conflicts
- Shopkeepers use faction for shop inventory associations
- Support for faction-based NPC behavior (future expansion)

## Future Enhancements

The system is designed to support:
- Inventory/equipment templates
- Spell/ability templates
- Dialog/reaction customization
- AI behavior patterns
- Faction-specific bonuses
- Loot table associations
- Quest giver status

---

**Need Help?** Check the NPC_SYSTEM.md for more details on NPC structure and database organization.
