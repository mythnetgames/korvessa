"""
Background submission and management system.

Allows players to submit, edit, and view their character backgrounds.
Staff can approve/reject backgrounds and provide feedback via pnotes.
Players receive 50 IP bonus upon first submission.
"""

from evennia import Command
from evennia.comms.models import ChannelDB


class CmdBackground(Command):
    """
    Manage your character's background story.
    
    Usage:
        background                  - View your current background
        background submit <text>    - Submit a new background
        background edit <text>      - Edit your background (only before approval)
        background status           - Check approval status
    
    Submitting a background grants you a one-time bonus of 50 IP!
    Once your background is approved by staff, it cannot be edited.
    Staff may provide feedback via pnotes if revisions are needed.
    """
    
    key = "background"
    aliases = ["bg"]
    locks = "cmd:all()"
    help_category = "Character"
    
    def func(self):
        caller = self.caller
        
        # Check for switches (staff commands)
        if "approve" in self.switches:
            self.approve_background()
            return
        elif "reject" in self.switches:
            self.reject_background()
            return
        elif "view" in self.switches:
            self.view_other_background()
            return
        
        # Parse command
        if not self.args or not self.args.strip():
            # No args: show current background
            if caller.check_permstring("Builder"):
                caller.msg(self.get_admin_help())
            else:
                caller.msg(self.get_player_help())
            return
        
        args = self.args.strip()
        
        # Check for subcommands
        if args.lower() == "status":
            self.show_status()
            return
        
        if args.lower().startswith("submit "):
            text = args[7:].strip()
            if not text:
                caller.msg("|rUsage: background submit <text>|n")
                return
            self.submit_background(text)
            return
        
        if args.lower().startswith("edit "):
            text = args[5:].strip()
            if not text:
                caller.msg("|rUsage: background edit <text>|n")
                return
            self.edit_background(text)
            return
        
        # Default: show appropriate help
        if caller.check_permstring("Builder"):
            caller.msg(self.get_admin_help())
        else:
            caller.msg(self.get_player_help())
    
    def get_player_help(self):
        """Show help text for players."""
        return (
            "|c=== Background System ===|n\n"
            "|wUsage:|n\n"
            "|wbackground|n - View your current background\n"
            "|wbackground submit <text>|n - Submit a new background (50 IP bonus)\n"
            "|wbackground edit <text>|n - Edit your background (before approval only)\n"
            "|wbackground status|n - Check approval status\n\n"
            "|ySubmitting a background grants a one-time bonus of 50 IP!|n\n"
            "|yOnce approved, your background cannot be edited.|n\n"
            "|yStaff may provide feedback via pnotes if revisions are needed.|n"
        )
    
    def get_admin_help(self):
        """Show help text for staff (Builder+)."""
        return (
            "|c=== Background System (Staff) ===|n\n"
            "|wPlayer Commands:|n\n"
            "|wbackground|n - View current background\n"
            "|wbackground submit <text>|n - Submit new background (50 IP)\n"
            "|wbackground edit <text>|n - Edit before approval\n"
            "|wbackground status|n - Check status\n\n"
            "|wStaff Commands:|n\n"
            "|wbackground/approve <character>|n - Approve a background\n"
            "|wbackground/reject <character> <reason>|n - Request revisions\n"
            "|wbackground/view <character>|n - View any character's background\n"
        )
    
    def show_background(self):
        """Display the character's current background."""
        caller = self.caller
        background = getattr(caller.db, 'background', None)
        approved = getattr(caller.db, 'background_approved', False)
        
        if not background:
            caller.msg("|yYou haven't submitted a background yet.|n")
            caller.msg("|cType |wbackground submit <text>|c to create one and earn 50 IP!|n")
            return
        
        status_str = "|gApproved|n" if approved else "|yPending Approval|n"
        
        caller.msg("|c" + "=" * 70 + "|n")
        caller.msg(f"|wCharacter Background for {caller.key}|n")
        caller.msg(f"|wStatus:|n {status_str}")
        caller.msg("|c" + "=" * 70 + "|n")
        caller.msg(background)
        caller.msg("|c" + "=" * 70 + "|n")
        
        if not approved:
            caller.msg("|yYour background is pending staff approval.|n")
            caller.msg("|yYou can still edit it with: |wbackground edit <text>|n")
    
    def show_status(self):
        """Show approval status and IP award status."""
        caller = self.caller
        background = getattr(caller.db, 'background', None)
        approved = getattr(caller.db, 'background_approved', False)
        ip_awarded = getattr(caller.db, 'background_ip_awarded', False)
        
        if not background:
            caller.msg("|yYou haven't submitted a background yet.|n")
            return
        
        caller.msg("|c=== Background Status ===|n")
        caller.msg(f"|wApproval Status:|n {'|gApproved|n' if approved else '|yPending|n'}")
        caller.msg(f"|wIP Bonus Received:|n {'|gYes|n' if ip_awarded else '|yNo|n'}")
        
        if not approved:
            caller.msg("|yYour background is still pending staff review.|n")
            caller.msg("|yCheck your pnotes for any staff feedback.|n")
    
    def submit_background(self, text):
        """Submit a new background."""
        caller = self.caller
        existing_background = getattr(caller.db, 'background', None)
        
        if existing_background:
            caller.msg("|rYou already have a background submitted.|n")
            caller.msg("|rUse |wbackground edit <text>|r to modify it (if not yet approved).|n")
            return
        
        if len(text) < 50:
            caller.msg("|rYour background must be at least 50 characters long.|n")
            caller.msg(f"|rCurrent length: {len(text)} characters.|n")
            return
        
        # Store background
        caller.db.background = text
        caller.db.background_approved = False
        
        # Award IP bonus (one-time, on first submission)
        if not getattr(caller.db, 'background_ip_awarded', False):
            current_ip = getattr(caller.db, 'ip', 0)
            caller.db.ip = current_ip + 50
            caller.db.background_ip_awarded = True
            
            caller.msg("|g=== Background Submitted! ===|n")
            caller.msg(f"|gYou've been awarded |y50 IP|g for submitting your background!|n")
            caller.msg(f"|wNew IP Total:|n |y{caller.db.ip}|n")
        else:
            caller.msg("|g=== Background Submitted! ===|n")
        
        caller.msg("|yYour background is now pending staff approval.|n")
        caller.msg("|yYou can view it with: |wbackground|n")
        caller.msg("|yYou can edit it with: |wbackground edit <text>|n")
        
        # Notify staff via Splattercast
        try:
            splattercast = ChannelDB.objects.get_channel("Splattercast")
            splattercast.msg(f"BACKGROUND_SUBMIT: {caller.key} (#{caller.id}) submitted a background for review")
        except:
            pass
    
    def edit_background(self, text):
        """Edit an existing background (only if not approved)."""
        caller = self.caller
        background = getattr(caller.db, 'background', None)
        approved = getattr(caller.db, 'background_approved', False)
        
        if not background:
            caller.msg("|rYou don't have a background yet. Use |wbackground submit <text>|r instead.|n")
            return
        
        if approved:
            caller.msg("|rYour background has already been approved and cannot be edited.|n")
            caller.msg("|rContact staff if you need changes made to an approved background.|n")
            return
        
        if len(text) < 50:
            caller.msg("|rYour background must be at least 50 characters long.|n")
            caller.msg(f"|rCurrent length: {len(text)} characters.|n")
            return
        
        # Update background
        caller.db.background = text
        
        caller.msg("|g=== Background Updated! ===|n")
        caller.msg("|yYour background has been updated and is pending staff approval.|n")
        caller.msg("|yYou can view it with: |wbackground|n")
        
        # Notify staff
        try:
            splattercast = ChannelDB.objects.get_channel("Splattercast")
            splattercast.msg(f"BACKGROUND_EDIT: {caller.key} (#{caller.id}) updated their background")
        except:
            pass
    
    def approve_background(self):
        """Staff command: Approve a character's background."""
        caller = self.caller
        
        if not caller.check_permstring("Builder"):
            caller.msg("|rYou don't have permission to approve backgrounds.|n")
            return
        
        if not self.args:
            caller.msg("|rUsage: background/approve <character>|n")
            return
        
        # Find target character
        from evennia.utils.search import search_object
        results = search_object(self.args, typeclass="typeclasses.characters.Character")
        
        if not results:
            caller.msg(f"|rCouldn't find character '{self.args}'.|n")
            return
        if len(results) > 1:
            caller.msg(f"|rMultiple matches found: {', '.join([r.key for r in results])}|n")
            return
        
        target = results[0]
        background = getattr(target.db, 'background', None)
        
        if not background:
            caller.msg(f"|r{target.key} doesn't have a background submitted.|n")
            return
        
        if getattr(target.db, 'background_approved', False):
            caller.msg(f"|y{target.key}'s background is already approved.|n")
            return
        
        # Approve background
        target.db.background_approved = True
        
        caller.msg(f"|g=== Approved Background for {target.key} ===|n")
        
        # Notify player if online
        if target.has_account:
            target.msg("|g=== Your Background Has Been Approved! ===|n")
            target.msg("|gYour character background has been reviewed and approved by staff.|n")
            target.msg("|gIt is now locked and cannot be edited.|n")
        
        # Log to Splattercast
        try:
            splattercast = ChannelDB.objects.get_channel("Splattercast")
            splattercast.msg(f"BACKGROUND_APPROVE: {caller.key} approved background for {target.key} (#{target.id})")
        except:
            pass
    
    def reject_background(self):
        """Staff command: Reject a background with feedback."""
        caller = self.caller
        
        if not caller.check_permstring("Builder"):
            caller.msg("|rYou don't have permission to reject backgrounds.|n")
            return
        
        if not self.args or ' ' not in self.args:
            caller.msg("|rUsage: background/reject <character> <reason>|n")
            return
        
        # Parse args: character name and reason
        parts = self.args.split(' ', 1)
        char_name = parts[0]
        reason = parts[1] if len(parts) > 1 else "No reason provided"
        
        # Find target character
        from evennia.utils.search import search_object
        results = search_object(char_name, typeclass="typeclasses.characters.Character")
        
        if not results:
            caller.msg(f"|rCouldn't find character '{char_name}'.|n")
            return
        if len(results) > 1:
            caller.msg(f"|rMultiple matches found: {', '.join([r.key for r in results])}|n")
            return
        
        target = results[0]
        background = getattr(target.db, 'background', None)
        
        if not background:
            caller.msg(f"|r{target.key} doesn't have a background submitted.|n")
            return
        
        # Send feedback via pnote
        from commands.pnote import add_pnote
        pnote_text = f"Background Feedback: {reason}\n\nPlease revise your background and resubmit using: background edit <text>"
        add_pnote(target, pnote_text, caller)
        
        caller.msg(f"|y=== Sent Feedback to {target.key} ===|n")
        caller.msg(f"|yFeedback: {reason}|n")
        caller.msg(f"|yA pnote has been sent to the player.|n")
        
        # Notify player if online
        if target.has_account:
            target.msg("|y=== Staff Feedback on Your Background ===|n")
            target.msg("|yStaff has reviewed your background and requested revisions.|n")
            target.msg("|yCheck your pnotes for detailed feedback: |wlook pnotes|n")
            target.msg("|yOnce revised, update it with: |wbackground edit <text>|n")
        
        # Log to Splattercast
        try:
            splattercast = ChannelDB.objects.get_channel("Splattercast")
            splattercast.msg(f"BACKGROUND_REJECT: {caller.key} sent feedback to {target.key} (#{target.id})")
        except:
            pass
    
    def view_other_background(self):
        """Staff command: View another character's background."""
        caller = self.caller
        
        if not caller.check_permstring("Builder"):
            caller.msg("|rYou don't have permission to view other backgrounds.|n")
            return
        
        if not self.args:
            caller.msg("|rUsage: background/view <character>|n")
            return
        
        # Find target character
        from evennia.utils.search import search_object
        results = search_object(self.args, typeclass="typeclasses.characters.Character")
        
        if not results:
            caller.msg(f"|rCouldn't find character '{self.args}'.|n")
            return
        if len(results) > 1:
            caller.msg(f"|rMultiple matches found: {', '.join([r.key for r in results])}|n")
            return
        
        target = results[0]
        background = getattr(target.db, 'background', None)
        approved = getattr(target.db, 'background_approved', False)
        ip_awarded = getattr(target.db, 'background_ip_awarded', False)
        
        if not background:
            caller.msg(f"|y{target.key} doesn't have a background submitted.|n")
            return
        
        status_str = "|gApproved|n" if approved else "|yPending Approval|n"
        
        caller.msg("|c" + "=" * 70 + "|n")
        caller.msg(f"|wCharacter Background for {target.key} (#{target.id})|n")
        caller.msg(f"|wStatus:|n {status_str}")
        caller.msg(f"|wIP Awarded:|n {'|gYes|n' if ip_awarded else '|yNo|n'}")
        caller.msg("|c" + "=" * 70 + "|n")
        caller.msg(background)
        caller.msg("|c" + "=" * 70 + "|n")
    
    def get_player_help(self):
        return (
            "|cBackground System|n\n"
            "|wbackground|n - View your current background\n"
            "|wbackground submit <text>|n - Submit a new background (50 IP bonus)\n"
            "|wbackground edit <text>|n - Edit your background (before approval)\n"
            "|wbackground status|n - Check approval status\n"
            "\nSubmitting a background grants a one-time 50 IP bonus.\n"
            "Once approved, your background cannot be edited.\n"
            "Staff may provide feedback via pnotes if revisions are needed.\n"
        )
    
    def get_admin_help(self):
        return (
            "|cBackground System (Staff)|n\n"
            "|wbackground/approve <character>|n - Approve a character's background\n"
            "|wbackground/reject <character> <reason>|n - Reject with feedback\n"
            "|wbackground/view <character>|n - View another character's background\n"
            "\nUse these commands to review, approve, or request revisions for player backgrounds.\n"
        )
