"""
Tailoring Commands - Create custom clothing through the tailoring skill system.

Commands:
- spawnmaterial: Admin command to create fresh material
- tname: Set the name of fresh material
- coverage: Configure body coverage for clothing
- color: Set the primary color
- see-thru: Toggle see-through state
- tdescribe: Set the item description
- messages: Set wear/remove/worn messages
- check: Verify requirements before finalizing
- finalize: Complete the clothing item
"""

from evennia import Command
from evennia.utils.search import search_object
from evennia import create_object
from typeclasses.tailoring import (
    FreshMaterial, VALID_COVERAGE_LOCATIONS, 
    COVERAGE_LOCATION_NAMES, LAYER_KEYWORDS, determine_layer_from_name
)


class CmdSpawnMaterial(Command):
    """
    Create fresh material for tailoring.
    
    Usage:
        spawnmaterial <material_type>
        spawnmaterial <material_type> to <character>
    
    Material types: cloth, leather, silk, denim, wool, synthetic, mesh
    
    Examples:
        spawnmaterial cloth
        spawnmaterial leather to John
        spawnmaterial silk
    """
    key = "spawnmaterial"
    aliases = ["spawn-material", "creatematerial"]
    locks = "cmd:perm(Builder)"
    help_category = "Building"
    
    VALID_MATERIALS = ["cloth", "leather", "silk", "denim", "wool", "synthetic", "mesh", "cotton", "linen", "velvet", "satin", "lace", "nylon", "polyester", "kevlar"]
    
    def func(self):
        caller = self.caller
        
        if not self.args:
            caller.msg("Usage: spawnmaterial <material_type> [to <character>]")
            caller.msg(f"Valid materials: {', '.join(self.VALID_MATERIALS)}")
            return
        
        args = self.args.strip()
        target = caller
        material_type = args
        
        # Check for "to <character>" syntax
        if " to " in args.lower():
            parts = args.lower().split(" to ", 1)
            material_type = parts[0].strip()
            target_name = parts[1].strip()
            
            # Find target character
            targets = search_object(target_name, typeclass="typeclasses.characters.Character")
            if not targets:
                targets = search_object(target_name, typeclass="typeclasses.npcs.NPC")
            
            if not targets:
                caller.msg(f"Character '{target_name}' not found.")
                return
            target = targets[0]
        
        material_type = material_type.lower()
        
        if material_type not in self.VALID_MATERIALS:
            caller.msg(f"Unknown material type: {material_type}")
            caller.msg(f"Valid materials: {', '.join(self.VALID_MATERIALS)}")
            return
        
        # Create the fresh material
        material = create_object(
            FreshMaterial,
            key=f"fresh {material_type}",
            location=target,
            attributes=[
                ("material_type", material_type),
                ("desc", f"A piece of fresh {material_type} ready to be tailored into clothing."),
                ("creator_dbref", caller.dbref),
                ("base_value", 0),
            ]
        )
        
        caller.msg(f"|gCreated fresh {material_type} in {target.key}'s inventory.|n")
        if target != caller:
            target.msg(f"|y{caller.key} has given you some fresh {material_type} for tailoring.|n")


