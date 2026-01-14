"""
SafetyNet Core Manager

Handles all data storage and retrieval for the SafetyNet system.
Uses a global script to store all SafetyNet data persistently.
"""

from datetime import datetime, timezone
from evennia import DefaultScript
from evennia.scripts.models import ScriptDB
from evennia import create_script
from world.safetynet.constants import (
    POST_DECAY_SECONDS,
    DEFAULT_ICE_RATING,
    MAX_ICE_RATING,
    SYSTEM_HANDLE,
    DEFAULT_FEED,
    AVAILABLE_FEEDS,
    MAX_HANDLES_PER_CHARACTER,
    MAX_PASSWORDS_PER_HANDLE,
)
from world.safetynet.utils import generate_password


# Global manager instance cache
_manager_cache = None


def get_safetynet_manager():
    """
    Get or create the global SafetyNet manager.
    
    Returns:
        SafetyNetManager instance
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
    managers = ScriptDB.objects.filter(db_key="safetynet_manager")
    if managers.exists():
        _manager_cache = managers.first()
        return _manager_cache
    
    # Create new manager
    _manager_cache = create_script(
        SafetyNetManager,
        key="safetynet_manager",
        persistent=True,
    )
    return _manager_cache


class SafetyNetManager(DefaultScript):
    """
    Global script that manages all SafetyNet data.
    
    Data Structure:
    
    db.handles = {
        "handle_name_lower": {
            "display_name": str,  # Original case handle name
            "owner_id": int,      # Character ID who created it
            "password": str,      # Single password for this handle
            "ice_rating": int,    # Security level 1-100
            "created": datetime,  # When created
            "session_char_id": int or None,  # Currently logged in character ID
        }
    }
    
    db.posts = [
        {
            "id": int,
            "handle": str,
            "feed": str,
            "message": str,
            "timestamp": datetime,
        }
    ]
    
    db.dms = {
        "handle_name_lower": [
            {
                "id": int,
                "from_handle": str,
                "message": str,
                "timestamp": datetime,
                "read": bool,
            }
        ]
    }
    
    db.next_post_id = int
    db.next_dm_id = int
    """
    
    def at_script_creation(self):
        """Initialize the manager data structures."""
        self.key = "safetynet_manager"
        self.desc = "Global SafetyNet data manager"
        self.persistent = True
        
        # Initialize data structures
        self.db.handles = {}
        self.db.posts = []
        self.db.dms = {}
        self.db.next_post_id = 1
        self.db.next_dm_id = 1
        
        # Create System account
        self._create_system_account()
    
    def _create_system_account(self):
        """Create the System account if it does not exist."""
        system_key = SYSTEM_HANDLE.lower()
        if system_key not in self.db.handles:
            self.db.handles[system_key] = {
                "display_name": SYSTEM_HANDLE,
                "owner_id": None,  # System has no owner
                "password": None,  # System cannot be logged into
                "ice_rating": MAX_ICE_RATING,  # Maximum security
                "created": datetime.now(timezone.utc),
                "session_char_id": None,
            }
    
    # =========================================================================
    # HANDLE MANAGEMENT
    # =========================================================================
    
    def create_handle(self, character, handle_name):
        """
        Create a new SafetyNet handle.
        
        Args:
            character: The character creating the handle
            handle_name: Desired handle name
            
        Returns:
            tuple: (success, message, password)
        """
        handle_key = handle_name.lower()
        
        # Check if handle already exists
        if handle_key in self.db.handles:
            return (False, "Handle already taken.", None)
        
        # Validate handle name
        if len(handle_name) < 2 or len(handle_name) > 20:
            return (False, "Handle must be 2-20 characters.", None)
        
        if not handle_name.replace("_", "").replace("-", "").isalnum():
            return (False, "Handle can only contain letters, numbers, underscores, and hyphens.", None)
        
        # Reserved names
        reserved = ["system", "admin", "safetynet", "anonymous", "null", "void"]
        if handle_key in reserved:
            return (False, "That handle is reserved.", None)
        
        # Generate initial password
        password = generate_password()
        
        # Create the handle
        self.db.handles[handle_key] = {
            "display_name": handle_name,
            "owner_id": character.id,
            "password": password,
            "ice_rating": DEFAULT_ICE_RATING,
            "created": datetime.now(timezone.utc),
            "session_char_id": None,
        }
        
        # Initialize DM inbox
        self.db.dms[handle_key] = []
        
        return (True, f"Handle '{handle_name}' created.", password)
    
    def get_handle(self, handle_name):
        """
        Get handle data by name.
        
        Args:
            handle_name: The handle to look up
            
        Returns:
            dict or None
        """
        return self.db.handles.get(handle_name.lower())
    
    def get_character_handles(self, character):
        """
        Get all handles owned by a character.
        
        Args:
            character: The character to look up
            
        Returns:
            list of handle dicts with their names
        """
        handles = []
        for handle_key, data in self.db.handles.items():
            if data.get("owner_id") == character.id:
                handles.append({"name": data["display_name"], "data": data})
        return handles
    
    def delete_handle(self, character, handle_name, password):
        """
        Delete a handle (requires ownership and password).
        
        Args:
            character: The character attempting deletion
            handle_name: The handle to delete
            password: Password for verification
            
        Returns:
            tuple: (success, message)
        """
        handle_key = handle_name.lower()
        handle_data = self.db.handles.get(handle_key)
        
        if not handle_data:
            return (False, "Handle not found.")
        
        if handle_data.get("owner_id") != character.id:
            return (False, "You do not own that handle.")
        
        if handle_data.get("password") != password:
            return (False, "Invalid password.")
        
        # Delete handle and associated DMs
        del self.db.handles[handle_key]
        if handle_key in self.db.dms:
            del self.db.dms[handle_key]
        
        return (True, f"Handle '{handle_name}' deleted.")
    
    # =========================================================================
    # LOGIN/SESSION MANAGEMENT
    # =========================================================================
    
    def login(self, character, handle_name, password):
        """
        Log a character into a SafetyNet handle.
        
        Args:
            character: The character logging in
            handle_name: The handle to log into
            password: The password to verify
            
        Returns:
            tuple: (success, message)
        """
        handle_key = handle_name.lower()
        handle_data = self.db.handles.get(handle_key)
        
        if not handle_data:
            return (False, "Invalid handle or password.")
        
        if handle_data.get("password") != password:
            return (False, "Invalid handle or password.")
        
        # Check if character is already logged into another handle
        current = self.get_logged_in_handle(character)
        if current:
            return (False, f"Already logged in as {current['display_name']}. Use sn/logout first.")
        
        # Log in
        handle_data["session_char_id"] = character.id
        
        # Store current login on character for quick lookup
        character.db.safetynet_handle = handle_data["display_name"]
        
        return (True, f"Logged in as {handle_data['display_name']}.")
    
    def logout(self, character):
        """
        Log a character out of their current SafetyNet session.
        
        Args:
            character: The character logging out
            
        Returns:
            tuple: (success, message)
        """
        current = self.get_logged_in_handle(character)
        if not current:
            return (False, "Not logged in.")
        
        # Find and clear the session
        for handle_key, data in self.db.handles.items():
            if data.get("session_char_id") == character.id:
                data["session_char_id"] = None
                break
        
        # Clear character's stored handle
        if hasattr(character.db, "safetynet_handle"):
            del character.db.safetynet_handle
        
        return (True, "Logged out.")
    
    def get_logged_in_handle(self, character):
        """
        Get the handle a character is currently logged into.
        
        Args:
            character: The character to check
            
        Returns:
            dict or None: Handle data if logged in
        """
        for handle_key, data in self.db.handles.items():
            if data.get("session_char_id") == character.id:
                return data
        return None
    
    def is_handle_online(self, handle_name):
        """
        Check if a handle has an active session.
        
        Args:
            handle_name: The handle to check
            
        Returns:
            bool
        """
        handle_data = self.db.handles.get(handle_name.lower())
        if not handle_data:
            return False
        return handle_data.get("session_char_id") is not None
    
    # =========================================================================
    # PASSWORD MANAGEMENT
    # =========================================================================
    
    def change_password(self, character, handle_name, old_password):
        """
        Change the password for a handle.
        
        Args:
            character: The character changing the password
            handle_name: The handle to change
            old_password: Current password for verification
            
        Returns:
            tuple: (success, message, new_password)
        """
        handle_key = handle_name.lower()
        handle_data = self.db.handles.get(handle_key)
        
        if not handle_data:
            return (False, "Handle not found.", None)
        
        if handle_data.get("owner_id") != character.id:
            return (False, "You do not own that handle.", None)
        
        if handle_data.get("password") != old_password:
            return (False, "Invalid password.", None)
        
        # Generate and set new password
        new_password = generate_password()
        handle_data["password"] = new_password
        
        return (True, "Password changed.", new_password)
    
    def add_password(self, character, handle_name, label=None):
        """
        Cannot add additional passwords - each handle has one password only.
        
        Args:
            character: The character attempting to add a password
            handle_name: The handle
            label: Unused (for compatibility)
            
        Returns:
            tuple: (success, message, new_password)
        """
        return (False, "Each SafetyNet handle can have only one password. Use 'sn/passchange' to rotate your password instead.", None)
    
    # =========================================================================
    # POST MANAGEMENT
    # =========================================================================
    
    def create_post(self, handle_name, feed, message):
        """
        Create a new post.
        
        Args:
            handle_name: The handle posting
            feed: The feed to post to
            message: The post content
            
        Returns:
            tuple: (success, message)
        """
        if feed not in AVAILABLE_FEEDS:
            return (False, f"Invalid feed. Available: {', '.join(AVAILABLE_FEEDS)}")
        
        if len(message) > 500:
            return (False, "Post too long. Maximum 500 characters.")
        
        if len(message) < 1:
            return (False, "Post cannot be empty.")
        
        post = {
            "id": self.db.next_post_id,
            "handle": handle_name,
            "feed": feed,
            "message": message,
            "timestamp": datetime.now(timezone.utc),
        }
        
        self.db.posts.append(post)
        self.db.next_post_id += 1
        
        # Notify SafetyNet channel and active terminals
        self._broadcast_post_notification(handle_name, feed, message)
        
        return (True, f"Posted to {feed}.")
    
    def get_posts(self, feed=None, limit=10, offset=0):
        """
        Get recent posts, optionally filtered by feed.
        
        Args:
            feed: Optional feed to filter by
            limit: Maximum posts to return
            offset: Number of posts to skip
            
        Returns:
            list of post dicts
        """
        # Clean up expired posts first
        self._cleanup_expired_posts()
        
        posts = self.db.posts
        
        if feed:
            posts = [p for p in posts if p.get("feed") == feed]
        
        # Sort by timestamp descending (newest first)
        posts = sorted(posts, key=lambda p: p.get("timestamp", datetime.min), reverse=True)
        
        return posts[offset:offset + limit]
    
    def get_posts_by_handle(self, handle_name, limit=10):
        """
        Get posts by a specific handle.
        
        Args:
            handle_name: The handle to filter by
            limit: Maximum posts to return
            
        Returns:
            list of post dicts
        """
        self._cleanup_expired_posts()
        
        posts = [p for p in self.db.posts if p.get("handle", "").lower() == handle_name.lower()]
        posts = sorted(posts, key=lambda p: p.get("timestamp", datetime.min), reverse=True)
        
        return posts[:limit]
    
    def _cleanup_expired_posts(self):
        """Remove posts older than POST_DECAY_SECONDS."""
        now = datetime.now(timezone.utc)
        cutoff = now.timestamp() - POST_DECAY_SECONDS
        
        valid_posts = []
        for post in self.db.posts:
            ts = post.get("timestamp")
            if ts:
                if ts.tzinfo is None:
                    ts = ts.replace(tzinfo=timezone.utc)
                if ts.timestamp() > cutoff:
                    valid_posts.append(post)
        
        self.db.posts = valid_posts
    
    # =========================================================================
    # DM MANAGEMENT
    # =========================================================================
    
    def send_dm(self, from_handle, to_handle, message):
        """
        Send a direct message.
        
        Args:
            from_handle: Sender handle name
            to_handle: Recipient handle name
            message: The message content
            
        Returns:
            tuple: (success, message)
        """
        to_key = to_handle.lower()
        
        if to_key not in self.db.handles:
            return (False, "Recipient handle not found.")
        
        if len(message) > 1000:
            return (False, "Message too long. Maximum 1000 characters.")
        
        if to_key not in self.db.dms:
            self.db.dms[to_key] = []
        
        dm = {
            "id": self.db.next_dm_id,
            "from_handle": from_handle,
            "message": message,
            "timestamp": datetime.now(timezone.utc),
            "read": False,
        }
        
        self.db.dms[to_key].append(dm)
        self.db.next_dm_id += 1
        
        # Check if recipient is online and notify them
        recipient_data = self.db.handles.get(to_key)
        if recipient_data and recipient_data.get("session_char_id"):
            self._notify_dm_recipient(recipient_data["session_char_id"], from_handle, message)
        
        # Notify SafetyNet channel and active terminals
        self._broadcast_dm_notification(from_handle, to_handle, message)
        
        return (True, f"Message sent to {to_handle}.")
    
    def _notify_dm_recipient(self, char_id, from_handle, message):
        """Send real-time DM notification to online recipient."""
        from evennia.objects.models import ObjectDB
        try:
            char = ObjectDB.objects.get(id=char_id)
            if char:
                # Truncate long messages for notification
                preview = message[:100] + "..." if len(message) > 100 else message
                char.msg(f"|c[SafetyNet DM from {from_handle}]|n {preview}")
        except:
            pass
    
    def _broadcast_post_notification(self, handle_name, feed, message):
        """Broadcast post notification to SafetyNet channel and active terminals."""
        from evennia.comms.models import ChannelDB
        from evennia.objects.models import ObjectDB
        
        try:
            # Send to SafetyNet admin channel
            channel = ChannelDB.objects.get_channel("SafetyNet")
            if channel:
                preview = message[:50] + "..." if len(message) > 50 else message
                channel.msg(f"|c[NEW POST]|n {handle_name} posted to {feed}: {preview}")
        except:
            pass
        
        # Notify all active characters with wristpads
        try:
            for handle_key, handle_data in self.db.handles.items():
                if handle_data.get("session_char_id"):
                    char = ObjectDB.objects.get(id=handle_data["session_char_id"])
                    if char:
                        preview = message[:50] + "..." if len(message) > 50 else message
                        char.msg(f"|y[SafetyNet Post]|n {handle_name}: {preview}")
        except:
            pass
    
    def _broadcast_dm_notification(self, from_handle, to_handle, message):
        """Broadcast DM notification to SafetyNet channel."""
        from evennia.comms.models import ChannelDB
        
        try:
            # Send to SafetyNet admin channel
            channel = ChannelDB.objects.get_channel("SafetyNet")
            if channel:
                preview = message[:50] + "..." if len(message) > 50 else message
                channel.msg(f"|c[NEW DM]|n {from_handle} -> {to_handle}: {preview}")
        except:
            pass
    
    def get_dms(self, handle_name, limit=10, offset=0, unread_only=False):
        """
        Get DMs for a handle.
        
        Args:
            handle_name: The handle to get DMs for
            limit: Maximum DMs to return
            offset: Number to skip
            unread_only: Only return unread DMs
            
        Returns:
            list of DM dicts
        """
        handle_key = handle_name.lower()
        dms = self.db.dms.get(handle_key, [])
        
        if unread_only:
            dms = [d for d in dms if not d.get("read", False)]
        
        # Sort by timestamp descending
        dms = sorted(dms, key=lambda d: d.get("timestamp", datetime.min), reverse=True)
        
        return dms[offset:offset + limit]
    
    def mark_dm_read(self, handle_name, dm_id):
        """Mark a DM as read."""
        handle_key = handle_name.lower()
        dms = self.db.dms.get(handle_key, [])
        
        for dm in dms:
            if dm.get("id") == dm_id:
                dm["read"] = True
                return True
        return False
    
    def get_dm_thread(self, handle_name, other_handle, limit=20):
        """
        Get DM thread between two handles.
        
        Args:
            handle_name: The requesting handle
            other_handle: The other party
            limit: Maximum messages
            
        Returns:
            list of DM dicts from both directions
        """
        handle_key = handle_name.lower()
        other_key = other_handle.lower()
        
        # Get DMs received from other
        received = [d for d in self.db.dms.get(handle_key, []) 
                    if d.get("from_handle", "").lower() == other_key]
        
        # Get DMs sent to other
        sent = [d for d in self.db.dms.get(other_key, [])
                if d.get("from_handle", "").lower() == handle_key]
        
        # Combine and sort
        all_dms = received + sent
        all_dms = sorted(all_dms, key=lambda d: d.get("timestamp", datetime.min), reverse=True)
        
        return all_dms[:limit]
    
    # =========================================================================
    # ICE MANAGEMENT
    # =========================================================================
    
    def get_ice_rating(self, handle_name):
        """Get ICE rating for a handle."""
        handle_data = self.db.handles.get(handle_name.lower())
        if not handle_data:
            return None
        return handle_data.get("ice_rating", DEFAULT_ICE_RATING)
    
    def set_ice_rating(self, character, handle_name, new_rating):
        """
        Set ICE rating for a handle (owner only).
        
        Args:
            character: The character setting the rating
            handle_name: The handle to modify
            new_rating: New ICE rating (1-10)
            
        Returns:
            tuple: (success, message)
        """
        handle_key = handle_name.lower()
        handle_data = self.db.handles.get(handle_key)
        
        if not handle_data:
            return (False, "Handle not found.")
        
        if handle_data.get("owner_id") != character.id:
            return (False, "You do not own that handle.")
        
        new_rating = max(1, min(MAX_ICE_RATING, int(new_rating)))
        handle_data["ice_rating"] = new_rating
        
        return (True, f"ICE rating set to {new_rating}.")
    
    def get_ice_scan(self, handle_name):
        """
        Get a summary of a handle's ICE profile for scanning.
        
        Args:
            handle_name: The handle to scan
            
        Returns:
            str or None: ICE profile summary
        """
        handle_data = self.db.handles.get(handle_name.lower())
        if not handle_data:
            return None
        
        ice = handle_data.get("ice_rating", DEFAULT_ICE_RATING)
        online = handle_data.get("session_char_id") is not None
        
        # Descriptive ICE levels
        if ice <= 2:
            level_desc = "|gMinimal|n"
        elif ice <= 4:
            level_desc = "|yBasic|n"
        elif ice <= 6:
            level_desc = "|yStandard|n"
        elif ice <= 8:
            level_desc = "|rHardened|n"
        else:
            level_desc = "|R[BLACK ICE]|n"
        
        status = "|g[ONLINE]|n" if online else "|r[OFFLINE]|n"
        
        return f"ICE Profile: {level_desc} (Rating: {ice}/10) - Status: {status}"
    
    # =========================================================================
    # HACKING
    # =========================================================================
    
    def attempt_hack(self, attacker, target_handle_name):
        """
        Attempt to hack a SafetyNet handle.
        
        Args:
            attacker: The character attempting the hack
            target_handle_name: The handle to hack
            
        Returns:
            dict with hack results
        """
        from world.safetynet.utils import resolve_hack
        from world.safetynet.constants import (
            HACK_DM_ACCESS_BASE,
            HACK_DM_ACCESS_PER_MARGIN,
            MSG_HACK_ALERT,
        )
        
        target_key = target_handle_name.lower()
        target_data = self.db.handles.get(target_key)
        
        if not target_data:
            return {"success": False, "message": "Handle not found."}
        
        # Cannot hack System
        if target_key == SYSTEM_HANDLE.lower():
            return {"success": False, "message": "Cannot hack System account."}
        
        online = target_data.get("session_char_id") is not None
        ice = target_data.get("ice_rating", DEFAULT_ICE_RATING)
        
        success, margin, message = resolve_hack(attacker, target_data, online, ice)
        
        result = {
            "success": success,
            "margin": margin,
            "message": message,
            "online": online,
        }
        
        if success:
            # Grant access to DMs based on margin
            dm_count = HACK_DM_ACCESS_BASE + (max(0, margin) * HACK_DM_ACCESS_PER_MARGIN)
            result["dms"] = self.get_dms(target_handle_name, limit=dm_count)
            
            # If online, trace location
            if online:
                char_id = target_data.get("session_char_id")
                result["trace"] = self._trace_location(char_id)
        else:
            # Alert the target
            self.send_dm(SYSTEM_HANDLE, target_data["display_name"], MSG_HACK_ALERT)
        
        return result
    
    def _trace_location(self, char_id):
        """
        Trace a character's location by their ID.
        
        Args:
            char_id: Character database ID
            
        Returns:
            str: Location description or None
        """
        from evennia.objects.models import ObjectDB
        try:
            char = ObjectDB.objects.get(id=char_id)
            if char and char.location:
                room = char.location
                coords = ""
                x = getattr(room.db, "x_coord", None)
                y = getattr(room.db, "y_coord", None)
                z = getattr(room.db, "z_coord", None)
                if x is not None and y is not None and z is not None:
                    coords = f" ({x}, {y}, {z})"
                return f"{room.key}{coords}"
        except:
            pass
        return None
    
    # =========================================================================
    # SEARCH
    # =========================================================================
    
    def search_posts(self, query, limit=20):
        """
        Search posts for a query string.
        
        Args:
            query: Search string
            limit: Maximum results
            
        Returns:
            list of matching posts
        """
        self._cleanup_expired_posts()
        query_lower = query.lower()
        
        matches = []
        for post in self.db.posts:
            if query_lower in post.get("message", "").lower():
                matches.append(post)
            elif query_lower in post.get("handle", "").lower():
                matches.append(post)
        
        # Sort by timestamp descending
        matches = sorted(matches, key=lambda p: p.get("timestamp", datetime.min), reverse=True)
        
        return matches[:limit]
    
    def search_handles(self, query, limit=10):
        """
        Search for handles matching a query.
        
        Args:
            query: Search string
            limit: Maximum results
            
        Returns:
            list of handle names
        """
        query_lower = query.lower()
        matches = []
        
        for handle_key, data in self.db.handles.items():
            if query_lower in handle_key or query_lower in data.get("display_name", "").lower():
                matches.append(data.get("display_name", handle_key))
        
        return matches[:limit]
