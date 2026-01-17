# Korvessa Website Theme Refactor - Deployment Guide

## Summary

The website has been refactored from a **cyberpunk "Kowloon"** theme to a **divine/apocalyptic "Korvessa"** theme matching the game's lore and setting.

## Changes Made

### 1. Navigation Menu (`web/templates/website/_menu.html`)
- **Replaced**: Cyberpunk neon colors (#00fff7, #a020f0, #ff00cc)
- **With**: Divine earth tones (#d4a574, #e8dcc8, #8b4513)
- **Added**: "Watcher's Eye" CSS visual element (glowing orbs flanking the title)
- **Styling**: Gold/brown gradient navbar with serif font
- **Terminology**: Changed "Decant Sleeve" → "Incarnate New Soul", "Manage Sleeves" → "Manage Souls"

### 2. Homepage Content (`web/templates/website/homepage/main-content.html`)
- **Complete rewrite** with setting-appropriate lore
- **Removed**: Cyberpunk "Kowloon chummer" narrative
- **Added**: Korvessa lore including:
  - The Herding (160 years ago)
  - The Watcher's protective sealing
  - The Sprinkling ceremony
  - Scholar's Passage history
  - Three Faction paths (Veloran, Feyliksian, Regalist)
- **Color scheme**: Dark browns/golds instead of neon
- **Typography**: Georgia serif fonts with proper spacing

### 3. Character Creation Form (`web/templates/website/character_form.html`)
- **Title**: "Define Your Existence" → "Incarnate Your Soul"
- **Subtitle**: Kowloon narrative → Korvessa setting narrative
- **Section headers**: "Your Nature" → "Your Essence"
- **Color scheme**: Updated to match homepage theme

### 4. Header Only Template (`web/templates/website/header_only.html`)
- **Background**: Updated to divine theme dark brown (#1a1410)

## Deployment Steps

To deploy the theme changes to production:

```bash
# On your development machine:
# All template files have been updated locally

# Copy files to remote server:
scp -i <path/to/ssh/key> \
  "web/templates/website/_menu.html" \
  ubuntu@3.15.195.148:/home/ubuntu/korvessa/web/templates/website/

scp -i <path/to/ssh/key> \
  "web/templates/website/homepage/main-content.html" \
  ubuntu@3.15.195.148:/home/ubuntu/korvessa/web/templates/website/homepage/

scp -i <path/to/ssh/key> \
  "web/templates/website/character_form.html" \
  ubuntu@3.15.195.148:/home/ubuntu/korvessa/web/templates/website/

scp -i <path/to/ssh/key> \
  "web/templates/website/header_only.html" \
  ubuntu@3.15.195.148:/home/ubuntu/korvessa/web/templates/website/

# On the remote server:
ssh -i <path/to/ssh/key> ubuntu@3.15.195.148 << 'EOF'
# Clear Python cache
find /home/ubuntu/korvessa -type d -name '__pycache__' -exec rm -rf {} + 2>/dev/null
find /home/ubuntu/korvessa -name '*.pyc' -delete 2>/dev/null

# Restart Evennia
export PATH=/home/ubuntu/korvessa/venv/bin:$PATH
cd /home/ubuntu/korvessa
evennia restart

# Wait for server to fully restart
sleep 6

# Test the homepage
curl -s http://localhost/ | grep -q 'Welcome to Korvessa' && echo 'SUCCESS: Theme deployed!' || echo 'PENDING: Server still initializing'
EOF
```

## Visual Theme Palette

**Primary Colors:**
- Title Gold: #e8dcc8
- Accent Brown: #8b4513
- Accent Gold: #d4a574
- Secondary Gold: #c19a6b
- Background Dark: #1a1410
- Content Dark: #2d1f0e

**Typography:**
- Primary Font: Georgia, Palatino, serif
- Letter Spacing: 1-2px for headings
- Line Height: 1.6

**Faction Card Colors:**
- Veloran (Order): #d4a574
- Feyliksian (Chance): #c5a572
- Regalus (Dominion): #8b4513

##Files Modified

1. `web/templates/website/_menu.html` - Navigation with Watcher eye theme
2. `web/templates/website/homepage/main-content.html` - Lore-rich homepage content
3. `web/templates/website/character_form.html` - Character creation with thematic messaging
4. `web/templates/website/header_only.html` - Background color update

## Theme Characteristics

- **Mood**: Medieval/mystical with apocalyptic undertones
- **Tone**: Divine authority, mystery, faction politics
- **Visual Language**: Gold accents on dark earth tones
- **Typography**: Serif fonts for sacred/formal content
- **Interactive Elements**: Faction-colored left borders on content cards

## Next Steps

1. **Deploy** the files using the steps above
2. **Test** that the homepage displays lore-appropriate content
3. **Verify** faction cards render with correct colors
4. **Check** character form updates with "Incarnate Your Soul" terminology
5. **Optional**: Update favicon and logo images to match divine theme

## Rollback

If needed to revert to the cyberpunk theme:
```bash
# Template files are in version control, revert as needed
git checkout web/templates/website/

# Clear cache and restart
find /home/ubuntu/korvessa -type d -name '__pycache__' -exec rm -rf {} + 2>/dev/null
cd /home/ubuntu/korvessa && evennia restart
```