class CmdTailorName(Command):
    """
    Set the name of your fresh material.
    
    Usage:
        tname <material>=<name>
    
    The name will be used to target the item and will be utilized in
    several messages. Do not include 'pair of' - the command will 
    prompt you if needed.
    
    Certain words in the name determine the clothing layer:
    - Layer 0: bikini, panties, underwear, bra, thong, boxers, stockings
    - Layer 1: (default - everything else)
    - Layer 2: blindfold, glasses, vest
    - Layer 3: jacket, waistcoat
    - Layer 4: coat, robe, trenchcoat, duster, apron, scrubs
    - Layer 5: tie, boots, scarf, belt, badge
    
    Examples:
        tname fresh cloth=silk blouse
        tname fresh leather=black leather jacket
    """
    key = "tname"
    aliases = ["tailor-name", "tailorname"]
    locks = "cmd:all()"
    help_category = "Tailoring"
    
    def func(self):
        caller = self.caller
        
        if not self.args or "=" not in self.args:
            caller.msg("Usage: tname <material>=<name>")
            return
        
        material_name, clothing_name = self.args.split("=", 1)
        material_name = material_name.strip()
        clothing_name = clothing_name.strip()
        
        if not clothing_name:
            caller.msg("You must specify a name for the clothing.")
            return
        
        # Find the material in inventory
        material = caller.search(material_name, location=caller, quiet=True)
        if not material:
            caller.msg(f"You don't have '{material_name}'.")
            return
        if isinstance(material, list):
            material = material[0]
        
        if not getattr(material, 'is_fresh_material', False):
            caller.msg(f"{material.key} is not fresh material for tailoring.")
            return
        
        # Set the name
        material.clothing_name = clothing_name
        
        # Determine layer from name
        layer = determine_layer_from_name(clothing_name)
        layer_desc = {0: "Undergarments", 1: "Base clothing", 2: "Accessories", 
                     3: "Outer wear", 4: "Heavy outerwear", 5: "Top layer"}
        
        # Mark as unfinalized if it was finalized
        if material.is_finalized:
            material.is_finalized = False
            caller.msg("|yChanging the name has unfinalized this item.|n")
        
        caller.msg(f"|gSet clothing name to: {clothing_name}|n")
        caller.msg(f"|cLayer: {layer} ({layer_desc.get(layer, 'Unknown')})|n")


class CmdTailorCoverage(Command):
    """
    Configure what body locations a piece of clothing covers.
    
    Usage:
        coverage <material>=<locations>
        coverage <material>                  - View current coverage
        coverage/list                        - List all valid locations
    
    Locations should be comma-separated. It's fine to avoid setting
    locations that your article may cover partially, allowing underlying
    articles to show through.
    
    Examples:
        coverage fresh cloth=chest,back,abdomen
        coverage fresh leather=chest,back,abdomen,larm,rarm
        coverage fresh cloth=head,face
    """
    key = "coverage"
    aliases = ["tailor-coverage"]
    locks = "cmd:all()"
    help_category = "Tailoring"
    
    def func(self):
        caller = self.caller
        # Ensure switches exists (for Evennia compatibility)
        switches = getattr(self, "switches", [])
        # Handle /list switch - check both switches and args
        if "list" in switches or (self.args and self.args.strip().lower() == "/list"):
            caller.msg("|c=== Valid Coverage Locations ===|n")
            for loc, name in sorted(COVERAGE_LOCATION_NAMES.items()):
                caller.msg(f"  |w{loc}|n - {name}")
            return
        
        if not self.args:
            caller.msg("Usage: coverage <material>=<locations>")
            caller.msg("       coverage/list to see valid locations")
            return
        
        # Check if viewing or setting
        if "=" not in self.args:
            # View current coverage
            material_name = self.args.strip()
            material = caller.search(material_name, location=caller, quiet=True)
            if not material:
                caller.msg(f"You don't have '{material_name}'.")
                return
            if isinstance(material, list):
                material = material[0]
            
            if not getattr(material, 'is_fresh_material', False):
                caller.msg(f"{material.key} is not fresh material for tailoring.")
                return
            
            coverage = material.clothing_coverage or []
            if coverage:
                friendly = [COVERAGE_LOCATION_NAMES.get(loc, loc) for loc in coverage]
                caller.msg(f"|cCurrent coverage:|n {', '.join(friendly)}")
            else:
                caller.msg("|yCoverage not yet set.|n")
            return
        
        material_name, locations_str = self.args.split("=", 1)
        material_name = material_name.strip()
        locations_str = locations_str.strip()
        
        # Find the material
        material = caller.search(material_name, location=caller, quiet=True)
        if not material:
            caller.msg(f"You don't have '{material_name}'.")
            return
        if isinstance(material, list):
            material = material[0]
        
        if not getattr(material, 'is_fresh_material', False):
            caller.msg(f"{material.key} is not fresh material for tailoring.")
            return
        
        # Parse locations
        locations = [loc.strip().lower() for loc in locations_str.split(",")]
        valid_locations = []
        invalid_locations = []
        
        for loc in locations:
            if loc in VALID_COVERAGE_LOCATIONS:
                valid_locations.append(loc)
            else:
                invalid_locations.append(loc)
        
        if invalid_locations:
            caller.msg(f"|rInvalid locations:|n {', '.join(invalid_locations)}")
            caller.msg("Use |wcoverage/list|n to see valid locations.")
            return
        
        if not valid_locations:
            caller.msg("You must specify at least one valid location.")
            return
        
        # Set coverage
        material.clothing_coverage = valid_locations
        
        # Mark as unfinalized
        if material.is_finalized:
            material.is_finalized = False
            caller.msg("|yChanging coverage has unfinalized this item.|n")
        
        friendly = [COVERAGE_LOCATION_NAMES.get(loc, loc) for loc in valid_locations]
        caller.msg(f"|gSet coverage to:|n {', '.join(friendly)}")


