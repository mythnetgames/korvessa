"""
Cooking System - Ingredients, Kitchenettes, and Food Items

This module provides typeclasses for the food crafting system:
- Ingredients: One-time use crafting material
- Kitchenette: Crafting station for cooking
- FoodItem: Consumable food or drink created from recipes
"""

from evennia import DefaultObject, AttributeProperty
from typeclasses.objects import ObjectParent


class Ingredients(ObjectParent, DefaultObject):
    """
    Ingredients for cooking. A one-time use item that can be used at a
    Kitchenette to craft food items from approved recipes.
    
    Attributes:
        is_ingredients: True - marks this as cooking ingredients
        quality: Quality level of ingredients (affects final result)
    """
    
    is_ingredients = AttributeProperty(True, autocreate=True)
    quality = AttributeProperty("standard", autocreate=True)  # standard, premium, exotic
    
    def at_object_creation(self):
        """Initialize ingredients."""
        super().at_object_creation()
        self.db.desc = "A package of fresh cooking ingredients, ready to be transformed into a meal."
        self.db.quality = "standard"
    
    def get_display_name(self, looker=None, **kwargs):
        """Return name with quality indicator."""
        quality = getattr(self.db, 'quality', 'standard')
        if quality == "premium":
            return f"|y{self.key}|n"
        elif quality == "exotic":
            return f"|m{self.key}|n"
        return self.key


class Kitchenette(ObjectParent, DefaultObject):
    """
    A cooking station where players can prepare food from approved recipes.
    
    When a player uses 'cook' while at a kitchenette, they can browse
    approved recipes and attempt to create food items.
    
    Attributes:
        is_kitchenette: True - marks this as a cooking station
        kitchen_name: Display name for the kitchen
        kitchen_desc: Description shown when cooking
    """
    
    is_kitchenette = AttributeProperty(True, autocreate=True)
    kitchen_name = AttributeProperty("kitchenette", autocreate=True)
    kitchen_desc = AttributeProperty("A small but functional cooking area.", autocreate=True)
    
    def at_object_creation(self):
        """Initialize kitchenette."""
        super().at_object_creation()
        self.db.desc = "A compact kitchenette with a small stovetop, prep counter, and basic cooking utensils."
    
    def return_appearance(self, looker, **kwargs):
        """Custom appearance showing cooking availability."""
        appearance = super().return_appearance(looker, **kwargs)
        appearance += "\n\n|cType |wcook|c to browse available recipes.|n"
        return appearance


