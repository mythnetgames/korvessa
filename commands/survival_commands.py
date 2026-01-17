"""
Eat and Drink Commands

Commands for consuming food and drink items, integrated with the survival system.
"""

from evennia import Command


class CmdEat(Command):
    """
    Eat food to satisfy hunger.
    
    Usage:
        eat <food>
        
    Examples:
        eat bread
        eat stew
    """
    
    key = "eat"
    aliases = ["consume", "devour"]
    help_category = "General"
    
    def func(self):
        """Execute the eat command."""
        caller = self.caller
        
        if not self.args:
            caller.msg("Eat what? Usage: eat <food>")
            return
        
        # Search for the food item
        food_name = self.args.strip()
        food = caller.search(food_name, location=caller, quiet=True)
        
        if not food:
            caller.msg(f"You don't have '{food_name}'.")
            return
        
        if len(food) > 1:
            caller.msg(f"Multiple items match '{food_name}'. Be more specific.")
            return
        
        food = food[0]
        
        # Check if it's actually food
        is_food_item = getattr(food, 'is_food_item', False) or getattr(food.db, 'is_food_item', False)
        is_food = getattr(food, 'is_food', True)
        if hasattr(food.db, 'is_food'):
            is_food = food.db.is_food
        
        if not is_food_item:
            caller.msg(f"You can't eat {food.get_display_name(caller)}.")
            return
        
        if not is_food:
            caller.msg(f"{food.get_display_name(caller)} is a drink, not food. Try 'drink' instead.")
            return
        
        # Get food properties
        consumes_remaining = getattr(food, 'consumes_remaining', 1)
        if hasattr(food.db, 'consumes_remaining'):
            consumes_remaining = food.db.consumes_remaining
        
        if consumes_remaining <= 0:
            caller.msg(f"{food.get_display_name(caller)} is empty.")
            return
        
        # Check if nutritious
        is_nutritious = getattr(food.db, 'nutritious', False)
        
        # Get consumption messages
        msg_self = getattr(food.db, 'msg_eat_self', None)
        msg_others = getattr(food.db, 'msg_eat_others', None)
        msg_finish_self = getattr(food.db, 'msg_finish_self', None)
        msg_finish_others = getattr(food.db, 'msg_finish_others', None)
        
        food_taste = getattr(food.db, 'food_taste', None)
        
        # Consume one bite
        consumes_remaining -= 1
        if hasattr(food, 'consumes_remaining'):
            food.consumes_remaining = consumes_remaining
        food.db.consumes_remaining = consumes_remaining
        
        # Record the meal in survival system
        from world.survival.core import record_meal
        meal_result = record_meal(caller, nutritious=is_nutritious)
        
        # Display messages
        is_finished = consumes_remaining <= 0
        
        if is_finished:
            # Finishing messages
            if msg_finish_self:
                caller.msg(self._process_message(msg_finish_self, caller, food))
            else:
                caller.msg(f"You finish eating {food.get_display_name(caller)}.")
            
            if msg_finish_others:
                caller.location.msg_contents(
                    self._process_message(msg_finish_others, caller, food),
                    exclude=caller
                )
            else:
                caller.location.msg_contents(
                    f"{caller.get_display_name()} finishes eating {food.get_display_name()}.",
                    exclude=caller
                )
            
            # Destroy the food item
            food.delete()
        else:
            # Regular eating messages
            if msg_self:
                caller.msg(self._process_message(msg_self, caller, food))
            else:
                caller.msg(f"You take a bite of {food.get_display_name(caller)}.")
            
            if food_taste:
                caller.msg(f"|c{food_taste}|n")
            
            if msg_others:
                caller.location.msg_contents(
                    self._process_message(msg_others, caller, food),
                    exclude=caller
                )
            else:
                caller.location.msg_contents(
                    f"{caller.get_display_name()} takes a bite of {food.get_display_name()}.",
                    exclude=caller
                )
            
            # Show remaining
            if consumes_remaining == 1:
                caller.msg(f"|y(1 bite remaining)|n")
            else:
                caller.msg(f"|=l({consumes_remaining} bites remaining)|n")
        
        # Show nutrition bonus message
        if is_nutritious and meal_result.get("nutrition_bonus"):
            caller.msg("|gYou feel nourished! Health bonus active for 2 hours.|n")
            if meal_result.get("helped_sober"):
                caller.msg("|gThe nutritious food helps clear your head.|n")
    
    def _process_message(self, msg, caller, food):
        """Process pronoun substitution in messages."""
        # Simple substitution - can be expanded
        msg = msg.replace("{name}", caller.get_display_name())
        msg = msg.replace("{food}", food.get_display_name())
        return msg


