"""
Disguise & Anonymity Commands

Commands for managing identity concealment:
- disguise: Apply/manage skill-based disguises
- adjust: Fix slipped anonymity items (hood, mask, etc.)
- undisguise: Remove active disguise
- scrutinize: Try to see through someone's disguise
"""

from evennia import Command
from world.disguise.core import (
    get_display_identity,
    get_anonymity_item,
    get_active_disguise,
    get_disguise_stability,
    apply_disguise,
    break_disguise,
    create_disguise_profile,
    delete_disguise_profile,
    adjust_anonymity_item,
    scrutinize,
    check_item_anonymity,
)
from world.combat.constants import (
    ANONYMITY_KEYWORDS,
    DISGUISE_STABILITY_MAX,
    DISGUISE_STABILITY_UNSTABLE,
)


class CmdDisguise(Command):
    """
    Manage skill-based disguises.
    
    Usage:
        disguise                     - Show current disguise status
        disguise list                - List saved disguise profiles
        disguise create <id>=<name>  - Create new disguise profile
        disguise select <id>         - Apply a saved disguise
        disguise remove              - Remove current disguise
        disguise delete <id>         - Delete a saved profile
    
    Disguise profiles use your Disguise skill to create convincing alternate
    identities. Higher skill means more stable disguises that resist slipping.
    
    When disguised, your display name changes and observers see your disguise
    identity instead of your true name. Disguises can slip during combat,
    physical altercations, or when scrutinized.
    
    Unlike item anonymity (hoods, masks), skill-based disguises provide actual
    alternate identities rather than generic descriptors.
    """
    key = "disguise"
    locks = "cmd:all()"
    help_category = "Character"
    
    def func(self):
        caller = self.caller
        # Preserve original args for commands that need capitalization
        original_args = self.args.strip()
        args = original_args.lower()
        
        if not args:
            self.show_status()
            return
        
        if args == "list":
            self.list_profiles()
            return
        
        if args == "remove":
            self.remove_disguise()
            return
        
        if args.startswith("create "):
            self.create_profile(original_args[7:])
            return
        
        if args.startswith("select "):
            self.select_profile(args[7:])
            return
        
        if args.startswith("delete "):
            self.delete_profile(args[7:])
            return
        
        caller.msg("|RUnknown disguise command. See 'help disguise'.|n")
    
    def show_status(self):
        """Show current disguise and anonymity status."""
        caller = self.caller
        
        msg = "|C=== Disguise Status ===|n\n"
        
        # Check item anonymity
        item, descriptor = get_anonymity_item(caller)
        if item:
            msg += f"|wItem Anonymity:|n Active via {item.key}\n"
            msg += f"  Descriptor: {descriptor}\n"
        else:
            # Check if they have an anonymity item that is not active
            found_inactive = False
            
            # Check worn_items database
            if hasattr(caller.db, "worn_items") and caller.db.worn_items:
                for location, items_at_location in caller.db.worn_items.items():
                    for obj in items_at_location:
                        if obj:
                            item_name_lower = obj.key.lower()
                            for keyword in ANONYMITY_KEYWORDS:
                                if keyword in item_name_lower:
                                    msg += f"|wItem Anonymity:|n |yInactive|n (use 'adjust' to activate)\n"
                                    msg += f"  Item: {obj.key}\n"
                                    found_inactive = True
                                    break
                        if found_inactive:
                            break
                    if found_inactive:
                        break
            
            # Fallback to currently_worn attribute
            if not found_inactive:
                for obj in caller.contents:
                    if hasattr(obj, "db") and getattr(obj.db, "currently_worn", False):
                        item_name_lower = obj.key.lower()
                        for keyword in ANONYMITY_KEYWORDS:
                            if keyword in item_name_lower:
                                msg += f"|wItem Anonymity:|n |yInactive|n (use 'adjust' to activate)\n"
                                msg += f"  Item: {obj.key}\n"
                                found_inactive = True
                                break
                        if found_inactive:
                            break
            
            if not found_inactive:
                msg += "|wItem Anonymity:|n None\n"
        
        # Check skill disguise
        disguise = get_active_disguise(caller)
        if disguise:
            stability = disguise.get("stability", DISGUISE_STABILITY_MAX)
            display_name = disguise.get("display_name", "Unknown")
            profile_id = disguise.get("profile_id", "?")
            
            # Color-code stability
            if stability > DISGUISE_STABILITY_UNSTABLE:
                stab_color = "|g"
            elif stability > 0:
                stab_color = "|y"
            else:
                stab_color = "|r"
            
            msg += f"\n|wSkill Disguise:|n Active\n"
            msg += f"  Profile: {profile_id}\n"
            msg += f"  Display Name: {display_name}\n"
            msg += f"  Stability: {stab_color}{stability}/{DISGUISE_STABILITY_MAX}|n\n"
        else:
            msg += "\n|wSkill Disguise:|n None\n"
        
        # Show disguise skill
        disguise_skill = getattr(caller.db, "disguise", 0)
        msg += f"\n|wDisguise Skill:|n {disguise_skill}\n"
        
        # Check if identity has slipped
        if getattr(caller.ndb, "identity_slipped", False):
            msg += "\n|R** Your identity has slipped! Use 'adjust' to restore anonymity. **|n\n"
        
        caller.msg(msg)
    
    def list_profiles(self):
        """List saved disguise profiles."""
        caller = self.caller
        profiles = getattr(caller.db, "disguise_profiles", {})
        
        if not profiles:
            caller.msg("|yYou have no saved disguise profiles.|n")
            caller.msg("Use 'disguise create <id>=<name>' to create one.")
            return
        
        msg = "|C=== Disguise Profiles ===|n\n"
        active = get_active_disguise(caller)
        active_id = active.get("profile_id") if active else None
        
        for profile_id, profile in profiles.items():
            marker = " |G(active)|n" if profile_id == active_id else ""
            display_name = profile.get("display_name", "Unknown")
            msg += f"  |w{profile_id}|n: {display_name}{marker}\n"
        
        caller.msg(msg)
    
    def create_profile(self, args):
        """Create a new disguise profile."""
        caller = self.caller
        
        if "=" not in args:
            caller.msg("|RUsage: disguise create <id>=<display name>|n")
            return
        
        profile_id, display_name = args.split("=", 1)
        profile_id = profile_id.strip()
        display_name = display_name.strip()
        
        if not profile_id or not display_name:
            caller.msg("|RBoth profile ID and display name are required.|n")
            return
        
        # Check for existing profile
        profiles = getattr(caller.db, "disguise_profiles", {})
        if profiles is None:
            profiles = {}
        if profile_id in profiles:
            caller.msg(f"|yProfile '{profile_id}' already exists. Use a different ID or delete it first.|n")
            return
        
        # Create the profile
        create_disguise_profile(caller, profile_id, display_name)
        caller.msg(f"|gCreated disguise profile '{profile_id}' with display name: {display_name}|n")
        caller.msg("Use 'disguise select <id>' to apply this disguise.")
    
    def select_profile(self, profile_id):
        """Apply a saved disguise profile."""
        caller = self.caller
        profile_id = profile_id.strip()
        
        profiles = getattr(caller.db, "disguise_profiles", {})
        if profile_id not in profiles:
            caller.msg(f"|RNo profile named '{profile_id}'. Use 'disguise list' to see available profiles.|n")
            return
        
        # Check disguise skill
        disguise_skill = getattr(caller.db, "disguise", 0)
        if disguise_skill < 10:
            caller.msg("|yWarning: Your Disguise skill is very low. Your disguise will be unstable.|n")
        
        if apply_disguise(caller, profile_id):
            profile = profiles[profile_id]
            caller.msg(f"You apply your disguise. You now appear as: {profile.get('display_name')}")
            if caller.location:
                caller.location.msg_contents(
                    f"{caller.key} takes a moment to adjust their appearance.",
                    exclude=[caller]
                )
        else:
            caller.msg("|RFailed to apply disguise.|n")
    
    def remove_disguise(self):
        """Voluntarily remove current disguise."""
        caller = self.caller
        
        disguise = get_active_disguise(caller)
        if not disguise:
            caller.msg("|yYou are not currently disguised.|n")
            return
        
        display_name = disguise.get("display_name", "someone")
        caller.db.active_disguise = None
        
        # Clear slip state
        if hasattr(caller.ndb, "identity_slipped"):
            delattr(caller.ndb, "identity_slipped")
        
        caller.msg("|gYou remove your disguise, revealing your true identity.|n")
        if caller.location:
            caller.location.msg_contents(
                f"|y{display_name} removes their disguise, revealing {caller.key}!|n",
                exclude=[caller]
            )
    
    def delete_profile(self, profile_id):
        """Delete a saved disguise profile."""
        caller = self.caller
        profile_id = profile_id.strip()
        
        if delete_disguise_profile(caller, profile_id):
            caller.msg(f"|gDeleted disguise profile '{profile_id}'.|n")
        else:
            caller.msg(f"|RNo profile named '{profile_id}'.|n")


