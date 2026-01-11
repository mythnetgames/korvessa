"""
Cooking Commands - Food crafting system

Commands for designing recipes, cooking food, and admin approval.

Player Commands:
- design: Start the recipe design menu
- cook: Cook a recipe at a kitchenette
- eat/drink: Consume food/drinks
- taste: Get a preview of food taste
- smell: Smell food/drink

Admin Commands:
- spawnkitchen: Create a kitchenette
- spawningredients: Create ingredients for testing
- recipes: View and manage recipe queue
- approverecipe: Approve a pending recipe
- rejectrecipe: Reject a pending recipe
"""

from evennia import Command, create_object
from evennia.utils.evmenu import EvMenu
from evennia.utils.search import search_object
from datetime import datetime
from random import randint
import math

from typeclasses.cooking import (
    Ingredients, Kitchenette, FoodItem,
    get_recipe_storage, get_all_approved_recipes, get_pending_recipes,
    get_recipe_by_id, add_pending_recipe, approve_recipe, reject_recipe,
    search_recipes, DIFFICULTY_SCALE, get_next_available_recipe_id
)


# =============================================================================
# PRONOUN SUBSTITUTION HELPER
# =============================================================================

def substitute_pronouns(text, char):
    """
    Substitute pronoun placeholders in text.
    
    Placeholders:
        %s - subjective (he/she/they)
        %o - objective (him/her/them)
        %p - possessive (his/her/their)
        %a - absolute possessive (his/hers/theirs)
        %r - reflexive (himself/herself/themselves)
        %n - character name
    """
    if not text or not char:
        return text
    
    # Get character's gender/pronouns
    gender = getattr(char.db, 'gender', 'ambiguous') or 'ambiguous'
    gender = gender.lower()
    
    pronoun_map = {
        'male': {'s': 'he', 'o': 'him', 'p': 'his', 'a': 'his', 'r': 'himself'},
        'female': {'s': 'she', 'o': 'her', 'p': 'her', 'a': 'hers', 'r': 'herself'},
        'ambiguous': {'s': 'they', 'o': 'them', 'p': 'their', 'a': 'theirs', 'r': 'themselves'},
    }
    
    pronouns = pronoun_map.get(gender, pronoun_map['ambiguous'])
    
    # Replace placeholders
    text = text.replace('%s', pronouns['s'])
    text = text.replace('%S', pronouns['s'].capitalize())
    text = text.replace('%o', pronouns['o'])
    text = text.replace('%O', pronouns['o'].capitalize())
    text = text.replace('%p', pronouns['p'])
    text = text.replace('%P', pronouns['p'].capitalize())
    text = text.replace('%a', pronouns['a'])
    text = text.replace('%A', pronouns['a'].capitalize())
    text = text.replace('%r', pronouns['r'])
    text = text.replace('%R', pronouns['r'].capitalize())
    text = text.replace('%n', char.key)
    text = text.replace('%N', char.key)
    
    return text


# =============================================================================
# EVMENU RECIPE DESIGNER
# =============================================================================

class RecipeDesignMenu(EvMenu):
    """Custom EvMenu for recipe design that suppresses auto option display."""
    
    def options_formatter(self, optionlist):
        """Suppress automatic option display."""
        return ""


def _recipe_data(caller):
    """Get or initialize recipe data from caller's ndb."""
    if not hasattr(caller.ndb, '_recipe_design') or caller.ndb._recipe_design is None:
        caller.ndb._recipe_design = {
            "name": "",
            "is_food": True,
            "description": "",
            "taste": "",
            "smell": "",
            "msg_eat_self": "",
            "msg_eat_others": "",
            "msg_finish_self": "",
            "msg_finish_others": "",
            "keywords": [],
        }
    return caller.ndb._recipe_design


def node_main_menu(caller, raw_string, **kwargs):
    """Main menu for recipe design."""
    data = _recipe_data(caller)
    
    # Build status display
    def status(field):
        # Special handling for boolean fields - they're always "set"
        if field == 'is_food':
            return "|g[SET]|n"
        return "|g[SET]|n" if data.get(field) else "|r[---]|n"
    
    item_type = "Food" if data.get("is_food", True) else "Drink"
    
    text = f"""
|c=== Recipe Designer ===|n

Design a new {item_type.lower()} recipe. Set all required fields before submitting.

|wCurrent Recipe:|n {data.get('name') or '(unnamed)'}

|w1.|n {status('name')} Name
|w2.|n {status('is_food')} Type: |w{item_type}|n
|w3.|n {status('description')} Description
|w4.|n {status('taste')} Taste
|w5.|n {status('smell')} Smell
|w6.|n {status('msg_eat_self')} Consume Message (1st person)
|w7.|n {status('msg_eat_others')} Consume Message (3rd person)
|w8.|n {status('msg_finish_self')} Finish Message (1st person)
|w9.|n {status('msg_finish_others')} Finish Message (3rd person)
|w10.|n Keywords: {', '.join(data.get('keywords', [])) or '(none)'}

|w[R]|n Review before submission
|w[S]|n Submit for approval
|w[Q]|n Quit without saving
"""
    
    options = (
        {"key": "1", "goto": "node_set_name"},
        {"key": "2", "goto": "node_set_type"},
        {"key": "3", "goto": "node_set_description"},
        {"key": "4", "goto": "node_set_taste"},
        {"key": "5", "goto": "node_set_smell"},
        {"key": "6", "goto": "node_set_eat_self"},
        {"key": "7", "goto": "node_set_eat_others"},
        {"key": "8", "goto": "node_set_finish_self"},
        {"key": "9", "goto": "node_set_finish_others"},
        {"key": "10", "goto": "node_set_keywords"},
        {"key": "r", "goto": "node_review"},
        {"key": "R", "goto": "node_review"},
        {"key": "s", "goto": "node_submit"},
        {"key": "S", "goto": "node_submit"},
        {"key": "q", "goto": "node_quit"},
        {"key": "Q", "goto": "node_quit"},
    )
    
    return text, options


def node_set_name(caller, raw_string, **kwargs):
    """Set recipe name."""
    text = """
|c=== Set Recipe Name ===|n

Enter the name for your recipe. This is what the food/drink will be called.

Examples: |wSteaming Bowl of Ramen|n, |wSynthetic Protein Shake|n, |wNeon District Street Tacos|n

|wType your name and press Enter, or type 'back' to return.|n
"""
    
    def _set_name(caller, raw_string, **kwargs):
        raw_string = raw_string.strip()
        if raw_string.lower() == 'back':
            return "node_main_menu"
        if len(raw_string) < 3:
            caller.msg("|rName must be at least 3 characters.|n")
            return "node_set_name"
        if len(raw_string) > 80:
            caller.msg("|rName must be 80 characters or less.|n")
            return "node_set_name"
        
        data = _recipe_data(caller)
        data["name"] = raw_string
        caller.msg(f"|gName set to:|n {raw_string}")
        return "node_main_menu"
    
    options = ({"key": "_default", "goto": _set_name},)
    return text, options


def node_set_type(caller, raw_string, **kwargs):
    """Set food or drink type."""
    data = _recipe_data(caller)
    current = "Food" if data.get("is_food", True) else "Drink"
    
    text = f"""
|c=== Set Item Type ===|n

Current type: |w{current}|n

|w1.|n Food (consumed with 'eat')
|w2.|n Drink (consumed with 'drink')
|w[B]|n Back to main menu
"""
    
    def _set_type(caller, raw_string, **kwargs):
        raw_string = raw_string.strip().lower()
        data = _recipe_data(caller)
        
        if raw_string == '1':
            data["is_food"] = True
            caller.msg("|gType set to:|n Food")
        elif raw_string == '2':
            data["is_food"] = False
            caller.msg("|gType set to:|n Drink")
        elif raw_string in ('b', 'back'):
            pass
        else:
            caller.msg("|rInvalid choice.|n")
            return "node_set_type"
        return "node_main_menu"
    
    options = ({"key": "_default", "goto": _set_type},)
    return text, options


def node_set_description(caller, raw_string, **kwargs):
    """Set recipe description."""
    text = """
|c=== Set Description ===|n

Enter the description of your food/drink as it appears when examined.
This should describe how it looks.

Example: |wA steaming bowl of rich broth with thick noodles, sliced pork,|n
|wsoft-boiled egg, and fresh green onions floating on top.|n

|wType your description and press Enter, or type 'back' to return.|n
"""
    
    def _set_desc(caller, raw_string, **kwargs):
        raw_string = raw_string.strip()
        if raw_string.lower() == 'back':
            return "node_main_menu"
        if len(raw_string) < 10:
            caller.msg("|rDescription must be at least 10 characters.|n")
            return "node_set_description"
        
        data = _recipe_data(caller)
        data["description"] = raw_string
        caller.msg("|gDescription set.|n")
        return "node_main_menu"
    
    options = ({"key": "_default", "goto": _set_desc},)
    return text, options


