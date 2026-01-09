"""
Tailoring System - Fresh Material and Custom Clothing Creation

This module provides the FreshMaterial typeclass for creating custom clothing items
through the tailoring skill system.
"""

from evennia import DefaultObject, AttributeProperty
from typeclasses.items import Item

# Layer keyword mappings - words in item name determine layer
LAYER_KEYWORDS = {
    0: ["bikini", "panties", "underwear", "bra", "thong", "boxers", "g-string", 
        "gstring", "sock", "stockings"],
    # Layer 1 is default - no keywords needed
    2: ["blindfold", "glasses", "vest"],
    3: ["jacket", "waistcoat"],
    4: ["tailcoat", "coat", "labcoat", "topcoat", "overcoat", "longcoat", 
        "greatcoat", "browncoat", "trenchcoat", "watchcoat", "trench", "robe", 
        "habit", "muumuu", "hawaiian", "bolero", "apron", "scrubs", "bathrobe", 
        "armband", "obi", "duster"],
    5: ["tie", "boots", "cane", "umbrella", "blindfold", "habit", "shawl", 
        "scarf", "armband", "necktie", "cummerbund", "belt", "veil", "parka", 
        "balaclava", "bandana", "bandanna", "sticker", "badge"]
}


def determine_layer_from_name(name):
    """
    Determine clothing layer based on keywords in the name.
    Returns layer number (0-5), defaults to 1.
    """
    name_lower = name.lower()
    for layer, keywords in LAYER_KEYWORDS.items():
        for keyword in keywords:
            if keyword in name_lower:
                return layer
    return 1  # Default layer