class CmdAdjust(Command):
    """
    Adjust an anonymity item to restore concealment after a slip.
    
    Usage:
        adjust          - Adjust your hood/mask/etc. back into place
        adjust <item>   - Adjust a specific item
    
    When your hood slips or mask is jostled, your true identity is briefly
    revealed. Use this command to restore your concealment.
    
    This takes a moment and cannot be done instantly in combat.
    """
    key = "adjust"
    aliases = ["fix", "pull up"]
    locks = "cmd:all()"
    help_category = "Character"
    
    ADJUST_COOLDOWN = 600  # Seconds between adjusts (10 minutes)
    
    def func(self):
        import time
        caller = self.caller
        
        # Check cooldown
        last_adjust = getattr(caller.ndb, "last_adjust_time", 0)
        if last_adjust is None:
            last_adjust = 0
        current_time = time.time()
        if current_time - last_adjust < self.ADJUST_COOLDOWN:
            remaining = self.ADJUST_COOLDOWN - (current_time - last_adjust)
            caller.msg(f"|yYou must wait {remaining:.1f} more seconds before adjusting again.|n")
            return
        
        # Check if in active combat - adjustment takes time
        if hasattr(caller.ndb, "combat_handler") and caller.ndb.combat_handler:
            # In combat - set as combat action instead of immediate
            handler = caller.ndb.combat_handler
            combatants = getattr(handler.db, "combatants", [])
            for entry in combatants:
                if entry.get("char") == caller:
                    entry["combat_action"] = "adjust_anonymity"
                    caller.msg("|yYou will attempt to adjust your concealment next round.|n")
                    return
        
        # Not in combat - immediate adjustment
        item = None
        if self.args:
            # Find specific item
            item_name = self.args.strip().lower()
            for obj in caller.contents:
                if item_name in obj.key.lower():
                    item = obj
                    break
            if not item:
                caller.msg(f"|RYou are not carrying anything called '{self.args.strip()}'.|n")
                return
        
        if adjust_anonymity_item(caller, item):
            # Set cooldown on successful adjust
            caller.ndb.last_adjust_time = time.time()
        else:
            caller.msg("|yYou have nothing to adjust. You need a hood, mask, or similar item.|n")


