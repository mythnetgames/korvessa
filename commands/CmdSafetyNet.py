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
        sn wear <handle>            - Brute force wear down ICE (risky)
        sn raise <handle>=<amount>  - Raise ICE by amount (1-20)
        sn proxy                    - Toggle proxy mode on device
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
            self.do_ice(device_type, device, subargs)
        elif primary_cmd == "hack":
            self.do_hack(device_type, device, subargs)
        elif primary_cmd == "wear":
            self.do_wear(device_type, device, subargs)
        elif primary_cmd == "upgrade":
            self.do_upgrade(device_type, subargs)
        elif primary_cmd == "raise":
            self.do_raise_ice(device_type, device, subargs)
        elif primary_cmd == "whois":
            self.do_whois(device_type, subargs)
        elif primary_cmd == "proxy":
            self.do_proxy(device_type, device, subargs)
        else:
            caller.msg(f"|rUnknown SafetyNet command: {primary_cmd}|n Use |wsn|n for help.")
    
    def do_status(self, device_type):
        """Show SafetyNet status and help."""
        caller = self.caller
        manager = get_safetynet_manager()
        
        output = []
        output.append("|#00ff00================ SafetyNet ================|n")
        output.append("|#00af00Municipal Safety & Communication Network|n")
        output.append("")
        
        # Device info
        device_name = "Wristpad" if device_type == "wristpad" else "Computer Terminal"
        output.append(f"|#00d700Device:|n {device_name}")
        
        # Login status
        handle_data = manager.get_logged_in_handle(caller)
        if handle_data:
            output.append(f"|#00d700Logged in as:|n |#5fff00{handle_data['display_name']}|n |#00ff00[ACTIVE]|n")
        else:
            output.append("|#00d700Logged in as:|n |r[NOT LOGGED IN]|n")
        
        # Quick stats
        
        output.append("")
        output.append("|#00af00SOCIAL COMMANDS:|n")
        output.append("  |#5fd700sn read|n                 - Read posts")
        output.append("  |#5fd700sn post|n <msg>           - Post message")
        output.append("  |#5fd700sn search|n <query>       - Search posts")
        output.append("  |#5fd700sn dm|n <handle>=<msg>    - Send DM")
        output.append("  |#5fd700sn inbox|n                - View DMs")
        output.append("  |#5fd700sn thread|n <handle>      - View thread")
        
        output.append("")
        output.append("|#00af00ACCOUNT COMMANDS:|n")
        output.append("  |#5fd700sn login|n <handle> <pass> - Log in")
        output.append("  |#5fd700sn logout|n                - Log out")
        output.append("  |#5fd700sn register|n <handle>     - Create handle")
        output.append("  |#5fd700sn delete|n <h>=<pass>     - Delete handle")
        output.append("  |#5fd700sn passchange|n <h>=<old>  - Change password")
        output.append("  |#5fd700sn whois|n <handle>        - Lookup handle")
        
        output.append("")
        output.append("|#00af00SECURITY COMMANDS:|n")
        output.append("  |#5fd700sn ice|n <handle>         - Scan ICE profile")
        output.append("  |#5fd700sn hack|n <handle>        - Attempt hack")
        output.append("  |#5fd700sn wear|n <handle>        - Wear down ICE")
        output.append("  |#5fd700sn raise|n <h>=<amt>      - Raise ICE")
        output.append("  |#5fd700sn proxy|n                - Toggle proxy mode")

        
        output.append("")
        output.append("|#00ff00==========================================|n")
        
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
    
    def _generate_hacker_header(self, device):
        """Generate a random hacker-style header line."""
        import random
        port = random.randint(1000, 9999)
        cpu = random.randint(12, 89)
        local_ip = f"{random.randint(10,192)}.{random.randint(0,255)}.{random.randint(0,255)}.{random.randint(1,254)}"
        cloak = "ACTIVE" if self._is_proxy_active(device) else "INACTIVE"
        return f"|#00ff00>>===Port:{port}=====CPU:{cpu}%===CLOAK:{cloak}====LOCALIP:{local_ip}<<|n"
    
    def _get_slotted_proxy(self, device):
        """Get the slotted proxy module from a device, if any."""
        if not device:
            return None
        
        # Check if device has a slotted proxy item
        proxy_item = getattr(device.db, "slotted_proxy", None)
        if proxy_item and proxy_item.db:
            return proxy_item
        return None
    
    def _is_proxy_active(self, device):
        """Check if device has a proxy slotted and enabled."""
        proxy = self._get_slotted_proxy(device)
        if not proxy:
            return False
        return getattr(proxy.db, "is_active", False)
    
    def _get_proxy_ice_bonus(self, device):
        """Get ICE bonus from proxy. Returns 0 if no proxy or not active."""
        if self._is_proxy_active(device):
            return 25  # +25 ICE when proxy is active and slotted
        return 0
    
    def do_ice(self, device_type, device, args):
        """Scan a handle's ICE profile with hacker cutscene."""
        import random
        caller = self.caller
        manager = get_safetynet_manager()
        
        if not args:
            caller.msg("|rUsage: sn ice <handle>|n")
            return
        
        handle = args.strip()
        has_proxy = self._is_proxy_active(device)
        
        # Hacker cutscene intro
        caller.msg(self._generate_hacker_header(device))
        caller.msg(f"|#00d700>get user = {handle}|n")
        caller.msg("|#00af00>running ice.scan|n")
        
        def step1():
            if has_proxy:
                caller.msg("|#5fd700>Proxy FOUND!|n")
            else:
                caller.msg("|#5fff00>No proxy detected!|n")
        
        def step2():
            caller.msg("|#00d700>>scanning ice.profile|n")
        
        def step3():
            caller.msg("|#00af00>run.scan |#5fff00[|#00af00*|#5fff00****]|n")
        
        def step4():
            caller.msg("|#00af00>run.scan |#5fff00[|#00af00||#5fff00|||*]|n")
        
        def step5():
            caller.msg("|#00af00>run.scan |#5fff00[|#00af00||||#5fff00|*]|n")
        
        def step6():
            caller.msg("|#00af00>run.scan |#5fff00[|#00af00|||||#5fff00]|n")
        
        def step7():
            caller.msg("|#5fff00>Scan Complete|n")
            caller.msg("|#00d700>>running get.ice.db.kwc|n")
        
        def final_result():
            scan = manager.get_ice_scan(handle)
            if scan:
                caller.msg(f"|#00ff00>>>ICE Profile: {handle}|n")
                caller.msg(scan)
                caller.msg("|#00ff00>>>END TRANSMISSION<<<|n")
            else:
                caller.msg("|r>>>ERROR: Handle not found in database<<<|n")
        
        # Chain the delays
        base_delay = 0.3 if device_type == "computer" else 0.6
        if has_proxy:
            base_delay *= 1.5  # Proxy slows things down
        
        delay(base_delay * 1, step1)
        delay(base_delay * 2, step2)
        delay(base_delay * 3, step3)
        delay(base_delay * 4, step4)
        delay(base_delay * 5, step5)
        delay(base_delay * 6, step6)
        delay(base_delay * 7, step7)
        delay(base_delay * 8, final_result)
    
    def do_hack(self, device_type, device, args):
        """Attempt to hack a handle with hacker cutscene."""
        import time
        import random
        caller = self.caller
        manager = get_safetynet_manager()
        
        if not args:
            caller.msg("|rUsage: sn hack <handle>|n")
            return
        
        # Check for cooldown
        cooldown_until = getattr(caller.ndb, 'hack_cooldown', None)
        if cooldown_until is not None and isinstance(cooldown_until, (int, float)):
            current_time = time.time()
            if current_time < cooldown_until:
                remaining = int(cooldown_until - current_time)
                caller.msg(f"|r[ICE LOCKOUT]|n ICE countermeasures active. Try again in {remaining} seconds.|n")
                return
        
        handle = args.strip()
        has_proxy = self._is_proxy_active(device)
        
        # Hacker cutscene intro
        caller.msg(self._generate_hacker_header(device))
        caller.msg(f"|#00d700>get user = {handle}|n")
        caller.msg("|#00af00>running intrusion.exe|n")
        
        base_delay = 0.4 if device_type == "computer" else 0.7
        if has_proxy:
            base_delay *= 1.5
        
        def step1():
            if has_proxy:
                caller.msg("|#5fd700>Proxy FOUND! Routing through secure tunnel...|n")
            else:
                caller.msg("|#5fff00>No proxy detected! Connection exposed!|n")
        
        def step2():
            caller.msg("|#00d700>>initiating ice.bypass|n")
        
        def step3():
            caller.msg("|#00af00>run.crack |#5fff00[|#00af00***|#5fff00]|n")
        
        def step4():
            caller.msg("|#00af00>run.crack |#5fff00[|#00af00****|#5fff00]|n")
        
        def step5():
            caller.msg("|#00af00>run.crack |#5fff00[|#00af00*****|#5fff00]|n")
        
        def step7():
            caller.msg("|#5fd700>>>ICE BREACHED|n")
            caller.msg("|#00d700>>running trace.protocol|n")
        
        def step8():
            caller.msg("|#00af00>run.trace |#5fff00[|#00af00***|#5fff00]|n")
        
        def step9():
            caller.msg("|#00af00>run.trace |#5fff00[|#00af00****|#5fff00]|n")
        
        def step10():
            caller.msg("|#00af00>run.trace |#5fff00[|#00af00*****|#5fff00]|n")
        
        def final_result():
            result = manager.attempt_hack(caller, handle)
            
            # Set cooldown on failure
            if not result.get("success"):
                cooldown_duration = 30
                caller.ndb.hack_cooldown = time.time() + cooldown_duration
            
            if result.get("success"):
                caller.msg("|#5fff00>>>ACCESS GRANTED<<<|n")
                caller.msg("|#00d700>>running get.credentials.db.kwc|n")
                
                if result.get("password"):
                    caller.msg(f"|#00ff00>Password: |#5fff00{result['password']}|n")
                
                # Show trace if available
                if result.get("trace"):
                    caller.msg("|#5fd700>Trace Found|n")
                    caller.msg(f"|#00af00>Location: |#5fff00{result['trace']}|n")
                elif result.get("online"):
                    caller.msg("|#00af00>Trace Failed: Signal bounced|n")
                else:
                    caller.msg("|#00af00>No trace: Target offline|n")
                
                # Show DMs if available
                dms = result.get("dms", [])
                if dms:
                    caller.msg(f"|#00ff00>>>Recovered Messages ({len(dms)})|n")
                    for dm in dms[:5]:
                        from_h = dm.get("from_handle", "?")
                        msg = dm.get("message", "")[:80]
                        caller.msg(f"|#00d700>  {from_h}: |#5fd700{msg}|n")
                
                caller.msg("|#00ff00>>>END TRANSMISSION<<<|n")
            else:
                caller.msg("|#00af00>>>|r[ACCESS DENIED]|#00af00<<<|n")
                caller.msg(f"|#00af00>ICE COUNTERMEASURES ACTIVE|n")
                caller.msg(f"|#00af00>LOCKOUT: |r30 seconds|#00af00|n")
                caller.msg("|#00af00>>>CONNECTION TERMINATED<<<|n")
                
                # Alert the target if online
                if result.get("alert") and result.get("target_char_id"):
                    from evennia.objects.models import ObjectDB
                    try:
                        target_char = ObjectDB.objects.get(id=result.get("target_char_id"))
                        if target_char:
                            target_char.msg(f"|#008700[SafetyNet System Alert]|w: |R{result['alert']}")
                    except:
                        pass
        
        # Chain the delays
        delay(base_delay * 1, step1)
        delay(base_delay * 2, step2)
        delay(base_delay * 3, step3)
        delay(base_delay * 4, step4)
        delay(base_delay * 5, step5)
        delay(base_delay * 6, step7)
        delay(base_delay * 7, step8)
        delay(base_delay * 8, step9)
        delay(base_delay * 9, step10)
        delay(base_delay * 10, final_result)
    
    def do_wear(self, device_type, device, args):
        """Attempt to wear down a handle's ICE with hacker cutscene."""
        import time
        caller = self.caller
        manager = get_safetynet_manager()
        
        if not args:
            caller.msg("|rUsage: sn wear <handle>|n")
            return
        
        handle = args.strip()
        has_proxy = self._is_proxy_active(device)
        
        # Hacker cutscene intro
        caller.msg(self._generate_hacker_header(device))
        caller.msg(f"|#00d700>get user = {handle}|n")
        caller.msg("|#00af00>running bruteforce.exe|n")
        
        base_delay = 0.4 if device_type == "computer" else 0.7
        if has_proxy:
            base_delay *= 1.5
        
        def step1():
            if has_proxy:
                caller.msg("|#5fd700>Proxy FOUND! Attack origin masked...|n")
            else:
                caller.msg("|#5fff00>No proxy detected! CAUTION: Traceable!|n")
        
        def step2():
            caller.msg("|#00d700>>initiating ice.degrade|n")
        
        def step3():
            caller.msg("|#00af00>run.wear |#5fff00[|#00af00***|#5fff00]|n")
        
        def step4():
            caller.msg("|#00af00>run.wear |#5fff00[|#00af00****|#5fff00]|n")
        
        def step5():
            caller.msg("|#00af00>run.wear |#5fff00[|#00af00*****|#5fff00]|n")
        
        def step6():
            caller.msg("|#5fd700>>>ATTACK COMPLETE|n")
            caller.msg("|#00d700>>analyzing results...|n")
        
        def final_result():
            result = manager.attempt_wear_ice(caller, handle)
            
            if result.get("success"):
                new_rating = result.get("new_rating", "?")
                caller.msg("|#5fff00>>>ICE DEGRADED<<<|n")
                caller.msg(f"|#00af00>Result: {result['message']}|n")
                caller.msg(f"|#00ff00>New ICE Rating: |#5fff00{new_rating}/100|n")
                caller.msg("|#00ff00>>>END TRANSMISSION<<<|n")
            else:
                caller.msg(f"|#00af00>>>|r[ATTACK FAILED]|#00af00<<<|n")
                caller.msg(f"|#00af00>Result: |r{result['message']}|#00af00|n")
                if result.get("traced"):
                    caller.msg("|#00af00>>>|r[WARNING: TRACED]|#00af00<<<|n")
                    caller.msg("|#00af00>Your location has been exposed to target!|n")
                    
                    # Alert the target if online
                    if result.get("alert") and result.get("target_char_id"):
                        from evennia.objects.models import ObjectDB
                        try:
                            target_char = ObjectDB.objects.get(id=result.get("target_char_id"))
                            if target_char:
                                target_char.msg(f"|#008700[SafetyNet System Alert]|w: |R{result['alert']}")
                        except:
                            pass
                caller.msg("|#00af00>>>CONNECTION TERMINATED<<<|n")
        
        # Chain the delays
        delay(base_delay * 1, step1)
        delay(base_delay * 2, step2)
        delay(base_delay * 3, step3)
        delay(base_delay * 4, step4)
        delay(base_delay * 5, step5)
        delay(base_delay * 6, step6)
        delay(base_delay * 7, final_result)
    
    def do_upgrade(self, device_type, args):
        """Upgrade ICE rating for a handle. ADMIN ONLY."""
        caller = self.caller
        
        # Check if caller is a builder or higher
        if not caller.check_permstring("Builder"):
            caller.msg("|rYou do not have permission to use this command.|n")
            return
        
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
    
    def do_raise_ice(self, device_type, device, args):
        """Decker function: Raise ICE with hacker cutscene."""
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
                caller.msg(f"|rThe network is busy. Please wait before trying again.|n")
                return
        
        if "=" not in args:
            caller.msg("|rUsage: sn raise <handle>=<amount>|n")
            return
        
        handle, amount_str = args.split("=", 1)
        handle = handle.strip()
        
        try:
            amount = int(amount_str.strip())
        except ValueError:
            caller.msg("|rAmount must be a number 1-20.|n")
            return
        
        # Check daily limit based on handle (not character) to prevent multi-user exploits
        today = str(date.today())
        handle_data = manager.get_handle(handle)
        if not handle_data:
            caller.msg("|rHandle not found.|n")
            return
        
        raised_today = handle_data.get('ice_raised_today', 0)
        raised_date = handle_data.get('ice_raised_date', None)
        
        # Reset if it is a new day
        if raised_date != today:
            raised_today = 0
            handle_data['ice_raised_today'] = 0
            handle_data['ice_raised_date'] = today
        
        # Check if this attempt would exceed daily limit
        if raised_today + amount > 20:
            caller.msg("|r[SafetyNet]|n ICE augmentation is currently unavailable due to network congestion. Please try again after system maintenance.")
            return
        
        # Record this attempt timestamp
        caller.ndb.last_raise_attempt = time.time()
        
        has_proxy = self._is_proxy_active(device)
        
        # Hacker cutscene intro
        caller.msg(self._generate_hacker_header(device))
        caller.msg(f"|#00d700>get user = {handle}|n")
        caller.msg(f"|#00af00>running ice.enhance +{amount}|n")
        
        base_delay = 0.4 if device_type == "computer" else 0.7
        if has_proxy:
            base_delay *= 1.5
        
        def step1():
            if has_proxy:
                caller.msg("|#5fd700>Proxy FOUND! Secure enhancement channel...|n")
            else:
                caller.msg("|#5fff00>No proxy detected! Direct connection...|n")
        
        def step2():
            caller.msg("|#00d700>>initiating ice.upgrade|n")
        
        def step3():
            caller.msg("|#00af00>run.enhance |#5fff00[|#00af00***|#5fff00]|n")
        
        def step4():
            caller.msg("|#00af00>run.enhance |#5fff00[|#00af00****|#5fff00]|n")
        
        def step5():
            caller.msg("|#00af00>run.enhance |#5fff00[|#00af00*****|#5fff00]|n")
        
        def step6():
            caller.msg("|#00af00>run.enhance |#5fff00[|#00af00*****|#5fff00]|n")
        
        def step7():
            caller.msg("|#5fd700>>>ENHANCEMENT COMPLETE|n")
            caller.msg("|#00d700>>verifying ice.integrity...|n")
        
        def final_result():
            success, message, new_rating, result_type = manager.raise_ice(caller, handle, amount)
            
            # Set cooldown on critical failure
            if result_type == 'critfail':
                cooldown_duration = 30
                caller.ndb.raise_cooldown = time.time() + cooldown_duration
            elif result_type == 'success':
                # Track daily ICE raised on handle (not character) to prevent multi-user exploits
                handle_data = manager.get_handle(handle)
                if handle_data:
                    today = str(date.today())
                    raised_today = handle_data.get('ice_raised_today', 0)
                    raised_date = handle_data.get('ice_raised_date', None)
                    
                    # Reset if it is a new day
                    if raised_date != today:
                        raised_today = 0
                    
                    handle_data['ice_raised_today'] = raised_today + amount
                    handle_data['ice_raised_date'] = today
            
            if success:
                caller.msg("|#5fff00>>>ICE UPGRADED<<<|n")
                caller.msg(f"|#00af00>Result: {message}|n")
                caller.msg(f"|#00ff00>New ICE Rating: |#5fff00{new_rating}/100|n")
                caller.msg("|#00ff00>>>END TRANSMISSION<<<|n")
            else:
                caller.msg("|#00af00>>>|r[FAILED]|#00af00<<<|n")
                caller.msg(f"|#00af00>Result: |r{message}|#00af00|n")
                if result_type == 'critfail':
                    caller.msg("|#00af00>SYSTEM LOCKOUT: |r30 seconds|#00af00|n")
                caller.msg("|#00af00>>>CONNECTION TERMINATED<<<|n")
        
        # Chain the delays
        delay(base_delay * 1, step1)
        delay(base_delay * 2, step2)
        delay(base_delay * 3, step3)
        delay(base_delay * 4, step4)
        delay(base_delay * 5, step5)
        delay(base_delay * 6, step6)
        delay(base_delay * 7, step7)
        delay(base_delay * 8, final_result)
    
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
    
    def do_proxy(self, device_type, device, args):
        """Toggle slotted proxy module on/off for enhanced security."""
        caller = self.caller
        
        if not device:
            caller.msg("|rNo device found.|n")
            return
        
        # Check if there's a proxy slotted
        proxy = self._get_slotted_proxy(device)
        
        if not proxy:
            caller.msg("|rNo proxy module slotted in this device.|n")
            caller.msg("|yYou need to slot a proxy module first.|n")
            return
        
        # Toggle proxy active status
        current_status = getattr(proxy.db, "is_active", False)
        new_status = not current_status
        proxy.db.is_active = new_status
        
        # Hacker-style output
        caller.msg(self._generate_hacker_header(device))
        caller.msg("|#00d700>system.proxy.toggle|n")
        
        def step1():
            caller.msg("|#00af00>>accessing proxy.settings|n")
        
        def step2():
            if new_status:
                caller.msg("|#5fd700>Proxy ENABLED|n")
                caller.msg("|#00af00>Routing all traffic through secure tunnel...|n")
            else:
                caller.msg("|#5fff00>Proxy DISABLED|n")
                caller.msg("|#00af00>Direct connection established...|n")
        
        def step3():
            caller.msg("|#00d700>>updating system.config|n")
        
        def final_result():
            if new_status:
                caller.msg("|#00ff00>>>PROXY ACTIVE<<<|n")
                caller.msg("|#00af00>Module Status:|n |#5fd700Active|n")
                caller.msg("|#00af00>Benefits:|n")
                caller.msg("|#5fd700>  +25 ICE rating when defending|n")
                caller.msg("|#5fd700>  Cloak status: ACTIVE|n")
                caller.msg("|#00ff00>>>END TRANSMISSION<<<|n")
            else:
                caller.msg("|#00ff00>>>PROXY INACTIVE<<<|n")
                caller.msg("|#00af00>Module Status:|n |#5fff00Inactive|n")
                caller.msg("|#00af00>Status:|n")
                caller.msg("|#5fd700>  Normal connection speed|n")
                caller.msg("|#5fff00>  Cloak status: INACTIVE|n")
                caller.msg("|#00af00>Note:|n")
                caller.msg("|#5fd700>  Proxy module remains slotted|n")
                caller.msg("|#00ff00>>>END TRANSMISSION<<<|n")
        
        base_delay = 0.3 if device_type == "computer" else 0.5
        
        delay(base_delay * 1, step1)
        delay(base_delay * 2, step2)
        delay(base_delay * 3, step3)
        delay(base_delay * 4, final_result)


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
