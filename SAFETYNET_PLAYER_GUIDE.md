# SafetyNet Player Guide

Welcome to SafetyNet, Kowloon's intranet social network. This guide covers everything you need to know to use the system as a player.

## Getting Started

### Requirements

To access SafetyNet, you need one of the following devices:

- **Wristpad**: A portable wrist-mounted computer. Slower connection but portable.
- **Computer Terminal**: A desktop computer station. Faster but stationary.
- **Portable Computer**: A compact laptop-like device. Medium speed and portable.

### Creating Your First Handle

A "handle" is your username on SafetyNet. You can create multiple handles for different personas.

1. Equip or be near a SafetyNet device
2. Type: `sn/register <handle_name>`
3. Your system-generated password will be displayed
4. **Save this password immediately** - it will not be shown again

Example:
```
sn/register shadowrunner
SafetyNet: Connected.
SafetyNet: Your password is: neon-phantom
[SafetyNet System] Save this password now. It will NOT be displayed again.
```

### Logging In

To access your handle:

```
sn/login <handle_name> <password>
```

You can be logged into only one handle at a time per character. Use `sn/logout` to switch handles.

## Using SafetyNet

### Feeds

SafetyNet has four public feeds where you can post and read messages:

1. **public** - General discussion and announcements
2. **market** - Buy/sell listings and trade offers
3. **rumors** - Gossip, hearsay, and questionable information
4. **jobs** - Work opportunities and contracts

### Posting

Post to any feed with:

```
sn/post <feed>=<message>
```

Example:
```
sn/post market=Selling military-grade cyberware. No questions asked. Contact for details.
sn/post jobs=Discreet extraction job, high pay. Need experienced solo immediately.
```

**Important**: Posts automatically decay after 72 hours and are permanently deleted.

### Reading Posts

View the latest posts from a feed:

```
sn/read <feed>
```

This shows the 10 most recent posts. Navigate with:
- `sn/read <feed>/next` - Next page of posts
- `sn/thread <post_number>` - View replies to a specific post (when implemented)

### Searching

Search all posts across all feeds:

```
sn/search <query>
```

Example:
```
sn/search cyberware
sn/search assassination
```

### Direct Messages (DMs)

Send private messages to other handles:

```
sn/dm <handle>=<message>
```

Example:
```
sn/dm shadowrunner=Are you interested in that extraction job we discussed?
```

Check your inbox:
```
sn/inbox
sn/inbox/next - Next page
sn/thread <handle> - View full conversation with handle
```

## Account Management

### Your Handles

List all your handles:

```
sn/handles
```

This shows which handles you own and their security status.

### Passwords

You get ONE password per handle. To change it:

```
sn/passchange <handle>=<old_password>
```

Your new password will be generated and displayed once. Save it immediately.

### Deleting a Handle

Permanently delete a handle (requires password verification):

```
sn/delete <handle>=<password>
```

**Warning**: This is permanent and cannot be undone. All DMs associated with the handle are also deleted.

## Security Information

### Online Status

Other users can see if you're currently logged in. Check who's online:

```
sn/ice <handle>
```

This shows:
- Online/offline status
- Handle's security rating (ICE)
- When the handle was created

### ICE Ratings

Each handle has an ICE (Intrusion Countermeasures & Electronics) rating that affects hacking difficulty. Higher ICE makes your account harder to infiltrate.

### Upgrading Security

Increase your handle's ICE rating:

```
sn/upgrade <handle>=<level>
```

Where level is 1-10. Higher levels cost more but provide better security against hacking attempts.

## Handle Lookup

Look up information about any handle (public information):

```
sn/whois <handle>
```

Returns:
- Handle name
- Creation date
- Online status
- ICE rating

## Connection Speeds

Different devices have different connection speeds:

- **Wristpad**: Slower (~2-5 seconds per operation). More secure and portable.
- **Computer**: Fast (~0.3-1 seconds per operation). Stationary but quick.

The connection delay simulates real network latency and is part of the atmosphere.

## Tips & Tricks

### Using Multiple Handles

Create different handles for different activities:
- Professional business handle
- Street contacts handle
- Anonymous rumor spreader handle

### Avoiding Detection

Posts are anonymously attributed to your handle, not your character name. This provides a layer of privacy between your in-game identity and your online presence.

### Ephemeral Posts

Remember that posts disappear after 72 hours. Important information should be archived privately or via DM.

### DM Organization

Use the thread view to keep conversations organized by contact. This is crucial for multi-party negotiations.

## Troubleshooting

### "No Access Device Detected"

You need a Wristpad or Computer nearby. Check your inventory or the room.

### "You must be logged in to do that"

You're not currently logged into a handle. Use `sn/login <handle> <password>`.

### "Already logged in as..."

Log out first with `sn/logout` before logging into a different handle.

### Password Lost

If you lose your password, there is no recovery system. The handle is permanently locked. Create a new handle with `sn/register`.

## In-Character Considerations

### Immersion

SafetyNet is deeply integrated into Kowloon's cyberpunk setting. Think of it like 1990s internet meets corporate intranet with a street edge.

### Roleplaying on SafetyNet

Your posts and DMs are in-character. Your handle is part of your street reputation. How you interact on SafetyNet reflects on your character IC.

### Information Control

Information posted on SafetyNet can spread. Valuable intel might get shared, leaked, or used against you. Be strategic about what you post.

---

For staff documentation, see [SAFETYNET_STAFF_GUIDE.md](SAFETYNET_STAFF_GUIDE.md).

**Last Updated**: January 14, 2026