def node_set_taste(caller, raw_string, **kwargs):
    """Set taste description."""
    text = """
|c=== Set Taste ===|n

Enter what your food/drink tastes like.

Example: |wRich, savory umami with hints of soy and miso, the noodles|n
|wperfectly chewy and the broth deeply satisfying.|n

|wType your taste description and press Enter, or type 'back' to return.|n
"""
    
    def _set_taste(caller, raw_string, **kwargs):
        raw_string = raw_string.strip()
        if raw_string.lower() == 'back':
            return "node_main_menu"
        if len(raw_string) < 10:
            caller.msg("|rTaste must be at least 10 characters.|n")
            return "node_set_taste"
        
        data = _recipe_data(caller)
        data["taste"] = raw_string
        caller.msg("|gTaste set.|n")
        return "node_main_menu"
    
    options = ({"key": "_default", "goto": _set_taste},)
    return text, options


def node_set_smell(caller, raw_string, **kwargs):
    """Set smell description."""
    text = """
|c=== Set Smell ===|n

Enter what your food/drink smells like.

Example: |wThe aroma of slow-simmered pork broth wafts up, mingling with|n
|wthe sharp scent of green onions and a hint of garlic.|n

|wType your smell description and press Enter, or type 'back' to return.|n
"""
    
    def _set_smell(caller, raw_string, **kwargs):
        raw_string = raw_string.strip()
        if raw_string.lower() == 'back':
            return "node_main_menu"
        if len(raw_string) < 10:
            caller.msg("|rSmell must be at least 10 characters.|n")
            return "node_set_smell"
        
        data = _recipe_data(caller)
        data["smell"] = raw_string
        caller.msg("|gSmell set.|n")
        return "node_main_menu"
    
    options = ({"key": "_default", "goto": _set_smell},)
    return text, options


def node_set_eat_self(caller, raw_string, **kwargs):
    """Set 1st person consumption message."""
    data = _recipe_data(caller)
    action = "eat" if data.get("is_food", True) else "drink"
    
    text = f"""
|c=== Set Consume Message (1st Person) ===|n

Enter the message YOU see when you {action} this item.
Use pronoun substitutions: %s (he/she/they), %o (him/her/them), 
%p (his/her/their), %r (himself/herself/themselves), %n (name)

Example for food: |wYou lift the bowl to your lips and slurp the rich broth,|n
|wsavoring each noodle as it slides down.|n

Example for drink: |wYou take a long sip, the cool liquid refreshing you instantly.|n

|wType your message and press Enter, or type 'back' to return.|n
"""
    
    def _set_msg(caller, raw_string, **kwargs):
        raw_string = raw_string.strip()
        if raw_string.lower() == 'back':
            return "node_main_menu"
        if len(raw_string) < 10:
            caller.msg("|rMessage must be at least 10 characters.|n")
            return "node_set_eat_self"
        
        data = _recipe_data(caller)
        data["msg_eat_self"] = raw_string
        caller.msg("|gConsume message (1st person) set.|n")
        return "node_main_menu"
    
    options = ({"key": "_default", "goto": _set_msg},)
    return text, options


def node_set_eat_others(caller, raw_string, **kwargs):
    """Set 3rd person consumption message."""
    data = _recipe_data(caller)
    action = "eats" if data.get("is_food", True) else "drinks"
    
    text = f"""
|c=== Set Consume Message (3rd Person) ===|n

Enter the message OTHERS see when someone {action} this item.
Use pronoun substitutions: %s (he/she/they), %o (him/her/them), 
%p (his/her/their), %r (himself/herself/themselves), %n (name)

Example for food: |w%n lifts the bowl to %p lips and slurps the rich broth.|n

Example for drink: |w%n takes a long sip from %p drink.|n

|wType your message and press Enter, or type 'back' to return.|n
"""
    
    def _set_msg(caller, raw_string, **kwargs):
        raw_string = raw_string.strip()
        if raw_string.lower() == 'back':
            return "node_main_menu"
        if len(raw_string) < 10:
            caller.msg("|rMessage must be at least 10 characters.|n")
            return "node_set_eat_others"
        
        data = _recipe_data(caller)
        data["msg_eat_others"] = raw_string
        caller.msg("|gConsume message (3rd person) set.|n")
        return "node_main_menu"
    
    options = ({"key": "_default", "goto": _set_msg},)
    return text, options


def node_set_finish_self(caller, raw_string, **kwargs):
    """Set 1st person finish message."""
    data = _recipe_data(caller)
    action = "eating" if data.get("is_food", True) else "drinking"
    
    text = f"""
|c=== Set Finish Message (1st Person) ===|n

Enter the message YOU see when you finish {action} this item.
Use pronoun substitutions if needed.

Example for food: |wYou set down the empty bowl, deeply satisfied.|n

Example for drink: |wYou drain the last drop and set down the empty glass.|n

|wType your message and press Enter, or type 'back' to return.|n
"""
    
    def _set_msg(caller, raw_string, **kwargs):
        raw_string = raw_string.strip()
        if raw_string.lower() == 'back':
            return "node_main_menu"
        if len(raw_string) < 10:
            caller.msg("|rMessage must be at least 10 characters.|n")
            return "node_set_finish_self"
        
        data = _recipe_data(caller)
        data["msg_finish_self"] = raw_string
        caller.msg("|gFinish message (1st person) set.|n")
        return "node_main_menu"
    
    options = ({"key": "_default", "goto": _set_msg},)
    return text, options


def node_set_finish_others(caller, raw_string, **kwargs):
    """Set 3rd person finish message."""
    data = _recipe_data(caller)
    action = "eating" if data.get("is_food", True) else "drinking"
    
    text = f"""
|c=== Set Finish Message (3rd Person) ===|n

Enter the message OTHERS see when someone finishes {action} this item.
Use pronoun substitutions: %s, %o, %p, %r, %n

Example for food: |w%n sets down the empty bowl with a satisfied expression.|n

Example for drink: |w%n drains the last drop and sets down the empty glass.|n

|wType your message and press Enter, or type 'back' to return.|n
"""
    
    def _set_msg(caller, raw_string, **kwargs):
        raw_string = raw_string.strip()
        if raw_string.lower() == 'back':
            return "node_main_menu"
        if len(raw_string) < 10:
            caller.msg("|rMessage must be at least 10 characters.|n")
            return "node_set_finish_others"
        
        data = _recipe_data(caller)
        data["msg_finish_others"] = raw_string
        caller.msg("|gFinish message (3rd person) set.|n")
        return "node_main_menu"
    
    options = ({"key": "_default", "goto": _set_msg},)
    return text, options


def node_set_keywords(caller, raw_string, **kwargs):
    """Set searchable keywords."""
    data = _recipe_data(caller)
    current = ', '.join(data.get('keywords', [])) or '(none)'
    
    text = f"""
|c=== Set Keywords ===|n

Current keywords: |w{current}|n

Enter comma-separated keywords to help players find this recipe.
Good keywords include ingredients, cuisine type, meal type, etc.

Example: |wramen, noodles, japanese, soup, pork, asian|n

|wType your keywords and press Enter, or type 'back' to return.|n
|wType 'clear' to remove all keywords.|n
"""
    
    def _set_keywords(caller, raw_string, **kwargs):
        raw_string = raw_string.strip()
        if raw_string.lower() == 'back':
            return "node_main_menu"
        if raw_string.lower() == 'clear':
            data = _recipe_data(caller)
            data["keywords"] = []
            caller.msg("|gKeywords cleared.|n")
            return "node_main_menu"
        
        # Parse keywords
        keywords = [kw.strip().lower() for kw in raw_string.split(',') if kw.strip()]
        
        data = _recipe_data(caller)
        data["keywords"] = keywords
        caller.msg(f"|gKeywords set:|n {', '.join(keywords)}")
        return "node_main_menu"
    
    options = ({"key": "_default", "goto": _set_keywords},)
    return text, options


def node_review(caller, raw_string, **kwargs):
    """Review recipe before submission."""
    data = _recipe_data(caller)
    
    item_type = "Food" if data.get("is_food", True) else "Drink"
    action = "eat" if data.get("is_food", True) else "drink"
    
    text = f"""
|c=== Recipe Review ===|n

|wName:|n {data.get('name') or '|r(not set)|n'}
|wType:|n {item_type}

|wDescription:|n
{data.get('description') or '|r(not set)|n'}

|wTaste:|n
{data.get('taste') or '|r(not set)|n'}

|wSmell:|n
{data.get('smell') or '|r(not set)|n'}

|wConsume Message (you see when you {action}):|n
{data.get('msg_eat_self') or '|r(not set)|n'}

|wConsume Message (others see):|n
{data.get('msg_eat_others') or '|r(not set)|n'}

|wFinish Message (you see):|n
{data.get('msg_finish_self') or '|r(not set)|n'}

|wFinish Message (others see):|n
{data.get('msg_finish_others') or '|r(not set)|n'}

|wKeywords:|n {', '.join(data.get('keywords', [])) or '(none)'}

|w[B]|n Back to main menu
"""
    
    options = (
        {"key": "b", "goto": "node_main_menu"},
        {"key": "B", "goto": "node_main_menu"},
        {"key": "_default", "goto": "node_main_menu"},
    )
    return text, options


