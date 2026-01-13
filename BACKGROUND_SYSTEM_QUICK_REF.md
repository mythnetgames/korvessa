# Background System Quick Reference

## Overview
The background submission system allows players to write their character's backstory and receive IP bonuses. Staff review and approve backgrounds to ensure quality and setting compliance.

## Player Commands

### View Background
```
background
```
Shows your current background and approval status.

### Submit Background
```
background submit <text>
```
- **First time only**: Awards 50 IP bonus
- Minimum 50 characters required
- Cannot submit if already have one (use edit instead)

### Edit Background
```
background edit <text>
```
- Can only edit BEFORE approval
- Locked after staff approval
- Minimum 50 characters required

### Check Status
```
background status
```
Shows:
- Approval status (Pending/Approved)
- IP bonus received status

## Staff Commands (Builder+)

### Approve Background
```
background/approve <character>
```
- Locks background (player can no longer edit)
- Notifies player if online
- Logs to Splattercast

### Reject with Feedback
```
background/reject <character> <reason>
```
- Sends pnote to player with reason
- Allows player to revise and resubmit
- Notifies player if online

### View Any Background
```
background/view <character>
```
Shows:
- Character's background text
- Approval status
- IP bonus status

## Database Fields

### Character Attributes
- `char.db.background` (str) - Background text
- `char.db.background_approved` (bool) - Approval status
- `char.db.background_ip_awarded` (bool) - IP bonus given flag

## Workflow

### Player Workflow
1. Create character (receive 200 IP)
2. Submit background: `background submit <text>` (+50 IP)
3. Check status: `background status`
4. If rejected, check pnotes for feedback
5. Revise: `background edit <text>`
6. Wait for approval

### Staff Workflow
1. See submission in Splattercast
2. Review: `background/view <character>`
3. Decision:
   - **Approve**: `background/approve <character>`
   - **Request changes**: `background/reject <character> <detailed feedback>`
4. Player receives pnote with feedback
5. Player revises and resubmits
6. Repeat review until approved

## Tips for Players

### Good Backgrounds
- At least 200-300 words recommended (minimum 50 characters)
- Explain character motivations
- Reference setting elements (Kowloon, slums, City, corps, etc.)
- Include character personality traits
- Describe formative experiences

### What to Avoid
- Generic/vague backstories
- Contradicting established lore
- Overpowered backgrounds (secret corporate heir, military super-soldier, etc.)
- Minimal effort submissions just for IP

### Example Structure
```
Born in [location], [character name] grew up [circumstances].
[Formative experience] shaped their [personality trait].
They learned to [skill/trade] from [mentor/experience].
Now they [current situation/goals].
```

## IP Economy

### Starting IP Breakdown
- Character creation: **200 IP**
- Background submission: **+50 IP**
- **Total possible starting IP**: 250 IP

### Background Bonus Rules
- Awarded ONLY on first submission
- Cannot be earned multiple times
- Given immediately upon submission
- Not dependent on approval

## Integration with Other Systems

### With Pnotes
- Staff feedback sent via pnotes
- Player checks with: `look pnotes` or `pread`

### With IP System
- IP awarded to `char.db.ip`
- Can immediately invest in skills
- See: `help ip` for investment options

### With Character Creation
- Promoted at end of chargen
- Not required but encouraged
- Can submit anytime after creation

## Staff Notes

### Review Criteria
1. **Length**: Reasonable depth (50+ chars minimum, 200+ recommended)
2. **Setting Fit**: Matches cyberpunk Kowloon setting
3. **Quality**: Not generic/copy-pasted
4. **Consistency**: Doesn't contradict lore
5. **Reasonable**: Not overpowered/implausible

### Feedback Guidelines
- Be specific about what needs improvement
- Reference setting elements if needed
- Suggest directions for revision
- Be constructive and helpful

### Common Issues
- Too short/minimal effort
- Contradicts setting
- Overpowered background
- Generic "grew up poor" with no detail
- No character motivation/personality

## Troubleshooting

### Player Can't Edit
- Background already approved (staff must manually edit if needed)
- Contact staff for post-approval changes

### IP Not Received
- Check `stats` command for current IP
- Verify `background status` shows IP awarded
- Contact staff if issue persists

### Pnote Not Received
- Check `look pnotes` or `plist`
- Staff may not have sent feedback yet
- Contact staff if rejection message received but no pnote

## Commands Summary

| Command | Access | Purpose |
|---------|--------|---------|
| `background` | All | View your background |
| `background submit <text>` | All | Submit new background (50 IP) |
| `background edit <text>` | All | Edit unapproved background |
| `background status` | All | Check approval/IP status |
| `background/approve <char>` | Builder+ | Approve a background |
| `background/reject <char> <reason>` | Builder+ | Request revisions |
| `background/view <char>` | Builder+ | View any background |