class CmdDrink(Command):
    """
    Drink a beverage to satisfy thirst.
    
    Usage:
        drink <beverage>
        
    Examples:
        drink water
        drink ale
        drink wine
        
    Drinking water or non-alcoholic beverages satisfies thirst.
    Alcoholic drinks cause intoxication with escalating effects.
    """
    
    key = "drink"
    aliases = ["sip", "quaff", "imbibe"]
    help_category = "General"
    
    def func(self):
        """Execute the drink command."""
        caller = self.caller
        
        if not self.args:
            caller.msg("Drink what? Usage: drink <beverage>")
            return
        
        # Search for the drink item
        drink_name = self.args.strip()
        drink = caller.search(drink_name, location=caller, quiet=True)
        
        if not drink:
            caller.msg(f"You don't have '{drink_name}'.")
            return
        
        if len(drink) > 1:
            caller.msg(f"Multiple items match '{drink_name}'. Be more specific.")
            return
        
        drink = drink[0]
        
        # Check if it's actually a drink
        is_food_item = getattr(drink, 'is_food_item', False) or getattr(drink.db, 'is_food_item', False)
        is_food = getattr(drink, 'is_food', True)
        if hasattr(drink.db, 'is_food'):
            is_food = drink.db.is_food
        
        if not is_food_item:
            caller.msg(f"You can't drink {drink.get_display_name(caller)}.")
            return
        
        if is_food:
            caller.msg(f"{drink.get_display_name(caller)} is food, not a drink. Try 'eat' instead.")
            return
        
        # Get drink properties
        consumes_remaining = getattr(drink, 'consumes_remaining', 1)
        if hasattr(drink.db, 'consumes_remaining'):
            consumes_remaining = drink.db.consumes_remaining
        
        if consumes_remaining <= 0:
            caller.msg(f"{drink.get_display_name(caller)} is empty.")
            return
        
        # Check if alcoholic
        is_alcohol = getattr(drink.db, 'is_alcohol', False)
        alcohol_strength = getattr(drink.db, 'alcohol_strength', 10)  # Default strength
        
        # Get consumption messages
        msg_self = getattr(drink.db, 'msg_eat_self', None)  # Uses same field
        msg_others = getattr(drink.db, 'msg_eat_others', None)
        msg_finish_self = getattr(drink.db, 'msg_finish_self', None)
        msg_finish_others = getattr(drink.db, 'msg_finish_others', None)
        
        drink_taste = getattr(drink.db, 'food_taste', None)
        
        # Consume one sip
        consumes_remaining -= 1
        if hasattr(drink, 'consumes_remaining'):
            drink.consumes_remaining = consumes_remaining
        drink.db.consumes_remaining = consumes_remaining
        
        # Record the drink in survival system
        from world.survival.core import record_drink, get_intoxication_tier, INTOXICATION_TIERS
        drink_result = record_drink(
            caller, 
            is_alcohol=is_alcohol, 
            alcohol_strength=alcohol_strength if is_alcohol else 0
        )
        
        # Display messages
        is_finished = consumes_remaining <= 0
        
        if is_finished:
            # Finishing messages
            if msg_finish_self:
                caller.msg(self._process_message(msg_finish_self, caller, drink))
            else:
                caller.msg(f"You finish drinking {drink.get_display_name(caller)}.")
            
            if msg_finish_others:
                caller.location.msg_contents(
                    self._process_message(msg_finish_others, caller, drink),
                    exclude=caller
                )
            else:
                caller.location.msg_contents(
                    f"{caller.get_display_name()} finishes drinking {drink.get_display_name()}.",
                    exclude=caller
                )
            
            # Destroy the drink item
            drink.delete()
        else:
            # Regular drinking messages
            if msg_self:
                caller.msg(self._process_message(msg_self, caller, drink))
            else:
                caller.msg(f"You take a sip of {drink.get_display_name(caller)}.")
            
            if drink_taste:
                caller.msg(f"|c{drink_taste}|n")
            
            if msg_others:
                caller.location.msg_contents(
                    self._process_message(msg_others, caller, drink),
                    exclude=caller
                )
            else:
                caller.location.msg_contents(
                    f"{caller.get_display_name()} takes a sip of {drink.get_display_name()}.",
                    exclude=caller
                )
            
            # Show remaining
            if consumes_remaining == 1:
                caller.msg(f"|y(1 sip remaining)|n")
            else:
                caller.msg(f"|=l({consumes_remaining} sips remaining)|n")
        
        # Show alcohol effects
        if is_alcohol and drink_result.get("tier_changed"):
            new_tier = drink_result.get("new_tier", "sober")
            tier_data = INTOXICATION_TIERS.get(new_tier, {})
            description = tier_data.get("description", "affected")
            
            if new_tier == "tipsy":
                caller.msg("|yYou're starting to feel a pleasant warmth.|n")
            elif new_tier == "buzzed":
                caller.msg("|yThe alcohol is going to your head. You feel buzzed.|n")
            elif new_tier == "drunk":
                caller.msg("|rYou're definitely drunk now. The world sways slightly.|n")
            elif new_tier == "very_drunk":
                caller.msg("|rYou're very drunk. Standing straight is becoming a challenge.|n")
            elif new_tier == "wasted":
                caller.msg("|R[WARNING]|r You're completely wasted. Your liver aches.|n")
            elif new_tier == "alcohol_poisoning":
                caller.msg("|R[DANGER]|r You feel sick. You may have alcohol poisoning!|n")
    
    def _process_message(self, msg, caller, drink):
        """Process pronoun substitution in messages."""
        msg = msg.replace("{name}", caller.get_display_name())
        msg = msg.replace("{drink}", drink.get_display_name())
        msg = msg.replace("{food}", drink.get_display_name())  # Some use {food}
        return msg