class FoodItem(ObjectParent, DefaultObject):
    """
    A consumable food or drink item created from an approved recipe.
    
    Attributes:
        is_food: True if food, False if drink
        recipe_id: ID of the recipe this was created from
        quality_rating: How well it was made (affects messages)
        consumes_remaining: How many bites/sips left (default 4)
        
        # Display properties
        food_name: Name of the food/drink
        food_desc: Description when examined
        food_taste: Description of the taste
        food_smell: Description of the smell
        
        # Consumption messages (support pronoun substitution)
        msg_eat_self: Message to eater (1st person)
        msg_eat_others: Message to others (3rd person)
        msg_finish_self: Message when finishing (1st person)
        msg_finish_others: Message when others see finish (3rd person)
        
        # Creator info
        creator_dbref: Who made this
        created_at: When it was made
    """
    
    is_food_item = AttributeProperty(True, autocreate=True)
    is_food = AttributeProperty(True, autocreate=True)  # True = food, False = drink
    recipe_id = AttributeProperty(None, autocreate=True)
    quality_rating = AttributeProperty("average", autocreate=True)  # poor, average, good, excellent
    consumes_remaining = AttributeProperty(4, autocreate=True)  # 4 bites/sips by default
    
    # Display properties
    food_name = AttributeProperty("", autocreate=True)
    food_desc = AttributeProperty("", autocreate=True)
    food_taste = AttributeProperty("", autocreate=True)
    food_smell = AttributeProperty("", autocreate=True)
    
    # Consumption messages
    msg_eat_self = AttributeProperty("", autocreate=True)
    msg_eat_others = AttributeProperty("", autocreate=True)
    msg_finish_self = AttributeProperty("", autocreate=True)
    msg_finish_others = AttributeProperty("", autocreate=True)
    
    # Creator tracking
    creator_dbref = AttributeProperty(None, autocreate=True)
    created_at = AttributeProperty(None, autocreate=True)
    
    def at_object_creation(self):
        """Initialize food item."""
        super().at_object_creation()
    
    def get_display_name(self, looker=None, **kwargs):
        """Return name with quality color coding."""
        quality = self.quality_rating
        name = self.food_name or self.key
        
        if quality == "poor":
            return f"|=l{name}|n"  # Gray for poor
        elif quality == "good":
            return f"|g{name}|n"  # Green for good
        elif quality == "excellent":
            return f"|y{name}|n"  # Yellow/gold for excellent
        return name  # Normal for average
    
    def return_appearance(self, looker, **kwargs):
        """Custom appearance with smell and type."""
        string = f"|c{self.get_display_name(looker)}|n"
        
        # Add food/drink indicator
        item_type = "food" if self.is_food else "drink"
        string += f"\n|w({item_type.capitalize()})|n"
        
        # Description
        if self.food_desc:
            string += f"\n\n{self.food_desc}"
        elif self.db.desc:
            string += f"\n\n{self.db.desc}"
        
        # Smell
        if self.food_smell:
            string += f"\n\n|cSmell:|n {self.food_smell}"
        
        # Quality indicator
        quality_descs = {
            "poor": "This looks like it was made by someone who had no idea what they were doing.",
            "average": "This looks reasonably well-prepared.",
            "good": "This looks professionally prepared.",
            "excellent": "This looks like it was crafted by a master chef."
        }
        string += f"\n\n|w{quality_descs.get(self.quality_rating, '')}|n"
        
        # Show remaining consumes
        remaining = self.consumes_remaining
        action = "bite" if self.is_food else "sip"
        if remaining > 1:
            string += f"\n{remaining} {action}s remaining.|n"
        elif remaining == 1:
            string += f"\n|y1 {action} remaining.|n"
        
        # Consumption hint
        action = "eat" if self.is_food else "drink"
        string += f"\n\nType |w{action} {self.key} to consume.|n"
        
        return string


# =============================================================================
# RECIPE STORAGE SYSTEM
# =============================================================================

# Global recipe storage - stored on a persistent script
# Structure of a recipe:
# {
#     "id": int,
#     "name": str,
#     "is_food": bool,  # True = food, False = drink
#     "description": str,
#     "taste": str,
#     "smell": str,
#     "msg_eat_self": str,  # 1st person consumption
#     "msg_eat_others": str,  # 3rd person consumption (others see)
#     "msg_finish_self": str,  # 1st person finishing
#     "msg_finish_others": str,  # 3rd person finishing
#     "difficulty": int,  # 0-100 cooking skill required
#     "status": str,  # "pending", "approved", "rejected"
#     "creator_dbref": str,
#     "creator_name": str,
#     "created_at": datetime,
#     "approved_by": str,
#     "approved_at": datetime,
#     "keywords": list,  # Searchable keywords
# }

def get_recipe_storage():
    """
    Get or create the global recipe storage script.
    
    Returns:
        Script: The recipe storage script
    """
    from evennia.scripts.models import ScriptDB
    from evennia import create_script
    
    # Try to find existing storage
    storage = ScriptDB.objects.filter(db_key="recipe_storage").first()
    if storage:
        return storage
    
    # Create new storage script
    from evennia.scripts.scripts import DefaultScript
    storage = create_script(
        DefaultScript,
        key="recipe_storage",
        persistent=True,
        desc="Global storage for cooking recipes"
    )
    storage.db.recipes = []
    storage.db.pending_recipes = []
    storage.db.next_recipe_id = 1
    return storage


def get_all_approved_recipes():
    """Get all approved recipes."""
    storage = get_recipe_storage()
    return [r for r in (storage.db.recipes or []) if r.get("status") == "approved"]


def get_pending_recipes():
    """Get all recipes pending approval."""
    storage = get_recipe_storage()
    return storage.db.pending_recipes or []


def get_recipe_by_id(recipe_id):
    """Get a specific recipe by ID."""
    storage = get_recipe_storage()
    
    # Check approved recipes
    for recipe in (storage.db.recipes or []):
        if recipe.get("id") == recipe_id:
            return recipe
    
    # Check pending recipes
    for recipe in (storage.db.pending_recipes or []):
        if recipe.get("id") == recipe_id:
            return recipe
    
    return None