class CmdTailorColor(Command):
    """
    Set the primary color of your clothing using xterm 256 colors.
    
    Usage:
        color <material>=<hex_code>:<color_name>
    
    The hex code is a 6-character xterm 256 color (RRGGBB format).
    The color name is what will be displayed in descriptions.
    Use %color in your descriptions to have the colored text inserted.
    
    Common xterm 256 hex codes:
        000000 = black       ff0000 = red         00ff00 = green
        0000ff = blue        ffff00 = yellow      ff00ff = magenta
        00ffff = cyan        ffffff = white       005f00 = forest green
        5f0000 = dark red    5f5f5f = gray        af8700 = gold
        870087 = purple      d75f00 = orange      00afaf = teal
    
    Examples:
        color fresh cloth=870000:crimson
        color fresh leather=000000:black
        color fresh silk=ffffaf:ivory
        color fresh cloth=005f00:forest green
    """
    key = "color"
    aliases = ["tailor-color"]
    locks = "cmd:all()"
    help_category = "Tailoring"
    
    def func(self):
        caller = self.caller
        
        if not self.args or "=" not in self.args:
            caller.msg("Usage: color <material>=<hex_code>:<color_name>")
            caller.msg("Example: color fresh cloth=005f00:forest green")
            return
        
        material_name, color_spec = self.args.split("=", 1)
        material_name = material_name.strip()
        color_spec = color_spec.strip()
        
        if ":" not in color_spec:
            caller.msg("Usage: color <material>=<hex_code>:<color_name>")
            caller.msg("Example: color fresh cloth=005f00:forest green")
            return
        
        color_code, color_name = color_spec.split(":", 1)
        color_code = color_code.strip().lower()
        color_name = color_name.strip().lower()
        
        if not color_code or not color_name:
            caller.msg("You must specify both a hex code and a color name.")
            caller.msg("Example: color fresh cloth=005f00:forest green")
            return
        
        # Validate hex code (should be 6 hex characters)
        if len(color_code) != 6:
            caller.msg(f"|rInvalid hex code:|n {color_code}")
            caller.msg("Hex code must be exactly 6 characters (RRGGBB format).")
            return
        
        try:
            int(color_code, 16)  # Validate it's valid hex
        except ValueError:
            caller.msg(f"|rInvalid hex code:|n {color_code}")
            caller.msg("Hex code must contain only hex characters (0-9, a-f).")
            return
        
        # Find the material
        material = caller.search(material_name, location=caller, quiet=True)
        if not material:
            caller.msg(f"You don't have '{material_name}'.")
            return
        if isinstance(material, list):
            material = material[0]
        
        if not getattr(material, 'is_fresh_material', False):
            caller.msg(f"{material.key} is not fresh material for tailoring.")
            return
        
        # Set the color code and name
        material.clothing_color_code = color_code
        material.clothing_color_name = color_name
        
        # Mark as unfinalized
        if material.is_finalized:
            material.is_finalized = False
            caller.msg("|yChanging the color has unfinalized this item.|n")
        
        # Show preview with actual color
        colored_preview = f"|#{color_code}{color_name}|n"
        caller.msg(f"|gSet primary color to:|n {colored_preview}")
        caller.msg("|cRemember:|n Use %color in your describe and messages worn to insert this colored text.")