def node_submit(caller, raw_string, **kwargs):
    """Submit recipe for approval."""
    data = _recipe_data(caller)
    
    # Validate all required fields
    required = ['name', 'description', 'taste', 'smell', 
                'msg_eat_self', 'msg_eat_others', 'msg_finish_self', 'msg_finish_others']
    missing = [f for f in required if not data.get(f)]
    
    if missing:
        text = f"""
|r=== Cannot Submit ===|n

The following required fields are not set:
{', '.join(missing)}

Please complete all fields before submitting.

|w[B]|n Back to main menu
"""
        options = (
            {"key": "b", "goto": "node_main_menu"},
            {"key": "B", "goto": "node_main_menu"},
            {"key": "_default", "goto": "node_main_menu"},
        )
        return text, options
    
    # Confirm submission
    text = f"""
|c=== Confirm Submission ===|n

You are about to submit |w{data.get('name')}|n for admin approval.

Once submitted, an admin will review your recipe and set its difficulty.
You will be notified when your recipe is approved or rejected.

|w[Y]|n Yes, submit for approval
|w[N]|n No, go back
"""
    
    def _confirm_submit(caller, raw_string, **kwargs):
        raw_string = raw_string.strip().lower()
        
        if raw_string in ('y', 'yes'):
            data = _recipe_data(caller)
            
            # Create recipe entry
            recipe_data = {
                "name": data["name"],
                "is_food": data["is_food"],
                "description": data["description"],
                "taste": data["taste"],
                "smell": data["smell"],
                "msg_eat_self": data["msg_eat_self"],
                "msg_eat_others": data["msg_eat_others"],
                "msg_finish_self": data["msg_finish_self"],
                "msg_finish_others": data["msg_finish_others"],
                "keywords": data.get("keywords", []),
                "creator_dbref": caller.dbref,
                "creator_name": caller.key,
                "created_at": datetime.now(),
            }
            
            # Add to pending queue
            recipe_id = add_pending_recipe(recipe_data)
            
            # Notify admins
            notify_admins_new_recipe(caller, recipe_data, recipe_id)
            
            caller.msg(f"|g=== Recipe Submitted ===|n")
            caller.msg(f"Your recipe |w{data['name']}|n has been submitted for approval.")
            caller.msg(f"Recipe ID: |w#{recipe_id}|n")
            caller.msg("You will be notified when it is reviewed.")
            
            # Clear design data
            if hasattr(caller.ndb, '_recipe_design'):
                del caller.ndb._recipe_design
            
            # Explicitly close the menu
            if hasattr(caller.ndb, '_evmenu'):
                caller.ndb._evmenu.close_menu()
            return None  # Exit menu
        
        return "node_main_menu"
    
    options = ({"key": "_default", "goto": _confirm_submit},)
    return text, options


def node_quit(caller, raw_string, **kwargs):
    """Quit without saving."""
    text = """
|y=== Quit Recipe Designer ===|n

Are you sure you want to quit? Your recipe will not be saved.

|w[Y]|n Yes, quit
|w[N]|n No, go back
"""
    
    def _confirm_quit(caller, raw_string, **kwargs):
        raw_string = raw_string.strip().lower()
        
        if raw_string in ('y', 'yes'):
            if hasattr(caller.ndb, '_recipe_design'):
                del caller.ndb._recipe_design
            if hasattr(caller.ndb, '_admin_recipe_design'):
                del caller.ndb._admin_recipe_design
            caller.msg("|yRecipe designer closed without saving.|n")
            # Explicitly close the menu
            if hasattr(caller.ndb, '_evmenu'):
                caller.ndb._evmenu.close_menu()
            return None  # Exit menu
        
        # Check if we're in admin mode to return to the right menu
        if getattr(caller.ndb, '_admin_recipe_design', False):
            return "node_admin_main_menu"
        return "node_main_menu"
    
    options = (
        {"key": "y", "goto": _confirm_quit},
        {"key": "Y", "goto": _confirm_quit},
        {"key": "yes", "goto": _confirm_quit},
        {"key": "n", "goto": _confirm_quit},
        {"key": "N", "goto": _confirm_quit},
        {"key": "no", "goto": _confirm_quit},
        {"key": "_default", "goto": _confirm_quit},
    )
    return text, options


def notify_admins_new_recipe(creator, recipe_data, recipe_id):
    """Notify admins of a new pending recipe."""
    from evennia.comms.models import ChannelDB
    from evennia.accounts.models import AccountDB
    
    msg = f"|y[RECIPE #{recipe_id}]|n {creator.key} submitted: {recipe_data['name']}"
    
    # Notify via Staff channel
    try:
        staff_channel = ChannelDB.objects.get_channel("Staff")
        if staff_channel:
            staff_channel.msg(msg)
    except Exception:
        pass
    
    # Also notify online admins
    for account in AccountDB.objects.filter(db_is_connected=True):
        if account.is_superuser:
            if account.character:
                account.character.msg(msg)


# =============================================================================
# PLAYER COMMANDS
# =============================================================================

class CmdDesignRecipe(Command):
    """
    Design a new food or drink recipe.
    
    Usage:
        design
    
    Opens the recipe designer menu where you can create a new recipe.
    Once completed, your recipe will be submitted for admin approval.
    When approved, you can cook it at any kitchenette.
    """
    key = "design"
    aliases = ["designrecipe", "design recipe", "recipe design"]
    locks = "cmd:all()"
    help_category = "Cooking"
    
    def func(self):
        caller = self.caller
        
        # Start the EvMenu
        RecipeDesignMenu(
            caller,
            "commands.CmdCooking",
            startnode="node_main_menu",
            cmdset_mergetype="Replace",
            cmd_on_exit=None,
        )


class CmdCook(Command):
    """
    Cook a recipe at a kitchenette.
    
    Usage:
        cook                    - Browse all available recipes
        cook <search term>      - Search for recipes by keyword
        cook #<recipe_id>       - Cook a specific recipe by ID
    
    You must be at a kitchenette and have ingredients to cook.
    Your cooking skill determines the quality of the result.
    """
    key = "cook"
    aliases = ["prepare", "make food"]
    locks = "cmd:all()"
    help_category = "Cooking"
    
    def func(self):
        caller = self.caller
        
        # Check for kitchenette
        kitchenette = None
        for obj in caller.location.contents:
            if getattr(obj, 'is_kitchenette', False):
                kitchenette = obj
                break
        
        if not kitchenette:
            caller.msg("|rYou need to be at a kitchenette to cook.|n")
            return
        
        # Check for ingredients
        ingredients = None
        for obj in caller.contents:
            if getattr(obj, 'is_ingredients', False):
                ingredients = obj
                break
        
        if not ingredients:
            caller.msg("|rYou need ingredients to cook. Buy some from a shop or ask an admin.|n")
            return
        
        # Get approved recipes
        recipes = get_all_approved_recipes()
        
        if not recipes:
            caller.msg("|yNo approved recipes available yet. Try designing one!|n")
            return
        
        args = self.args.strip()
        
        # Cook specific recipe by ID
        if args.startswith('#'):
            try:
                recipe_id = int(args[1:])
                recipe = get_recipe_by_id(recipe_id)
                if not recipe or recipe.get("status") != "approved":
                    caller.msg(f"|rRecipe #{recipe_id} not found or not approved.|n")
                    return
                self.attempt_cooking(caller, recipe, ingredients, kitchenette)
                return
            except ValueError:
                caller.msg("|rInvalid recipe ID. Use cook #<number>|n")
                return
        
        # Search recipes
        if args:
            results = search_recipes(args)
            if not results:
                caller.msg(f"|yNo recipes found matching '{args}'.|n")
                return
            recipes = results
        
        # Display recipe list
        self.display_recipe_list(caller, recipes)
    
    def display_recipe_list(self, caller, recipes):
        """Display a paginated list of recipes."""
        caller.msg("|c=== Available Recipes ===|n")
        caller.msg(f"|wFound {len(recipes)} recipe(s).|n")
        caller.msg("")
        
        for recipe in recipes[:20]:  # Show first 20
            item_type = "Food" if recipe.get("is_food", True) else "Drink"
            caller.msg(f"|w#{recipe['id']}|n {recipe['name']} ({item_type})|n")
        
        if len(recipes) > 20:
            caller.msg(f"|y... and {len(recipes) - 20} more. Use 'cook <keyword>' to narrow search.|n")
        
        caller.msg("")
        caller.msg("|cUse 'cook #<id>' to cook a recipe.|n")
    
    def get_difficulty_color(self, difficulty):
        """Get color code for difficulty."""
        if difficulty <= 20:
            return "|g"
        elif difficulty <= 45:
            return "|y"
        elif difficulty <= 75:
            return "|m"
        elif difficulty <= 89:
            return "|r"
        else:
            return "|R"
    
    def attempt_cooking(self, caller, recipe, ingredients, kitchenette):
        """Attempt to cook a recipe."""
        difficulty = recipe.get("difficulty", 50)
        recipe_name = recipe.get("name", "Unknown")
        
        # Get cooking skill
        cooking_skill = getattr(caller.db, 'cooking', 0) or 0
        
        # Roll cooking check (skill + random vs difficulty)
        roll = randint(1, 20)
        total = cooking_skill + roll
        
        # Calculate success margin
        margin = total - (difficulty / 2)  # Divide difficulty for balance
        
        # Determine quality based on margin
        if margin < -20:
            quality = "inedible"
        elif margin < -5:
            quality = "poor"
        elif margin < 10:
            quality = "average"
        elif margin < 25:
            quality = "good"
        else:
            quality = "excellent"
        
        # Consume ingredients
        caller.msg(f"|cYou begin preparing {recipe_name}...|n")
        
        if quality == "inedible":
            # Critical failure - ingredients wasted, no food produced
            caller.msg(f"|rDisaster! Your attempt at {recipe_name} is a complete failure.|n")
            caller.msg("|rThe result is utterly inedible. Your ingredients are wasted.|n")
            ingredients.delete()
            caller.location.msg_contents(
                f"{caller.key} attempts to cook but produces something that looks toxic.",
                exclude=[caller]
            )
            return
        
        # Success - create food item
        ingredients.delete()
        
        food = create_object(
            FoodItem,
            key=recipe_name,
            location=caller,
            attributes=[
                ("is_food", recipe.get("is_food", True)),
                ("recipe_id", recipe.get("id")),
                ("quality_rating", quality),
                ("food_name", recipe_name),
                ("food_desc", recipe.get("description", "")),
                ("food_taste", recipe.get("taste", "")),
                ("food_smell", recipe.get("smell", "")),
                ("msg_eat_self", recipe.get("msg_eat_self", "")),
                ("msg_eat_others", recipe.get("msg_eat_others", "")),
                ("msg_finish_self", recipe.get("msg_finish_self", "")),
                ("msg_finish_others", recipe.get("msg_finish_others", "")),
                ("creator_dbref", caller.dbref),
                ("created_at", datetime.now()),
            ]
        )
        
        # Quality messages
        quality_msgs = {
            "poor": f"|yYou manage to produce {recipe_name}, though it looks a bit sad.|n",
            "average": f"|gYou successfully prepare {recipe_name}.|n",
            "good": f"|gYou expertly craft a delicious {recipe_name}!|n",
            "excellent": f"|G|*You create a masterpiece! This {recipe_name} is perfection!|n",
        }
        
        caller.msg(quality_msgs.get(quality, f"|gYou prepare {recipe_name}.|n"))
        caller.msg(f"|cQuality: {quality.capitalize()}|n")
        
        caller.location.msg_contents(
            f"{caller.key} finishes cooking and produces {food.get_display_name(caller)}.",
            exclude=[caller]
        )


