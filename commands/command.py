"""
Commands

Commands describe the input the account can do to the game.

"""

from evennia.commands.command import Command as BaseCommand

# from evennia import default_cmds


class Command(BaseCommand):
    """
    Base command (you may see this if a child command had no help text defined)

    Note that the class's `__doc__` string is used by Evennia to create the
    automatic help entry for the command, so make sure to document consistently
    here. Without setting one, the parent's docstring will show (like now).

    """

    # Each Command class implements the following methods, called in this order
    # (only func() is actually required):
    #
    #     - at_pre_cmd(): If this returns anything truthy, execution is aborted.
    #     - parse(): Should perform any extra parsing needed on self.args
    #         and store the result on self.
    #     - func(): Performs the actual work.
    #     - at_post_cmd(): Extra actions, often things done after
    #         every command, like prompts.
    #
    
    def at_post_cmd(self):
        """
        This hook is called after every command execution.
        Shows combat prompt if character is in combat and prompt is enabled.
        """
        caller = self.caller
        
        # Only show prompt for characters in combat with prompt enabled
        if not hasattr(caller, 'ndb'):
            return
            
        handler = getattr(caller.ndb, 'combat_handler', None)
        if not handler or not handler.is_active:
            return
            
        # Check if prompt is disabled (default is on)
        if getattr(caller.db, 'combat_prompt', True) is False:
            return
            
        # Build and send the combat prompt
        self._send_combat_prompt(caller)
    
    def _send_combat_prompt(self, char):
        """
        Send a combat status prompt to a character showing vital information.
        Shows: Blood level, bleeding status, stamina %, and critical organs.
        """
        parts = []
        
        # --- HEALTH STATUS (Blood Level) ---
        blood_level = 100.0
        if hasattr(char, 'medical_state') and char.medical_state:
            blood_level = getattr(char.medical_state, 'blood_level', 100.0)
        
        if blood_level > 75:
            health_color = "|g"
            health_status = "Healthy"
        elif blood_level > 50:
            health_color = "|y"
            health_status = "Wounded"
        elif blood_level > 25:
            health_color = "|r"
            health_status = "Injured"
        else:
            health_color = "|R"
            health_status = "Critical"
        
        parts.append(f"{health_color}Blood: {blood_level:.0f}% ({health_status})|n")
        
        # --- BLEEDING STATUS ---
        is_bleeding = False
        bleed_rate = 0
        if hasattr(char, 'medical_state') and char.medical_state:
            bleed_rate = char.medical_state.calculate_blood_loss_rate()
            is_bleeding = bleed_rate > 0
        
        if is_bleeding and bleed_rate > 0:
            if bleed_rate >= 3:
                parts.append("|R[BLEEDING HEAVILY]|n")
            elif bleed_rate >= 1.5:
                parts.append("|r[BLEEDING]|n")
            else:
                parts.append("|y[bleeding]|n")
        
        # --- STAMINA STATUS ---
        stamina = getattr(char.ndb, "stamina", None)
        if stamina:
            stam_pct = (stamina.stamina_current / stamina.stamina_max * 100) if stamina.stamina_max > 0 else 0
            if stam_pct > 50:
                stam_color = "|g"
            elif stam_pct > 20:
                stam_color = "|y"
            else:
                stam_color = "|r"
            parts.append(f"{stam_color}Stamina: {stam_pct:.0f}%|n")
        
        # --- CRITICAL ORGAN DAMAGE ---
        critical_organs = []
        if hasattr(char, 'medical_state') and char.medical_state:
            for organ_name, organ in char.medical_state.organs.items():
                if hasattr(organ, 'get_functionality_percentage'):
                    functionality = organ.get_functionality_percentage()
                    if functionality < 0.25 and organ.current_hp < organ.max_hp:
                        critical_organs.append(organ_name.replace('_', ' '))
        
        if critical_organs:
            organ_list = ", ".join(critical_organs)
            parts.append(f"|R[CRITICAL: {organ_list}]|n")
        
        # --- SEND THE PROMPT ---
        if parts:
            prompt = " | ".join(parts)
            char.msg(f"|w[Combat]|n {prompt}")


# -------------------------------------------------------------
#
# The default commands inherit from
#
#   evennia.commands.default.muxcommand.MuxCommand.
#
# If you want to make sweeping changes to default commands you can
# uncomment this copy of the MuxCommand parent and add
#
#   COMMAND_DEFAULT_CLASS = "commands.command.MuxCommand"
#
# to your settings file. Be warned that the default commands expect
# the functionality implemented in the parse() method, so be
# careful with what you change.
#
# -------------------------------------------------------------