class CmdSurvivalStatus(Command):
    """
    Check your hunger, thirst, and intoxication status.
    
    Usage:
        status
        survival
        
    Shows your current hunger, thirst, intoxication level,
    and any active effects.
    """
    
    key = "survival"
    aliases = ["hungerstatus", "thirst", "intoxication"]
    help_category = "General"
    
    def func(self):
        """Display survival status."""
        caller = self.caller
        
        from world.survival.core import (
            check_survival_effects, 
            get_nutrition_bonus_remaining,
            INTOXICATION_TIERS
        )
        
        effects = check_survival_effects(caller)
        
        lines = ["|c=== Survival Status ===|n"]
        
        # Hunger
        if effects["starving"]:
            lines.append("|r[STARVING]|n You are desperately hungry!")
        elif effects["hungry"]:
            lines.append("|y[HUNGRY]|n You could use a meal.")
        else:
            lines.append("|g[FED]|n Your stomach is satisfied.")
        
        # Thirst
        if effects["dehydrated"]:
            lines.append("|r[DEHYDRATED]|n You are severely dehydrated!")
        elif effects["thirsty"]:
            lines.append("|y[THIRSTY]|n You could use a drink.")
        else:
            lines.append("|g[HYDRATED]|n You are well hydrated.")
        
        # Intoxication
        intox_level = effects["intoxication_level"]
        intox_tier = effects["intoxication_tier"]
        
        if intox_tier == "sober":
            lines.append("|g[SOBER]|n You are completely sober.")
        else:
            tier_data = INTOXICATION_TIERS.get(intox_tier, {})
            description = tier_data.get("description", intox_tier)
            
            if intox_tier in ["wasted", "alcohol_poisoning"]:
                lines.append(f"|r[{intox_tier.upper()}]|n You are {description}!")
            elif intox_tier in ["drunk", "very_drunk"]:
                lines.append(f"|y[{intox_tier.upper()}]|n You are {description}.")
            else:
                lines.append(f"|c[{intox_tier.upper()}]|n You are {description}.")
        
        # Nutrition bonus
        if effects["has_nutrition_bonus"]:
            remaining = get_nutrition_bonus_remaining(caller)
            minutes = int(remaining / 60)
            lines.append(f"|g[NOURISHED]|n Health bonus active ({minutes} minutes remaining)")
        
        # Active maluses
        if effects["stat_maluses"]:
            malus_parts = []
            for stat, amount in effects["stat_maluses"].items():
                if amount != 0:
                    malus_parts.append(f"{stat.capitalize()} {amount:+d}")
            if malus_parts:
                lines.append(f"|y[STAT EFFECTS]|n {', '.join(malus_parts)}")
        
        # Stamina effects
        if effects["stamina_effects"]:
            if "lowered_stamina_pool" in effects["stamina_effects"]:
                lines.append("|r[STAMINA]|n Maximum stamina reduced from dehydration")
            if "lowered_stamina_regen" in effects["stamina_effects"]:
                lines.append("|r[STAMINA]|n Stamina regeneration severely reduced")
            elif "reduced_stamina_regen" in effects["stamina_effects"]:
                lines.append("|y[STAMINA]|n Stamina regeneration reduced from thirst")
        
        # Health effects
        if "lowered_max_health" in effects["health_effects"]:
            lines.append("|r[HEALTH]|n Maximum health reduced from starvation")
        
        caller.msg("\n".join(lines))