class CmdEat(Command):
    """
    Eat food.
    
    Usage:
        eat <food>
    
    Consumes a food item, displaying the appropriate messages.
    """
    key = "eat"
    locks = "cmd:all()"
    help_category = "Cooking"
    
    def func(self):
        caller = self.caller
        
        if not self.args:
            caller.msg("Usage: eat <food>")
            return
        
        # Find the food
        item = caller.search(self.args.strip(), location=caller, quiet=True)
        if not item:
            caller.msg(f"You don't have '{self.args.strip()}'.")
            return
        if isinstance(item, list):
            item = item[0]
        
        # Check if it's food
        if not getattr(item, 'is_food_item', False):
            caller.msg(f"You can't eat {item.key}.")
            return
        
        if not getattr(item, 'is_food', True):
            caller.msg(f"That's a drink. Use 'drink {item.key}' instead.")
            return
        
        # Consume the food
        self.consume_item(caller, item)
    
    def consume_item(self, caller, item):
        """Consume the food item."""
        # Get current consumes remaining
        consumes = getattr(item, 'consumes_remaining', 1)
        if consumes is None:
            consumes = 1
        
        # Get messages
        msg_self = item.msg_eat_self or f"You eat the {item.key}."
        msg_others = item.msg_eat_others or f"%n eats the {item.key}."
        msg_finish_self = item.msg_finish_self or "You finish eating."
        msg_finish_others = item.msg_finish_others or "%n finishes eating."
        
        # Substitute pronouns
        msg_self = substitute_pronouns(msg_self, caller)
        msg_others = substitute_pronouns(msg_others, caller)
        msg_finish_self = substitute_pronouns(msg_finish_self, caller)
        msg_finish_others = substitute_pronouns(msg_finish_others, caller)
        
        # Send consume messages
        caller.msg(msg_self)
        caller.location.msg_contents(msg_others, exclude=[caller])
        
        # Decrement consumes
        consumes -= 1
        
        if consumes <= 0:
            # Finished - show finish messages and delete
            caller.msg(msg_finish_self)
            caller.location.msg_contents(msg_finish_others, exclude=[caller])
            item.delete()
        else:
            # Still has bites left
            item.consumes_remaining = consumes
            bite_word = "bite" if consumes > 1 else "bite"
            caller.msg(f"({consumes} {bite_word} remaining)|n")


class CmdDrink(Command):
    """
    Drink a beverage.
    
    Usage:
        drink <drink>
    
    Consumes a drink item, displaying the appropriate messages.
    """
    key = "drink"
    locks = "cmd:all()"
    help_category = "Cooking"
    
    def func(self):
        caller = self.caller
        
        if not self.args:
            caller.msg("Usage: drink <beverage>")
            return
        
        # Find the drink
        item = caller.search(self.args.strip(), location=caller, quiet=True)
        if not item:
            caller.msg(f"You don't have '{self.args.strip()}'.")
            return
        if isinstance(item, list):
            item = item[0]
        
        # Check if it's a drink
        if not getattr(item, 'is_food_item', False):
            caller.msg(f"You can't drink {item.key}.")
            return
        
        if getattr(item, 'is_food', True):
            caller.msg(f"That's food. Use 'eat {item.key}' instead.")
            return
        
        # Consume the drink
        self.consume_item(caller, item)
    
    def consume_item(self, caller, item):
        """Consume the drink item."""
        # Get current consumes remaining
        consumes = getattr(item, 'consumes_remaining', 1)
        if consumes is None:
            consumes = 1
        
        # Get messages
        msg_self = item.msg_eat_self or f"You drink the {item.key}."
        msg_others = item.msg_eat_others or f"%n drinks the {item.key}."
        msg_finish_self = item.msg_finish_self or "You finish drinking."
        msg_finish_others = item.msg_finish_others or "%n finishes drinking."
        
        # Substitute pronouns
        msg_self = substitute_pronouns(msg_self, caller)
        msg_others = substitute_pronouns(msg_others, caller)
        msg_finish_self = substitute_pronouns(msg_finish_self, caller)
        msg_finish_others = substitute_pronouns(msg_finish_others, caller)
        
        # Send consume messages
        caller.msg(msg_self)
        caller.location.msg_contents(msg_others, exclude=[caller])
        
        # Decrement consumes
        consumes -= 1
        
        if consumes <= 0:
            # Finished - show finish messages and delete
            caller.msg(msg_finish_self)
            caller.location.msg_contents(msg_finish_others, exclude=[caller])
            item.delete()
        else:
            # Still has sips left
            item.consumes_remaining = consumes
            sip_word = "sip" if consumes > 1 else "sip"
            caller.msg(f"|c({consumes} {sip_word} remaining)|n")


class CmdTaste(Command):
    """
    Get a preview of what food tastes like.
    
    Usage:
        taste <food/drink>
    
    Gives you a hint of the taste without consuming the item.
    """
    key = "taste"
    locks = "cmd:all()"
    help_category = "Cooking"
    
    def func(self):
        caller = self.caller
        
        if not self.args:
            caller.msg("Usage: taste <food/drink>")
            return
        
        item = caller.search(self.args.strip(), location=caller, quiet=True)
        if not item:
            # Also check room
            item = caller.search(self.args.strip(), location=caller.location, quiet=True)
        
        if not item:
            caller.msg(f"You can't find '{self.args.strip()}'.")
            return
        if isinstance(item, list):
            item = item[0]
        
        if not getattr(item, 'is_food_item', False):
            caller.msg(f"You can't taste {item.key}.")
            return
        
        if item.food_taste:
            action = "take a small taste of" if item.is_food else "take a small sip of"
            caller.msg(f"You {action} the {item.key}.")
            caller.msg(f"|cTaste:|n {item.food_taste}")
        else:
            caller.msg(f"The {item.key} doesn't have a distinct taste description.")


class CmdSmellFood(Command):
    """
    Smell food or drink.
    
    Usage:
        sniff <food/drink>
    
    Get a description of how the item smells.
    """
    key = "sniff"
    aliases = ["smell food"]
    locks = "cmd:all()"
    help_category = "Cooking"
    
    def func(self):
        caller = self.caller
        
        if not self.args:
            caller.msg("Usage: sniff <food/drink>")
            return
        
        item = caller.search(self.args.strip(), location=caller, quiet=True)
        if not item:
            item = caller.search(self.args.strip(), location=caller.location, quiet=True)
        
        if not item:
            caller.msg(f"You can't find '{self.args.strip()}'.")
            return
        if isinstance(item, list):
            item = item[0]
        
        if not getattr(item, 'is_food_item', False):
            caller.msg(f"You sniff {item.key} but it's not food.")
            return
        
        if item.food_smell:
            caller.msg(f"You lean in and sniff the {item.key}.")
            caller.msg(f"|cSmell:|n {item.food_smell}")
        else:
            caller.msg(f"The {item.key} doesn't have a particularly notable smell.")


