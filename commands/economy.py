"""
Economy Commands

Player and admin commands for the economy system.
"""

import time
from evennia import Command, CmdSet
from evennia.utils.search import search_object
from world.economy.constants import (
    PAYDAY_PAYOUT,
    PAYDAY_PERIOD_SECONDS,
    CURRENCY_SYMBOL,
)
from world.economy.utils import (
    now_ts,
    format_time_remaining,
    can_claim_payday,
    format_currency,
)


class CmdCount(Command):
    """
    Count your cash on hand.
    
    Usage:
        count
        
    Shows how much cash you have on your person.
    """
    
    key = "count"
    aliases = ["cash", "money"]
    locks = "cmd:all()"
    help_category = "Economy"
    
    def func(self):
        caller = self.caller
        cash = caller.cash_on_hand or 0
        caller.msg(f"Cash on hand: {CURRENCY_SYMBOL}{cash:,}")


class CmdDropMoney(Command):
    """
    Drop some cash on the ground.
    
    Usage:
        dropmoney <amount>
        dropm <amount>
        drop money <amount>
        
    Examples:
        dropmoney 50
        dropm 100
        drop money 25
        
    Drops the specified amount of cash as a pile on the floor.
    """
    
    key = "dropmoney"
    aliases = ["dropm", "drop money"]
    locks = "cmd:all()"
    help_category = "Economy"
    
    def func(self):
        caller = self.caller
        
        if not self.args:
            caller.msg("Usage: dropmoney <amount>")
            return
        
        # Parse amount
        try:
            amount = int(self.args.strip())
        except ValueError:
            caller.msg("Amount must be a number.")
            return
        
        if amount <= 0:
            caller.msg("Amount must be greater than zero.")
            return
        
        # Check if caller has enough cash
        cash = caller.cash_on_hand or 0
        if amount > cash:
            caller.msg("You don't have that much cash on hand.")
            return
        
        # Deduct from cash on hand
        caller.cash_on_hand = cash - amount
        
        # Create money pile
        from typeclasses.money_pile import create_money_pile
        pile = create_money_pile(caller.location, amount, merge=True)
        
        # Messages
        caller.msg(f"You drop {CURRENCY_SYMBOL}{amount:,} on the floor.")
        caller.location.msg_contents(
            f"{caller.key} drops some cash on the floor.",
            exclude=[caller]
        )


class CmdGetMoney(Command):
    """
    Pick up cash from the ground.
    
    Usage:
        getmoney
        get money
        take money
        take cash
        
    Picks up a pile of cash from the ground and adds it to your cash on hand.
    If there are multiple piles, picks up the first one found.
    """
    
    key = "getmoney"
    aliases = ["get money", "take money", "take cash", "get cash", "pickup money", "pickup cash"]
    locks = "cmd:all()"
    help_category = "Economy"
    
    def func(self):
        caller = self.caller
        
        # Find money piles in the room
        piles = []
        for obj in caller.location.contents:
            if obj.tags.has("money_pile", category="economy"):
                piles.append(obj)
        
        if not piles:
            caller.msg("There is no cash here to pick up.")
            return
        
        # Pick up the first pile
        pile = piles[0]
        value = pile.value or 0
        
        if value <= 0:
            pile.delete()
            caller.msg("That pile is empty.")
            return
        
        # Add to cash on hand
        current = caller.cash_on_hand or 0
        caller.cash_on_hand = current + value
        
        # Message
        caller.msg(f"You pick up {CURRENCY_SYMBOL}{value:,}.")
        caller.location.msg_contents(
            f"{caller.key} picks up some cash.",
            exclude=[caller]
        )
        
        # Delete the pile
        pile.delete()


class CmdPayday(Command):
    """
    Claim your weekly payday.
    
    Usage:
        payday
        
    Every 7 days, you can claim a payday of 1,000 dollars.
    The first payday is available 7 days after character creation.
    If you miss a payday, you can still claim it later without
    losing the next one.
    """
    
    key = "payday"
    locks = "cmd:all()"
    help_category = "Economy"
    
    def func(self):
        caller = self.caller
        current_time = now_ts()
        
        # Initialize payday anchor if not set
        anchor = caller.payday_anchor_ts
        if not anchor:
            # Use current time as anchor for legacy characters
            anchor = current_time
            caller.payday_anchor_ts = anchor
        
        last_claim = caller.last_payday_claim_ts
        
        # Check if payday can be claimed
        can_claim, next_due, seconds_until = can_claim_payday(
            anchor, last_claim, current_time, PAYDAY_PERIOD_SECONDS
        )
        
        if not can_claim:
            # Show time remaining
            time_str = format_time_remaining(seconds_until)
            caller.msg(f"Your next payday is in {time_str}.")
            return
        
        # Claim payday
        payout = PAYDAY_PAYOUT
        current_cash = caller.cash_on_hand or 0
        caller.cash_on_hand = current_cash + payout
        caller.last_payday_claim_ts = current_time
        
        caller.msg(f"Payday! You receive {CURRENCY_SYMBOL}{payout:,}.")
        caller.msg(f"Cash on hand: {CURRENCY_SYMBOL}{caller.cash_on_hand:,}")


