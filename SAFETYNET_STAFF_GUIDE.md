# SafetyNet Staff Guide

This guide provides staff with technical information and administrative procedures for managing the SafetyNet system in Kowloon MUD.

## System Overview

SafetyNet is a persistent, IC social network implemented as a global manager script. It handles:

- Handle creation and management
- Post creation and decay
- Direct messaging (DMs)
- Account security (ICE ratings)
- Hacking and intrusion mechanics
- Session management

## Architecture

### Key Components

**SafetyNetManager** (`world/safetynet/core.py`):
- Global persistent script storing all data in `db.attributes`
- Accessed via `get_safetynet_manager()` singleton function
- Handles all business logic for accounts, posts, messages

**CmdSafetyNet** (`commands/CmdSafetyNet.py`):
- Main user-facing command with ~20 subcommands
- Device validation and connection delay simulation
- All player-facing operations

**Device Typeclasses** (`typeclasses/items.py`):
- `Wristpad`: Portable, slow (2.5-5 second delays)
- `ComputerTerminal`: Stationary, fast (0.3-1 second delays)
- `PortableComputer`: Portable, medium speed

**Spawn Prototypes** (`world/prototypes.py`):
- Pre-configured device templates for easy spawning

**Decay Script** (`scripts/safetynet_decay.py`):
- Runs hourly to clean up posts older than 72 hours
- Maintains database integrity

## Data Storage

All SafetyNet data is stored in a global script's database attributes:

### db.handles

Dictionary structure for user accounts:

```python
db.handles = {
    "handlename_lower": {
        "display_name": "HandleName",
        "owner_id": character_id,
        "password": "hashed_or_plain_password",
        "ice_rating": 1-10,
        "created": datetime_object,
        "session_char_id": None or character_id,  # Currently logged in
    }
}
```

### db.posts

List of all posts across all feeds:

```python
db.posts = [
    {
        "id": post_id_number,
        "handle": "handlename",
        "feed": "public|market|rumors|jobs",
        "message": "Post content up to 500 chars",
        "timestamp": datetime_object,
    }
]
```

### db.dms

Dictionary mapping handles to their DM inboxes:

```python
db.dms = {
    "handlename_lower": [
        {
            "id": dm_id,
            "from_handle": "sender",
            "message": "DM content",
            "timestamp": datetime_object,
            "read": True/False,
        }
    ]
}
```

### db.managed_rooms & db.next_post_id & db.next_dm_id

Supporting data:
- `managed_rooms`: List of room objects (for future multi-room expansion)
- `next_post_id`: Auto-incrementing post ID counter
- `next_dm_id`: Auto-incrementing DM ID counter
- `combat_is_running`: Boolean flag for system status

## Administrative Commands

### Staff Spawning

Spawn devices for players using prototypes:

```
@spawn/db world/prototypes:WRISTPAD
@spawn/db world/prototypes:COMPUTER_TERMINAL
@spawn/db world/prototypes:PORTABLE_COMPUTER
```

Or manually with `@create`:

```
@create/drop typeclasses.items.Wristpad
@create/drop typeclasses.items.ComputerTerminal
```

### Debugging SafetyNet

View the manager object:

```
py from world.safetynet.core import get_safetynet_manager; m = get_safetynet_manager(); print(m)
```

View all handles:

```
py from world.safetynet.core import get_safetynet_manager; m = get_safetynet_manager(); import pprint; pprint.pprint(list(m.db.handles.keys()))
```

View posts in a feed:

```
py from world.safetynet.core import get_safetynet_manager; m = get_safetynet_manager(); pprint.pprint([p for p in m.db.posts if p["feed"] == "public"][:5])
```

Check a handle's DMs:

```
py from world.safetynet.core import get_safetynet_manager; m = get_safetynet_manager(); pprint.pprint(m.db.dms.get("handlename", []))
```

## Technical Details

### Connection Delays

Simulates network latency based on device type:

**Wristpad** (slow access):
- Read: 2.5s
- Post: 3.0s
- DM: 2.0s
- Search: 4.0s
- Hack: 5.0s
- Login: 2.0s

**Computer** (fast access):
- Read: 0.3s
- Post: 0.5s
- DM: 0.3s
- Search: 0.5s
- Hack: 1.0s
- Login: 0.3s

Delays are implemented via `evennia.utils.delay()` callbacks. Players see a `[SafetyNet] Connecting...` message during the delay.

### Password Generation

Passwords are generated as two random words from large cyberpunk-themed word lists:

```python
def generate_password():
    word1 = random.choice(PASSWORD_WORDS_1)  # 250+ words
    word2 = random.choice(PASSWORD_WORDS_2)  # 250+ words
    return f"{word1}-{word2}"
```

With 250+ words per list, there are 62,500+ possible combinations, making brute force attacks computationally expensive even without rate limiting.

### Hacking System

Hacking attempts use skill-based resolution:

1. **Attacker rolls**: Decking skill (or Smrt stat fallback) + d20
2. **Difficulty**: 10 + ICE rating + online/offline modifier
3. **Margin of success**: Determines DM access depth
4. **Success**: Attacker can read 5 DMs + (2 * margin of success)