# =============================================================================
# ADMIN COMMANDS
# =============================================================================

class CmdSpawnKitchenette(Command):
    """
    Create a kitchenette for cooking.
    
    Usage:
        spawnkitchen [name]
    
    Creates a kitchenette object in the current room.
    """
    key = "spawnkitchen"
    aliases = ["spawn kitchen", "spawnkitchenette"]
    locks = "cmd:perm(Builder)"
    help_category = "Building"
    
    def func(self):
        caller = self.caller
        name = self.args.strip() or "kitchenette"
        
        kitchenette = create_object(
            Kitchenette,
            key=name,
            location=caller.location,
        )
        
        caller.msg(f"|gCreated {name} in {caller.location.key}.|n")


class CmdSpawnIngredients(Command):
    """
    Spawn cooking ingredients.
    
    Usage:
        spawningredients [quality]
        spawningredients [quality] to <character>
    
    Quality can be: standard, premium, exotic
    """
    key = "spawningredients"
    aliases = ["spawn ingredients"]
    locks = "cmd:perm(Builder)"
    help_category = "Building"
    
    VALID_QUALITIES = ["standard", "premium", "exotic"]
    
    def func(self):
        caller = self.caller
        args = self.args.strip()
        target = caller
        quality = "standard"
        
        # Parse arguments
        if " to " in args.lower():
            parts = args.lower().split(" to ", 1)
            quality_arg = parts[0].strip()
            target_name = parts[1].strip()
            
            # Find target
            targets = search_object(target_name, typeclass="typeclasses.characters.Character")
            if not targets:
                caller.msg(f"Character '{target_name}' not found.")
                return
            target = targets[0]
            
            if quality_arg in self.VALID_QUALITIES:
                quality = quality_arg
        elif args:
            if args.lower() in self.VALID_QUALITIES:
                quality = args.lower()
        
        # Create ingredients
        ingredients = create_object(
            Ingredients,
            key=f"{quality} ingredients",
            location=target,
            attributes=[
                ("quality", quality),
                ("desc", f"A package of {quality} cooking ingredients."),
            ]
        )
        
        caller.msg(f"|gCreated {quality} ingredients in {target.key}'s inventory.|n")
        if target != caller:
            target.msg(f"|y{caller.key} has given you some {quality} cooking ingredients.|n")


class CmdRecipes(Command):
    """
    View and manage the recipe queue.
    
    Usage:
        recipes                 - View pending recipes
        recipes all             - View all recipes (approved and pending)
        recipes #<id>           - View specific recipe details
        recipes scale           - Show difficulty scale reference
    """
    key = "recipes"
    locks = "cmd:perm(Builder)"
    help_category = "Admin"
    
    def func(self):
        caller = self.caller
        args = self.args.strip().lower()
        
        if args == "scale":
            caller.msg(DIFFICULTY_SCALE)
            return
        
        if args.startswith('#'):
            try:
                recipe_id = int(args[1:])
                self.show_recipe_details(caller, recipe_id)
                return
            except ValueError:
                caller.msg("|rInvalid recipe ID.|n")
                return
        
        if args == "all":
            self.show_all_recipes(caller)
        else:
            self.show_pending_recipes(caller)
    
    def show_pending_recipes(self, caller):
        """Show pending recipes."""
        pending = get_pending_recipes()
        
        if not pending:
            caller.msg("|yNo pending recipes.|n")
            return
        
        caller.msg("|c=== Pending Recipe Submissions ===|n")
        caller.msg("")
        
        for recipe in pending:
            creator = recipe.get("creator_name", "Unknown")
            created = recipe.get("created_at")
            if hasattr(created, 'strftime'):
                created = created.strftime('%Y-%m-%d %H:%M')
            
            caller.msg(f"|w#{recipe['id']}|n {recipe['name']}")
            caller.msg(f"    Creator: {creator} | Submitted: {created}")
            caller.msg(f"    Type: {'Food' if recipe.get('is_food', True) else 'Drink'}")
            caller.msg(f"    |wapproverecipe #{recipe['id']} <difficulty>|n to approve")
            caller.msg(f"    |wrejectrecipe #{recipe['id']} <reason>|n to reject")
            caller.msg("")
    
    def show_all_recipes(self, caller):
        """Show all recipes."""
        storage = get_recipe_storage()
        all_recipes = (storage.db.recipes or []) + (storage.db.pending_recipes or [])
        
        if not all_recipes:
            caller.msg("|yNo recipes in the system.|n")
            return
        
        caller.msg("|c=== All Recipes ===|n")
        
        for recipe in all_recipes:
            status = recipe.get("status", "unknown")
            status_color = "|g" if status == "approved" else "|y" if status == "pending" else "|r"
            
            caller.msg(f"|w#{recipe['id']}|n {recipe['name']} - {status_color}{status.upper()}|n")
    
    def show_recipe_details(self, caller, recipe_id):
        """Show detailed info for a specific recipe."""
        recipe = get_recipe_by_id(recipe_id)
        
        if not recipe:
            caller.msg(f"|rRecipe #{recipe_id} not found.|n")
            return
        
        item_type = "Food" if recipe.get("is_food", True) else "Drink"
        status = recipe.get("status", "unknown")
        
        caller.msg(f"|c=== Recipe #{recipe_id}: {recipe.get('name')} ===|n")
        caller.msg(f"|wStatus:|n {status.upper()}")
        caller.msg(f"|wType:|n {item_type}")
        caller.msg(f"|wCreator:|n {recipe.get('creator_name', 'Unknown')}")
        caller.msg(f"|wCreated:|n {recipe.get('created_at', 'Unknown')}")
        caller.msg("")
        caller.msg(f"|wDescription:|n {recipe.get('description', 'N/A')}")
        caller.msg(f"|wTaste:|n {recipe.get('taste', 'N/A')}")
        caller.msg(f"|wSmell:|n {recipe.get('smell', 'N/A')}")
        caller.msg("")
        caller.msg(f"|wConsume (self):|n {recipe.get('msg_eat_self', 'N/A')}")
        caller.msg(f"|wConsume (others):|n {recipe.get('msg_eat_others', 'N/A')}")
        caller.msg(f"|wFinish (self):|n {recipe.get('msg_finish_self', 'N/A')}")
        caller.msg(f"|wFinish (others):|n {recipe.get('msg_finish_others', 'N/A')}")
        caller.msg(f"|wKeywords:|n {', '.join(recipe.get('keywords', []))}")
        
        if status == "pending":
            caller.msg("")
            caller.msg(f"|wapproverecipe #{recipe_id} <difficulty>|n to approve")
            caller.msg(f"|wrejectrecipe #{recipe_id} <reason>|n to reject")


class CmdApproveRecipe(Command):
    """
    Approve a pending recipe.
    
    Usage:
        approverecipe #<id> <difficulty>
    
    Difficulty should be 0-100:
        0-20:   Novice - simple preparations
        21-45:  Competent - home cooking
        46-75:  Seasoned - professional level
        76-89:  Advanced - high-end restaurant
        90-100: Mastery - world-class chef
    
    Example:
        approverecipe #5 35
    """
    key = "approverecipe"
    aliases = ["approve recipe"]
    locks = "cmd:perm(Builder)"
    help_category = "Admin"
    
    def func(self):
        caller = self.caller
        
        if not self.args:
            caller.msg("Usage: approverecipe #<id> <difficulty>")
            caller.msg("Use 'recipes scale' to see the difficulty scale.")
            return
        
        parts = self.args.strip().split()
        if len(parts) < 2:
            caller.msg("Usage: approverecipe #<id> <difficulty>")
            return
        
        # Parse recipe ID
        id_str = parts[0]
        if id_str.startswith('#'):
            id_str = id_str[1:]
        
        try:
            recipe_id = int(id_str)
        except ValueError:
            caller.msg("|rInvalid recipe ID.|n")
            return
        
        # Parse difficulty
        try:
            difficulty = int(parts[1])
            if not 0 <= difficulty <= 100:
                caller.msg("|rDifficulty must be 0-100.|n")
                return
        except ValueError:
            caller.msg("|rDifficulty must be a number 0-100.|n")
            return
        
        # Get recipe to find creator
        recipe = get_recipe_by_id(recipe_id)
        if not recipe:
            caller.msg(f"|rRecipe #{recipe_id} not found.|n")
            return
        
        if recipe.get("status") != "pending":
            caller.msg(f"|rRecipe #{recipe_id} is not pending approval.|n")
            return
        
        # Approve
        if approve_recipe(recipe_id, caller, difficulty):
            caller.msg(f"|gRecipe #{recipe_id} '{recipe['name']}' approved with difficulty {difficulty}.|n")
            
            # Notify creator if online
            creator_dbref = recipe.get("creator_dbref")
            if creator_dbref:
                from evennia.utils.search import search_object
                creators = search_object(creator_dbref)
                if creators:
                    creator = creators[0]
                    creator.msg(f"|g[RECIPE APPROVED]|n Your recipe '{recipe['name']}' has been approved! You can now cook it at any kitchenette.|n")
        else:
            caller.msg(f"|rFailed to approve recipe #{recipe_id}.|n")


