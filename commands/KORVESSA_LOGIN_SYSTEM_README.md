# Korvessa Login System

## Overview

This system implements a two-stage login process:

1. **Initial Login Screen** - Account creation/login
2. **Character Menu** - Character management after account authentication

## Files Created/Modified

### New Files
- `commands/unlogged_commands.py` - Initial login commands (create, connect)
- `commands/character_menu.py` - Character management commands (1-11 menu)
- This document

### Modified Files
- `typeclasses/accounts.py` - Enhanced Account class with new attributes
- `server/conf/connection_screens.py` - Updated splash screen

## New Account Attributes

When an account is created, these attributes are initialized:

```
account.db.email              # Email address (string)
account.db.created_chars      # List of character keys
account.db.retired_chars      # List of retired character keys
account.db.pending_apps       # List of pending applications
```

## Menu System (After Login)

```
1.  Login a character
2.  Submit a character application (approval required)
3.  Delete a pending application
4.  Retire your current character
5.  View your characters
6.  Update your e-mail address
7.  Change your account password
8.  Send/Check OOC Mail
11. Log Out
```

## Command Mappings

### Unlogged-in Commands
- `create <username> <password>` or `c` - Create new account
- `connect <username> <password>` or `login` or `l` - Log into account

### Character Menu Commands
| Menu | Command | Aliases |
|------|---------|---------|
| 1 | login | play, 1 |
| 2 | apply | 2 |
| 3 | delete_app | 3 |
| 4 | retire | 4 |
| 5 | characters | chars, 5 |
| 6 | email | 6 |
| 7 | password | 7 |
| 8 | mail | oocmail, 8 |
| 11 | logout | quit, 11 |

## Implementation Status

### Completed
✓ Account creation/login
✓ Character menu framework
✓ Password management
✓ Email management
✓ Character listing
✓ Account logout

### To Implement (Stubs in place)
- [ ] Character application system with approval
- [ ] Character retirement system
- [ ] OOC Mail system

## Usage

### For Players

1. **Create Account:**
   ```
   create myusername mypassword
   ```

2. **Login:**
   ```
   connect myusername mypassword
   ```

3. **Character Menu:** After login, you'll see the menu. Use numbers 1-8 or 11 to navigate.

### For Staff

To access account information:
```
@py account = search.account("username")[0]
print(account.db.email)
print(account.db.created_chars)
print(account.db.pending_apps)
```

To reset account data:
```
@py account = search.account("username")[0]; account.db.email = "newemail@test.com"
```

## Next Steps

1. **Integrate Character Creation** - Link to Korvessa character creation system with personality system
2. **Application System** - Implement staff approval workflow for character applications
3. **Character Retirement** - Move characters to retired list with archive
4. **OOC Mail** - OOC mail system between accounts

## Notes

- Validation is basic (email, password length). Enhance as needed.
- Character slots can be implemented via `account.get_available_character_slots()`
- This system coexists with Evennia's default commands