class CmdTailorSeeThru(Command):
    """
    Toggle the see-through state of a piece of clothing.
    
    Usage:
        see-thru <material>
    
    Toggles whether underlying clothing, nakeds, tattoos, and cyberware
    show through this piece of clothing. Useful for jewelry, watches,
    eyeglasses, mesh clothing, etc.
    
    Examples:
        see-thru fresh mesh
        see-thru fresh cloth
    """
    key = "see-thru"
    aliases = ["seethru", "seethrough", "see-through"]
    locks = "cmd:all()"
    help_category = "Tailoring"
    
    def func(self):
        caller = self.caller
        
        if not self.args:
            caller.msg("Usage: see-thru <material>")
            return
        
        material_name = self.args.strip()
        
        # Find the material
        material = caller.search(material_name, location=caller, quiet=True)
        if not material:
            caller.msg(f"You don't have '{material_name}'.")
            return
        if isinstance(material, list):
            material = material[0]
        
        if not getattr(material, 'is_fresh_material', False):
            caller.msg(f"{material.key} is not fresh material for tailoring.")
            return
        
        # Toggle see-thru
        material.clothing_see_thru = not material.clothing_see_thru
        
        # Mark as unfinalized
        if material.is_finalized:
            material.is_finalized = False
            caller.msg("|yChanging see-thru has unfinalized this item.|n")
        
        if material.clothing_see_thru:
            caller.msg(f"|gEnabled see-thru:|n Underlying items will show through.")
        else:
            caller.msg(f"|gDisabled see-thru:|n Underlying items will be hidden.")


class CmdTailorDescribe(Command):
    """
    Set the description of your clothing item.
    
    Usage:
        tdescribe <material>=<description>
    
    This is what you see when you look AT the article of clothing,
    not when you look at someone wearing it. You MUST include the
    string %color in the description so that the item's color can
    be dynamically changed.
    
    Avoid using gender pronouns (his, her) or specific names, as the
    item could be worn by someone else. Use pronoun tokens instead:
        %p - possessive (his/her/their)
        %s - subjective (he/she/they)
        %o - objective (him/her/them)
        %r - reflexive (himself/herself/themselves)
    
    Examples:
        tdescribe fresh cloth=This elegant blouse is made of %color silk, with delicate embroidery along the collar.
        tdescribe fresh leather=A well-crafted %color leather jacket with brass buttons.
    """
    key = "tdescribe"
    aliases = ["tailor-describe", "tdesc"]
    locks = "cmd:all()"
    help_category = "Tailoring"
    
    def func(self):
        caller = self.caller
        
        if not self.args or "=" not in self.args:
            caller.msg("Usage: tdescribe <material>=<description>")
            return
        
        material_name, description = self.args.split("=", 1)
        material_name = material_name.strip()
        description = description.strip()
        
        if not description:
            caller.msg("You must provide a description.")
            return
        
        # Find the material
        material = caller.search(material_name, location=caller, quiet=True)
        if not material:
            caller.msg(f"You don't have '{material_name}'.")
            return
        if isinstance(material, list):
            material = material[0]
        
        if not getattr(material, 'is_fresh_material', False):
            caller.msg(f"{material.key} is not fresh material for tailoring.")
            return
        
        # Check for %color
        if "%color" not in description.lower() and material.clothing_color_name:
            if material.clothing_color_name.lower() not in description.lower():
                caller.msg(f"|yWarning:|n Your description should include either '%color' or the word '{material.clothing_color_name}'.")
        
        # Set description
        material.clothing_desc = description
        
        # Mark as unfinalized
        if material.is_finalized:
            material.is_finalized = False
            caller.msg("|yChanging the description has unfinalized this item.|n")
        
        caller.msg(f"|gSet item description.|n")
        caller.msg(f"|cPreview:|n {description}")