Example:
- Attacker rolls: 4 (skill) + 15 (d20) = 19
- Target ICE: 5, Online (-2 modifier) = Difficulty 13
- Margin: 19 - 13 = 6
- DMs accessible: 5 + (2 * 6) = 17 most recent DMs

### Session Management

Handles track current login state via `session_char_id`:

- `None`: Handle logged out
- `character_id`: Handle currently logged in by that character
- One character can be logged into one handle at a time
- Multiple characters can own the same handle (cooperative accounts)

## Moderating Content

### Removing Posts

Find a post ID and manually delete from database:

```
py from world.safetynet.core import get_safetynet_manager; m = get_safetynet_manager(); m.db.posts = [p for p in m.db.posts if p["id"] != POST_ID]
```

### Deleting Handles

Remove a problematic handle:

```
py from world.safetynet.core import get_safetynet_manager; m = get_safetynet_manager(); del m.db.handles["handlename_lower"]; del m.db.dms["handlename_lower"]
```

### Viewing Moderation-Relevant Data

View posts by a specific handle:

```
py from world.safetynet.core import get_safetynet_manager; m = get_safetynet_manager(); pprint.pprint([p for p in m.db.posts if p["handle"].lower() == "handlename"])
```

View DM thread between two handles:

```
py from world.safetynet.core import get_safetynet_manager; m = get_safetynet_manager(); pprint.pprint([d for d in m.db.dms.get("handlename1", []) if d["from_handle"].lower() == "handlename2"])
```

## Performance Considerations

### Database Size

- Each post: ~200-300 bytes (handle, feed, message, timestamp)
- Each DM: ~150-200 bytes
- With 1000 posts + 500 DMs: ~400 KB total

SafetyNet is designed to be lightweight. The decay system automatically removes posts every 72 hours.

### Scaling

For large player bases:

1. **Archive old posts**: Move posts older than 30 days to a separate archive database
2. **Periodic cleanup**: Run decay script more frequently (currently hourly)
3. **Pagination**: Already implemented (10 posts/DMs per page)
4. **Indexing**: Consider adding handle index if performance degrades

### Monitoring

Check script execution time in server logs. If SafetyNet operations slow down:

1. Verify decay script is running (checks `at_repeat()`)
2. Check database size with `py len(m.db.posts)`
3. Monitor command response times during peak usage

## Integration Points

### Character Integration

- SafetyNet tied to character objects, not player accounts
- Multiple characters can have the same handle (cooperative groups)
- Logout clears character `db.safetynet_handle` attribute

### Item Integration

- Device checking via inventory and room location
- Wristpad has priority over Computer for command validation
- Items must have `is_wristpad=True` or `is_computer=True` attributes

### Command Integration

- SafetyNet command registered in `CharacterCmdSet`
- Device validation gates access
- All commands run through single `CmdSafetyNet` class

## Future Enhancement Points

### Potential Features

1. **Block/ignore lists**: Prevent DMs from specific handles
2. **Post threading**: Replies and conversations
3. **Handle verification**: Prove ownership of official accounts
4. **Corporate channels**: Private feeds for organizations
5. **Market contracts**: Binding agreements through SafetyNet
6. **Encryption upgrades**: Hacking cost/difficulty scales
7. **Audit logs**: Track handle activity for investigation
8. **Profile customization**: Bio, avatar, status messages
9. **Federation**: Connect with external SafetyNet servers (IC)
10. **VPN/proxy chains**: Hide location and identity

### Code Locations to Extend

- `world/safetynet/core.py`: Add methods to SafetyNetManager
- `commands/CmdSafetyNet.py`: Add subcommands to `CmdSafetyNet`
- `world/safetynet/messages/`: Add rich narrative messages
- `scripts/safetynet_decay.py`: Modify cleanup logic

## Troubleshooting

### "Get or create combat" error

This might appear if SafetyNetManager conflicts with other scripts. Check:

```
py import inspect; from world.safetynet.core import get_safetynet_manager; print(inspect.getfile(get_safetynet_manager))
```

### Posts not decaying

Check decay script is running:

```
py from scripts.safetynet_decay import start_decay_script; start_decay_script()
```

### Handles not persisting

Ensure database commit is happening. Check with:

```
py from world.safetynet.core import get_safetynet_manager; m = get_safetynet_manager(); print(len(m.db.handles))
```

Should be > 0 if handles exist.

### DM delivery issues

Check session tracking:

```
py from world.safetynet.core import get_safetynet_manager; m = get_safetynet_manager(); pprint.pprint({h: d.get("session_char_id") for h, d in m.db.handles.items()})
```

## Maintenance Schedule

### Daily

- Monitor for player issues
- Check error logs for SafetyNet exceptions

### Weekly

- Verify decay script ran (check post count)
- Review flagged content if moderation reporting added

### Monthly

- Archive old posts if needed
- Update documentation based on deployed features
- Performance review if > 5000 posts

## References

- Player Guide: [SAFETYNET_PLAYER_GUIDE.md](SAFETYNET_PLAYER_GUIDE.md)
- Technical Reference: [AGENTS.md](AGENTS.md) - See SafetyNet section
- Core Module: `world/safetynet/core.py`
- Command Implementation: `commands/CmdSafetyNet.py`

---

**Last Updated**: January 14, 2026
**Version**: 1.0
**Maintained By**: Development Team