def add_pending_recipe(recipe_data):
    """
    Add a new recipe to the pending queue.
    
    Args:
        recipe_data (dict): Recipe information
        
    Returns:
        int: The assigned recipe ID
    """
    storage = get_recipe_storage()
    
    # Assign ID
    recipe_id = storage.db.next_recipe_id or 1
    storage.db.next_recipe_id = recipe_id + 1
    
    recipe_data["id"] = recipe_id
    recipe_data["status"] = "pending"
    
    # Add to pending queue
    pending = storage.db.pending_recipes or []
    pending.append(recipe_data)
    storage.db.pending_recipes = pending
    
    return recipe_id


def approve_recipe(recipe_id, approver, difficulty):
    """
    Approve a pending recipe.
    
    Args:
        recipe_id (int): ID of recipe to approve
        approver: Character/Account who approved
        difficulty (int): Difficulty rating 0-100
        
    Returns:
        bool: True if approved, False if not found
    """
    from datetime import datetime
    
    storage = get_recipe_storage()
    pending = storage.db.pending_recipes or []
    
    for i, recipe in enumerate(pending):
        if recipe.get("id") == recipe_id:
            # Update recipe
            recipe["status"] = "approved"
            recipe["difficulty"] = difficulty
            recipe["approved_by"] = approver.key if hasattr(approver, 'key') else str(approver)
            recipe["approved_at"] = datetime.now()
            
            # Move to approved list
            recipes = storage.db.recipes or []
            recipes.append(recipe)
            storage.db.recipes = recipes
            
            # Remove from pending
            pending.pop(i)
            storage.db.pending_recipes = pending
            
            return True
    
    return False


def reject_recipe(recipe_id, reason=""):
    """
    Reject a pending recipe.
    
    Args:
        recipe_id (int): ID of recipe to reject
        reason (str): Reason for rejection
        
    Returns:
        bool: True if rejected, False if not found
    """
    storage = get_recipe_storage()
    pending = storage.db.pending_recipes or []
    
    for i, recipe in enumerate(pending):
        if recipe.get("id") == recipe_id:
            recipe["status"] = "rejected"
            recipe["rejection_reason"] = reason
            pending.pop(i)
            storage.db.pending_recipes = pending
            return True
    
    return False


def search_recipes(query, approved_only=True):
    """
    Search recipes by keyword.
    
    Args:
        query (str): Search query
        approved_only (bool): Only search approved recipes
        
    Returns:
        list: Matching recipes
    """
    storage = get_recipe_storage()
    query_lower = query.lower()
    results = []
    
    recipes = storage.db.recipes or []
    if not approved_only:
        recipes = recipes + (storage.db.pending_recipes or [])
    
    for recipe in recipes:
        if approved_only and recipe.get("status") != "approved":
            continue
        
        # Search in name
        if query_lower in recipe.get("name", "").lower():
            results.append(recipe)
            continue
        
        # Search in keywords
        keywords = recipe.get("keywords", [])
        if any(query_lower in kw.lower() for kw in keywords):
            results.append(recipe)
            continue
        
        # Search in description
        if query_lower in recipe.get("description", "").lower():
            results.append(recipe)
    
    return results


# =============================================================================
# DIFFICULTY SCALE REFERENCE
# =============================================================================

DIFFICULTY_SCALE = """
|c=== Cooking Difficulty Scale (0-100) ===|n

|w0-20:|n   |gNovice|n - Simple preparations anyone can make
          Examples: Toast, scrambled eggs, instant noodles, sandwiches
          
|w21-45:|n  |yCompetent|n - Home cooking level, requires some skill
          Examples: Stir fry, pasta dishes, simple soups, basic baking
          
|w46-75:|n  |mSeasoned|n - Professional level cooking
          Examples: Complex sauces, multi-course meals, pastries, sushi
          
|w76-89:|n  |rAdvanced|n - High-end restaurant quality
          Examples: Molecular gastronomy, intricate desserts, fusion cuisine
          
|w90-100:|n |R|*Mastery|n - World-class chef level
          Examples: Michelin-star dishes, avant-garde techniques

|cTip:|n Consider the complexity of preparation, number of techniques involved,
and potential for things to go wrong when setting difficulty.
"""
