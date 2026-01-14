# SafetyNet Documentation Index

Complete documentation and reference for Kowloon's SafetyNet intranet social system.

## Quick Links

### For Players

Start here if you're a player character wanting to use SafetyNet:

1. **[SAFETYNET_PLAYER_GUIDE.md](SAFETYNET_PLAYER_GUIDE.md)** - Everything you need to know
   - Getting started and registration
   - Using feeds and posting
   - Direct messaging
   - Account management
   - Troubleshooting

2. **[SAFETYNET_PASSWORD_GUIDE.md](SAFETYNET_PASSWORD_GUIDE.md)** - How passwords work
   - Password format and security
   - Password generation
   - Changing and recovering passwords
   - Tips for account security

### For Staff & Builders

Administrative and technical documentation:

1. **[SAFETYNET_STAFF_GUIDE.md](SAFETYNET_STAFF_GUIDE.md)** - Technical reference
   - System architecture
   - Database structure
   - Administrative commands
   - Content moderation
   - Performance monitoring
   - Troubleshooting
   - Maintenance schedule

2. **[SAFETYNET_DEVICE_SPAWNING.md](SAFETYNET_DEVICE_SPAWNING.md)** - Device management
   - Spawning commands (@spawnsn, @wristpad, etc.)
   - Device specifications
   - Installation recommendations
   - Device properties and restrictions
   - Best practices for zone design

3. **[SAFETYNET_IMPLEMENTATION_SUMMARY.md](SAFETYNET_IMPLEMENTATION_SUMMARY.md)** - Complete overview
   - What was implemented
   - Architecture overview
   - Integration points
   - Deployment checklist
   - Known limitations and future work

## System Overview

SafetyNet is Kowloon's IC social network providing:

- **Handle Management**: Create unlimited handles with unique passwords
- **Public Feeds**: Post to four themed feeds (public, market, rumors, jobs)
- **Direct Messaging**: Private communication between handles
- **Security System**: ICE ratings and hacking mechanics
- **Device-Based Access**: Requires Wristpad or Computer
- **Post Decay**: Posts automatically expire after 72 hours

## Core Components

### Code Files

| File | Purpose | Lines |
|------|---------|-------|
| `world/safetynet/constants.py` | System constants and 250+ word password lists | 250+ |
| `world/safetynet/utils.py` | Utility functions for common operations | 250+ |
| `world/safetynet/core.py` | SafetyNetManager global script | 800+ |
| `world/safetynet/__init__.py` | Package exports | 10 |
| `commands/CmdSafetyNet.py` | Main player-facing command | 840+ |
| `commands/CmdSpawnSafetyNet.py` | Device spawning commands | 130+ |
| `typeclasses/items.py` | Device typeclasses (additions) | 90+ |
| `world/prototypes.py` | Device spawn prototypes (additions) | 80+ |
| `scripts/safetynet_decay.py` | Post expiry cleanup | 60+ |
| `commands/default_cmdsets.py` | Command registration (additions) | 10 |

### Documentation Files

| File | Purpose | Audience |
|------|---------|----------|
| SAFETYNET_PLAYER_GUIDE.md | Complete player guide | Players |
| SAFETYNET_PASSWORD_GUIDE.md | Password system explanation | Players |
| SAFETYNET_STAFF_GUIDE.md | Technical reference | Staff |
| SAFETYNET_DEVICE_SPAWNING.md | Device reference | Builders |
| SAFETYNET_IMPLEMENTATION_SUMMARY.md | System overview | Staff/Devs |
| SAFETYNET_DOCUMENTATION_INDEX.md | This file | Everyone |

## Key Features

### Handles (Accounts)

- Unlimited per character
- Single password each
- Cyberpunk-themed auto-generated passwords
- Session tracking (one character per handle)
- Ownership verification

### Posts

- Four themed feeds: public, market, rumors, jobs
- 500 character limit
- 72-hour automatic expiry
- Pagination (10 per page)
- Full-text search

### Direct Messages

- Private handle-to-handle communication
- Read/unread tracking
- Thread organization
- Real-time delivery to online handles
- Pagination support

### Security

- ICE ratings (1-10) per handle
- Skill-based hacking (decking skill)
- Online/offline access difficulty modifiers
- Margin-based DM access on successful hack
- Upgradeable security levels

### Devices

**Wristpad**
- Portable (worn on wrist)
- Slow connection (2-5 second delays)
- Budget-friendly

**Computer Terminal**
- Stationary (desk-mounted)
- Fast connection (0.3-1 second delays)
- Corporate feel

**Portable Computer**
- Portable laptop
- Fast connection
- Medium price point

## Commands Reference

### Player Commands

All player commands use the `sn` prefix:

```
sn/read <feed>          - Read posts from feed
sn/post <feed>=<msg>    - Create post
sn/login <handle> <pw>  - Log in to handle
sn/logout               - Log out
sn/dm <handle>=<msg>    - Send DM
sn/inbox                - View inbox
sn/inbox/next           - Next page
sn/thread <handle>      - View thread
sn/search <query>       - Search posts
sn/handles              - List your handles
sn/register <handle>    - Create handle
sn/delete <handle>=<pw> - Delete handle
sn/passchange <handle>  - Change password
sn/ice <handle>         - Check ICE
sn/hack <handle>        - Attempt hack
sn/upgrade <handle>     - Upgrade ICE
sn/whois <handle>       - Lookup handle
```

