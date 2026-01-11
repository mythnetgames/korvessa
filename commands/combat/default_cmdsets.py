from commands.combat.core_actions import CmdDummyReset

class CombatCmdSet(CmdSet):
    def at_cmdset_creation(self):
        self.add(CmdDummyReset())