class CmdRejectRecipe(Command):
    """
    Reject a pending recipe.
    
    Usage:
        rejectrecipe #<id> <reason>
    
    Example:
        rejectrecipe #5 Description too vague, please add more detail.
    """
    key = "rejectrecipe"
    aliases = ["reject recipe"]
    locks = "cmd:perm(Builder)"
    help_category = "Admin"
    
    def func(self):
        caller = self.caller
        
        if not self.args:
            caller.msg("Usage: rejectrecipe #<id> <reason>")
            return
        
        parts = self.args.strip().split(None, 1)
        if len(parts) < 2:
            caller.msg("Usage: rejectrecipe #<id> <reason>")
            return
        
        # Parse recipe ID
        id_str = parts[0]
        if id_str.startswith('#'):
            id_str = id_str[1:]
        
        try:
            recipe_id = int(id_str)
        except ValueError:
            caller.msg("|rInvalid recipe ID.|n")
            return
        
        reason = parts[1]
        
        # Get recipe to find creator
        recipe = get_recipe_by_id(recipe_id)
        if not recipe:
            caller.msg(f"|rRecipe #{recipe_id} not found.|n")
            return
        
        if recipe.get("status") != "pending":
            caller.msg(f"|rRecipe #{recipe_id} is not pending approval.|n")
            return
        
        recipe_name = recipe.get("name", "Unknown")
        
        # Reject
        if reject_recipe(recipe_id, reason):
            caller.msg(f"|yRecipe #{recipe_id} '{recipe_name}' rejected.|n")
            
            # Notify creator if online
            creator_dbref = recipe.get("creator_dbref")
            if creator_dbref:
                from evennia.utils.search import search_object
                creators = search_object(creator_dbref)
                if creators:
                    creator = creators[0]
                    creator.msg(f"|r[RECIPE REJECTED]|n Your recipe '{recipe_name}' was not approved.")
                    creator.msg(f"|wReason:|n {reason}")
        else:
            caller.msg(f"|rFailed to reject recipe #{recipe_id}.|n")


class CmdEditRecipe(Command):
    """
    Edit a recipe you've created.
    
    Usage:
        editrecipe #<id>
    
    This allows you to edit recipes you've created, either pending approval
    or already approved. The recipe designer menu will load with your current
    recipe data so you can make changes.
    
    Example:
        editrecipe #5
    """
    key = "editrecipe"
    aliases = ["edit recipe"]
    locks = "cmd:all()"
    help_category = "Cooking"
    
    def func(self):
        caller = self.caller
        
        if not self.args:
            caller.msg("Usage: editrecipe #<id>")
            return
        
        # Parse recipe ID
        recipe_id_str = self.args.strip().lstrip('#')
        try:
            recipe_id = int(recipe_id_str)
        except ValueError:
            caller.msg("Usage: editrecipe #<id> (e.g., editrecipe #5)")
            return
        
        # Get recipe
        recipe = get_recipe_by_id(recipe_id)
        if not recipe:
            caller.msg(f"|rRecipe #{recipe_id} not found.|n")
            return
        
        # Check if caller is the creator or an admin
        creator_dbref = recipe.get("creator_dbref")
        is_creator = str(caller.dbref) == str(creator_dbref)
        is_admin = caller.check_permstring("Builder")
        
        if not (is_creator or is_admin):
            caller.msg(f"|rYou can only edit recipes you created.|n")
            return
        
        # Load recipe data into caller's recipe design state
        caller.ndb._recipe_design = {
            "name": recipe.get("name", ""),
            "is_food": recipe.get("is_food", True),
            "description": recipe.get("description", ""),
            "taste": recipe.get("taste", ""),
            "smell": recipe.get("smell", ""),
            "msg_eat_self": recipe.get("msg_eat_self", ""),
            "msg_eat_others": recipe.get("msg_eat_others", ""),
            "msg_finish_self": recipe.get("msg_finish_self", ""),
            "msg_finish_others": recipe.get("msg_finish_others", ""),
            "keywords": recipe.get("keywords", []),
            "difficulty": recipe.get("difficulty", 50),
            "nutritious": recipe.get("nutritious", False),
            "recipe_id": recipe_id,  # Track original ID for updates
        }
        
        caller.msg(f"|gLoading recipe #{recipe_id}: {recipe.get('name')}|n")
        
        # Start the EvMenu with edit context
        from evennia.utils.evmenu import EvMenu
        
        RecipeDesignMenu(
            caller,
            "commands.CmdCooking",
            startnode="node_edit_main_menu",
            cmdset_mergetype="Replace",
            cmd_on_exit=None,
        )


def node_edit_main_menu(caller, raw_string, **kwargs):
    """Main menu for editing an existing recipe."""
    data = _recipe_data(caller)
    recipe_id = data.get("recipe_id")
    recipe_status = "Editing Recipe"
    if recipe_id:
        recipe_status = f"Editing Recipe #{recipe_id}"
    
    def status(key):
        """Show status indicator for field."""
        return "|g✓|n" if data.get(key) else "|r✗|n"
    
    text = f"""
|c=== {recipe_status} ===|n
|yChanges are NOT saved until you submit.|n

|w1.|n {status('name')} Name: {data.get('name') or '(not set)'}
|w2.|n {status('is_food')} Type: {'Food' if data.get('is_food', True) else 'Drink'}
|w3.|n {status('description')} Description: {len(data.get('description', '')) or 0} chars
|w4.|n {status('taste')} Taste: {len(data.get('taste', '')) or 0} chars
|w5.|n {status('smell')} Smell: {len(data.get('smell', '')) or 0} chars
|w6.|n {status('msg_eat_self')} Consume Message (1st person)
|w7.|n {status('msg_eat_others')} Consume Message (3rd person)
|w8.|n {status('msg_finish_self')} Finish Message (1st person)
|w9.|n {status('msg_finish_others')} Finish Message (3rd person)
|w10.|n Keywords: {', '.join(data.get('keywords', [])) or '(none)'}
|w11.|n Difficulty: |w{data.get('difficulty', 50)}|n

|w[R]|n Review changes
|w[S]|n Save changes (submit for re-approval)
|w[Q]|n Quit without saving
"""
    
    options = (
        {"key": "1", "goto": "node_set_name"},
        {"key": "2", "goto": "node_set_type"},
        {"key": "3", "goto": "node_set_description"},
        {"key": "4", "goto": "node_set_taste"},
        {"key": "5", "goto": "node_set_smell"},
        {"key": "6", "goto": "node_set_eat_self"},
        {"key": "7", "goto": "node_set_eat_others"},
        {"key": "8", "goto": "node_set_finish_self"},
        {"key": "9", "goto": "node_set_finish_others"},
        {"key": "10", "goto": "node_set_keywords"},
        {"key": "11", "goto": "node_set_difficulty"},
        {"key": "r", "goto": "node_review"},
        {"key": "R", "goto": "node_review"},
        {"key": "s", "goto": "node_edit_submit"},
        {"key": "S", "goto": "node_edit_submit"},
        {"key": "q", "goto": "node_quit"},
        {"key": "Q", "goto": "node_quit"},
        {"key": "_default", "goto": "node_edit_main_menu"},
    )
    
    return text, options