### Staff Commands

Device spawning:

```
@spawnsn wristpad           - Spawn standard wristpad
@spawnsn wristpad/deluxe    - Spawn deluxe wristpad
@spawnsn computer           - Spawn desktop computer
@spawnsn computer/personal  - Spawn personal computer
@spawnsn computer/portable  - Spawn portable computer

@wristpad                   - Quick spawn wristpad
@computer                   - Quick spawn computer
@portablecomp               - Quick spawn portable computer
```

## Getting Started

### For Players

1. Locate a SafetyNet device (Wristpad or Computer)
2. Use `sn/register <your_handle>`
3. Save the password that appears
4. Use `sn/login <handle> <password>` to start using SafetyNet
5. Try `sn/post public=<message>` to post

### For Staff

1. Spawn devices using `@spawnsn` commands
2. Place in appropriate locations (markets, offices, etc.)
3. Players can immediately start using SafetyNet
4. Check [SAFETYNET_STAFF_GUIDE.md](SAFETYNET_STAFF_GUIDE.md) for admin operations

### For Developers

1. Review [SAFETYNET_IMPLEMENTATION_SUMMARY.md](SAFETYNET_IMPLEMENTATION_SUMMARY.md)
2. Read source code in `world/safetynet/`
3. Check [SAFETYNET_STAFF_GUIDE.md](SAFETYNET_STAFF_GUIDE.md) for architecture details
4. See future enhancement points in summary

## Constants & Configuration

### System Settings

All in `world/safetynet/constants.py`:

- POST_DECAY_SECONDS: 259200 (72 hours)
- POSTS_PER_PAGE: 10
- DMS_PER_PAGE: 10
- MAX_HANDLES_PER_CHARACTER: None (unlimited)
- MAX_PASSWORDS_PER_HANDLE: 1

### Device Delays

- Wristpad: 2.5-5 seconds
- Computer: 0.3-1 seconds

### ICE Settings

- Default rating: 1
- Max rating: 10
- Online modifier: -2 (easier)
- Offline modifier: +3 (harder)

### Password Generation

- Word List 1: 250+ cyberpunk adjectives
- Word List 2: 250+ niche nouns
- Format: `word1-word2`
- Total combinations: 62,500+

## Troubleshooting

### Can't Access SafetyNet

- Ensure you have a Wristpad or Computer
- Check you're in the same room as the device
- Try `sn/help` for command syntax

### Password Issues

- Passwords are case-insensitive
- Include the hyphen: `neon-phantom` not `neonphantom`
- Lost password? Contact staff for reset

### Performance Issues

- Ensure decay script is running (hourly cleanup)
- Check post count: `py len(get_safetynet_manager().db.posts)`
- Monitor during peak usage times

### Moderation Issues

- See [SAFETYNET_STAFF_GUIDE.md](SAFETYNET_STAFF_GUIDE.md) for removal procedures
- Use search to find problematic posts
- Contact admin for handle deletion

## Frequently Asked Questions

**Q: Can I have multiple handles?**
A: Yes, unlimited handles per character.

**Q: What if I lose my password?**
A: Contact staff. No automatic recovery exists.

**Q: How long do posts stay?**
A: 72 hours, then automatically deleted.

**Q: Can others see my DMs?**
A: Only if they successfully hack your account.

**Q: How do I protect my handle?**
A: Increase ICE rating with `sn/upgrade`.

**Q: Can I block other handles?**
A: Not yet - planned for future version.

**Q: How much do devices cost?**
A: Depends on roleplay cost in your zone - staff determine IC prices.

## Getting Help

### For Players

- Read [SAFETYNET_PLAYER_GUIDE.md](SAFETYNET_PLAYER_GUIDE.md)
- Check [SAFETYNET_PASSWORD_GUIDE.md](SAFETYNET_PASSWORD_GUIDE.md)
- Ask staff for IC reasons why you can't access
- Contact admin for technical issues

### For Staff

- Read [SAFETYNET_STAFF_GUIDE.md](SAFETYNET_STAFF_GUIDE.md)
- Check [SAFETYNET_DEVICE_SPAWNING.md](SAFETYNET_DEVICE_SPAWNING.md)
- Review [SAFETYNET_IMPLEMENTATION_SUMMARY.md](SAFETYNET_IMPLEMENTATION_SUMMARY.md)
- Check source code for detailed comments

### For Developers

- All architectural details in [SAFETYNET_STAFF_GUIDE.md](SAFETYNET_STAFF_GUIDE.md)
- Implementation overview in [SAFETYNET_IMPLEMENTATION_SUMMARY.md](SAFETYNET_IMPLEMENTATION_SUMMARY.md)
- Source code thoroughly commented
- Future enhancements documented

## Version History

**v1.0** - January 14, 2026
- Initial implementation
- Core features complete
- All documentation finished
- Production ready

## Credits

**Implementation**: Development Team
**Documentation**: Technical Writers
**Testing**: QA & Community

## Next Steps

1. Place devices in key locations
2. Distribute player guide to community
3. Train staff on admin procedures
4. Monitor for issues first week
5. Gather feedback for improvements

---

**Last Updated**: January 14, 2026
**Status**: Production Ready
**Questions**: Contact staff or development team
