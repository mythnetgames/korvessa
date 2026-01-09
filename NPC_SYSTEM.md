# NPC System Guide

## Overview

The NPC system allows builders and admins to create non-player characters with the following capabilities:

- **Reactions**: Scripted responses to player keywords/triggers
- **Puppeting**: Admins can temporarily control NPCs
- **Zones**: NPCs can be restricted to specific zones for wandering
- **Personality**: Accents, idle emotes, and customizable personality traits

## Commands

### Creation

**@create-npc <name>**
**@create-npc <name>=<description>**

Create a new NPC at your current location.

Examples:
```
@create-npc street vendor
@create-npc gang member=A rough-looking street enforcer with a scarred face.
```

### Puppeting

**@puppet <npc>**
- Take control of an NPC
- Your admin character will be moved to the NPC's location
- You will now control the NPC and can execute commands as it

**@unpuppet**
- Stop puppeting an NPC
- You will return to your admin character's previous location

Example flow:
```
# Admin is in the admin room
@puppet street vendor
# Admin is now controlling the vendor at the market location
say Welcome to my stall!
# The vendor says the message
@unpuppet
# Admin is back in the admin room
```

### Reactions

**@npc-react <npc>=<trigger>/<action>**

Add a reaction for when someone says a keyword.

Examples:
```
@npc-react street vendor=hello/say Hey there, friend!
@npc-react street vendor=greetings/emote smiles warmly and nods
@npc-react street vendor=how are you/say I'm doing well, thanks for asking!
```

Action types:
- `say <message>` - NPC says something
- `emote <action>` - NPC performs an emote
- `pose <action>` - NPC poses (longer form action)

**@npc-react <npc>/list**

List all reactions for an NPC.

**@npc-react <npc>/remove=<trigger>**

Remove all reactions for a trigger keyword.

Examples:
```
@npc-react street vendor/list
@npc-react street vendor/remove=hello
```

### Configuration

**@npc-config <npc>=<setting>:<value>**

Configure NPC properties.

Settings:
- `wander:<yes/no>` - Enable/disable wandering
- `zone:<zone_name>` - Set the zone the NPC can wander in
- `accent:<accent_name>` - Set the NPC's accent

Examples:
```
@npc-config street vendor=wander:yes
@npc-config street vendor=zone:market
@npc-config street vendor=accent:thick_accent
```

**@npc-config <npc>/info**

Display current configuration for an NPC.

Example:
```
@npc-config street vendor/info
```

Output:
```
=== Configuration for street vendor ===
Can Wander: True
Zone: market
Accent: thick_accent
Being Puppeted: False
```

## Reaction System Details

### How Reactions Work

When a player says something in the same room as an NPC with reactions, the NPC will:

1. Check if their message contains any of the trigger keywords
2. Randomly select one of the reactions for that trigger
3. Execute the selected action

### Multiple Reactions Per Trigger

You can add multiple reactions for the same trigger. Each time that trigger is used, one random reaction will be executed.

Example:
```
@npc-react street vendor=hello/say Hey there!
@npc-react street vendor=hello/say What can I do for you?
@npc-react street vendor=hello/emote looks up from their stall
```

When someone says "hello", the vendor will randomly choose one of these three reactions.

### Trigger Matching

- Triggers are case-insensitive
- Partial matches are used (if trigger is "hello", it will match "hello there" or "say hello")
- Each trigger is independent

## Puppet System Details

### What Puppeting Does

When you puppet an NPC:

1. Your admin character is moved to the NPC's location
2. You now control the NPC instead of your admin character
3. All commands you execute are executed by the NPC
4. When you unpuppet, you return to your previous location

### Admin/NPC Command Parity

NPCs have access to the same commands as player characters, including:
- `say`, `emote`, `pose` - Communication
- `look` - Perception
- `inventory`, `take`, `drop` - Item management
- Combat commands (if equipped with weapons)
- Any builder/admin commands your account has access to

### Puppet State Preservation

The system automatically preserves:
- Admin character's previous location
- Admin character's inventory
- Admin character's state

When you unpuppet, everything is restored to how it was before.

## Zone System Details

### Zone Management

NPCs can be restricted to specific zones:

```
@npc-config street vendor=zone:market
```

The zone name is a string - you can use any naming convention you prefer:
- Simple names: "market", "warehouse", "street"
- Hierarchical names: "district_1_market", "gang_territory_north"

### Zone Enforcement

The zone system provides a framework for limiting NPC wandering. When an NPC's wandering script checks if it can move to a new location, it will verify:

1. The location exists
2. The location's zone matches the NPC's assigned zone
3. If not, the NPC stays in its current location

### Location Zone Tracking

