# NPC System Quick Reference

## One-Minute Summary

NPCs are **non-player characters** that builders can create and configure. Admins can puppet (control) them, and they have scripted reactions to player keywords.

## Quick Commands

### Create NPC
```
@create-npc [name]                    # Create an NPC
@create-npc [name]=[description]      # Create with description
```

### Puppet NPC
```
@puppet [npc]        # Take control of NPC (you move to their location)
@unpuppet            # Stop controlling NPC (you return to previous location)
```

### Add Reactions
```
@npc-react [npc]=[trigger]/say [message]     # NPC says something
@npc-react [npc]=[trigger]/emote [action]    # NPC emotes
@npc-react [npc]=[trigger]/pose [action]     # NPC poses (longer action)
```

### View/Remove Reactions
```
@npc-react [npc]/list                        # List all reactions
@npc-react [npc]/remove=[trigger]            # Remove all reactions for trigger
```

### Configure NPC
```
@npc-config [npc]=wander:yes                 # Enable wandering
@npc-config [npc]=zone:[zone_name]           # Set wander zone
@npc-config [npc]=accent:[accent_name]       # Set accent/dialect
@npc-config [npc]/info                       # View configuration
```

## Practical Examples

### Example 1: Market Vendor

```
@create-npc street vendor=A weathered merchant with kind eyes.
@npc-config street vendor=zone:market
@npc-react street vendor=hello/say Welcome to my stall!
@npc-react street vendor=wares/say Quality goods at fair prices.
@npc-react street vendor=price/say Everything's reasonably priced.
```

Now when players say "hello" or "wares" near the vendor, they get responses.

### Example 2: Grumpy Guard

```
@create-npc guard=A stern-faced sentinel.
@npc-config guard=zone:fortress
@npc-react guard=hello/say State your business.
@npc-react guard=who/say Who are YOU?
@npc-react guard=trouble/emote eyes you suspiciously
```

### Example 3: Friendly Bartender

```
@create-npc bartender=A jovial fellow wiping down the bar.
@npc-config bartender=zone:tavern
@npc-react bartender=hello/say Welcome in! What's your poison?
@npc-react bartender=drink/say Coming right up!
@npc-react bartender=quiet/emote chuckles to himself
```

## Puppeting an NPC

```
# You're an admin at your admin room
@puppet bartender

# You're now controlling the bartender
# Your character appears at the bartender's location
say Thanks for stopping by!
emote polishes a glass

# Do admin tasks while puppeted if needed
@py print("I'm the bartender!")

# Return to your admin character
@unpuppet

# You're back at your admin room
```

## Key Concepts

**Trigger**: The keyword players say that activates a reaction
- Case-insensitive: "Hello", "HELLO", "hello" all work
- Partial match: If trigger is "hello", it will match "hello there" or "say hello"

**Action**: What the NPC does when triggered
- `say` - NPC speaks
- `emote` - NPC performs a short action
- `pose` - NPC performs a longer, more dramatic action

**Zone**: A named area where NPC can wander
- Just a text name (e.g., "market", "fortress", "tavern")
- Rooms should have `room.db.zone = "market"` to be in that zone
- Prevents NPCs from wandering outside their assigned area

**Puppet**: Admin takes control of an NPC
- Your admin character is saved and hidden
- You control the NPC instead
- Use `@unpuppet` to return to admin character

## Common Patterns

### Greeting NPC
```
@npc-react friendly=hello/say Hello! Nice to see you.
@npc-react friendly=hello/emote waves warmly
@npc-react friendly=name/say My name is [NPC_NAME]!
@npc-react friendly=how are you/say I'm doing great!
```

### Informative NPC
```
@npc-react scholar=hello/say Greetings, student of knowledge!
@npc-react scholar=history/say History is the teacher of lessons.
@npc-react scholar=science/say Science uncovers the world's mysteries.
@npc-react scholar=question/say A fine question! Let me explain...
```

### Suspicious NPC
```
@npc-react suspicious=hello/emote eyes you warily
@npc-react suspicious=who/say Who's asking?
@npc-react suspicious=why/say Because I want to know.
@npc-react suspicious=trouble/pose steps closer threateningly
```

## Troubleshooting

**NPC not reacting?**
- Verify the reaction exists: `@npc-react [npc]/list`
- Players must say the exact trigger keyword
- NPC must be in same room as player
- Check capitalization (should be case-insensitive, but verify)

**Can't puppet NPC?**
- Ensure you're an Admin
- Ensure you have an active puppet (character)
- Ensure NPC exists and isn't already puppeted

**Reactions not saved?**
- Check: `@npc-react [npc]/list`
- Try adding the reaction again
- Use `@npc-config [npc]/info` to verify NPC exists

## Tips & Tricks

### Multiple Reactions Per Trigger
Add multiple reactions to the same trigger for variety:
```
@npc-react vendor=hello/say Hi there!
@npc-react vendor=hello/say Welcome!
@npc-react vendor=hello/emote smiles at you
```
The NPC will randomly pick one each time.

### Role-Play While Puppeting
While puppeted, you can do anything your admin account can:
```
@puppet npc_name
say Let me tell you a story...
emote settles into a chair
pose leans forward with interest
@py db_objects[0].db.interesting_fact = "Something interesting"
@unpuppet
```

### Zone System
Set up zones by configuring NPCs:
```
@npc-config npc1=zone:market
@npc-config npc2=zone:market
@npc-config npc3=zone:fortress
```
Then ensure rooms have: `room.db.zone = "market"` or `room.db.zone = "fortress"`

### Character Consistency
NPCs retain all character abilities:
- Can own items
- Can participate in combat
- Can have equipment
- Can gain experience (if configured)
- Can perform any command you set up

## File Locations

For reference:
- **NPC Typeclass**: `typeclasses/npcs.py`
- **Admin Commands**: `commands/npc_admin.py`
- **Full Documentation**: `NPC_SYSTEM.md`
- **Reaction Examples**: `NPC_REACTION_EXAMPLES.md`

## Command Summary Table

| Command | Permission | Purpose |
|---------|-----------|---------|
| @create-npc | Admin | Create new NPC |
| @puppet | Admin | Take control of NPC |
| @unpuppet | Admin | Stop controlling NPC |
| @npc-react | Builder+ | Add/remove/list reactions |
| @npc-config | Builder+ | Configure NPC properties |

---

**Last Updated:** 2024
**Status:** Ready for use ✓
