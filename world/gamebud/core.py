"""
Gamebud Core Manager

Handles all data storage and retrieval for the Okama Gamebud system.
Uses a global script to store all Gamebud messages persistently.
"""

from datetime import datetime, timezone
from evennia import DefaultScript
from evennia.scripts.models import ScriptDB
from evennia import create_script
from world.gamebud.constants import (
    MAX_MESSAGES_STORED,
    MAX_ALIAS_LENGTH,
    MAX_MESSAGE_LENGTH,
    MESSAGES_PER_PAGE,
    GAMEBUD_PORT,
    GAMEBUD_IP,
    UI_TEMPLATE,
    MESSAGE_LINE_TEMPLATE,
    EMPTY_MESSAGE_LINE,
    MSG_NEW_MESSAGE,
    DEFAULT_SHELL_COLOR,
    DEFAULT_ALIAS_COLOR,
)
import random
import string


# Global manager instance cache
_manager_cache = None


def generate_random_alias():
    """
    Generate a random alphanumeric alias for a Gamebud with no set alias.
    Returns a string of random letters and numbers with varying capitalization.
    
    Returns:
        str: Random alias string (e.g., "aB3xQ9p2")
    """
    chars = string.ascii_letters + string.digits
    return ''.join(random.choice(chars) for _ in range(8))


def get_gamebud_manager():
    """
    Get or create the global Gamebud manager.
    
    Returns:
        GamebudManager instance
    """
    global _manager_cache
    
    if _manager_cache is not None:
        # Verify it still exists
        try:
            if _manager_cache.pk:
                return _manager_cache
        except:
            pass
    
    # Try to find existing manager script
    managers = ScriptDB.objects.filter(db_key="gamebud_manager")
    if managers.exists():
        _manager_cache = managers.first()
        return _manager_cache
    
    # Create new manager
    _manager_cache = create_script(
        GamebudManager,
        key="gamebud_manager",
        persistent=True,
    )
    return _manager_cache