For zones to work effectively, rooms should have their zone stored in their database:

```python
# In room creation/configuration
room.db.zone = "market"
```

## Accent System Details

Accents are stored as string names and can be used to modify NPC speech patterns:

```
@npc-config street vendor=accent:heavy_accent
@npc-config street vendor=accent:upper_class
@npc-config street vendor=accent:none
```

The accent name is available for your scripts to use when customizing NPC dialogue or applying accent filters.

## Personality System Details

NPCs have a personality database with these properties:

```python
npc.db.npc_personality = {
    "greeting": "Hello there.",        # What NPC says on first meeting
    "idle_emotes": ["looks around", "sighs", "checks the time"],
    "idle_chance": 0.05,               # 5% chance per turn for idle emote
}
```

### Idle Emotes

NPCs have a chance to perform random idle emotes each turn:
- Set `idle_chance` to a value between 0 and 1 (e.g., 0.05 for 5%)
- NPCs will randomly select from `idle_emotes` list
- Idle emotes help make NPCs feel more alive

### Customizing Personality

To customize an NPC's personality:

```python
# Via admin commands (future feature)
vendor = search_object("street vendor")[0]
vendor.db.npc_personality["greeting"] = "Welcome to my shop!"
vendor.db.npc_personality["idle_emotes"] = ["arranges wares", "counts coins", "hums a tune"]
vendor.db.npc_personality["idle_chance"] = 0.1  # 10% chance
```

## Advanced Usage

### NPC-to-NPC Interactions

NPCs can interact with each other when puppeted. One admin can puppet an NPC, interact with other NPCs, then unpuppet.

### Combining With Combat

NPCs created with this system are full characters and can participate in combat:
1. Equip them with weapons via `give <npc> <weapon>`
2. They can be attacked with combat commands
3. They have stats that can be modified

### Scripting Reactions Dynamically

Reactions can be added/removed programmatically:

```python
# In a script or admin command
vendor = search_object("street vendor")[0]
vendor.add_reaction("poison", "say I don't sell that kind of thing!")
vendor.add_reaction("news", "say Have you heard about the disturbance?")
```

### Complex Reactions

For more complex reactions that need conditional logic, consider:
1. Using your puppeting system to handle complex interactions manually
2. Creating reaction triggers that lead to longer conversations
3. Adding multiple reactions per trigger to simulate different moods

## Troubleshooting

### NPC Not Reacting

- Check reactions are configured: `@npc-config <npc>/info`
- Verify the trigger keyword matches what players are saying
- Ensure the NPC is in the same room as the player
- Check that the NPC's reaction list isn't empty: `@npc-react <npc>/list`

### Cannot Puppet NPC

- Verify you have Admin permissions
- Ensure you have an active puppet (connected character)
- Check the NPC isn't already being puppeted by someone else
- Ensure the NPC exists and is in the same location as your character

### NPC Not Wandering

- Verify `wander:yes` is set: `@npc-config <npc>/info`
- Check that a zone is assigned: `@npc-config <npc>=zone:<zone>`
- Ensure target locations have the same zone configured

## Future Enhancements

Planned features:

- [ ] NPC dialogue trees and conversation branching
- [ ] NPC memory system (remembering interactions with players)
- [ ] NPC combat AI and tactics
- [ ] NPC healing/medical abilities
- [ ] NPC crafting and trade capabilities
- [ ] NPC faction relationships
- [ ] NPC daily schedules/patrol routes
- [ ] NPC random encounter generation

## Database Attributes

### NPC Database Attributes

```python
npc.db.is_npc = True                    # Marks this as an NPC
npc.db.npc_can_wander = False           # Whether NPC can wander
npc.db.npc_zone = None                  # Zone restriction
npc.db.npc_accent = None                # Accent name
npc.db.npc_reactions = {}               # {trigger: [actions]}
npc.db.puppeted_by = None               # Admin account controlling NPC
npc.db.admin_location = None            # Where admin was before puppeting
npc.db.admin_saved_state = {}           # Saved admin state
npc.db.npc_personality = {              # Personality settings
    "greeting": "Hello there.",
    "idle_emotes": ["looks around", "sighs"],
    "idle_chance": 0.05,
}
```

## Command Reference

| Command | Admin Only | Builder | Purpose |
|---------|-----------|---------|---------|
| @create-npc | Yes | - | Create new NPC |
| @puppet | Yes | - | Take control of NPC |
| @unpuppet | Yes | - | Stop controlling NPC |
| @npc-react | No | Yes | Add/remove/list reactions |
| @npc-config | No | Yes | Configure NPC properties |

---

*Last Updated: 2024*
*Part of the Kowloon game system*