class CmdTailorMessages(Command):
    """
    View and set the various messages for your clothing.
    
    Usage:
        messages <material>                      - View all messages
        messages <material>=<type>:<message>     - Set a specific message
    
    Message types:
        wear    - Message wearer sees when putting it on
        owear   - Message others see when someone wears it
        remove  - Message wearer sees when taking it off
        oremove - Message others see when someone removes it
        worn    - Description shown on character (MUST include %color)
    
    Pronoun tokens (use these instead of he/she/his/her):
        %p - possessive (his/her/their)
        %s - subjective (he/she/they)
        %o - objective (him/her/them)
        %r - reflexive (himself/herself/themselves)
        %n - character's name
    
    Examples:
        messages fresh cloth=wear:You slip into the elegant blouse.
        messages fresh cloth=owear:%n slips into an elegant blouse.
        messages fresh cloth=worn:An elegant %color silk blouse with delicate embroidery.
    """
    key = "messages"
    aliases = ["tailor-messages", "msg"]
    locks = "cmd:all()"
    help_category = "Tailoring"
    
    def func(self):
        caller = self.caller
        
        if not self.args:
            caller.msg("Usage: messages <material> or messages <material>=<type>:<message>")
            return
        
        # Check if setting or viewing
        if "=" not in self.args:
            # View messages
            material_name = self.args.strip()
            material = caller.search(material_name, location=caller, quiet=True)
            if not material:
                caller.msg(f"You don't have '{material_name}'.")
                return
            if isinstance(material, list):
                material = material[0]
            
            if not getattr(material, 'is_fresh_material', False):
                caller.msg(f"{material.key} is not fresh material for tailoring.")
                return
            
            caller.msg(f"|c=== Messages for {material.key} ===|n")
            caller.msg(f"|wwear:|n {material.msg_wear or '|r(not set)|n'}")
            caller.msg(f"|wowear:|n {material.msg_owear or '|r(not set)|n'}")
            caller.msg(f"|wremove:|n {material.msg_remove or '|r(not set)|n'}")
            caller.msg(f"|woremove:|n {material.msg_oremove or '|r(not set)|n'}")
            caller.msg(f"|wworn:|n {material.msg_worn or '|r(not set)|n'}")
            return
        
        material_name, rest = self.args.split("=", 1)
        material_name = material_name.strip()
        rest = rest.strip()
        
        if ":" not in rest:
            caller.msg("Usage: messages <material>=<type>:<message>")
            caller.msg("Types: wear, owear, remove, oremove, worn")
            return
        
        msg_type, message = rest.split(":", 1)
        msg_type = msg_type.strip().lower()
        message = message.strip()
        
        # Find the material
        material = caller.search(material_name, location=caller, quiet=True)
        if not material:
            caller.msg(f"You don't have '{material_name}'.")
            return
        if isinstance(material, list):
            material = material[0]
        
        if not getattr(material, 'is_fresh_material', False):
            caller.msg(f"{material.key} is not fresh material for tailoring.")
            return
        
        # Set the appropriate message
        valid_types = ["wear", "owear", "remove", "oremove", "worn"]
        if msg_type not in valid_types:
            caller.msg(f"|rInvalid message type:|n {msg_type}")
            caller.msg(f"Valid types: {', '.join(valid_types)}")
            return
        
        # Special check for worn - must include %color
        if msg_type == "worn":
            if "%color" not in message.lower() and material.clothing_color_name:
                if material.clothing_color_name.lower() not in message.lower():
                    caller.msg(f"|yWarning:|n The worn message should include either '%color' or the word '{material.clothing_color_name}'.")
        
        # Set the message
        setattr(material, f"msg_{msg_type}", message)
        
        # Mark as unfinalized
        if material.is_finalized:
            material.is_finalized = False
            caller.msg("|yChanging messages has unfinalized this item.|n")
        
        caller.msg(f"|gSet {msg_type} message.|n")
        caller.msg(f"|cPreview:|n {message}")


