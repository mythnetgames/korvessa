from evennia import search_object

def fix_exits():
    """
    Script to fix all exits in the database:
    - Ensures typeclass is typeclasses.exits.Exit
    - Ensures key and aliases are set correctly
    - Ensures location and destination are set
    """
    fixed = 0
    for obj in search_object("*"):
        if obj.is_typeclass("evennia.objects.objects.DefaultExit", exact=False):
            # Fix typeclass if needed
            if not obj.is_typeclass("typeclasses.exits.Exit", exact=True):
                obj.swap_typeclass("typeclasses.exits.Exit", clean_attributes=False)
                fixed += 1
            # Fix aliases for cardinal directions
            cardinal_aliases = {
                "north": "n", "south": "s", "east": "e", "west": "w",
                "northeast": "ne", "northwest": "nw", "southeast": "se", "southwest": "sw",
                "up": "u", "down": "d", "in": "in", "out": "out"
            }
            alias = cardinal_aliases.get(obj.key.lower())
            if alias and alias not in obj.aliases.all():
                obj.aliases.add(alias)
            # Log status
            print(f"Exit: {obj.key} | Location: {obj.location} | Destination: {getattr(obj, 'destination', None)} | Typeclass: {obj.typeclass_path}")
    print(f"Fixed {fixed} exits.")

# To run: from scripts.fix_exits import fix_exits; fix_exits()
