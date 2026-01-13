"""
Speak Command - Language switching and proficiency display

Usage:
    speak                           - List known languages with proficiency
    speak <language>                - Switch to speaking that language
    learn <language> <ip_amount>    - Spend IP to learn a language

Examples:
    speak cantonese      - Switch primary language to Cantonese
    speak english        - Switch to English
    speak                - Show all languages you know and proficiency
    learn mandarin 50    - Spend 50 IP to learn/improve Mandarin
"""

from evennia import Command
from world.language.constants import LANGUAGES
from world.language.utils import (
    get_character_languages,
    set_primary_language,
    get_language_proficiency,
    spend_ip_on_language,
    get_ip_spent_today_on_language,
    get_daily_ip_cap_for_language,
    get_language_learning_speed,
)


class CmdSpeak(Command):
    """
    Switch primary language or display language proficiencies.
    """
    key = "speak"
    aliases = ["language", "lang"]
    locks = "cmd:all()"
    help_category = "General"

    def func(self):
        caller = self.caller
        
        if not self.args or not self.args.strip():
            # Display mode - show all known languages with proficiency
            return self.show_languages(caller)
        
        # Parse input
        args = self.args.strip().lower().split()
        language_input = args[0]
        
        # Try to find matching language
        language_code = self.find_language(language_input)
        
        if not language_code:
            caller.msg(f"|rUnknown language: {language_input}|n")
            caller.msg("Use |yspeak|n to see available languages.")
            return
        
        # Set as primary language
        success, message = set_primary_language(caller, language_code)
        if success:
            caller.msg(f"|g{message}|n")
            caller.location.msg_contents(
                f"|y{caller.name} switches to speaking {LANGUAGES[language_code]['name']}.|n",
                exclude=[caller]
            )
        else:
            caller.msg(f"|r{message}|n")
    
    def show_languages(self, caller):
        """Display all known languages with proficiency."""
        from world.language.constants import ALL_LANGUAGES
        
        languages = get_character_languages(caller)
        primary = languages['primary']
        known = sorted(list(languages['known']))
        
        # Check if Builder or higher
        is_builder = caller.locks.check_lockstring(caller, "perm(Builder)")
        
        if is_builder:
            # Builders see all languages
            display_langs = sorted(ALL_LANGUAGES)
            text = "|cAll Languages (Builder View):|n\n"
        else:
            # Regular players see only known languages
            display_langs = known
            text = "|cLanguages You Know:|n\n"
        
        text += "-" * 60 + "\n"
        
        if not display_langs:
            text += "You don't know any languages yet.\n"
            caller.msg(text)
            return
        
        for lang_code in display_langs:
            lang_name = LANGUAGES[lang_code]['name']
            proficiency = get_language_proficiency(caller, lang_code)
            is_known = lang_code in known
            is_primary = " |g(primary)|n" if lang_code == primary else ""
            
            # Proficiency bar
            bar_length = 20
            filled = int(proficiency / 5)  # 5% per character
            bar = "|g" + "=" * filled + "|n" + "-" * (bar_length - filled)
            
            # Mark unknown languages if builder
            unknown_marker = "" if is_known else " |r(unknown)|n"
            
            text += f"{lang_name:30} {bar} {proficiency:6.1f}%{is_primary}{unknown_marker}\n"
        
        text += "-" * 60 + "\n"
        
        # Show learning speed
        learning_speed = get_language_learning_speed(caller)
        # Try both 'smarts' and 'smrt' as the stat might be named either way
        smarts = getattr(caller.db, 'smarts', None) or getattr(caller.db, 'smrt', 1)
        text += f"\nSmarts: {smarts} | Learning Speed: {learning_speed:.2f}x\n"
        text += f"You learn languages {learning_speed:.0%} faster than normal.\n"
        
        caller.msg(text)
    
    def find_language(self, input_str):
        """Find language by code or partial name match."""
        input_lower = input_str.lower()
        
        # Exact code match
        if input_lower in LANGUAGES:
            return input_lower
        
        # Partial name match
        for code, info in LANGUAGES.items():
            if input_lower in info['name'].lower():
                return code
        
        return None


class CmdLearn(Command):
    """
    Spend IP to learn or improve a language.
    """
    key = "learn"
    aliases = ["practice"]
    locks = "cmd:all()"
    help_category = "General"

    def func(self):
        caller = self.caller
        
        if not self.args or not self.args.strip():
            caller.msg("Usage: learn <language> <ip_amount>")
            caller.msg("Example: learn mandarin 50")
            return
        
        args = self.args.strip().lower().split()
        
        if len(args) < 2:
            caller.msg("Usage: learn <language> <ip_amount>")
            return
        
        language_input = args[0]
        ip_str = args[1]
        
        # Find language
        cmd_speak = CmdSpeak()
        language_code = cmd_speak.find_language(language_input)
        
        if not language_code:
            caller.msg(f"|rUnknown language: {language_input}|n")
            return
        
        # Parse IP amount
        try:
            ip_amount = int(ip_str)
        except ValueError:
            caller.msg(f"|rInvalid IP amount: {ip_str}|n")
            return
        
        # Spend IP
        success, proficiency_gain, message = spend_ip_on_language(caller, language_code, ip_amount)
        
        if success:
            caller.msg(f"|g{message}|n")
            caller.location.msg_contents(
                f"|y{caller.name} practices {LANGUAGES[language_code]['name']}.|n",
                exclude=[caller]
            )
        else:
            caller.msg(f"|r{message}|n")
    
    def get_help(self, caller):
        """Show help for learn command."""
        text = "Usage: learn <language> <ip_amount>\n\n"
        text += "Spend IP to learn or improve a language.\n\n"
        text += "Cost: 5 IP = 1% proficiency\n"
        text += "Daily Caps:\n"
        
        for lang_code in sorted(LANGUAGES.keys()):
            spent_today = get_ip_spent_today_on_language(caller, lang_code)
            daily_cap = get_daily_ip_cap_for_language(caller, lang_code)
            text += f"  {LANGUAGES[lang_code]['name']}: {spent_today}/{daily_cap} IP used\n"
        
        text += "\nExample: learn mandarin 50\n"
        return text
