# SafetyNet Password System - Player Information

## How SafetyNet Passwords Work

When you create a new handle on SafetyNet, the system automatically generates a secure password for you. This password is displayed once and should be saved immediately.

## Password Format

SafetyNet passwords follow a cyberpunk naming convention:

```
<word1>-<word2>
```

**Example passwords:**
- `neon-phantom`
- `chrome-runner`
- `glitch-nexus`
- `turbocharged-decker`
- `quantum-fortress`
- `plasma-syndicate`

## Password Security

### Why the Format?

The two-word format with a large word pool provides excellent security:

- **Word Pool**: 250+ words per position = 62,500+ possible combinations
- **No Dictionary Attacks**: Cyberpunk-themed words aren't in standard dictionaries
- **Case Insensitive**: Passwords work with any capitalization
- **Easy to Remember**: Two words are easier than random characters
- **Immersive**: Passwords feel like they belong in the Kowloon setting

### Examples of Generated Passwords

**Word Set 1** includes:
- Cyberpunk slang: chrome, neon, cyber, ghost, glitch, viral, razor, toxic
- Technical terms: quantum, photonic, modulation, entropy, cascade
- Chinese romanization: jianghu, kefu, dashi, shuajie
- Obscure words: pellucid, lambent, tenebrous, ephemeral
- And 200+ more...

**Word Set 2** includes:
- Entities: runner, decker, syndicate, nexus, network, mainframe
- Locations: street, alley, tower, fortress, datacenter, bunker
- Technical: algorithm, protocol, firewall, gateway, cipher
- Chinese romanization: zhenren, tianshen, yumeng, baishe
- And 200+ more...

## Password Management

### Creating a Handle

```
sn/register <handle_name>
```

Your password appears once:

```
SafetyNet: Your handle 'shadowrunner' has been created.
SafetyNet: Your password is: neon-phantom
[SafetyNet System] Save this password now. It will NOT be displayed again.
```

**Critical**: Copy and save this password immediately. There is no recovery system.

### Logging In

```
sn/login shadowrunner neon-phantom
```

Case doesn't matter:

```
sn/login shadowrunner NEON-PHANTOM    (works)
sn/login shadowrunner Neon-Phantom    (works)
```

### Changing Your Password

```
sn/passchange shadowrunner=neon-phantom
```

You'll get a new random password:

```
SafetyNet: Password changed.
Your new password: chrome-fortress
[SafetyNet System] Save this password now. It will NOT be displayed again.
```

### Important Notes

- Each handle has **ONE password only**
- Passwords are displayed only during creation and change
- You cannot recover a lost password
- If you lose the password, the handle is locked permanently

## Security Tips

### Protecting Your Passwords

1. **Save immediately**: Write passwords down or use a password manager IC
2. **Don't share**: Keep passwords secret from other players
3. **Unique handles**: Create different handles for different purposes
4. **Rotate regularly**: Change passwords periodically for security

### Account Recovery

If you lose your password:

- Contact a staff member for administrative help
- They may be able to reset your password
- No automatic recovery system exists

### Multiple Handles

You can create multiple handles with different personas:

- **Business handle**: For legitimate trade
- **Street handle**: For underworld contacts
- **Anonymous handle**: For rumors and gossip

Each has its own password and reputation.

## Hacking Attempts

Other characters can attempt to hack your handle. When someone hacks you:

1. They attempt to break your ICE (security rating)
2. If successful, they access your recent DMs
3. Successful hackers see notification on your account

### Protecting Against Hacks

- **Upgrade ICE**: `sn/upgrade shadowrunner=<level>` (costs in-game resources)
- **Be Online**: Logged-in handles are harder to hack (-2 difficulty)
- **Security Awareness**: Don't post sensitive information publicly

## Password Strength Comparison

### SafetyNet Passwords vs Common Systems

| System | Format | Security | Memorability |
|--------|--------|----------|--------------|
| SafetyNet | word-word | High (62,500+ combos) | Good |
| Dictionary Password | 8 characters | Variable | Variable |
| Random String | xyz789a1 | Very High | Poor |

SafetyNet balances immersion, security, and usability.

## Examples in Character

When your character learns a handle's password, you're essentially memorizing or writing it down:

**IC Roleplay**:
- "My handle is 'shadowrunner', password's 'neon-phantom' - write it down"
- "Memorized the decker's login: 'glitch-nexus'"
- "She scrawled her handle and password on a data chip"

**OOC Reality**:
- Passwords are just text strings
- You need both handle AND password to log in
- Sharing passwords is risky (other characters could impersonate you)

## Troubleshooting

### "Invalid password"

Check:
- Spelling (case doesn't matter, but punctuation does)
- The hyphen is there: `neon-phantom` not `neonphantom`
- You're using the right handle
- Passwords are case-insensitive

### "Already logged in as..."

You can only use one handle per character at a time:

```
sn/logout                  # Log out first
sn/login newhandle mypasswd  # Then log in to new handle
```

### Locked Handle

If you lose your password, contact staff for help. They may be able to:
- Reset your password
- Delete the handle so you can create a new one
- Recover access if there's a legitimate reason

## FAQ

**Q: Can I share my password with another player?**
A: You could, but then they can impersonate your handle. Not recommended.

**Q: What happens if my password is wrong?**
A: Login fails. You'll need the correct password.

**Q: Can staff see my password?**
A: Staff can reset passwords but cannot view existing passwords.

**Q: How long are passwords?**
A: Two words plus hyphen, typically 10-20 characters.

**Q: Can passwords have special characters?**
A: No, only letters and hyphen. SafetyNet uses simple but elegant formatting.

**Q: What if I forget my password?**
A: You'll need to contact staff for assistance. Start a new handle if needed.

---

**For More Information**: See [SAFETYNET_PLAYER_GUIDE.md](SAFETYNET_PLAYER_GUIDE.md)

**Last Updated**: January 14, 2026