class CmdScrutinize(Command):
    """
    Carefully study someone to try to see through their disguise.
    
    Usage:
        scrutinize <target>
    
    Uses your SMRT and perception-related skills against their Disguise skill.
    Success reveals their true identity to you.
    
    This is an obvious action - the target will know they are being studied.
    Repeated scrutiny damages disguise stability.
    """
    key = "scrutinize"
    aliases = ["study", "examine closely"]
    locks = "cmd:all()"
    help_category = "Character"
    
    def func(self):
        caller = self.caller
        
        if not self.args:
            caller.msg("|RScrutinize who?|n")
            return
        
        target_name = self.args.strip()
        
        # Find target in room
        target = caller.search(target_name, location=caller.location)
        if not target:
            return
        
        if target == caller:
            caller.msg("|yYou study yourself intently. Yep, still you.|n")
            return
        
        # Check if target has any concealment
        item, descriptor = get_anonymity_item(target)
        disguise = get_active_disguise(target)
        
        if not item and not disguise:
            caller.msg(f"|y{target.key} is not disguised or concealed.|n")
            return
        
        # Notify the target
        display_name, is_true = get_display_identity(target, caller)
        target.msg(f"|y{caller.key} studies you intently, trying to see through your disguise.|n")
        
        # Announce to room
        if caller.location:
            caller.location.msg_contents(
                f"|y{caller.key} studies {display_name} intently.|n",
                exclude=[caller, target]
            )
        
        # Perform scrutiny
        success, message = scrutinize(caller, target)
        caller.msg(message)


