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
        sn/read [feed]              - Read recent posts (default: public)
        sn/read/next                - Show next page of posts
        sn/post <feed>=<message>    - Post to a feed
        sn/login <handle> <pass>    - Log into a handle
        sn/logout                   - Log out of current handle
        sn/dm <handle>=<message>    - Send a direct message
        sn/inbox                    - View your DM inbox
        sn/inbox/next               - Next page of inbox
        sn/thread <handle>          - View DM thread with handle
        sn/search <query>           - Search posts
        sn/handles                  - List your handles
        sn/register <handle>        - Create a new handle
        sn/delete <handle>=<pass>   - Delete a handle
        sn/passchange <handle>=<old>- Change password (generates new)
        sn/ice <handle>             - Scan a handle's ICE profile
        sn/hack <handle>            - Attempt to hack a handle
        sn/upgrade <handle>=<level> - Upgrade your ICE (1-10)
        sn/whois <handle>           - Look up handle info
    
    Feeds: public, market, rumors, jobs
    
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
        
        # Parse switches
        switches = self.switches
        args = self.args.strip() if self.args else ""
        
        # Route to appropriate handler
        if not switches and not args:
            self.do_status(device_type)
        elif "read" in switches:
            if "next" in switches:
                self.do_read_next(device_type)
            else:
                self.do_read(device_type, args)
        elif "post" in switches:
            self.do_post(device_type, args)
        elif "login" in switches:
            self.do_login(device_type, args)
        elif "logout" in switches:
            self.do_logout(device_type)
        elif "dm" in switches:
            self.do_dm(device_type, args)
        elif "inbox" in switches:
            if "next" in switches:
                self.do_inbox_next(device_type)
            else:
                self.do_inbox(device_type)
        elif "thread" in switches:
            self.do_thread(device_type, args)
        elif "search" in switches:
            self.do_search(device_type, args)
        elif "handles" in switches:
            self.do_handles(device_type)
        elif "register" in switches:
            self.do_register(device_type, args)
        elif "delete" in switches:
            self.do_delete(device_type, args)
        elif "passchange" in switches:
            self.do_passchange(device_type, args)
        elif "passadd" in switches:
            self.do_passadd(device_type, args)
        elif "ice" in switches:
            self.do_ice(device_type, args)
        elif "hack" in switches:
            self.do_hack(device_type, args)
        elif "upgrade" in switches:
            self.do_upgrade(device_type, args)
        elif "whois" in switches:
            self.do_whois(device_type, args)
        else:
            # Check if first word is a subcommand
            parts = args.split(None, 1)
            if parts:
                subcmd = parts[0].lower()
                subargs = parts[1] if len(parts) > 1 else ""
                
                if subcmd == "read":
                    self.do_read(device_type, subargs)
                elif subcmd == "post":
                    self.do_post(device_type, subargs)
                elif subcmd == "login":
                    self.do_login(device_type, subargs)
                elif subcmd == "logout":
                    self.do_logout(device_type)
                elif subcmd == "dm":
                    self.do_dm(device_type, subargs)
                elif subcmd == "inbox":
                    self.do_inbox(device_type)
                elif subcmd == "thread":
                    self.do_thread(device_type, subargs)
                elif subcmd == "search":
                    self.do_search(device_type, subargs)
                elif subcmd == "handles":
                    self.do_handles(device_type)
                elif subcmd == "register":
                    self.do_register(device_type, subargs)
                elif subcmd == "delete":
                    self.do_delete(device_type, subargs)
                elif subcmd == "passchange":
                    self.do_passchange(device_type, subargs)
                elif subcmd == "passadd":
                    self.do_passadd(device_type, subargs)
                elif subcmd == "ice":
                    self.do_ice(device_type, subargs)
                elif subcmd == "hack":
                    self.do_hack(device_type, subargs)
                elif subcmd == "upgrade":
                    self.do_upgrade(device_type, subargs)
                elif subcmd == "whois":
                    self.do_whois(device_type, subargs)
                else:
                    caller.msg(f"|rUnknown SafetyNet command.|n Use |wsn|n for help.")
            else:
                self.do_status(device_type)
    
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
        output.append("  |wsn/read|n [feed]          - Read posts")
        output.append("  |wsn/post|n <feed>=<msg>    - Post message")
        output.append("  |wsn/login|n <handle> <pass>- Log in")
        output.append("  |wsn/logout|n               - Log out")
        output.append("  |wsn/dm|n <handle>=<msg>    - Send DM")
        output.append("  |wsn/inbox|n                - View DMs")
        output.append("  |wsn/register|n <handle>    - Create handle")
        output.append("  |wsn/handles|n              - List your handles")
        output.append("  |wsn/ice|n <handle>         - Scan ICE profile")
        output.append("  |wsn/hack|n <handle>        - Attempt hack")
        output.append("")
        output.append(f"|wFeeds:|n {', '.join(AVAILABLE_FEEDS)}")
        output.append("|w=====================================|n")
        
        delay_time = get_connection_delay(device_type, "read")
        delayed_output(caller, "\n".join(output), delay_time)
    
    def do_read(self, device_type, args):
        """Read posts from a feed."""
        caller = self.caller
        manager = get_safetynet_manager()
        
        feed = args.strip().lower() if args else DEFAULT_FEED
        
        if feed not in AVAILABLE_FEEDS:
            caller.msg(f"|rInvalid feed.|n Available: {', '.join(AVAILABLE_FEEDS)}")
            return
        
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
        lines.append(f"|w===== SafetyNet: #{feed} =====|n")
        
        if not posts:
            lines.append("|yNo posts in this feed.|n")
        else:
            for post in posts:
                handle = post.get("handle", "Unknown")
                message = post.get("message", "")
                timestamp = post.get("timestamp")
                
                indicator = get_online_indicator(handle, manager)
                time_str = format_timestamp(timestamp) if timestamp else "?"
                
                lines.append(f"|c{handle}|n {indicator} |K({time_str})|n")
                lines.append(f"  {message}")
                lines.append("")
        
        lines.append("|wUse sn/read/next for more posts.|n")
        lines.append("|w================================|n")
        
        return "\n".join(lines)
    
    def do_post(self, device_type, args):
        """Post to a feed."""
        caller = self.caller
        manager = get_safetynet_manager()
        
        # Check login
        handle_data = manager.get_logged_in_handle(caller)
        if not handle_data:
            caller.msg(MSG_NOT_LOGGED_IN)
            return
        
        if "=" not in args:
            caller.msg("|rUsage: sn/post <feed>=<message>|n")
            caller.msg(f"|wFeeds:|n {', '.join(AVAILABLE_FEEDS)}")
            return
        
        feed, message = args.split("=", 1)
        feed = feed.strip().lower()
        message = message.strip()
        
        if not message:
            caller.msg("|rMessage cannot be empty.|n")
            return
        
        def do_post_delayed():
            success, result_msg = manager.create_post(
                handle_data["display_name"],
                feed,
                message
            )
            if success:
                caller.msg(MSG_POST_SUCCESS.format(feed=feed))
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
            caller.msg("|rUsage: sn/login <handle> <password>|n")
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
            caller.msg("|rUsage: sn/dm <handle>=<message>|n")
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
                
                lines.append(f"{read_marker}|cFrom: {from_handle}|n {indicator} |K({time_str})|n")
                # Truncate long messages
                preview = message[:150] + "..." if len(message) > 150 else message
                lines.append(f"  {preview}")
                lines.append("")
        
        lines.append("|wUse sn/inbox/next for more. sn/thread <handle> for conversation.|n")
        lines.append("|w==========================================|n")
        
        return "\n".join(lines)
    
    def do_thread(self, device_type, args):
        """View DM thread with a handle."""
        caller = self.caller
        manager = get_safetynet_manager()
        
        handle_data = manager.get_logged_in_handle(caller)
        if not handle_data:
            caller.msg(MSG_NOT_LOGGED_IN)
            return
        
        if not args:
            caller.msg("|rUsage: sn/thread <handle>|n")
            return
        
        other_handle = args.strip()
        my_handle = handle_data["display_name"]
        
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
                
                lines.append(f"|c{from_handle}|n |K({time_str})|n")
                lines.append(f"  {message}")
                lines.append("")
        
        lines.append("|w==========================================|n")
        
        delay_time = get_connection_delay(device_type, "read")
        delayed_output(caller, "\n".join(lines), delay_time)
    
    def do_search(self, device_type, args):
        """Search posts."""
        caller = self.caller
        manager = get_safetynet_manager()
        
        if not args:
            caller.msg("|rUsage: sn/search <query>|n")
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
                    
                    lines.append(f"|c{handle}|n {indicator} in #{feed} |K({time_str})|n")
                    preview = message[:100] + "..." if len(message) > 100 else message
                    lines.append(f"  {preview}")
                    lines.append("")
            
            lines.append("|w==============================|n")
            caller.msg("\n".join(lines))
        
        delay_time = get_connection_delay(device_type, "search")
        if delay_time > 0.5:
            caller.msg(MSG_CONNECTING)
        delay(delay_time, do_search_delayed)
    
    def do_handles(self, device_type):
        """List character's handles."""
        caller = self.caller
        manager = get_safetynet_manager()
        
        handles = manager.get_character_handles(caller)
        
        lines = []
        lines.append("|w===== Your SafetyNet Handles =====|n")
        
        if not handles:
            lines.append("|yNo handles. Use sn/register <name> to create one.|n")
        else:
            current = manager.get_logged_in_handle(caller)
            for h in handles:
                name = h["name"]
                data = h["data"]
                ice = data.get("ice_rating", 1)
                is_current = current and current.get("display_name") == name
                marker = " |g[ACTIVE]|n" if is_current else ""
                
                lines.append(f"  |c{name}|n{marker} - ICE: {ice}/10")
        
        lines.append("|w==================================|n")
        
        delay_time = get_connection_delay(device_type, "read")
        delayed_output(caller, "\n".join(lines), delay_time)
    
    def do_register(self, device_type, args):
        """Register a new handle."""
        caller = self.caller
        manager = get_safetynet_manager()
        
        if not args:
            caller.msg("|rUsage: sn/register <handle>|n")
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
            caller.msg("|rUsage: sn/delete <handle>=<password>|n")
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
            caller.msg("|rUsage: sn/passchange <handle>=<old_password>|n")
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
        caller.msg("Use |w'sn/passchange <handle> <old_password>'|n to rotate your password instead.")
    
    def do_ice(self, device_type, args):
        """Scan a handle's ICE profile."""
        caller = self.caller
        manager = get_safetynet_manager()
        
        if not args:
            caller.msg("|rUsage: sn/ice <handle>|n")
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
            caller.msg("|rUsage: sn/hack <handle>|n")
            return
        
        handle = args.strip()
        
        def do_hack_delayed():
            result = manager.attempt_hack(caller, handle)
            
            lines = []
            lines.append("|w===== INTRUSION ATTEMPT =====|n")
            lines.append(f"|yTarget:|n {handle}")
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
            caller.msg("|rUsage: sn/upgrade <handle>=<level>|n")
            caller.msg("|yICE levels: 1-10 (higher = more secure)|n")
            return
        
        handle, level = args.split("=", 1)
        handle = handle.strip()
        
        try:
            level = int(level.strip())
        except ValueError:
            caller.msg("|rICE level must be a number 1-10.|n")
            return
        
        success, message = manager.set_ice_rating(caller, handle, level)
        
        if success:
            caller.msg(f"|g{message}|n")
        else:
            caller.msg(f"|r{message}|n")
    
    def do_whois(self, device_type, args):
        """Look up handle info."""
        caller = self.caller
        manager = get_safetynet_manager()
        
        if not args:
            caller.msg("|rUsage: sn/whois <handle>|n")
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


class SafetyNetCmdSet(CmdSet):
    """Command set for SafetyNet commands."""
    
    key = "safetynet_cmdset"
    
    def at_cmdset_creation(self):
        self.add(CmdSafetyNet())