def node_edit_submit(caller, raw_string, **kwargs):
    """Submit edited recipe for re-approval."""
    data = _recipe_data(caller)
    recipe_id = data.get("recipe_id")
    
    # Validate all required fields
    required = ['name', 'description', 'taste', 'smell', 
                'msg_eat_self', 'msg_eat_others', 'msg_finish_self', 'msg_finish_others']
    missing = [f for f in required if not data.get(f)]
    
    if missing:
        text = f"""
|r=== Cannot Submit ===|n

The following required fields are not set:
{', '.join(missing)}

Please complete all fields before submitting.

|w[B]|n Back to main menu
"""
        options = (
            {"key": "b", "goto": "node_edit_main_menu"},
            {"key": "B", "goto": "node_edit_main_menu"},
            {"key": "_default", "goto": "node_edit_main_menu"},
        )
        return text, options
    
    # Confirm submission
    text = f"""
|c=== Confirm Re-Submission ===|n

You are about to submit your changes to |w{data.get('name')}|n for re-review.

The recipe will return to pending status and an admin will review your changes.
You will be notified when the updated recipe is approved.

|w[Y]|n Yes, submit changes for re-approval
|w[N]|n No, go back
"""
    
    def _confirm_resubmit(caller, raw_string, **kwargs):
        raw_string = raw_string.strip().lower()
        
        if raw_string in ('y', 'yes'):
            data = _recipe_data(caller)
            recipe_id = data.get("recipe_id")
            
            # Update the recipe
            storage = get_recipe_storage()
            all_recipes = (storage.db.recipes or []) + (storage.db.pending_recipes or [])
            
            recipe_found = False
            for recipe in all_recipes:
                if recipe.get("id") == recipe_id:
                    # Update recipe fields
                    recipe["name"] = data["name"]
                    recipe["is_food"] = data["is_food"]
                    recipe["description"] = data["description"]
                    recipe["taste"] = data["taste"]
                    recipe["smell"] = data["smell"]
                    recipe["msg_eat_self"] = data["msg_eat_self"]
                    recipe["msg_eat_others"] = data["msg_eat_others"]
                    recipe["msg_finish_self"] = data["msg_finish_self"]
                    recipe["msg_finish_others"] = data["msg_finish_others"]
                    recipe["keywords"] = data.get("keywords", [])
                    recipe["difficulty"] = data.get("difficulty", 50)
                    recipe["nutritious"] = data.get("nutritious", False)
                    
                    # If approved, revert to pending for re-review
                    if recipe.get("status") == "approved":
                        recipe["status"] = "pending"
                        # Move back to pending queue
                        approved = storage.db.recipes or []
                        approved = [r for r in approved if r.get("id") != recipe_id]
                        storage.db.recipes = approved
                        
                        pending = storage.db.pending_recipes or []
                        pending.append(recipe)
                        storage.db.pending_recipes = pending
                    else:
                        # Just update in-place for pending recipes
                        storage.db.recipes = storage.db.recipes or []
                        storage.db.pending_recipes = storage.db.pending_recipes or []
                    
                    recipe_found = True
                    break
            
            if recipe_found:
                caller.msg(f"|g=== Recipe Updated ===|n")
                caller.msg(f"Your recipe |w{data['name']}|n has been updated.")
                if recipe.get("status") == "pending":
                    caller.msg("It will be reviewed by an admin soon.")
                else:
                    caller.msg("|yYour previously approved recipe has been returned to pending status for re-review.|n")
                
                # Clear design data
                if hasattr(caller.ndb, '_recipe_design'):
                    del caller.ndb._recipe_design
                
                # Close menu
                if hasattr(caller.ndb, '_evmenu'):
                    caller.ndb._evmenu.close_menu()
                return None
            else:
                caller.msg(f"|rFailed to find recipe #{recipe_id}.|n")
                return "node_edit_main_menu"
        
        return "node_edit_main_menu"
    
    options = ({"key": "_default", "goto": _confirm_resubmit},)
    return text, options


class CmdAdminCreateFood(Command):
    """
    Create a food/drink item for shops, stores, and restaurants (admin only).
    
    Usage:
        admincreatefood <name> = <description>
        admincreatefood <name> = <description> | <taste>
        admincreatefood <name> = <description> | <taste> | <smell>
        admincreatefood <name> = <description> | <taste> | <smell> | <type>
    
    Type: 'food' (default) or 'drink'
    
    This creates consumable food/drink items for shops, stores, and restaurants.
    They can be purchased and consumed by players but don't have a difficulty rating.
    
    Custom Consume Messages:
    To set custom consume messages, edit the item after creation with:
        @set <item>/msg_eat_self = "Your custom message"
        @set <item>/msg_eat_others = "$Your message where $ is the consumer"
    
    For Shops:
    Set the value/price with:
        @set <item>/value = <number>
    
    Examples:
        admincreatefood burger = A juicy burger | Savory and delicious | Meat aroma
        admincreatefood wine = A glass of fine wine | Fruity and smooth | Earthy | drink
        admincreatefood ramen = Steaming hot ramen | Umami-rich | Broth aroma
    """
    key = "admincreatefood"
    aliases = ["createfood", "makefood"]
    locks = "cmd:perm(Builder)"
    help_category = "Admin"
    
    def func(self):
        caller = self.caller
        
        if not self.args or '=' not in self.args:
            caller.msg("Usage: admincreatefood <name> = <description> | <taste> | <smell> | <type>")
            caller.msg("Type: 'food' (default) or 'drink'")
            caller.msg("\nExample: admincreatefood burger = A juicy burger | Savory | Meat aroma")
            return
        
        # Parse arguments
        name_part, desc_part = self.args.split('=', 1)
        name = name_part.strip()
        
        if not name:
            caller.msg("|rFood name cannot be empty.|n")
            return
        
        # Parse description, taste, smell, and type
        parts = [p.strip() for p in desc_part.split('|')]
        description = parts[0] if len(parts) > 0 else ""
        taste = parts[1] if len(parts) > 1 else ""
        smell = parts[2] if len(parts) > 2 else ""
        item_type = parts[3].lower() if len(parts) > 3 else "food"
        
        if item_type not in ("food", "drink"):
            caller.msg("|rType must be 'food' or 'drink'.|n")
            return
        
        is_food = (item_type == "food")
        action = "eat" if is_food else "drink"
        
        # Create the food item
        try:
            food = create_object(
                FoodItem,
                key=name,
                location=caller,
                attributes=[
                    ("is_food", is_food),
                    ("food_name", name),
                    ("food_desc", description),
                    ("food_taste", taste),
                    ("food_smell", smell),
                    ("msg_eat_self", f"You {action} the {name}."),
                    ("msg_eat_others", f"$You {action} the {name}."),
                    ("msg_finish_self", f"You finish the {name}."),
                    ("msg_finish_others", f"$You finish the {name}."),
                    ("creator_dbref", caller.dbref),
                    ("creator_name", caller.key),
                    ("created_at", datetime.now()),
                    ("is_shop_item", True),
                ]
            )
            
            caller.msg(f"|g=== Food Item Created ===|n")
            caller.msg(f"|wName:|n {name}")
            caller.msg(f"|wType:|n {item_type.capitalize()}")
            caller.msg(f"|wDescription:|n {description}")
            if taste:
                caller.msg(f"|wTaste:|n {taste}")
            if smell:
                caller.msg(f"|wSmell:|n {smell}")
            caller.msg(f"|wCreated by:|n {caller.key}")
            
            caller.msg(f"\n|c[To add to a shop]:|n")
            caller.msg(f"Use your shop system to add this item. Players can now purchase and consume it.")
            
            caller.msg(f"\n|c[To customize]:|n")
            caller.msg(f"@set {food.dbref}/msg_eat_self = Your custom message")
            caller.msg(f"@set {food.dbref}/msg_eat_others = Custom message with $")
            caller.msg(f"@set {food.dbref}/value = <price>")
            
            caller.location.msg_contents(
                f"{caller.key} creates {food.get_display_name(caller)}.",
                exclude=[caller]
            )
            
        except Exception as e:
            caller.msg(f"|rError creating food: {e}|n")


class CmdAdminDesignRecipe(Command):
    """
    Admin recipe designer - creates recipes that are auto-approved.
    
    Usage:
        adesign
    
    Opens the recipe designer menu where admins can create a recipe.
    Unlike player-designed recipes, admin recipes are automatically approved
    and immediately available for cooking.
    """
    key = "adesign"
    aliases = ["admindesign", "admin design"]
    locks = "cmd:perm(Builder)"
    help_category = "Admin"
    
    def func(self):
        caller = self.caller
        
        # Mark this as an admin design session
        caller.ndb._admin_recipe_design = True
        
        # Start the EvMenu
        RecipeDesignMenu(
            caller,
            "commands.CmdCooking",
            startnode="node_admin_main_menu",
            cmdset_mergetype="Replace",
            cmd_on_exit=None,
        )


def node_admin_main_menu(caller, raw_string, **kwargs):
    """Admin main menu for recipe design."""
    data = _recipe_data(caller)
    
    # Build status display
    def status(field):
        if field == 'is_food':
            return "|g[SET]|n"
        return "|g[SET]|n" if data.get(field) else "|r[---]|n"
    
    item_type = "Food" if data.get("is_food", True) else "Drink"
    
    text = f"""
|c=== Admin Recipe Designer ===|n

Design a new {item_type.lower()} recipe. Admin recipes are |gauto-approved|n.

|wCurrent Recipe:|n {data.get('name') or '(unnamed)'}

|w1.|n {status('name')} Name
|w2.|n {status('is_food')} Type: |w{item_type}|n
|w3.|n {status('description')} Description
|w4.|n {status('taste')} Taste
|w5.|n {status('smell')} Smell
|w6.|n {status('msg_eat_self')} Consume Message (1st person)
|w7.|n {status('msg_eat_others')} Consume Message (3rd person)
|w8.|n {status('msg_finish_self')} Finish Message (1st person)
|w9.|n {status('msg_finish_others')} Finish Message (3rd person)
|w10.|n Keywords: {', '.join(data.get('keywords', [])) or '(none)'}
|w11.|n Difficulty: |w{data.get('difficulty', 50)}|n
|w12.|n Nutritious: {'|g✓|n' if data.get('nutritious', False) else '|r✗|n'} (provides 2-hour healing buff)

|w[R]|n Review before saving
|w[S]|n Save recipe (auto-approved)
|w[Q]|n Quit without saving
"""
    
    options = (
        {"key": "1", "goto": "node_set_name"},
        {"key": "2", "goto": "node_set_type"},
        {"key": "3", "goto": "node_set_description"},
        {"key": "4", "goto": "node_set_taste"},
        {"key": "5", "goto": "node_set_smell"},
        {"key": "6", "goto": "node_set_eat_self"},
        {"key": "7", "goto": "node_set_eat_others"},
        {"key": "8", "goto": "node_set_finish_self"},
        {"key": "9", "goto": "node_set_finish_others"},
        {"key": "10", "goto": "node_set_keywords"},
        {"key": "11", "goto": "node_admin_set_difficulty"},
        {"key": "12", "goto": "node_admin_set_nutritious"},
        {"key": "r", "goto": "node_admin_review"},
        {"key": "R", "goto": "node_admin_review"},
        {"key": "s", "goto": "node_admin_submit"},
        {"key": "S", "goto": "node_admin_submit"},
        {"key": "q", "goto": "node_quit"},
        {"key": "Q", "goto": "node_quit"},
        {"key": "_default", "goto": "node_admin_main_menu"},
    )
    return text, options


