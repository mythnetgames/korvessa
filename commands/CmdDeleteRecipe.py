"""
Delete an approved recipe (admin only).

Usage:
    deleterecipe #<id>

Deletes the approved recipe with the given ID. Works for both admin and player recipes.
"""

from evennia.commands.command import Command
from commands.CmdCooking import get_recipe_storage, get_recipe_by_id

class CmdDeleteRecipe(Command):
    """
    Delete an approved recipe by ID (admin only).
    
    Usage:
        deleterecipe #<id>
    """
    key = "deleterecipe"
    aliases = ["delete recipe", "removerecipe", "remrecipe"]
    locks = "cmd:perm(Builder)"
    help_category = "Admin"
    
    def func(self):
        caller = self.caller
        args = self.args.strip()
        if not args or not args.startswith('#'):
            caller.msg("Usage: deleterecipe #<id>")
            return
        try:
            recipe_id = int(args[1:])
        except ValueError:
            caller.msg("|rInvalid recipe ID.|n")
            return
        storage = get_recipe_storage()
        recipes = storage.db.recipes or []
        recipe = next((r for r in recipes if r.get("id") == recipe_id), None)
        if not recipe:
            caller.msg(f"|rRecipe #{recipe_id} not found or not approved.|n")
            return
        recipes = [r for r in recipes if r.get("id") != recipe_id]
        storage.db.recipes = recipes
        caller.msg(f"|gRecipe #{recipe_id} ('{recipe.get('name','?')}') deleted.|n")
        caller.location.msg_contents(f"{caller.key} deletes recipe #{recipe_id} ({recipe.get('name','?')}).", exclude=[caller])
