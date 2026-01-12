# NPC Stats & Skills Quick Reference

## STATS (1-10 scale)

```
┌─────────┬──────────────────┬─────────────────────────────────────┐
│ STAT    │ Full Name        │ Affects                             │
├─────────┼──────────────────┼─────────────────────────────────────┤
│ body    │ Body             │ HP, damage resistance, carrying      │
│ ref     │ Reflexes         │ Initiative, evasion, reaction       │
│ dex     │ Dexterity        │ Accuracy, precision, climbing       │
│ tech    │ Technical        │ Hacking, repair, device usage       │
│ smrt    │ Intelligence     │ Reasoning, knowledge, tactics       │
│ will    │ Willpower        │ Mental resistance, determination    │
│ edge    │ Edge/Luck        │ Chance events, critical moments     │
│ emp     │ Empathy/Social   │ Reading emotions, rapport, charm    │
└─────────┴──────────────────┴─────────────────────────────────────┘
```

### Stat Benchmarks
- **1-2**: Weak (civilians, untrained)
- **3-4**: Below Average (common people)
- **5**: Average Human (standard NPCs)
- **6-7**: Above Average (trained/experienced)
- **8-9**: Exceptional (elite, masters)
- **10**: Legendary (rare, powerful)

---

## SKILLS (0-100 scale)

```
┌──────────────┬────────────────────────────────────────────────┐
│ SKILL        │ Description                                    │
├──────────────┼────────────────────────────────────────────────┤
│ brawling     │ Unarmed fighting, fists, kicks, wrestling      │
│ blades       │ Knives, swords, machetes, edged weapons        │
│ blunt        │ Clubs, hammers, pipes, crushing weapons        │
│ ranged       │ Guns, bows, throwing weapons, distance combat  │
│ grapple      │ Holds, joint locks, submission techniques      │
│ dodge        │ Evasion, blocking, defensive movement         │
│ stealth      │ Sneaking, hiding, moving silently             │
│ intimidate   │ Threatening, coercion, fear-based influence   │
│ persuasion   │ Talking, charming, negotiating                │
│ perception   │ Noticing details, awareness, sight/hearing    │
└──────────────┴────────────────────────────────────────────────┘
```

### Skill Benchmarks
- **0**: Untrained (no experience)
- **1-20**: Novice (minimal training)
- **20-40**: Trained (regular experience)
- **40-60**: Experienced (veteran level)
- **60-80**: Expert (elite level)
- **80-100**: Master (legendary level)

---

## QUICK BUILD TEMPLATES

### Weak Thug
```yaml
Stats:  body:3 ref:2 dex:2 tech:1 smrt:1 will:1 edge:1 emp:1
Skills: brawling:15 blades:10 blunt:15 intimidate:20
```

### Standard Thug
```yaml
Stats:  body:4 ref:3 dex:3 tech:1 smrt:2 will:2 edge:2 emp:1
Skills: brawling:25 blades:15 blunt:20 dodge:10 intimidate:30 perception:15
```

### Veteran Thug
```yaml
Stats:  body:5 ref:4 dex:4 tech:2 smrt:3 will:3 edge:3 emp:2
Skills: brawling:40 blades:35 blunt:35 dodge:30 intimidate:45 perception:25
```

### Gang Leader
```yaml
Stats:  body:5 ref:5 dex:5 tech:4 smrt:5 will:5 edge:4 emp:6
Skills: brawling:50 blades:45 ranged:40 grapple:45 dodge:40 
        intimidate:60 persuasion:55 perception:45 stealth:30
```

### Security Guard
```yaml
Stats:  body:5 ref:4 dex:4 tech:2 smrt:3 will:4 edge:2 emp:2
Skills: ranged:40 dodge:35 perception:40 intimidate:35 brawling:30
```

### Soldier/Elite Fighter
```yaml
Stats:  body:6 ref:5 dex:5 tech:3 smrt:4 will:4 edge:3 emp:3
Skills: brawling:45 blades:40 ranged:50 dodge:45 perception:50 
        intimidate:40 stealth:25
```

### Stealth/Assassin
```yaml
Stats:  body:4 ref:6 dex:7 tech:3 smrt:4 will:5 edge:3 emp:2
Skills: blades:70 ranged:65 grapple:50 dodge:60 stealth:85 
        perception:60 intimidate:35
```

### Merchant/Shopkeeper
```yaml
Stats:  body:2 ref:2 dex:2 tech:2 smrt:5 will:4 edge:3 emp:6
Skills: persuasion:60 perception:35 intimidate:15 stealth:10
```

### Hacker/Tech Specialist
```yaml
Stats:  body:2 ref:4 dex:4 tech:8 smrt:7 will:4 edge:2 emp:2
Skills: dodge:20 perception:40 stealth:35
```

---

## COMMANDS

```
/designnpc                  # Start NPC designer
/spawnnpc                   # List all NPCs
/spawnnpc <keyword>         # Search NPCs
/spawnnpc <number>          # Spawn selected NPC
```

---

## TIPS

✓ Most NPCs should have stats 3-5 (average)
✓ Combat skills 0-40 for regular NPCs
✓ Elite NPCs: 50-70 in main skills
✓ Leaders: Higher empathy/persuasion
✓ Fighters: Higher combat stats/skills
✓ Create 3 versions: weak, medium, strong
✓ Reuse templates for mass spawning

---

**Remember:** Stats define potential, Skills define training!
