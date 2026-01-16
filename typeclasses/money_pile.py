"""
Money Pile Typeclass

Physical money objects that can be dropped and picked up.
"""

from evennia.objects.objects import DefaultObject
from evennia.typeclasses.attributes import AttributeProperty
from world.economy.constants import MONEY_PILE_KEY, MONEY_PILE_ALIASES, CURRENCY_SYMBOL


class MoneyPile(DefaultObject):
    """
    A pile of cash on the ground.
    
    Attributes:
        value: The amount of money in the pile
    """
    
    value = AttributeProperty(0, category="economy", autocreate=True)
    
    def at_object_creation(self):
        """Called when the money pile is first created."""
        super().at_object_creation()
        
        # Set key and aliases
        self.key = MONEY_PILE_KEY
        for alias in MONEY_PILE_ALIASES:
            if alias != self.key:
                self.aliases.add(alias)
        
        # Set default description
        self.db.desc = "A pile of cash."
        
        # Prevent wearing/equipping
        self.locks.add("wear:false()")
        self.locks.add("wield:false()")
        
        # Tag for easy lookup
        self.tags.add("money_pile", category="economy")
    
    def get_display_name(self, looker=None, **kwargs):
        """Return the display name with value hint."""
        if self.value > 0:
            return f"pile of cash ({CURRENCY_SYMBOL}{self.value:,})"
        return "pile of cash"
    
    def return_appearance(self, looker, **kwargs):
        """Return the appearance when looked at."""
        desc = f"A small pile of cash.\nIt looks like about {CURRENCY_SYMBOL}{self.value:,}."
        return desc
    
    def at_get(self, getter, **kwargs):
        """
        Called when someone picks up this money pile.
        Add the value to their cash_on_hand and delete the pile.
        """
        if hasattr(getter, "db") and hasattr(getter.db, "cash_on_hand"):
            current = getter.db.cash_on_hand or 0
            getter.db.cash_on_hand = current + self.value
            getter.msg(f"You pick up {CURRENCY_SYMBOL}{self.value:,}.")
            
            # Notify the room
            if getter.location:
                getter.location.msg_contents(
                    f"{getter.key} picks up some cash.",
                    exclude=[getter]
                )
            
            # Delete the pile after pickup
            self.delete()
            return False  # Prevent normal get behavior (item going to inventory)
        
        return True  # Allow normal get if not a character


def create_money_pile(location, value, merge=True):
    """
    Create a money pile in the specified location.
    
    Args:
        location: Room to create the pile in
        value: Amount of money in the pile
        merge: If True, merge with existing pile instead of creating new one
        
    Returns:
        MoneyPile: The created or merged pile
    """
    from evennia import create_object
    
    if merge:
        # Check for existing money piles in the room
        for obj in location.contents:
            if obj.is_typeclass("typeclasses.money_pile.MoneyPile"):
                obj.value = (obj.value or 0) + value
                return obj
    
    # Create new pile
    pile = create_object(
        MoneyPile,
        key=MONEY_PILE_KEY,
        location=location
    )
    pile.value = value
    
    return pile