class FreshMaterial(DefaultObject):
    """
    Fresh material for tailoring. This is an unfinished clothing item that
    must be configured and finalized before it can be worn.
    
    Attributes:
        is_fresh_material: True - marks this as fresh material
        material_type: Type of material (cloth, leather, etc.)
        clothing_name: The configured name for the final clothing
        clothing_color: Primary color (must appear in descriptions)
        clothing_coverage: List of body locations covered
        clothing_see_thru: Whether underlying items show through
        clothing_desc: Description when examining the item
        msg_wear: Message when wearer puts it on
        msg_owear: Message others see when someone wears it
        msg_remove: Message when wearer removes it
        msg_oremove: Message others see when someone removes it
        msg_worn: Description shown on character when worn
        is_finalized: Whether the item has been finalized
        finalize_count: Number of times finalized (affects value)
        creator_dbref: DBREF of the character who created this
        base_value: Calculated value based on tailoring skill
    """
    
    # Material identification
    is_fresh_material = AttributeProperty(True, autocreate=True)
    material_type = AttributeProperty("cloth", autocreate=True)
    
    # Clothing configuration
    clothing_name = AttributeProperty("", autocreate=True)
    clothing_color_code = AttributeProperty("", autocreate=True)  # xterm 256 hex code (e.g., "005f00")
    clothing_color_name = AttributeProperty("", autocreate=True)  # Display name (e.g., "forest green")
    clothing_coverage = AttributeProperty([], autocreate=True)
    clothing_see_thru = AttributeProperty(False, autocreate=True)
    clothing_desc = AttributeProperty("", autocreate=True)
    
    # Messages
    msg_wear = AttributeProperty("", autocreate=True)
    msg_owear = AttributeProperty("", autocreate=True)
    msg_remove = AttributeProperty("", autocreate=True)
    msg_oremove = AttributeProperty("", autocreate=True)
    msg_worn = AttributeProperty("", autocreate=True)
    
    # Finalization tracking
    is_finalized = AttributeProperty(False, autocreate=True)
    finalize_count = AttributeProperty(0, autocreate=True)
    creator_dbref = AttributeProperty(None, autocreate=True)
    base_value = AttributeProperty(0, autocreate=True)
    
    def at_object_creation(self):
        """Initialize fresh material."""
        super().at_object_creation()
        self.db.desc = "A piece of fresh material ready to be tailored into clothing."
    
    def is_wearable(self):
        """Fresh material can only be worn if finalized."""
        return self.is_finalized
    
    def get_layer(self):
        """Determine layer based on clothing name."""
        if self.clothing_name:
            return determine_layer_from_name(self.clothing_name)
        return 1
    
    def check_requirements(self):
        """
        Check if all required fields are set for finalization.
        Returns tuple of (all_valid, requirements_dict)
        """
        requirements = {
            "name": {
                "set": bool(self.clothing_name),
                "required": True,
                "description": "Item name (@tname)"
            },
            "color": {
                "set": bool(self.clothing_color_code and self.clothing_color_name),
                "required": True,
                "description": "Primary color (@color)"
            },
            "coverage": {
                "set": bool(self.clothing_coverage),
                "required": True,
                "description": "Body coverage (@coverage)"
            },
            "describe": {
                "set": bool(self.clothing_desc),
                "required": True,
                "description": "Item description (@tdescribe)"
            },
            "msg_wear": {
                "set": bool(self.msg_wear),
                "required": True,
                "description": "Wear message (@messages wear)"
            },
            "msg_owear": {
                "set": bool(self.msg_owear),
                "required": True,
                "description": "Others wear message (@messages owear)"
            },
            "msg_remove": {
                "set": bool(self.msg_remove),
                "required": True,
                "description": "Remove message (@messages remove)"
            },
            "msg_oremove": {
                "set": bool(self.msg_oremove),
                "required": True,
                "description": "Others remove message (@messages oremove)"
            },
            "msg_worn": {
                "set": bool(self.msg_worn),
                "required": True,
                "description": "Worn description (@messages worn)"
            }
        }
        
        # Check %color appears in descriptions (we use %color token now, not literal color name)
        if self.clothing_color_name:
            # Check for %color token OR the literal color name
            if self.clothing_desc:
                has_token = "%color" in self.clothing_desc.lower()
                has_literal = self.clothing_color_name.lower() in self.clothing_desc.lower()
                requirements["color_in_desc"] = {
                    "set": has_token or has_literal,
                    "required": True,
                    "description": f"%color or '{self.clothing_color_name}' in @tdescribe"
                }
            
            if self.msg_worn:
                has_token = "%color" in self.msg_worn.lower()
                has_literal = self.clothing_color_name.lower() in self.msg_worn.lower()
                requirements["color_in_worn"] = {
                    "set": has_token or has_literal,
                    "required": True,
                    "description": f"%color or '{self.clothing_color_name}' in @messages worn"
                }
        
        all_valid = all(
            req["set"] for req in requirements.values() if req["required"]
        )
        
        return all_valid, requirements
    
    def finalize(self, tailor):
        """
        Finalize the material into wearable clothing.
        
        Args:
            tailor: The character finalizing the item
            
        Returns:
            tuple of (success, message, Item or None)
        """
        # Check requirements
        all_valid, requirements = self.check_requirements()
        if not all_valid:
            missing = [req["description"] for req in requirements.values() 
                      if req["required"] and not req["set"]]
            return False, f"Missing requirements: {', '.join(missing)}", None
        
        # Get tailoring skill
        tailoring_skill = getattr(tailor, 'tailoring', 0)
        
        # Calculate value based on skill
        # Base value = skill * 10, with some randomness
        import random
        skill_modifier = max(1, tailoring_skill)
        base_value = skill_modifier * 10 + random.randint(-5, 15)
        
        # Reduce value for subsequent finalizations
        self.finalize_count += 1
        if self.finalize_count > 1:
            reduction = 0.2 * (self.finalize_count - 1)  # 20% per re-finalization
            base_value = int(base_value * max(0.2, 1 - reduction))
        
        base_value = max(1, base_value)
        self.base_value = base_value
        
        # Convert to proper clothing item
        from evennia import create_object
        
        # Build the colored text substitution: |#RRGGBB color name|n
        colored_text = f"|#{self.clothing_color_code}{self.clothing_color_name}|n"
        
        # Item name should never have color codes - use plain name
        item_name = self.clothing_name.replace("%color", self.clothing_color_name)
        
        # Create the actual clothing item
        clothing = create_object(
            Item,
            key=item_name,
            location=tailor,
            attributes=[
                ("desc", self.clothing_desc.replace("%color", colored_text)),
                ("coverage", self.clothing_coverage),
                ("worn_desc", self.msg_worn.replace("%color", colored_text)),
                ("color", self.clothing_color_name),
                ("color_code", self.clothing_color_code),
                ("material", self.material_type),
                ("layer", self.get_layer()),
                ("see_thru", self.clothing_see_thru),
                ("msg_wear", self.msg_wear.replace("%color", colored_text)),
                ("msg_owear", self.msg_owear.replace("%color", colored_text)),
                ("msg_remove", self.msg_remove.replace("%color", colored_text)),
                ("msg_oremove", self.msg_oremove.replace("%color", colored_text)),
                ("creator_dbref", tailor.dbref),
                ("base_value", base_value),
                ("is_tailored", True),
            ]
        )
        
        # Delete the fresh material
        self.delete()
        
        return True, f"You finish tailoring the {clothing.key}. (Value: {base_value})", clothing
    
    def unfinalize(self):
        """Mark item as unfinalized (after editing)."""
        if self.is_finalized:
            self.is_finalized = False
            return True
        return False


# Valid body locations for coverage
VALID_COVERAGE_LOCATIONS = [
    "head", "face", "leye", "reye", "lear", "rear", "neck",
    "lshoulder", "rshoulder", "larm", "rarm", "lhand", "rhand",
    "chest", "back", "abdomen", "groin", "ass",
    "lthigh", "rthigh", "lshin", "rshin", "lfoot", "rfoot"
]

# Friendly names for coverage locations
COVERAGE_LOCATION_NAMES = {
    "head": "head",
    "face": "face",
    "leye": "left eye",
    "reye": "right eye",
    "lear": "left ear",
    "rear": "right ear",
    "neck": "neck",
    "lshoulder": "left shoulder",
    "rshoulder": "right shoulder",
    "larm": "left arm",
    "rarm": "right arm",
    "lhand": "left hand",
    "rhand": "right hand",
    "chest": "chest",
    "back": "back",
    "abdomen": "abdomen",
    "groin": "groin",
    "ass": "rear",
    "lthigh": "left thigh",
    "rthigh": "right thigh",
    "lshin": "left shin",
    "rshin": "right shin",
    "lfoot": "left foot",
    "rfoot": "right foot"
}
