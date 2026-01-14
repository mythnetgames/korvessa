"""
SafetyNet Commands

All commands for the SafetyNet intranet social system.
All commands use the "sn" prefix with switches.
"""

from evennia import Command, CmdSet
from evennia.utils import delay
from world.safetynet.core import get_safetynet_manager
from world.safetynet.utils import (
    check_access_device,
    get_connection_delay,
    delayed_output,
    format_timestamp,
    get_online_indicator,
)
from world.safetynet.constants import (
    MSG_NO_DEVICE,
    MSG_CONNECTING,
    MSG_NOT_LOGGED_IN,
    MSG_ALREADY_LOGGED_IN,
    MSG_LOGIN_SUCCESS,
    MSG_LOGIN_FAILED,
    MSG_LOGOUT_SUCCESS,
    MSG_POST_SUCCESS,
    MSG_DM_SENT,
    MSG_HANDLE_NOT_FOUND,
    MSG_HACK_SUCCESS,
    MSG_HACK_FAILED,
    MSG_PASSWORD_CHANGED,
    MSG_PASSWORD_ADDED,
    MSG_PASSWORD_REMINDER,
    POSTS_PER_PAGE,
    DMS_PER_PAGE,
    AVAILABLE_FEEDS,
    DEFAULT_FEED,
    SYSTEM_HANDLE,
)


