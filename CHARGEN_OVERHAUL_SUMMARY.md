# Character Generation System Overhaul Summary

## Changes Made

### 1. Stat System Redesign
- **Old System**: All stats start at 1, distribute 35 points, max 10
- **New System**: All stats start at 5, distribute 12 points, max 12, min still 1

### 2. Implementation Details

#### Modified Files:
- `commands/charcreate.py`:
  - Updated `validate_stat_distribution()` to check for 12 distribution points above base 5
  - Updated `first_char_stat_assign()` to initialize stats at 5 instead of 1
  - Updated all display text to show "Distribute 12 points" and "1-12" ranges
  - Updated reset command to reset stats to 5 instead of 1
  - Updated `first_char_confirm()` to show distribution points instead of total
  - Updated `first_char_finalize()` to:
    - Award 200 IP to new characters
    - Display IP award message
    - Encourage players to invest IP in skills
    - Promote background submission system (50 IP bonus)

#### Stat Distribution Math:
- Base value: 5 for all 7 stats = 35 total base
- Distribution points: 12 available
- Maximum achievable per stat: 12 (5 base + 7 distribution if all points put in one stat)
- Minimum achievable per stat: 1 (can go below base)
- Average if distributed evenly: 5 + (12/7) = ~6.7 per stat

#### Examples:
- Specialist: body 12, reflexes 5, dex 5, tech 5, smarts 5, will 5, edge 5 (12 points used)
- Balanced: body 6, reflexes 7, dex 7, tech 6, smarts 6, will 7, edge 6 (12 points used)
- Dumping stats: body 8, reflexes 8, dex 8, tech 1, smarts 1, will 1, edge 1 (9 points used, 3 spent below base)

### 3. Background System
Created comprehensive background submission system with approval workflow.

#### New Command: `background`
- **Player Commands**:
  - `background` - View current background
  - `background submit <text>` - Submit new background (50 IP bonus on first submission)
  - `background edit <text>` - Edit background before approval
  - `background status` - Check approval status
  
- **Staff Commands** (Builder+):
  - `background/approve <character>` - Approve a background
  - `background/reject <character> <reason>` - Reject with feedback via pnotes
  - `background/view <character>` - View any character's background

#### Features:
- **50 IP Bonus**: Players receive 50 IP when they first submit a background
- **Minimum Length**: 50 characters required
- **Editability**: Can be edited until approved, locked after approval
- **Staff Feedback**: Rejections send pnotes with revision requests
- **Status Tracking**: 
  - `char.db.background` - Background text
  - `char.db.background_approved` - Approval boolean
  - `char.db.background_ip_awarded` - IP bonus given (prevents double-dipping)
- **Notifications**: Splattercast logging for staff awareness

#### New File:
- `commands/CmdBackground.py` - Complete background management system

#### Integration:
- Added to `commands/default_cmdsets.py` in `CharacterCmdSet`
- Promoted during character creation completion message

### 4. IP Economy Changes
- **New Characters**: Receive 200 IP at creation
- **Background Bonus**: Additional 50 IP for submitting a background
- **Total Possible Starting IP**: 250 IP (200 + 50 background bonus)

### 5. Character Creation Flow
1. Name entry (first/last)
2. Sex selection
3. Stat distribution (base 5, 12 points, max 12)
4. Confirmation
5. Primary language selection
6. Secondary language selection (if Smarts >= 7)
7. Character creation
8. **NEW**: 200 IP award message
9. **NEW**: IP system explanation
10. **NEW**: Background submission promotion (50 IP bonus)

### 6. Messages Updated
- Stat assignment screen shows "Distribute 12 points" instead of "35 points"
- Range display shows "1-12" instead of "1-10"
- Reset message says "Reset all stats to 5" instead of "1"
- Confirmation shows "Distribution points used: X/12" instead of "Total: X/35"
- Completion includes comprehensive IP and background system explanation

## Testing Checklist

### Character Creation
- [ ] Create new character
- [ ] Verify stats start at 5
- [ ] Distribute 12 points
- [ ] Confirm stats can go from 1 to 12
- [ ] Verify reset returns stats to 5
- [ ] Verify validation rejects wrong point totals
- [ ] Verify character receives 200 IP on creation
- [ ] Verify background submission promotion message

### Background System
- [ ] Submit initial background (should award 50 IP)
- [ ] View background with `background`
- [ ] Check status with `background status`
- [ ] Edit background before approval
- [ ] Verify IP bonus only given once
- [ ] Staff: Approve a background
- [ ] Staff: Reject with feedback (pnote sent)
- [ ] Verify approved backgrounds cannot be edited
- [ ] Staff: View other character's backgrounds

### Integration
- [ ] Verify flash clones inherit stats correctly
- [ ] Verify template respawns work
- [ ] Verify existing characters unaffected
- [ ] Test stat modification in-game still works

## Database Schema
No database migrations required - all changes use existing infrastructure:
- Stats stored as before (AttributeProperty)
- IP stored in `char.db.ip`
- Background data:
  - `char.db.background` (str)
  - `char.db.background_approved` (bool)
  - `char.db.background_ip_awarded` (bool)

## Backwards Compatibility
- Existing characters keep their current stats unchanged
- Stat system changes only affect new character creation
- Flash clones inherit stats from dead characters (no change)
- Template-based respawns use template values (no change)
- AttributeProperty defaults still set to 1 as fallback (safe)

## Notes
- Empathy calculation unchanged: edge + willpower
- Language selection still requires Smarts >= 7 for second language
- Passive language learning still requires Smarts >= 4
- All combat, IP investment, and skill systems unaffected
