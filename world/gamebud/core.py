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
            "message": str,         # The message content
            "timestamp": datetime,  # When posted
            "sender_id": int,       # Character ID who sent it
        }
    ]
    
    db.next_id = int  # Counter for message IDs
    """
    
    def at_script_creation(self):
        """Initialize the Gamebud manager data structures."""
        self.db.messages = []
        self.db.next_id = 1
    
    def add_message(self, alias, message, sender):
        """
        Add a new message to the lobby.
        
        Args:
            alias (str): The sender's display alias
            message (str): The message content
            sender: The character object who sent it
            
        Returns:
            dict: The created message entry
        """
        # Create message entry
        entry = {
            "id": self.db.next_id,
            "alias": alias[:MAX_ALIAS_LENGTH],
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
    
    # Get message count
    msg_count = manager.get_message_count()
    
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
        message_lines += MESSAGE_LINE_TEMPLATE.format(name=name, message=content)
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