def node_admin_set_difficulty(caller, raw_string, **kwargs):
    """Set recipe difficulty (admin only)."""
    data = _recipe_data(caller)
    current = data.get("difficulty", 50)
    
    text = f"""
|c=== Set Difficulty ===|n

Current difficulty: |w{current}|n

Difficulty scale:
  |g0-20|n:   Novice - simple preparations
  |y21-45|n:  Competent - home cooking
  |m46-75|n:  Seasoned - professional level
  |r76-89|n:  Advanced - high-end restaurant
  |R90-100|n: Mastery - world-class chef

Enter a number from 0-100, or |w[B]|n to go back.
"""
    
    def _set_difficulty(caller, raw_string, **kwargs):
        raw_string = raw_string.strip().lower()
        data = _recipe_data(caller)
        
        if raw_string in ('b', 'back'):
            return "node_admin_main_menu"
        
        try:
            difficulty = int(raw_string)
            if 0 <= difficulty <= 100:
                data["difficulty"] = difficulty
                caller.msg(f"|gDifficulty set to:|n {difficulty}")
                return "node_admin_main_menu"
            else:
                caller.msg("|rDifficulty must be between 0 and 100.|n")
                return "node_admin_set_difficulty"
        except ValueError:
            caller.msg("|rPlease enter a valid number.|n")
            return "node_admin_set_difficulty"
    
    options = ({"key": "_default", "goto": _set_difficulty},)
    return text, options


def node_admin_set_nutritious(caller, raw_string, **kwargs):
    """Toggle nutritious flag (admin only)."""
    data = _recipe_data(caller)
    current_status = data.get("nutritious", False)
    
    text = f"""
|c=== Toggle Nutritious Flag ===|n

Nutritious food provides a minor healing buff for 2 hours when consumed.

Current status: {'|gYes - This food is nutritious|n' if current_status else '|rNo - This food is regular|n'}

|w[Y]|n Yes, make this nutritious
|w[N]|n No, make this regular food
|w[B]|n Go back without changing
"""
    
    def _toggle_nutritious(caller, raw_string, **kwargs):
        raw_string = raw_string.strip().lower()
        data = _recipe_data(caller)
        
        if raw_string in ('y', 'yes'):
            data["nutritious"] = True
            caller.msg("|gThis recipe is now marked as nutritious.|n")
            return "node_admin_main_menu"
        elif raw_string in ('n', 'no'):
            data["nutritious"] = False
            caller.msg("|yThis recipe is now marked as regular food.|n")
            return "node_admin_main_menu"
        elif raw_string in ('b', 'back'):
            return "node_admin_main_menu"
        else:
            return "node_admin_set_nutritious"
    
    options = ({"key": "_default", "goto": _toggle_nutritious},)
    return text, options


def node_admin_review(caller, raw_string, **kwargs):
    """Review recipe before saving (admin)."""
    data = _recipe_data(caller)
    
    item_type = "Food" if data.get("is_food", True) else "Drink"
    action = "eat" if data.get("is_food", True) else "drink"
    
    text = f"""
|c=== Admin Recipe Review ===|n

|wName:|n {data.get('name') or '|r(not set)|n'}
|wType:|n {item_type}
|wDifficulty:|n {data.get('difficulty', 50)}

|wDescription:|n
{data.get('description') or '|r(not set)|n'}

|wTaste:|n
{data.get('taste') or '|r(not set)|n'}

|wSmell:|n
{data.get('smell') or '|r(not set)|n'}

|wConsume Message (you see when you {action}):|n
{data.get('msg_eat_self') or '|r(not set)|n'}

|wConsume Message (others see):|n
{data.get('msg_eat_others') or '|r(not set)|n'}

|wFinish Message (you see):|n
{data.get('msg_finish_self') or '|r(not set)|n'}

|wFinish Message (others see):|n
{data.get('msg_finish_others') or '|r(not set)|n'}

|wKeywords:|n {', '.join(data.get('keywords', [])) or '(none)'}

|w[B]|n Back to main menu
"""
    
    options = (
        {"key": "b", "goto": "node_admin_main_menu"},
        {"key": "B", "goto": "node_admin_main_menu"},
        {"key": "_default", "goto": "node_admin_main_menu"},
    )
    return text, options


def node_admin_submit(caller, raw_string, **kwargs):
    """Save and auto-approve recipe (admin)."""
    data = _recipe_data(caller)
    
    # Validate all required fields
    required = ['name', 'description', 'taste', 'smell', 
                'msg_eat_self', 'msg_eat_others', 'msg_finish_self', 'msg_finish_others']
    missing = [f for f in required if not data.get(f)]
    
    if missing:
        text = f"""
|r=== Cannot Save ===|n

The following required fields are not set:
{', '.join(missing)}

Please complete all fields before saving.

|w[B]|n Back to main menu
"""
        options = (
            {"key": "b", "goto": "node_admin_main_menu"},
            {"key": "B", "goto": "node_admin_main_menu"},
            {"key": "_default", "goto": "node_admin_main_menu"},
        )
        return text, options
    
    # Confirm save
    text = f"""
|c=== Confirm Save ===|n

You are about to save |w{data.get('name')}|n as an |gauto-approved|n recipe.

This recipe will be immediately available for cooking by all players.

|w[Y]|n Yes, save and approve
|w[N]|n No, go back
"""
    
    def _confirm_save(caller, raw_string, **kwargs):
        raw_string = raw_string.strip().lower()
        
        if raw_string in ('y', 'yes'):
            data = _recipe_data(caller)
            
            # Create recipe entry (auto-approved)
            recipe_data = {
                "name": data["name"],
                "is_food": data["is_food"],
                "description": data["description"],
                "taste": data["taste"],
                "smell": data["smell"],
                "msg_eat_self": data["msg_eat_self"],
                "msg_eat_others": data["msg_eat_others"],
                "msg_finish_self": data["msg_finish_self"],
                "msg_finish_others": data["msg_finish_others"],
                "keywords": data.get("keywords", []),
                "creator_dbref": caller.dbref,
                "creator_name": caller.key,
                "created_at": datetime.now(),
                "difficulty": data.get("difficulty", 50),
                "nutritious": data.get("nutritious", False),
                "status": "approved",
                "is_admin_created": True,
            }
            
            # Add directly to approved recipes
            storage = get_recipe_storage()
            recipes = storage.db.recipes or []
            
            # Get lowest available ID
            recipe_id = get_next_available_recipe_id()
            
            recipe_data["id"] = recipe_id
            recipes.append(recipe_data)
            storage.db.recipes = recipes
            
            caller.msg(f"|g=== Recipe Saved ===|n")
            caller.msg(f"Your recipe |w{data['name']}|n has been saved and auto-approved.")
            caller.msg(f"Recipe ID: |w#{recipe_id}|n")
            caller.msg(f"Difficulty: |w{data.get('difficulty', 50)}|n")
            caller.msg("Players can now cook this recipe at any kitchenette.")
            
            # Clear design data
            if hasattr(caller.ndb, '_recipe_design'):
                del caller.ndb._recipe_design
            if hasattr(caller.ndb, '_admin_recipe_design'):
                del caller.ndb._admin_recipe_design
            
            # Explicitly close the menu
            if hasattr(caller.ndb, '_evmenu'):
                caller.ndb._evmenu.close_menu()
            return None  # Exit menu
        
        return "node_admin_main_menu"
    
    options = ({"key": "_default", "goto": _confirm_save},)
    return text, options


# =============================================================================
# COMMAND SET CONTAINER
# =============================================================================

class CookingCmdSet:
    """Container for cooking commands."""
    
    @staticmethod
    def get_commands():
        return [
            CmdDesignRecipe,
            CmdCook,
            CmdEat,
            CmdDrink,
            CmdTaste,
            CmdSmellFood,
            CmdSpawnKitchenette,
            CmdSpawnIngredients,
            CmdRecipes,
            CmdApproveRecipe,
            CmdRejectRecipe,
            CmdAdminCreateFood,
            CmdAdminDesignRecipe,
        ]