class CmdSafetyNet(Command):
    """
    Access the SafetyNet intranet social system.
    
    Usage:
        sn                          - Show status and help
        sn read                     - Read recent posts
        sn post <message>           - Post to SafetyNet
        sn login <handle> <pass>    - Log into a handle
        sn logout                   - Log out of current handle
        sn dm <handle>=<message>    - Send a direct message
        sn inbox                    - View your DM inbox
        sn thread <handle>          - View DM thread with handle
        sn thread <handle> delete   - Delete a DM thread (needs confirmation)
        sn search <query>           - Search posts
        sn register <handle>        - Create a new handle
        sn delete <handle>=<pass>   - Delete a handle
        sn passchange <handle>=<old>- Change password (generates new)
        sn ice <handle>             - Scan a handle's ICE profile
        sn hack <handle>            - Attempt to hack a handle
        sn upgrade <handle>=<level> - Upgrade your ICE (1-100)
        sn raise <handle>=<amount>  - Decker: Raise ICE by amount (1-20)
        sn whois <handle>           - Look up handle info
    
    Requires a Wristpad or Computer to access.
    """
    
    key = "sn"
    aliases = ["safetynet"]
    locks = "cmd:all()"
    help_category = "Communication"
    
    def func(self):
        caller = self.caller
        
        # Check for access device
        device_type, device = check_access_device(caller)
        if not device_type:
            caller.msg(MSG_NO_DEVICE)
            return
        
        # Parse args - first word is subcommand, rest is arguments
        args = self.args.strip() if self.args else ""
        
        if not args:
            # No subcommand, show status
            self.do_status(device_type)
            return
        
        # Split into subcommand and remaining args
        parts = args.split(None, 1)
        primary_cmd = parts[0].lower()
        subargs = parts[1] if len(parts) > 1 else ""
        
        # Route to appropriate handler
        if primary_cmd == "read":
            if subargs == "next":
                self.do_read_next(device_type)
            else:
                self.do_read(device_type, subargs)
        elif primary_cmd == "post":
            self.do_post(device_type, subargs)
        elif primary_cmd == "login":
            self.do_login(device_type, subargs)
        elif primary_cmd == "logout":
            self.do_logout(device_type)
        elif primary_cmd == "dm":
            self.do_dm(device_type, subargs)
        elif primary_cmd == "inbox":
            if subargs == "next":
                self.do_inbox_next(device_type)
            else:
                self.do_inbox(device_type)
        elif primary_cmd == "thread":
            self.do_thread(device_type, subargs)
        elif primary_cmd == "search":
            self.do_search(device_type, subargs)
        elif primary_cmd == "register":
            self.do_register(device_type, subargs)
        elif primary_cmd == "delete":
            self.do_delete(device_type, subargs)
        elif primary_cmd == "passchange":
            self.do_passchange(device_type, subargs)
        elif primary_cmd == "passadd":
            self.do_passadd(device_type, subargs)
        elif primary_cmd == "ice":
            self.do_ice(device_type, subargs)
        elif primary_cmd == "hack":
            self.do_hack(device_type, subargs)
        elif primary_cmd == "upgrade":
            self.do_upgrade(device_type, subargs)
        elif primary_cmd == "raise":
            self.do_raise_ice(device_type, subargs)
        elif primary_cmd == "whois":
            self.do_whois(device_type, subargs)
        else:
            caller.msg(f"|rUnknown SafetyNet command: {primary_cmd}|n Use |wsn|n for help.")
    
    def do_status(self, device_type):
        """Show SafetyNet status and help."""
        caller = self.caller
        manager = get_safetynet_manager()
        
        output = []
        output.append("|w============= SafetyNet =============|n")
        output.append("|yMunicipal Safety & Communication Network|n")
        output.append("")
        
        # Device info
        device_name = "Wristpad" if device_type == "wristpad" else "Computer Terminal"
        output.append(f"|wDevice:|n {device_name}")
        
        # Login status
        handle_data = manager.get_logged_in_handle(caller)
        if handle_data:
            output.append(f"|wLogged in as:|n |c{handle_data['display_name']}|n |g[ACTIVE]|n")
        else:
            output.append("|wLogged in as:|n |r[NOT LOGGED IN]|n")
        
        # Quick stats
        handles = manager.get_character_handles(caller)
        output.append(f"|wYour handles:|n {len(handles)}")
        
        output.append("")
        output.append("|wCommands:|n")
        output.append("  |wsn read|n               - Read posts")
        output.append("  |wsn post|n <msg>         - Post message")
        output.append("  |wsn login|n <h> <pass>   - Log in")
        output.append("  |wsn logout|n             - Log out")
        output.append("  |wsn dm|n <h>=<msg>       - Send DM")
        output.append("  |wsn inbox|n              - View DMs")
        output.append("  |wsn register|n <handle>  - Create handle")
        output.append("  |wsn ice|n <handle>       - Scan ICE profile")
        output.append("  |wsn hack|n <handle>      - Attempt hack")
        output.append("")
        output.append(f"|wFeeds:|n {', '.join(AVAILABLE_FEEDS)}")
        output.append("|w=====================================|n")
        
        delay_time = get_connection_delay(device_type, "read")
        delayed_output(caller, "\n".join(output), delay_time)
    
    def do_read(self, device_type, args):
        """Read posts from SafetyNet."""
        caller = self.caller
        manager = get_safetynet_manager()
        
        feed = DEFAULT_FEED
        
        # Store pagination state
        caller.ndb.sn_feed = feed
        caller.ndb.sn_offset = 0
        
        posts = manager.get_posts(feed=feed, limit=POSTS_PER_PAGE, offset=0)
        
        output = self._format_posts(posts, feed, manager)
        
        delay_time = get_connection_delay(device_type, "read")
        delayed_output(caller, output, delay_time)
    
    def do_read_next(self, device_type):
        """Show next page of posts."""
        caller = self.caller
        manager = get_safetynet_manager()
        
        feed = getattr(caller.ndb, "sn_feed", DEFAULT_FEED)
        offset = getattr(caller.ndb, "sn_offset", 0) + POSTS_PER_PAGE
        caller.ndb.sn_offset = offset
        
        posts = manager.get_posts(feed=feed, limit=POSTS_PER_PAGE, offset=offset)
        
        if not posts:
            caller.msg("|yNo more posts.|n")
            return
        
        output = self._format_posts(posts, feed, manager)
        
        delay_time = get_connection_delay(device_type, "read")
        delayed_output(caller, output, delay_time)
    
    def _format_posts(self, posts, feed, manager):
        """Format posts for display."""
        lines = []
        lines.append(f"|w===== SafetyNet Feed =====|n")
        
        if not posts:
            lines.append("|yNo posts.|n")
        else:
            for post in posts:
                handle = post.get("handle", "Unknown")
                message = post.get("message", "")
                timestamp = post.get("timestamp")
                
                indicator = get_online_indicator(handle, manager)
                time_str = format_timestamp(timestamp) if timestamp else "?"
                
                lines.append(f"|c{handle}|n {indicator} |#ffff87({time_str})|n")
                lines.append(f"  {message}")
                lines.append("")
        
        lines.append("|wUse 'sn read next' for more posts.|n")
        lines.append("|w===========================|n")
        
        return "\n".join(lines)
    
    def do_post(self, device_type, args):
        """Post to SafetyNet."""
        caller = self.caller
        manager = get_safetynet_manager()
        
        # Check login
        handle_data = manager.get_logged_in_handle(caller)
        if not handle_data:
            caller.msg(MSG_NOT_LOGGED_IN)
            return
        
        message = args.strip()
        
        if not message:
            caller.msg("|rUsage: sn post <message>|n")
            return
        
        def do_post_delayed():
            success, result_msg = manager.create_post(
                handle_data["display_name"],
                DEFAULT_FEED,
                message
            )
            if success:
                caller.msg("|gSafetyNet: Post submitted.|n")
            else:
                caller.msg(f"|r{result_msg}|n")
        
        delay_time = get_connection_delay(device_type, "post")
        if delay_time > 0.5:
            caller.msg(MSG_CONNECTING)
        delay(delay_time, do_post_delayed)
    
    def do_login(self, device_type, args):
        """Log into a SafetyNet handle."""
        caller = self.caller
        manager = get_safetynet_manager()
        
        parts = args.split(None, 1)
        if len(parts) < 2:
            caller.msg("|rUsage: sn login <handle> <password>|n")
            caller.msg("|yNote: Password is two words, e.g., 'chrome runner'|n")
            return
        
        handle = parts[0]
        password = parts[1]
        
        def do_login_delayed():
            success, message = manager.login(caller, handle, password)
            if success:
                caller.msg(MSG_LOGIN_SUCCESS.format(handle=handle))
            else:
                caller.msg(MSG_LOGIN_FAILED)
        
        delay_time = get_connection_delay(device_type, "login")
        if delay_time > 0.5:
            caller.msg(MSG_CONNECTING)
        delay(delay_time, do_login_delayed)
    
    def do_logout(self, device_type):
        """Log out of current SafetyNet session."""
        caller = self.caller
        manager = get_safetynet_manager()
        
        success, message = manager.logout(caller)
        if success:
            caller.msg(MSG_LOGOUT_SUCCESS)
        else:
            caller.msg(f"|r{message}|n")
    
    def do_dm(self, device_type, args):
        """Send a direct message."""
        caller = self.caller
        manager = get_safetynet_manager()
        
        # Check login
        handle_data = manager.get_logged_in_handle(caller)
        if not handle_data:
            caller.msg(MSG_NOT_LOGGED_IN)
            return
        
        if "=" not in args:
            caller.msg("|rUsage: sn dm <handle>=<message>|n")
            return
        
        to_handle, message = args.split("=", 1)
        to_handle = to_handle.strip()
        message = message.strip()
        
        if not message:
            caller.msg("|rMessage cannot be empty.|n")
            return
        
        def do_dm_delayed():
            success, result_msg = manager.send_dm(
                handle_data["display_name"],
                to_handle,
                message
            )
            if success:
                caller.msg(MSG_DM_SENT.format(handle=to_handle))
            else:
                caller.msg(f"|r{result_msg}|n")
        
        delay_time = get_connection_delay(device_type, "dm")
        if delay_time > 0.5:
            caller.msg(MSG_CONNECTING)
        delay(delay_time, do_dm_delayed)
    
    def do_inbox(self, device_type):
        """View DM inbox."""
        caller = self.caller
        manager = get_safetynet_manager()
        
        # Check login
        handle_data = manager.get_logged_in_handle(caller)
        if not handle_data:
            caller.msg(MSG_NOT_LOGGED_IN)
            return
        
        caller.ndb.sn_inbox_offset = 0
        handle_name = handle_data["display_name"]
        
        dms = manager.get_dms(handle_name, limit=DMS_PER_PAGE, offset=0)
        
        output = self._format_inbox(dms, handle_name, manager)
        
        delay_time = get_connection_delay(device_type, "read")
        delayed_output(caller, output, delay_time)
    
    def do_inbox_next(self, device_type):
        """Show next page of inbox."""
        caller = self.caller
        manager = get_safetynet_manager()
        
        handle_data = manager.get_logged_in_handle(caller)
        if not handle_data:
            caller.msg(MSG_NOT_LOGGED_IN)
            return
        
        offset = getattr(caller.ndb, "sn_inbox_offset", 0) + DMS_PER_PAGE
        caller.ndb.sn_inbox_offset = offset
        handle_name = handle_data["display_name"]
        
        dms = manager.get_dms(handle_name, limit=DMS_PER_PAGE, offset=offset)
        
        if not dms:
            caller.msg("|yNo more messages.|n")
            return
        
        output = self._format_inbox(dms, handle_name, manager)
        
        delay_time = get_connection_delay(device_type, "read")
        delayed_output(caller, output, delay_time)
    
    def _format_inbox(self, dms, handle_name, manager):
        """Format inbox for display."""
        lines = []
        lines.append(f"|w===== SafetyNet: Inbox ({handle_name}) =====|n")
        
        if not dms:
            lines.append("|yNo messages.|n")
        else:
            for dm in dms:
                from_handle = dm.get("from_handle", "Unknown")
                message = dm.get("message", "")
                timestamp = dm.get("timestamp")
                read = dm.get("read", False)
                dm_id = dm.get("id")
                
                indicator = get_online_indicator(from_handle, manager)
                time_str = format_timestamp(timestamp) if timestamp else "?"
                read_marker = "" if read else "|Y[NEW]|n "
                
                # Mark as read
                manager.mark_dm_read(handle_name, dm_id)
                
                lines.append(f"{read_marker}|cFrom: {from_handle}|n {indicator} |#ffff87({time_str})|n")
                # Truncate long messages
                preview = message[:150] + "..." if len(message) > 150 else message
                lines.append(f"  {preview}")
                lines.append("")
        
        lines.append("|wUse 'sn inbox next' for more. 'sn thread <handle>' for conversation.|n")
        lines.append("|w==========================================|n")
        
        return "\n".join(lines)
    
    def do_thread(self, device_type, args):
        """View DM thread with a handle or delete it."""
        caller = self.caller
        manager = get_safetynet_manager()
        
        handle_data = manager.get_logged_in_handle(caller)
        if not handle_data:
            caller.msg(MSG_NOT_LOGGED_IN)
            return
        
        if not args:
            caller.msg("|rUsage: sn thread <handle> [delete]|n")
            return
        
        # Parse args for optional 'delete' command
        parts = args.strip().split()
        other_handle = parts[0]
        delete_flag = len(parts) > 1 and parts[1].lower() == "delete"
        
        my_handle = handle_data["display_name"]
        
        if delete_flag:
            # Confirm deletion
            if len(parts) < 3 or parts[2] != "!":
                caller.msg(f"|rThis will DELETE the entire conversation with {other_handle}.|n")
                caller.msg(f"|rRe-run with an exclamation mark to confirm: sn thread {other_handle} delete !|n")
                return
            
            success, msg = manager.delete_dm_thread(my_handle, other_handle)
            if success:
                caller.msg(f"|g{msg}|n")
            else:
                caller.msg(f"|r{msg}|n")
            return
        
        dms = manager.get_dm_thread(my_handle, other_handle, limit=20)
        
        lines = []
        lines.append(f"|w===== Thread: {my_handle} <-> {other_handle} =====|n")
        
        if not dms:
            lines.append("|yNo messages in this thread.|n")
        else:
            # Reverse to show oldest first
            for dm in reversed(dms):
                from_handle = dm.get("from_handle", "Unknown")
                message = dm.get("message", "")
                timestamp = dm.get("timestamp")
                
                time_str = format_timestamp(timestamp) if timestamp else "?"
                
                lines.append(f"|c{from_handle}|n |#ffff87({time_str})|n")
                lines.append(f"  {message}")
                lines.append("")
        
        lines.append("|wUse 'sn thread <handle> delete' to delete this conversation.|n")
        lines.append("|w==========================================|n")
        
        delay_time = get_connection_delay(device_type, "read")
        delayed_output(caller, "\n".join(lines), delay_time)
    
    def do_search(self, device_type, args):
        """Search posts."""
        caller = self.caller
        manager = get_safetynet_manager()
        
        if not args:
            caller.msg("|rUsage: sn search <query>|n")
            return
        
        query = args.strip()
        
        def do_search_delayed():
            posts = manager.search_posts(query, limit=20)
            
            lines = []
            lines.append(f"|w===== Search: '{query}' =====|n")
            
            if not posts:
                lines.append("|yNo results found.|n")
            else:
                lines.append(f"|yFound {len(posts)} result(s):|n")
                lines.append("")
                for post in posts[:10]:
                    handle = post.get("handle", "Unknown")
                    feed = post.get("feed", "?")
                    message = post.get("message", "")
                    timestamp = post.get("timestamp")
                    
                    indicator = get_online_indicator(handle, manager)
                    time_str = format_timestamp(timestamp) if timestamp else "?"
                    
                    lines.append(f"|c{handle}|n {indicator} in #{feed} |#ffff87({time_str})|n")
                    preview = message[:100] + "..." if len(message) > 100 else message
                    lines.append(f"  {preview}")
                    lines.append("")
            
            lines.append("|w==============================|n")
            caller.msg("\n".join(lines))
        
        delay_time = get_connection_delay(device_type, "search")
        if delay_time > 0.5:
            caller.msg(MSG_CONNECTING)
        delay(delay_time, do_search_delayed)
    
    def do_register(self, device_type, args):
        """Register a new handle."""
        caller = self.caller
        manager = get_safetynet_manager()
        
        if not args:
            caller.msg("|rUsage: sn register <handle>|n")
            return
        
        handle_name = args.strip()
        
        def do_register_delayed():
            success, message, password = manager.create_handle(caller, handle_name)
            
            if success:
                caller.msg(f"|g{message}|n")
                caller.msg(f"|wYour password:|n {password}")
                caller.msg(MSG_PASSWORD_REMINDER)
            else:
                caller.msg(f"|r{message}|n")
        
        delay_time = get_connection_delay(device_type, "post")
        if delay_time > 0.5:
            caller.msg(MSG_CONNECTING)
        delay(delay_time, do_register_delayed)
    
    def do_delete(self, device_type, args):
        """Delete a handle."""
        caller = self.caller
        manager = get_safetynet_manager()
        
        if "=" not in args:
            caller.msg("|rUsage: sn delete <handle>=<password>|n")
            return
        
        handle, password = args.split("=", 1)
        handle = handle.strip()
        password = password.strip()
        
        success, message = manager.delete_handle(caller, handle, password)
        
        if success:
            caller.msg(f"|g{message}|n")
        else:
            caller.msg(f"|r{message}|n")
    
    def do_passchange(self, device_type, args):
        """Change a handle's password."""
        caller = self.caller
        manager = get_safetynet_manager()
        
        if "=" not in args:
            caller.msg("|rUsage: sn passchange <handle>=<old_password>|n")
            return
        
        handle, old_pass = args.split("=", 1)
        handle = handle.strip()
        old_pass = old_pass.strip()
        
        success, message, new_password = manager.change_password(caller, handle, old_pass)
        
        if success:
            caller.msg(MSG_PASSWORD_CHANGED)
            caller.msg(f"|wYour new password:|n {new_password}")
            caller.msg(MSG_PASSWORD_REMINDER)
        else:
            caller.msg(f"|r{message}|n")
    
    def do_passadd(self, device_type, args):
        """Inform user that each handle can only have one password."""
        caller = self.caller
        caller.msg("|yNote:|n Each SafetyNet handle can only have one password.")
        caller.msg("Use |w'sn passchange <handle> <old_password>'|n to rotate your password instead.")
    
    def do_ice(self, device_type, args):
        """Scan a handle's ICE profile."""
        caller = self.caller
        manager = get_safetynet_manager()
        
        if not args:
            caller.msg("|rUsage: sn ice <handle>|n")
            return
        
        handle = args.strip()
        
        def do_ice_delayed():
            scan = manager.get_ice_scan(handle)
            if scan:
                caller.msg(f"|w===== ICE Scan: {handle} =====|n")
                caller.msg(scan)
                caller.msg("|w=============================|n")
            else:
                caller.msg(MSG_HANDLE_NOT_FOUND)
        
        delay_time = get_connection_delay(device_type, "search")
        if delay_time > 0.5:
            caller.msg(MSG_CONNECTING)
        delay(delay_time, do_ice_delayed)
    
    def do_hack(self, device_type, args):
        """Attempt to hack a handle."""
        caller = self.caller
        manager = get_safetynet_manager()
        
        if not args:
            caller.msg("|rUsage: sn hack <handle>|n")
            return
        
        # Check for cooldown
        import time
        cooldown_until = getattr(caller.ndb, 'hack_cooldown', None)
        if cooldown_until is not None and isinstance(cooldown_until, (int, float)):
            current_time = time.time()
            if current_time < cooldown_until:
                remaining = int(cooldown_until - current_time)
                caller.msg(f"|r[ICE LOCKOUT]|n ICE countermeasures active. Try again in {remaining} seconds.|n")
                return
        
        handle = args.strip()
        
        def do_hack_delayed():
            result = manager.attempt_hack(caller, handle)
            
            # Set cooldown on failure
            if not result.get("success"):
                import time
                cooldown_duration = 30  # 30 second cooldown on failed hacks
                caller.ndb.hack_cooldown = time.time() + cooldown_duration
            
            lines = []
            lines.append("|w===== INTRUSION ATTEMPT =====|n")
            lines.append(f"|yTarget:|n {handle}")
            
            if result.get("success") and result.get("password"):
                lines.append(f"|yPassword:|n {result['password']}")
            
            lines.append(f"|yResult:|n {result['message']}")
            
            if result.get("success"):
                lines.append("")
                lines.append(MSG_HACK_SUCCESS)
                
                # Show trace if available
                if result.get("trace"):
                    lines.append("")
                    lines.append(f"|gTrace successful:|n Signal originates from '{result['trace']}'.")
                elif result.get("online"):
                    lines.append("|yTrace failed:|n Could not pinpoint location.")
                else:
                    lines.append("|yNo trace:|n Target offline.")
                
                # Show DMs if available
                dms = result.get("dms", [])
                if dms:
                    lines.append("")
                    lines.append(f"|w----- Recovered Messages ({len(dms)}) -----|n")
                    for dm in dms[:5]:
                        from_h = dm.get("from_handle", "?")
                        msg = dm.get("message", "")[:80]
                        lines.append(f"  |c{from_h}:|n {msg}")
            else:
                lines.append("")
                lines.append(MSG_HACK_FAILED)
                lines.append(f"|r[ICE TRIGGERED]|n 30 second lockout initiated.|n")
            
            lines.append("|w=============================|n")
            caller.msg("\n".join(lines))
        
        delay_time = get_connection_delay(device_type, "hack")
        caller.msg("|y[SafetyNet] Initiating intrusion sequence...|n")
        delay(delay_time, do_hack_delayed)
    
    def do_upgrade(self, device_type, args):
        """Upgrade ICE rating for a handle."""
        caller = self.caller
        manager = get_safetynet_manager()
        
        if "=" not in args:
            caller.msg("|rUsage: sn upgrade <handle>=<level>|n")
            caller.msg("|yICE levels: 1-100 (higher = more secure)|n")
            return
        
        handle, level = args.split("=", 1)
        handle = handle.strip()
        
        try:
            level = int(level.strip())
        except ValueError:
            caller.msg("|rICE level must be a number 1-100.|n")
            return
        
        success, message = manager.set_ice_rating(caller, handle, level)
        
        if success:
            caller.msg(f"|g{message}|n")
        else:
            caller.msg(f"|r{message}|n")
    
    def do_raise_ice(self, device_type, args):
        """Decker function: Raise ICE by a small amount (1-20 per use) with skill check."""
        import time
        from datetime import date
        
        caller = self.caller
        manager = get_safetynet_manager()
        
        # Check for cooldown from critical failure
        raise_cooldown = getattr(caller.ndb, 'raise_cooldown', None)
        if raise_cooldown is not None and isinstance(raise_cooldown, (int, float)):
            current_time = time.time()
            if current_time < raise_cooldown:
                remaining = int(raise_cooldown - current_time)
                caller.msg(f"|r[SYSTEM LOCKED]|n Systems still recovering. Try again in {remaining} seconds.|n")
                return
        
        # Check spam cooldown (10 second minimum between attempts)
        last_raise = getattr(caller.ndb, 'last_raise_attempt', None)
        if last_raise is not None and isinstance(last_raise, (int, float)):
            current_time = time.time()
            if current_time - last_raise < 10:
                caller.msg(f"|r[SPAM PROTECTION]|n Wait before attempting again.|n")
                return
        
        if "=" not in args:
            caller.msg("|rUsage: sn raise <handle>=<amount>|n")
            caller.msg("|yAmount: 1-20 per action (max 20/day)|n")
            caller.msg("|yRisk: Failure locks you out, critical failure locks you out for 30 seconds|n")
            return
        
        handle, amount_str = args.split("=", 1)
        handle = handle.strip()
        
        try:
            amount = int(amount_str.strip())
        except ValueError:
            caller.msg("|rAmount must be a number 1-20.|n")
            return
        
        # Check daily limit
        today = str(date.today())
        raised_today = getattr(caller.ndb, 'ice_raised_today', 0)
        raised_date = getattr(caller.ndb, 'ice_raised_date', None)
        
        # Reset if it's a new day
        if raised_date != today:
            raised_today = 0
        
        # Check if this attempt would exceed daily limit
        if raised_today + amount > 20:
            remaining_daily = 20 - raised_today
            caller.msg(f"|r[DAILY LIMIT]|n You can only raise {remaining_daily} more ICE points today.|n")
            return
        
        # Record this attempt timestamp
        caller.ndb.last_raise_attempt = time.time()
        
        def do_raise_delayed():
            success, message, new_rating, result_type = manager.raise_ice(caller, handle, amount)
            
            # Set cooldown on critical failure
            if result_type == 'critfail':
                cooldown_duration = 30  # 30 second cooldown on critical failure
                caller.ndb.raise_cooldown = time.time() + cooldown_duration
            elif result_type == 'success':
                # Track daily ICE raised on success
                today = str(date.today())
                raised_today = getattr(caller.ndb, 'ice_raised_today', 0)
                raised_date = getattr(caller.ndb, 'ice_raised_date', None)
                
                # Reset if it's a new day
                if raised_date != today:
                    raised_today = 0
                
                caller.ndb.ice_raised_today = raised_today + amount
                caller.ndb.ice_raised_date = today
            
            if success:
                caller.msg(f"{message}")
                caller.msg(f"|wNew ICE Rating:|n {new_rating}/100")
                if result_type == 'success':
                    total_raised = getattr(caller.ndb, 'ice_raised_today', 0)
                    remaining = 20 - total_raised
                    caller.msg(f"|wDaily limit:|n {total_raised}/20 points used ({remaining} remaining)|n")
            else:
                caller.msg(f"|r{message}|n")
        
        delay_time = get_connection_delay(device_type, "write")
        if delay_time > 0.5:
            caller.msg("|yInitiating ICE enhancement...|n")
        delay(delay_time, do_raise_delayed)
    
    def do_whois(self, device_type, args):
        """Look up handle info."""
        caller = self.caller
        manager = get_safetynet_manager()
        
        if not args:
            caller.msg("|rUsage: sn whois <handle>|n")
            return
        
        handle = args.strip()
        
        def do_whois_delayed():
            handle_data = manager.get_handle(handle)
            
            if not handle_data:
                caller.msg(MSG_HANDLE_NOT_FOUND)
                return
            
            display_name = handle_data.get("display_name", handle)
            created = handle_data.get("created")
            online = handle_data.get("session_char_id") is not None
            
            lines = []
            lines.append(f"|w===== WHOIS: {display_name} =====|n")
            
            if display_name.lower() == SYSTEM_HANDLE.lower():
                lines.append("|wType:|n System Account")
                lines.append("|wStatus:|n Always Active")
            else:
                status = "|g[ONLINE]|n" if online else "|r[OFFLINE]|n"
                lines.append(f"|wStatus:|n {status}")
                
                if created:
                    lines.append(f"|wCreated:|n {format_timestamp(created)}")
                
                # Get recent posts
                posts = manager.get_posts_by_handle(display_name, limit=3)
                if posts:
                    lines.append("|wRecent activity:|n")
                    for post in posts:
                        feed = post.get("feed", "?")
                        time_str = format_timestamp(post.get("timestamp"))
                        lines.append(f"  Post in #{feed} ({time_str})")
            
            lines.append("|w=============================|n")
            caller.msg("\n".join(lines))
        
        delay_time = get_connection_delay(device_type, "search")
        if delay_time > 0.5:
            caller.msg(MSG_CONNECTING)
        delay(delay_time, do_whois_delayed)