class GamebudManager(DefaultScript):
    """
    Global script that manages all Gamebud messages.
    
    Data Structure:
    
    db.messages = [
        {
            "id": int,
            "alias": str,           # Sender display name
            "alias_color": str,     # ANSI color code for alias
            "message": str,         # The message content
            "timestamp": datetime,  # When posted
            "sender_id": int,       # Character ID who sent it
        }
    ]
    
    db.private_messages = [
        {
            "id": int,
            "from_alias": str,      # Sender alias
            "from_color": str,      # Sender alias color
            "to_alias": str,        # Recipient alias
            "message": str,         # The message content
            "timestamp": datetime,  # When sent
            "sender_id": int,       # Character ID who sent it
            "read": bool,           # Has message been read
        }
    ]
    
    db.next_id = int  # Counter for message IDs
    db.next_pm_id = int  # Counter for private message IDs
    """
    
    def at_script_creation(self):
        """Initialize the Gamebud manager data structures."""
        self.db.messages = []
        self.db.private_messages = []
        self.db.next_id = 1
        self.db.next_pm_id = 1
    
    def add_message(self, alias, message, sender, alias_color=None):
        """
        Add a new message to the lobby.
        
        Args:
            alias (str): The sender's display alias
            message (str): The message content
            sender: The character object who sent it
            alias_color (str): ANSI color code for the alias
            
        Returns:
            dict: The created message entry
        """
        if alias_color is None:
            alias_color = DEFAULT_ALIAS_COLOR
            
        # Create message entry
        entry = {
            "id": self.db.next_id,
            "alias": alias[:MAX_ALIAS_LENGTH],
            "alias_color": alias_color,
            "message": message[:MAX_MESSAGE_LENGTH],
            "timestamp": datetime.now(timezone.utc),
            "sender_id": sender.id if sender else None,
        }
        
        # Add to messages list
        self.db.messages.append(entry)
        self.db.next_id += 1
        
        # Prune old messages if over limit
        while len(self.db.messages) > MAX_MESSAGES_STORED:
            self.db.messages.pop(0)
        
        # Notify all Gamebud holders
        self._notify_gamebud_holders(alias, sender)
        
        return entry
    
    def get_messages(self, page=0):
        """
        Get a page of messages.
        
        Args:
            page (int): Page number (0-indexed)
            
        Returns:
            list: List of message entries for this page
        """
        messages = list(self.db.messages)
        messages.reverse()  # Most recent first
        
        start = page * MESSAGES_PER_PAGE
        end = start + MESSAGES_PER_PAGE
        
        return messages[start:end]
    
    def get_total_pages(self):
        """
        Get total number of message pages.
        
        Returns:
            int: Number of pages
        """
        total = len(self.db.messages)
        if total == 0:
            return 0
        return (total + MESSAGES_PER_PAGE - 1) // MESSAGES_PER_PAGE
    
    def get_message_count(self):
        """
        Get total message count.
        
        Returns:
            int: Number of messages
        """
        return len(self.db.messages)
    
    # =========================================================================
    # PRIVATE MESSAGE METHODS
    # =========================================================================
    
    def send_private_message(self, from_alias, from_color, to_alias, message, sender):
        """
        Send a private message to another alias.
        
        Args:
            from_alias (str): Sender's alias
            from_color (str): Sender's alias color
            to_alias (str): Recipient's alias
            message (str): The message content
            sender: The character who sent it
            
        Returns:
            dict: The created message entry
        """
        # Initialize private_messages if it doesn't exist (migration)
        if not hasattr(self.db, "private_messages") or self.db.private_messages is None:
            self.db.private_messages = []
        if not hasattr(self.db, "next_pm_id") or self.db.next_pm_id is None:
            self.db.next_pm_id = 1
        
        entry = {
            "id": self.db.next_pm_id,
            "from_alias": from_alias[:MAX_ALIAS_LENGTH],
            "from_color": from_color,
            "to_alias": to_alias[:MAX_ALIAS_LENGTH].lower(),
            "message": message[:MAX_MESSAGE_LENGTH],
            "timestamp": datetime.now(timezone.utc),
            "sender_id": sender.id if sender else None,
            "read": False,
        }
        
        self.db.private_messages.append(entry)
        self.db.next_pm_id += 1
        
        # Prune old private messages (keep last 100)
        while len(self.db.private_messages) > 100:
            self.db.private_messages.pop(0)
        
        # Notify recipient if they have a Gamebud with matching alias
        self._notify_pm_recipient(to_alias, from_alias)
        
        return entry
    
    def get_private_messages(self, alias):
        """
        Get all private messages for an alias.
        
        Args:
            alias (str): The recipient alias to get messages for
            
        Returns:
            list: List of private message entries
        """
        if not hasattr(self.db, "private_messages") or self.db.private_messages is None:
            return []
        
        alias_lower = alias.lower()
        messages = [m for m in self.db.private_messages if m["to_alias"] == alias_lower]
        messages.reverse()  # Most recent first
        return messages
    
    def get_unread_count(self, alias):
        """
        Get count of unread private messages for an alias.
        
        Args:
            alias (str): The alias to check
            
        Returns:
            int: Number of unread messages
        """
        if not hasattr(self.db, "private_messages") or self.db.private_messages is None:
            return 0
        
        alias_lower = alias.lower()
        return sum(1 for m in self.db.private_messages 
                   if m["to_alias"] == alias_lower and not m["read"])
    
    def mark_messages_read(self, alias):
        """
        Mark all messages for an alias as read.
        
        Args:
            alias (str): The alias whose messages to mark read
        """
        if not hasattr(self.db, "private_messages") or self.db.private_messages is None:
            return
        
        alias_lower = alias.lower()
        for msg in self.db.private_messages:
            if msg["to_alias"] == alias_lower:
                msg["read"] = True
    
    def _notify_pm_recipient(self, to_alias, from_alias):
        """
        Notify the recipient of a private message.
        
        Args:
            to_alias (str): Recipient alias
            from_alias (str): Sender alias
        """
        from evennia.objects.models import ObjectDB
        
        to_alias_lower = to_alias.lower()
        
        # Find all Gamebud objects
        gamebuds = ObjectDB.objects.filter(db_typeclass_path__contains="OkamaGamebud")
        
        for gamebud in gamebuds:
            # Check if gamebud has matching alias
            gb_alias = getattr(gamebud.db, "alias", None)
            if not gb_alias or gb_alias.lower() != to_alias_lower:
                continue
            
            # Check if gamebud is held by a character
            holder = gamebud.location
            if not holder or not hasattr(holder, "msg"):
                continue
            
            # Skip if muted
            if gamebud.db.muted:
                continue
            
            # Send notification
            holder.msg(f"|c*beep*|n Private message from |w{from_alias}|n!")

    def _notify_gamebud_holders(self, sender_alias, sender):
        """
        Notify all characters holding a Gamebud about a new message.
        
        Args:
            sender_alias (str): The alias of the sender
            sender: The character who sent the message
        """
        from evennia.objects.models import ObjectDB
        
        # Find all Gamebud objects
        gamebuds = ObjectDB.objects.filter(db_typeclass_path__contains="OkamaGamebud")
        
        for gamebud in gamebuds:
            # Check if gamebud is held by a character
            holder = gamebud.location
            if not holder:
                continue
            
            # Skip if holder is the sender
            if holder == sender:
                continue
            
            # Skip if holder is not a character (e.g., in a room or container)
            if not hasattr(holder, "msg"):
                continue
            
            # Skip if muted
            if gamebud.db.muted:
                continue
            
            # Send notification
            holder.msg(MSG_NEW_MESSAGE.format(sender=sender_alias))