# from evennia.utils import utils
#
#
# class MuxCommand(Command):
#     """
#     This sets up the basis for a MUX command. The idea
#     is that most other Mux-related commands should just
#     inherit from this and don't have to implement much
#     parsing of their own unless they do something particularly
#     advanced.
#
#     Note that the class's __doc__ string (this text) is
#     used by Evennia to create the automatic help entry for
#     the command, so make sure to document consistently here.
#     """
#     def has_perm(self, srcobj):
#         """
#         This is called by the cmdhandler to determine
#         if srcobj is allowed to execute this command.
#         We just show it here for completeness - we
#         are satisfied using the default check in Command.
#         """
#         return super().has_perm(srcobj)
#
#     def at_pre_cmd(self):
#         """
#         This hook is called before self.parse() on all commands
#         """
#         pass
#
#     def at_post_cmd(self):
#         """
#         This hook is called after the command has finished executing
#         (after self.func()).
#         """
#         pass
#
#     def parse(self):
#         """
#         This method is called by the cmdhandler once the command name
#         has been identified. It creates a new set of member variables
#         that can be later accessed from self.func() (see below)
#
#         The following variables are available for our use when entering this
#         method (from the command definition, and assigned on the fly by the
#         cmdhandler):
#            self.key - the name of this command ('look')
#            self.aliases - the aliases of this cmd ('l')
#            self.permissions - permission string for this command
#            self.help_category - overall category of command
#
#            self.caller - the object calling this command
#            self.cmdstring - the actual command name used to call this
#                             (this allows you to know which alias was used,
#                              for example)
#            self.args - the raw input; everything following self.cmdstring.
#            self.cmdset - the cmdset from which this command was picked. Not
#                          often used (useful for commands like 'help' or to
#                          list all available commands etc)
#            self.obj - the object on which this command was defined. It is often
#                          the same as self.caller.
#
#         A MUX command has the following possible syntax:
#
#           name[ with several words][/switch[/switch..]] arg1[,arg2,...] [[=|,] arg[,..]]
#
#         The 'name[ with several words]' part is already dealt with by the
#         cmdhandler at this point, and stored in self.cmdname (we don't use
#         it here). The rest of the command is stored in self.args, which can
#         start with the switch indicator /.
#
#         This parser breaks self.args into its constituents and stores them in the
#         following variables:
#           self.switches = [list of /switches (without the /)]
#           self.raw = This is the raw argument input, including switches
#           self.args = This is re-defined to be everything *except* the switches
#           self.lhs = Everything to the left of = (lhs:'left-hand side'). If
#                      no = is found, this is identical to self.args.
#           self.rhs: Everything to the right of = (rhs:'right-hand side').
#                     If no '=' is found, this is None.
#           self.lhslist - [self.lhs split into a list by comma]
#           self.rhslist - [list of self.rhs split into a list by comma]
#           self.arglist = [list of space-separated args (stripped, including '=' if it exists)]
#
#           All args and list members are stripped of excess whitespace around the
#           strings, but case is preserved.
#         """
#         raw = self.args
#         args = raw.strip()
#
#         # split out switches
#         switches = []
#         if args and len(args) > 1 and args[0] == "/":
#             # we have a switch, or a set of switches. These end with a space.
#             switches = args[1:].split(None, 1)
#             if len(switches) > 1:
#                 switches, args = switches
#                 switches = switches.split('/')
#             else:
#                 args = ""
#                 switches = switches[0].split('/')
#         arglist = [arg.strip() for arg in args.split()]
#
#         # check for arg1, arg2, ... = argA, argB, ... constructs
#         lhs, rhs = args, None
#         lhslist, rhslist = [arg.strip() for arg in args.split(',')], []
#         if args and '=' in args:
#             lhs, rhs = [arg.strip() for arg in args.split('=', 1)]
#             lhslist = [arg.strip() for arg in lhs.split(',')]
#             rhslist = [arg.strip() for arg in rhs.split(',')]
#
#         # save to object properties:
#         self.raw = raw
#         self.switches = switches
#         self.args = args.strip()
#         self.arglist = arglist
#         self.lhs = lhs
#         self.lhslist = lhslist
#         self.rhs = rhs
#         self.rhslist = rhslist
#
#         # if the class has the account_caller property set on itself, we make
#         # sure that self.caller is always the account if possible. We also create
#         # a special property "character" for the puppeted object, if any. This
#         # is convenient for commands defined on the Account only.
#         if hasattr(self, "account_caller") and self.account_caller:
#             if utils.inherits_from(self.caller, "evennia.objects.objects.DefaultObject"):
#                 # caller is an Object/Character
#                 self.character = self.caller
#                 self.caller = self.caller.account
#             elif utils.inherits_from(self.caller, "evennia.accounts.accounts.DefaultAccount"):
#                 # caller was already an Account
#                 self.character = self.caller.get_puppet(self.session)
#             else:
#                 self.character = None
