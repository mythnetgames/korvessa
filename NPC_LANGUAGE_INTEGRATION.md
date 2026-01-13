NPC Language System Integration

OVERVIEW

The NPC language system has been fully integrated into the NPC designer (designnpc command). NPCs can now be created with specific languages and language preferences, and these settings are stored and applied when NPCs are spawned.

SYSTEM COMPONENTS

1. Language Constants (world/language/constants.py)
   - 10 languages defined: English, Mandarin, Cantonese, Japanese, Korean, Vietnamese, Russian, Arabic, Hindi, Tradeband
   - Each language has name, description, and native flag
   - DEFAULT_LANGUAGE = 'cantonese'
   - MAX_LANGUAGES = 10

2. Language Utilities (world/language/utils.py)
   - initialize_character_languages(character, primary_language, additional_languages)
     Initializes character's language system with primary and known languages
   
   - get_language_flavor_text(character, verb="says")
     Returns formatted text like "*speaking Language in a [voice]*"
     Uses character.db.voice if set, otherwise generic form
   
   - check_can_speak_language(character, language_code)
     Returns True if character knows the language

3. NPC Builder Storage (world/builder_storage.py)
   - add_npc() function signature includes:
     * primary_language="english"
     * known_languages=None (defaults to ["english"])
   - NPC templates store both fields in database

4. NPC Designer Menu (commands/builder_menus.py)
   - npc_start(): Initializes NPC data with:
     * primary_language: "english"
     * known_languages: ["english"]
   
   - npc_properties(): Main menu shows option 5 for "Languages"
   
   - npc_languages(): Full interactive language configuration:
     * Lists all 10 languages with checkboxes
     * Shows which is primary language
     * Toggle languages by number or code
     * Set primary language with "primary <code>"
     * Supports up to 10 languages per NPC
   
   - npc_save(): Passes language data to add_npc() storage function

5. NPC Spawner (commands/builder_spawners.py)
   - CmdSpawnNPC._handle_spawn() now:
     * Reads primary_language from NPC template
     * Reads known_languages from NPC template
     * Sets both on spawned NPC object
     * Calls initialize_character_languages() to ensure system is initialized

COMPLETE FLOW

1. Designer Creates NPC:
   - designnpc [name]
   - Follows 7-step process
   - Step 5: Languages
   - Can toggle languages and set primary language

2. Designer Saves Template:
   - Data stored with primary_language and known_languages fields
   - add_npc() stores in builder_storage

3. Builder Spawns NPC:
   - spawnnpc [name/id]
   - CmdSpawnNPC._handle_spawn() creates NPC object
   - Sets db.primary_language from template
   - Sets db.known_languages from template
   - Calls initialize_character_languages() to ensure NDB initialized

4. NPC Uses Language:
   - When NPC speaks, get_language_flavor_text() formats output
   - Uses character.db.voice for accent if set
   - Format: "*speaking [Language] in a [voice]*"

DESIGNER MENU OPTION 5: LANGUAGES

Display shows:
- Current primary language
- List of all 10 languages with checkboxes
- [X] for known languages, [ ] for unknown
- Known languages count (X/10)

Commands:
- Enter number to toggle language (add/remove)
- "primary <code>" to set primary language
- "b" to go back

Constraints:
- Minimum 1 language (English by default)
- Maximum 10 languages
- Cannot remove primary language without setting new primary first

DATABASE STORAGE

NPC Template Data Structure:
{
    "id": "npc_1",
    "name": "Street Vendor",
    "desc": "An old street vendor",
    "faction": "neutral",
    "wandering_zone": "downtown",
    "is_shopkeeper": false,
    "primary_language": "english",
    "known_languages": ["english", "mandarin", "cantonese"],
    "stats": {...},
    "skills": {...},
    "created_by": "admin"
}

Character NPC Database Attributes:
- character.db.primary_language: "english"
- character.db.known_languages: set(["english", "mandarin", "cantonese"])

LANGUAGE SUPPORT

Supported Languages:
1. arabic - A language from the Middle East
2. cantonese - The primary language of Kowloon
3. english - Corporate + technical lingua franca. Used by a lot of Corpcits
4. hindi - Spoken by the Indian laborers, merchants, and cultural enclaves
5. japanese - Spoken by the shadowy Yakuza of Kowloon
6. korean - From the peninsula of Korea. Popular in contemporary pop music
7. mandarin - The older language of the mainland. Used by state officials, corporate envoys, mainland migrants
8. russian - The cold, wintery language of the USSR
9. tradeband - A mixed language consisting of a Cantonese base + English tech verbs + Japanese and Korean slang
10. vietnamese - Hailing from Vietnam, this language is spoken by many of the factory workers

Each language displays with proper name in menus and messages.

EXAMPLE USAGE

Designer creates NPC:
```
> designnpc
> Step 1: Street Vendor
> Step 2: An old man selling noodles from a cart
> ...
> Step 5 (Languages):
  [X] English (primary)
  [ ] Mandarin
  [X] Cantonese
  etc.
  > primary mandarin
  [X] English
  [X] Mandarin (primary)
  [X] Cantonese
  > b
> Step 6: Stats
> Step 7: Skills
> Save
```

NPC saved with: primary_language="mandarin", known_languages=["english", "mandarin", "cantonese"]

Builder spawns NPC:
```
> spawnnpc
1. Street Vendor (npc_1)
> 1
Spawned: Street Vendor
```

NPC object now has:
- db.primary_language = "mandarin"
- db.known_languages = {"english", "mandarin", "cantonese"}

When NPC speaks:
- *speaking Mandarin Chinese in a [voice]*
- (voice comes from character.db.voice if set)

INTEGRATION POINTS

Files Modified:
1. world/language/constants.py - Language definitions
2. world/language/utils.py - Language utilities
3. commands/builder_menus.py - Designer menu flow
4. world/builder_storage.py - NPC template storage
5. commands/builder_spawners.py - NPC spawning

Files Created:
- world/language/__init__.py - Package initialization

VALIDATION

All files checked for syntax errors - no issues found.
Language system is fully integrated and ready for use.

NEXT STEPS (OPTIONAL ENHANCEMENTS)

1. Add language-based NPC dialog filtering
   - NPCs only respond to speech in languages they know
   - Could filter commands or just emotes

2. Add accent variation
   - Currently uses character.db.voice
   - Could expand to accent descriptions per language

3. Add language learning
   - Allow characters to learn languages from NPCs
   - Progressive language skill system

4. Add communication fallback
   - Pidgin/broken language when speaker doesn't know primary language
   - "speaks broken Mandarin"

5. Add language skills
   - Connect to existing skill system
   - Affect fluency/accent of speech