class CmdPullUp(Command):
    """
    Pull up your hood to activate anonymity.
    
    Usage:
        pullup          - Pull up your hood/mask/etc.
        pullup <item>   - Pull up a specific item
    
    Activates the anonymity feature of hoodies, masks, and similar items.
    Your identity will be concealed until the item slips or is removed.
    """
    key = "pullup"
    aliases = ["hood up", "mask on"]
    locks = "cmd:all()"
    help_category = "Character"
    
    def func(self):
        caller = self.caller
        
        # Find anonymity-capable item
        target_item = None
        
        if self.args:
            item_name = self.args.strip().lower()
            # Check worn items first
            if hasattr(caller.db, "worn_items") and caller.db.worn_items:
                for location, items_at_location in caller.db.worn_items.items():
                    for obj in items_at_location:
                        if obj and item_name in obj.key.lower():
                            target_item = obj
                            break
                    if target_item:
                        break
            # Fallback to contents with currently_worn flag
            if not target_item:
                for obj in caller.contents:
                    if hasattr(obj, "db") and getattr(obj.db, "currently_worn", False):
                        if item_name in obj.key.lower():
                            target_item = obj
                            break
        else:
            # Auto-find first anonymity-capable worn item
            if hasattr(caller.db, "worn_items") and caller.db.worn_items:
                for location, items_at_location in caller.db.worn_items.items():
                    for obj in items_at_location:
                        if obj:
                            item_name_lower = obj.key.lower()
                            for keyword in ANONYMITY_KEYWORDS:
                                if keyword in item_name_lower:
                                    target_item = obj
                                    break
                        if target_item:
                            break
                    if target_item:
                        break
            
            # Fallback to currently_worn attribute
            if not target_item:
                for obj in caller.contents:
                    if hasattr(obj, "db") and getattr(obj.db, "currently_worn", False):
                        item_name_lower = obj.key.lower()
                        for keyword in ANONYMITY_KEYWORDS:
                            if keyword in item_name_lower:
                                target_item = obj
                                break
                        if target_item:
                            break
        
        if not target_item:
            caller.msg("|yYou have nothing that can provide anonymity.|n")
            return
        
        # Check if item covers face (required for anonymity)
        coverage = getattr(target_item.db, "coverage", [])
        if "face" not in coverage:
            caller.msg(f"|yYour {target_item.key} does not cover your face - it cannot conceal your identity.|n")
            return
        
        # Check if already active
        if getattr(target_item.db, "anonymity_active", False):
            caller.msg(f"|yYour {target_item.key} is already providing anonymity.|n")
            return
        
        # Activate anonymity
        target_item.db.anonymity_active = True
        target_item.db.provides_anonymity = True
        
        # Clear any slip state
        if hasattr(caller.ndb, "identity_slipped"):
            delattr(caller.ndb, "identity_slipped")
        caller.ndb.emote_count_since_adjust = 0
        
        caller.msg(f"|gYou pull up your {target_item.key}, concealing your identity.|n")
        if caller.location:
            caller.location.msg_contents(
                f"|y{caller.key} pulls up their {target_item.key}.|n",
                exclude=[caller]
            )