def check_gamebud_device(character):
    """
    Check if character has a Gamebud device.
    
    Args:
        character: The character to check
        
    Returns:
        OkamaGamebud or None
    """
    for obj in character.contents:
        if getattr(obj.db, "is_gamebud", False):
            return obj
    return None


def format_gamebud_display(gamebud, page=0):
    """
    Format the Gamebud UI display.
    
    Args:
        gamebud: The Gamebud device
        page (int): Current message page
        
    Returns:
        str: Formatted UI display
    """
    manager = get_gamebud_manager()
    
    # Get alias - should always have one (either set or random)
    alias = gamebud.db.alias or generate_random_alias()
    
    # Shell color is always bright white
    shell_color = DEFAULT_SHELL_COLOR
    
    # Get unread private message count for this alias
    msg_count = manager.get_unread_count(alias)
    
    # Get messages for current page
    messages = manager.get_messages(page)
    
    # Format message lines
    message_lines = ""
    messages_shown = 0
    for msg in messages:
        # Name is max 10 chars, left aligned
        name = msg["alias"][:10].ljust(10)
        # Message is max 40 chars (to fit display width)
        content = msg["message"][:40].ljust(40)
        # Get alias color from message - add pipe prefix for ANSI
        alias_color = msg.get("alias_color", DEFAULT_ALIAS_COLOR)
        message_lines += MESSAGE_LINE_TEMPLATE.format(
            name=name, 
            message=content,
            alias_color=f"|{alias_color}"
        )
        messages_shown += 1
    
    # Fill remaining lines if less than 3 messages
    while messages_shown < MESSAGES_PER_PAGE:
        message_lines += EMPTY_MESSAGE_LINE
        messages_shown += 1
    
    # Build display
    cpu = random.randint(65, 99)
    
    # Generate loading bar based on CPU percentage
    bar_filled = int(cpu / 10)
    bar_empty = 10 - bar_filled
    loading_bar = "|" * bar_filled + "\\*" * min(bar_empty, 3)
    
    display = UI_TEMPLATE.format(
        port=GAMEBUD_PORT.ljust(2),
        cpu=str(cpu).rjust(2),
        ip=GAMEBUD_IP,
        alias=alias,
        msg_count=str(msg_count),
        messages=message_lines,
        bar=loading_bar,
    )
    
    return display