class CmdSpawnCash(Command):
    """
    Spawn cash into a character's hands (admin command).
    
    Usage:
        spawncash <amount>
        spawncash <amount> <target>
        
    Examples:
        spawncash 1000
        spawncash 500 Bob
        
    Adds the specified amount to the target's cash on hand.
    If no target is specified, adds to your own cash.
    """
    
    key = "spawncash"
    aliases = ["givecash", "addcash"]
    locks = "cmd:perm(Builder)"
    help_category = "Admin"
    
    def func(self):
        caller = self.caller
        
        if not self.args:
            caller.msg("Usage: spawncash <amount> [<target>]")
            return
        
        args = self.args.strip().split()
        
        # Parse amount
        try:
            amount = int(args[0])
        except ValueError:
            caller.msg("Amount must be a number.")
            return
        
        if amount <= 0:
            caller.msg("Amount must be greater than zero.")
            return
        
        # Find target
        if len(args) > 1:
            target_name = " ".join(args[1:])
            targets = search_object(target_name)
            
            # Filter to characters
            target = None
            for t in targets:
                if t.is_typeclass("typeclasses.characters.Character"):
                    target = t
                    break
            
            if not target:
                caller.msg(f"Character '{target_name}' not found.")
                return
        else:
            target = caller
        
        # Add cash
        current = target.cash_on_hand or 0
        target.cash_on_hand = current + amount
        
        if target == caller:
            caller.msg(f"You spawn {CURRENCY_SYMBOL}{amount:,} into your hands.")
        else:
            caller.msg(f"You spawn {CURRENCY_SYMBOL}{amount:,} into {target.key}'s hands.")
            target.msg(f"You receive {CURRENCY_SYMBOL}{amount:,}.")


class CmdSpawnMoneyPile(Command):
    """
    Spawn a money pile on the ground (admin command).
    
    Usage:
        spawnmoneypile <amount>
        
    Creates a pile of cash in the current room for testing.
    """
    
    key = "spawnmoneypile"
    aliases = ["spawnpile"]
    locks = "cmd:perm(Builder)"
    help_category = "Admin"
    
    def func(self):
        caller = self.caller
        
        if not self.args:
            caller.msg("Usage: spawnmoneypile <amount>")
            return
        
        # Parse amount
        try:
            amount = int(self.args.strip())
        except ValueError:
            caller.msg("Amount must be a number.")
            return
        
        if amount <= 0:
            caller.msg("Amount must be greater than zero.")
            return
        
        # Create money pile
        from typeclasses.money_pile import create_money_pile
        pile = create_money_pile(caller.location, amount, merge=False)
        
        caller.msg(f"You spawn a pile of {CURRENCY_SYMBOL}{amount:,} on the ground.")


class CmdSetPaydayAnchor(Command):
    """
    Set a character's payday anchor time (admin command).
    
    Usage:
        setpaydayanchor <target>
        setpaydayanchor <target> = now
        setpaydayanchor <target> = <days ago>
        
    Examples:
        setpaydayanchor Bob = now
        setpaydayanchor Bob = 7
        
    Sets the payday anchor. Use a number to set it that many days ago,
    or 'now' to set it to the current time.
    """
    
    key = "setpaydayanchor"
    locks = "cmd:perm(Builder)"
    help_category = "Admin"
    
    def func(self):
        caller = self.caller
        
        if not self.args:
            caller.msg("Usage: setpaydayanchor <target> [= now|<days ago>]")
            return
        
        if "=" in self.args:
            target_name, value = self.args.split("=", 1)
            target_name = target_name.strip()
            value = value.strip().lower()
        else:
            target_name = self.args.strip()
            value = "now"
        
        # Find target
        targets = search_object(target_name)
        target = None
        for t in targets:
            if t.is_typeclass("typeclasses.characters.Character"):
                target = t
                break
        
        if not target:
            caller.msg(f"Character '{target_name}' not found.")
            return
        
        # Parse value
        current_time = now_ts()
        if value == "now":
            new_anchor = current_time
        else:
            try:
                days_ago = float(value)
                new_anchor = current_time - (days_ago * 86400)
            except ValueError:
                caller.msg("Value must be 'now' or a number of days.")
                return
        
        target.payday_anchor_ts = new_anchor
        target.last_payday_claim_ts = None  # Reset claims
        
        caller.msg(f"Set {target.key}'s payday anchor. Next payday in 7 days from anchor.")


class EconomyCmdSet(CmdSet):
    """Command set for economy commands."""
    
    key = "economy"
    
    def at_cmdset_creation(self):
        self.add(CmdCount())
        self.add(CmdDropMoney())
        self.add(CmdGetMoney())
        self.add(CmdPayday())
        self.add(CmdSpawnCash())
        self.add(CmdSpawnMoneyPile())
        self.add(CmdSetPaydayAnchor())