class CmdPullDown(Command):
    """
    Pull down your hood to reveal your identity.
    
    Usage:
        pulldown          - Pull down your hood/mask/etc.
        pulldown <item>   - Pull down a specific item
    
    Deactivates the anonymity feature, revealing your true identity.
    """
    key = "pulldown"
    aliases = ["hood down", "mask off"]
    locks = "cmd:all()"
    help_category = "Character"
    
    def func(self):
        caller = self.caller
        
        # Find active anonymity item
        target_item = None
        
        if self.args:
            item_name = self.args.strip().lower()
            # Check worn items first
            if hasattr(caller.db, "worn_items") and caller.db.worn_items:
                for location, items_at_location in caller.db.worn_items.items():
                    for obj in items_at_location:
                        if obj and item_name in obj.key.lower():
                            target_item = obj
                            break
                    if target_item:
                        break
            # Fallback to currently_worn attribute
            if not target_item:
                for obj in caller.contents:
                    if hasattr(obj, "db") and getattr(obj.db, "currently_worn", False):
                        if item_name in obj.key.lower():
                            target_item = obj
                            break
        else:
            # Find currently active anonymity item
            target_item, _ = get_anonymity_item(caller)
        
        if not target_item:
            caller.msg("|yYou have no anonymity to remove.|n")
            return
        
        if not getattr(target_item.db, "anonymity_active", False):
            caller.msg(f"|yYour {target_item.key} is not providing anonymity.|n")
            return
        
        # Deactivate
        target_item.db.anonymity_active = False
        
        caller.msg(f"|gYou pull down your {target_item.key}, revealing your face.|n")
        if caller.location:
            caller.location.msg_contents(
                f"|y{caller.key} pulls down their {target_item.key}, revealing their face.|n",
                exclude=[caller]
            )


class CmdExpose(Command):
    """
    Expose your true identity, canceling your disguise.
    
    Usage:
        expose me   - Reveal your true identity to everyone
    
    This immediately ends any active disguise or anonymity, revealing who you
    really are to everyone in the area. Useful if you want to drop your cover
    or wear a mask/hood without hiding your identity.
    """
    key = "expose me"
    aliases = ["expose"]
    locks = "cmd:all()"
    help_category = "Character"
    
    def func(self):
        caller = self.caller
        
        # Check if they have an active disguise or anonymity
        item, item_descriptor = get_anonymity_item(caller)
        disguise = get_active_disguise(caller)
        
        if not item and not disguise:
            caller.msg("|yYou are not disguised or wearing an anonymity item.|n")
            return
        
        # Clear identity slip state (so they're no longer "slipped")
        if hasattr(caller.ndb, "identity_slipped"):
            delattr(caller.ndb, "identity_slipped")
        
        # Deactivate any anonymity item
        if item:
            item.db.anonymity_active = False
        
        # Clear any active disguise
        if disguise:
            disguise["stability"] = 0  # Break the disguise
        
        # Send confirmation message
        if item and disguise:
            caller.msg(f"|gYou expose your true identity, dropping both your {item.key} and your disguise.|n")
        elif item:
            caller.msg(f"|gYou expose your true identity, dropping your {item.key}.|n")
        else:
            caller.msg("|gYou expose your true identity, dropping your disguise.|n")
        
        # Notify observers
        if caller.location:
            observer_msg = f"{caller.key} reveals their true identity."
            caller.location.msg_contents(observer_msg, exclude=[caller])
