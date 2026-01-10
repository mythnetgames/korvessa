# Investment Points (IP) System Specification

## Overview

The Investment Points (IP) system allows players to improve their character's skills through earned points. Unlike character levels, skills are individually raised by spending IP, creating meaningful progression choices.

## Core Concepts

### Skills
- Range from 0 to 100 (base cap)
- Can exceed 100 with buffs/augmentations
- Raw values show to hundredths (e.g., 45.12)
- Effective values are the integer used for skill checks

### Rounding Rules
- **Normal rounding**: If thousandths digit < 5, round DOWN (truncate)
- **Buff rounding**: If thousandths digit >= 5, round UP
- Example: 45.124 → 45.12 (effective: 45), 45.125 → 45.13 (effective: 46)

## IP Progression Tiers

Skills cost more IP to raise as they increase, using tiered exponential growth:

| Tier | Skill Range | Base Cost | Growth Rate | Description |
|------|-------------|-----------|-------------|-------------|
| 1 | 0-20 | 1 IP | +4%/level | Novice - everyday learning |
| 2 | 21-45 | 2 IP | +6%/level | Competent - above average |
| 3 | 46-75 | 4 IP | +7.5%/level | Seasoned professional |
| 4 | 76-89 | 8 IP | +9%/level | Very advanced - prodigy-like |
| 5 | 90-99 | 16 IP | +12%/level | Near-perfect mastery |

### Sample Costs
| From | To | IP Cost |
|------|-----|---------|
| 0 | 1 | 1 |
| 20 | 21 | 2 |
| 45 | 46 | 4 |
| 50 | 51 | 5 |
| 75 | 76 | 8 |
| 89 | 90 | 16 |
| 99 | 100 | 49 |

### Total IP to Reach Milestones (from 0)
| Target | Total IP |
|--------|----------|
| 20 | ~24 |
| 50 | ~130 |
| 75 | ~360 |
| 100 | ~1,100 |

---

## Admin IP Reward Guidelines

### Tiny Reward: 1-5 IP
- Minor RP contribution
- Basic participation in scenes
- Small helpful actions

### Small Reward: 5-15 IP
- Good scene participation
- Completing simple tasks
- Consistent roleplay presence

### Moderate Reward: 15-30 IP
- Excellent roleplay scenes
- Moderate story contribution
- Creative problem solving

### Large Reward: 30-50 IP
- Significant plot advancement
- Exceptional RP that impacts others
- Running events for other players

### Major Reward: 50-100 IP
- Major story arc completion
- Outstanding contribution to the game world
- Exceptional player service

### Automatic Grants
- **3-5 IP** every 4 hours for logged-in players
- Grant times: 00:00, 04:00, 08:00, 12:00, 16:00, 20:00

---

## Commands

### Player Commands

#### `invest`
View IP and skill cost information.
```
invest                    - Show IP overview and tier costs
invest <skill>            - See cost to raise a specific skill
invest <skill> <amount>   - Invest IP into a skill
invest <skill> max        - Invest as much IP as possible
```

#### `stats` / `score`
View character stats including current IP and skill values.

### Admin Commands

#### `ip <character> [amount]`
Grant or subtract IP from a player.
```
ip Bob                    - View Bob's current IP
ip Bob 50                 - Grant Bob 50 IP
ip Bob +50                - Grant Bob 50 IP
ip Bob -25                - Subtract 25 IP from Bob
```

#### `setskill <character> <skill> <value>`
Directly set a character's skill value (for earned adjustments).
```
setskill Bob brawling 50      - Set Bob's brawling to 50
setskill Bob brawling +10     - Add 10 to Bob's brawling
setskill Bob "martial arts" 75 - Set martial arts to 75
```

---

## Starting the IP Grant Script

Run once as admin to enable automatic IP grants:
```
@py from scripts.ip_grant_script import IPGrantScript; IPGrantScript.create_if_not_exists()
```

To check status:
```
@script ip_grant_script
```

To stop:
```
@script/stop ip_grant_script
```

---

## Implementation Notes

### File Locations
- `commands/CmdIP.py` - IP, setskill, and invest commands
- `commands/CmdStats.py` - Updated stats display with IP
- `scripts/ip_grant_script.py` - Automatic IP distribution
- `world/combat/utils.py` - IP cost calculation functions

### Data Storage
- `character.db.ip` - Current IP balance
- `character.db.<skill_name>` - Skill values (can be float for buff precision)

### Skill Names (internal)
Skills use underscores internally: `modern_medicine`, `martial_arts`, `paint_draw_sculpt`