class CmdTailorCheck(Command):
    """
    Check if your clothing is ready to be finalized.
    
    Usage:
        check <material>
    
    Shows a checklist of all required fields. Green means set,
    red means not set. Use this to verify your work before
    finalizing.
    
    Examples:
        check fresh cloth
        check fresh leather
    """
    key = "check"
    aliases = ["tailor-check"]
    locks = "cmd:all()"
    help_category = "Tailoring"
    
    def func(self):
        caller = self.caller
        
        if not self.args:
            caller.msg("Usage: check <material>")
            return
        
        material_name = self.args.strip()
        
        # Find the material
        material = caller.search(material_name, location=caller, quiet=True)
        if not material:
            caller.msg(f"You don't have '{material_name}'.")
            return
        if isinstance(material, list):
            material = material[0]
        
        if not getattr(material, 'is_fresh_material', False):
            caller.msg(f"{material.key} is not fresh material for tailoring.")
            return
        
        all_valid, requirements = material.check_requirements()
        
        caller.msg(f"|c=== Tailoring Checklist for {material.key} ===|n")
        
        for req_name, req_info in requirements.items():
            desc = req_info['description']
            if req_name == "name":
                desc = desc.replace("@name", "tname")
            status = "|g✓|n" if req_info["set"] else "|r✗|n"
            caller.msg(f"  {status} {desc}")
        
        caller.msg("")
        if all_valid:
            caller.msg("|g✓ Ready to finalize!|n")
        else:
            caller.msg("|r✗ Not ready - complete the red items above.|n")
        
        # Show additional info
        if material.clothing_name:
            layer = material.get_layer()
            layer_desc = {0: "Undergarments", 1: "Base clothing", 2: "Accessories", 
                        3: "Outer wear", 4: "Heavy outerwear", 5: "Top layer"}
            caller.msg(f"\n|cLayer:|n {layer} ({layer_desc.get(layer, 'Unknown')})")
        
        if material.clothing_see_thru:
            caller.msg("|cSee-thru:|n Yes (underlying items will show)")


class CmdTailorFinalize(Command):
    """
    Complete your work on an article of clothing.
    
    Usage:
        finalize <material>
    
    Use check to validate your work before finalizing. When you
    finalize, your tailoring skill determines the value of the
    article. The first time you finalize gives the best value -
    each subsequent finalization reduces the value by 20%.
    
    Examples:
        finalize fresh cloth
        finalize fresh leather
    """
    key = "finalize"
    aliases = ["tailor-finalize"]
    locks = "cmd:all()"
    help_category = "Tailoring"
    
    def func(self):
        caller = self.caller
        
        if not self.args:
            caller.msg("Usage: finalize <material>")
            return
        
        material_name = self.args.strip()
        
        # Find the material
        material = caller.search(material_name, location=caller, quiet=True)
        if not material:
            caller.msg(f"You don't have '{material_name}'.")
            return
        if isinstance(material, list):
            material = material[0]
        
        if not getattr(material, 'is_fresh_material', False):
            caller.msg(f"{material.key} is not fresh material for tailoring.")
            return
        
        # Check tailoring skill
        tailoring_skill = getattr(caller, 'tailoring', 0)
        
        # Warn if low skill
        if tailoring_skill < 3:
            caller.msg("|yWarning:|n Your tailoring skill is low. The resulting item may have reduced value.")
        
        # Attempt to finalize
        success, message, clothing = material.finalize(caller)
        
        if success:
            caller.msg(f"|g{message}|n")
            if clothing:
                caller.msg(f"|cThe {clothing.key} is now in your inventory and ready to wear.|n")
        else:
            caller.msg(f"|r{message}|n")
            caller.msg("Use |wcheck|n to see what's missing.")


# Command set for easy importing
class TailoringCmdSet:
    """Container for tailoring commands."""
    
    @staticmethod
    def get_commands():
        return [
            CmdSpawnMaterial,
            CmdTailorName,
            CmdTailorCoverage,
            CmdTailorColor,
            CmdTailorSeeThru,
            CmdTailorDescribe,
            CmdTailorMessages,
            CmdTailorCheck,
            CmdTailorFinalize,
        ]