class CmdSafetyNetAdmin(Command):
    """
    Admin SafetyNet management commands.
    
    Usage:
        snadmin ice <handle>=<level>    - Set ICE rating (1-100)
        snadmin reset <handle>          - Reset password
        snadmin info <handle>           - Show detailed handle info
        snadmin nuke <handle>           - Delete handle and data
        snadmin stats                   - Show SafetyNet statistics
    
    Builders and higher only.
    """
    
    key = "snadmin"
    aliases = []
    locks = "cmd:perm(Builder)"
    help_category = "Admin"
    
    def func(self):
        caller = self.caller
        args = self.args.strip() if self.args else ""
        
        manager = get_safetynet_manager()
        
        if not args:
            self.show_admin_help()
            return
        
        # Split into subcommand and remaining args
        parts = args.split(None, 1)
        primary_cmd = parts[0].lower()
        subargs = parts[1] if len(parts) > 1 else ""
        
        if primary_cmd == "ice":
            self.do_admin_ice(manager, subargs)
        elif primary_cmd == "reset":
            self.do_admin_reset(manager, subargs)
        elif primary_cmd == "info":
            self.do_admin_info(manager, subargs)
        elif primary_cmd == "nuke":
            self.do_admin_nuke(manager, subargs)
        elif primary_cmd == "stats":
            self.do_admin_stats(manager, subargs)
        else:
            caller.msg(f"|rUnknown admin command: {primary_cmd}|n")
            self.show_admin_help()
    
    def show_admin_help(self):
        """Show admin command help."""
        caller = self.caller
        output = ["|w=== SafetyNet Admin Commands ===|n"]
        output.append("")
        output.append("|wsnadmin ice|n <handle>=<level>")
        output.append("  Set ICE rating for a handle (1-100)")
        output.append("")
        output.append("|wsnadmin reset|n <handle>")
        output.append("  Force password reset for a handle")
        output.append("")
        output.append("|wsnadmin info|n <handle>")
        output.append("  Show detailed information about a handle")
        output.append("")
        output.append("|wsnadmin nuke|n <handle>")
        output.append("  Permanently delete a handle and all data")
        output.append("")
        output.append("|wsnadmin stats|n")
        output.append("  Show SafetyNet system statistics")
        output.append("")
        caller.msg("\n".join(output))
    
    def do_admin_ice(self, manager, args):
        """Set ICE rating for a handle."""
        caller = self.caller
        
        if "=" not in args:
            caller.msg("|rUsage: snadmin ice <handle>=<level>|n")
            return
        
        handle_name, level_str = args.split("=", 1)
        handle_name = handle_name.strip()
        level_str = level_str.strip()
        
        try:
            level = int(level_str)
            if level < 1 or level > 100:
                caller.msg("|rICE level must be between 1 and 100.|n")
                return
        except ValueError:
            caller.msg("|rICE level must be a number.|n")
            return
        
        # Find handle and set ICE
        handle_key = handle_name.lower()
        if handle_key in manager.db.handles:
            manager.db.handles[handle_key]["ice_rating"] = level
            caller.msg(f"|gSet ICE rating for {handle_name} to {level}.|n")
        else:
            caller.msg(f"|rHandle '{handle_name}' not found.|n")
    
    def do_admin_reset(self, manager, args):
        """Force reset a handle's password."""
        caller = self.caller
        
        handle_name = args.strip()
        if not handle_name:
            caller.msg("|rUsage: snadmin reset <handle>|n")
            return
        
        # Find and reset handle
        handle_key = handle_name.lower()
        if handle_key in manager.db.handles:
            new_pass = manager.generate_password()
            manager.db.handles[handle_key]["password"] = new_pass
            caller.msg(f"|gReset password for {handle_name}.|n")
            caller.msg(f"|wNew password:|n {new_pass}")
        else:
            caller.msg(f"|rHandle '{handle_name}' not found.|n")
    
    def do_admin_info(self, manager, args):
        """Show detailed handle information."""
        caller = self.caller
        
        handle_name = args.strip()
        if not handle_name:
            caller.msg("|rUsage: snadmin info <handle>|n")
            return
        
        # Find handle and display info
        handle_key = handle_name.lower()
        if handle_key in manager.db.handles:
            handle_data = manager.db.handles[handle_key]
            lines = [""]
            lines.append(f"|wHandle:|n {handle_data.get('display_name')}")
            if handle_data.get('owner_id'):
                lines.append(f"|wOwner ID:|n {handle_data.get('owner_id')}")
            else:
                lines.append("|wOwner:|n System Account")
            lines.append(f"|wICE Rating:|n {handle_data.get('ice_rating', 0)}/100")
            lines.append(f"|wCreated:|n {format_timestamp(handle_data.get('created', 0))}")
            lines.append(f"|wOnline:|n {'Yes' if handle_data.get('session_char_id') else 'No'}")
            caller.msg("".join(lines))
        else:
            caller.msg(f"|rHandle '{handle_name}' not found.|n")
    
    def do_admin_nuke(self, manager, args):
        """Delete a handle permanently."""
        caller = self.caller
        
        handle_name = args.strip()
        if not handle_name:
            caller.msg("|rUsage: snadmin nuke <handle>|n")
            return
        
        # Confirm deletion
        if not self.args.endswith("!"):
            caller.msg(f"|rThis will PERMANENTLY delete {handle_name} and all its data.|n")
            caller.msg(f"|rRe-run with an exclamation mark to confirm: snadmin nuke {handle_name}!|n")
            return
        
        # Find and delete handle
        handle_key = handle_name.lower()
        if handle_key in manager.db.handles:
            del manager.db.handles[handle_key]
            if handle_key in manager.db.dms:
                del manager.db.dms[handle_key]
            caller.msg(f"|rDeleted handle '{handle_name}' and all associated data.|n")
        else:
            caller.msg(f"|rHandle '{handle_name}' not found.|n")
    
    def do_admin_stats(self, manager, args):
        """Show SafetyNet statistics."""
        caller = self.caller
        
        total_handles = len(manager.db.handles)
        total_posts = len(manager.db.posts)
        total_dms = sum(len(dms) for dms in manager.db.dms.values())
        online_handles = sum(1 for h in manager.db.handles.values() if h.get('session_char_id'))
        
        lines = ["|w=== SafetyNet Statistics ===|n"]
        lines.append(f"|wTotal Handles:|n {total_handles}")
        lines.append(f"|wOnline Handles:|n {online_handles}")
        lines.append(f"|wTotal Posts:|n {total_posts}")
        lines.append(f"|wTotal DMs:|n {total_dms}")
        
        caller.msg("\n".join(lines))


class SafetyNetCmdSet(CmdSet):
    """Command set for SafetyNet commands."""
    
    key = "safetynet_cmdset"
    
    def at_cmdset_creation(self):
        self.add(CmdSafetyNet())
        self.add(CmdSafetyNetAdmin())
