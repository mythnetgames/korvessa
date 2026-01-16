from evennia import DefaultObject, AttributeProperty
from world.combat.constants import DEFAULT_CLOTHING_LAYER

# ANSI Color definitions for clothing descriptions
COLOR_DEFINITIONS = {
    # Standard colors
    "black": "|=l",       # Black (256-color)
    "red": "|r",          # Red
    "green": "|g",        # Green
    "yellow": "|y",       # Yellow
    "blue": "|b",         # Blue
    "magenta": "|m",      # Magenta
    "cyan": "|c",         # Cyan
    "white": "|w",        # White
    # Bright colors
    "bright_black": "|K", # Dark Gray
    "bright_red": "|R",   # Bright Red
    "bright_green": "|G", # Bright Green
    "bright_yellow": "|Y",# Bright Yellow
    "bright_blue": "|B",  # Bright Blue
    "bright_magenta": "|M", # Bright Magenta
    "bright_cyan": "|C",  # Bright Cyan
    "bright_white": "|W", # Bright White
    # Additional colors for armor and materials
    "gunmetal": "|=l",    # Gunmetal gray
    "rust-brown": "|y",   # Rust brown
    "dark brown": "|y",   # Dark brown
    "matte black": "|=l", # Matte black
    "steel": "|w",        # Steel gray/white
}

class Item(DefaultObject):
    """
    A general-purpose item. In Gelatinous Monster, all items are
    potential weapons. This typeclass ensures that all objects have
    basic combat-relevant properties.
    
    Items become wearable clothing by setting coverage and worn_desc attributes.
    """
    
    # ===================================================================
    # CLOTHING SYSTEM ATTRIBUTES
    # ===================================================================
    
    # Coverage definition - which body locations this item covers (base state)
    # Empty list = not wearable, populated list = clothing item
    coverage = AttributeProperty([], autocreate=True)
    
    # Clothing-specific description that appears when worn (base state)
    # Empty string = not clothing, populated = worn description
    worn_desc = AttributeProperty("", autocreate=True)
    
    # ANSI color definition for this item
    # Used for atmospheric descriptions and visual immersion
    color = AttributeProperty("", autocreate=True)
    
    # Material type for this item (for future armor/crafting systems)
    # Examples: "leather", "steel", "silk", "kevlar", "titanium"
    material = AttributeProperty("", autocreate=True)
    
    # Weight of item in pounds (for encumbrance system)
    # Examples: t-shirt=0.2, jeans=1.2, kevlar vest=4.5, steel plate=12.0
    weight = AttributeProperty(0.5, autocreate=True)  # Default 0.5 lbs
    
    # Layer priority for stacking items (higher = outer layer)
    layer = AttributeProperty(DEFAULT_CLOTHING_LAYER, autocreate=True)
    
    # ===================================================================
    # ARMOR SYSTEM ATTRIBUTES
    # ===================================================================
    
    # Armor rating (0 = no armor, 10 = maximum protection)
    armor_rating = AttributeProperty(0, autocreate=True)
    
    # Type of armor material (affects damage type effectiveness)
    armor_type = AttributeProperty("", autocreate=True)
    
    # Current armor durability  
    armor_durability = AttributeProperty(0, autocreate=True)
    
    # Maximum armor durability
    max_armor_durability = AttributeProperty(0, autocreate=True)
    
    # Original armor rating (for repair calculations)
    base_armor_rating = AttributeProperty(0, autocreate=True)
    
    # Plate carrier system - can accept armor plates
    is_plate_carrier = AttributeProperty(False, autocreate=True)
    
    # Installed plates for plate carriers (dict of slot_name: plate_object)
    installed_plates = AttributeProperty({}, autocreate=True)
    
    # Available plate slots for carriers (list of slot names)
    plate_slots = AttributeProperty([], autocreate=True)
    
    # Is this item an armor plate that can be installed?
    is_armor_plate = AttributeProperty(False, autocreate=True)
    
    # Plate size compatibility (small, medium, large, extra_large)
    plate_size = AttributeProperty("", autocreate=True)
    
    # Multiple style properties for combination states
    style_properties = AttributeProperty({}, autocreate=True)
    # Structure: {"adjustable": "rolled", "closure": "zipped"}
    
    # Style configurations defining all possible combinations
    style_configs = AttributeProperty({}, autocreate=True)
    # Structure: {
    #     "adjustable": {
    #         "rolled": {"coverage_mod": [...], "desc_mod": "with sleeves rolled up"},
    #         "normal": {"coverage_mod": [], "desc_mod": ""}
    #     },
    #     "closure": {
    #         "zipped": {"coverage_mod": [...], "desc_mod": "zipped tight"},
    #         "unzipped": {"coverage_mod": [...], "desc_mod": "hanging open"}
    #     }
    # }
    
    # ===================================================================
    # STICKY GRENADE SYSTEM ATTRIBUTES
    # ===================================================================
    
    # Metal content level (0-10): Amount of metal in the item
    # 0 = No metal whatsoever
    # 1-3 = Minimal metal (buckles, rivets, small fasteners)
    # 4-6 = Moderate metal (metal plates, reinforcements, chainmail sections)
    # 7-9 = Heavy metal (predominantly metal construction)
    # 10 = Pure metal (entirely metal construction)
    metal_level = AttributeProperty(0, autocreate=True)
    
    # Magnetic responsiveness level (0-10): How magnetic the metal is
    # 0 = Non-magnetic (no ferrous metals - aluminum, titanium, synthetic, cloth, leather)
    # 1-3 = Weakly magnetic (stainless steel, treated/alloyed metals with low iron content)
    # 4-6 = Moderately magnetic (mild steel, some carbon steel)
    # 7-9 = Highly magnetic (carbon steel, most ferrous alloys)
    # 10 = Pure ferrous metal (raw iron, unalloyed steel)
    # NOTE: Titanium and aluminum are NOT magnetic (magnetic_level=0) despite being metal
    magnetic_level = AttributeProperty(0, autocreate=True)
    
    # Reference to sticky grenade attached to this armor (if any)
    stuck_grenade = AttributeProperty(None, autocreate=True)
    
    # ===================================================================
    # ANONYMITY SYSTEM ATTRIBUTES
    # ===================================================================
    
    # Whether this item can provide anonymity (e.g., hoodies, masks, helmets)
    # When True and anonymity_active is True, wearer's identity is concealed
    provides_anonymity = AttributeProperty(False, autocreate=True)
    
    # Whether the anonymity feature is currently active
    # For hoodies: hood is up; For masks: mask is on face; etc.
    anonymity_active = AttributeProperty(False, autocreate=True)
    
    # Custom descriptor when anonymity is active (e.g., 'a hooded figure')
    # If empty, system will generate based on item name keywords
    anonymity_descriptor = AttributeProperty("", autocreate=True)
    
    # ===================================================================
    # CLOTHING SYSTEM METHODS
    # ===================================================================
    
    def is_wearable(self):
        """Check if this item can be worn as clothing"""
        return bool(self.coverage) and bool(self.worn_desc)
    
    def get_current_coverage(self):
        """Get coverage for current combination of style states"""
        coverage = list(self.coverage)  # Start with base coverage
        
        if not self.style_configs or not self.style_properties:
            return coverage
        
        # Apply modifications from each active style property in deterministic order
        for property_name in sorted(self.style_properties.keys()):
            property_state = self.style_properties[property_name]
            
            if property_name in self.style_configs:
                property_config = self.style_configs[property_name]
                if property_state in property_config:
                    state_config = property_config[property_state]
                    coverage_mod = state_config.get("coverage_mod", [])
                    
                    # Apply coverage modifications
                    for mod in coverage_mod:
                        if mod.startswith("+"):
                            # Add location if not already covered
                            location = mod[1:]
                            if location not in coverage:
                                coverage.append(location)
                        elif mod.startswith("-"):
                            # Remove location if currently covered
                            location = mod[1:]
                            if location in coverage:
                                coverage.remove(location)
        
        return coverage
    
    def get_current_worn_desc(self):
        """Get worn description incorporating all active style states"""
        if not self.style_configs or not self.style_properties:
            return f"{self.worn_desc}." if self.worn_desc else ""
        
        # For multi-property items, we need to handle combinations
        # Priority order: check properties in sorted order, use first non-empty desc_mod
        for property_name in sorted(self.style_properties.keys()):
            property_state = self.style_properties[property_name]
            
            if property_name in self.style_configs:
                property_config = self.style_configs[property_name]
                if property_state in property_config:
                    state_config = property_config[property_state]
                    desc_mod = state_config.get("desc_mod", "").strip()
                    if desc_mod:
                        # First non-empty desc_mod wins - this allows for sophisticated combinations
                        return f"{desc_mod}." if not desc_mod.endswith('.') else desc_mod
        
        # No active desc_mod found, use base worn_desc
        return f"{self.worn_desc}." if self.worn_desc else ""
    
    def can_style_property_to(self, property_name, state_name):
        """Check if item can transition specific property to given state"""
        if property_name not in self.style_configs:
            return False
        if state_name not in self.style_configs[property_name]:
            return False
        
        # Always allow transitions to valid states - the validation is structural, not functional
        return True
    
    def set_style_property(self, property_name, state_name):
        """Set specific style property to given state with validation"""
        if not self.can_style_property_to(property_name, state_name):
            return False
        
        if not self.style_properties:
            self.style_properties = {}
        
        self.style_properties[property_name] = state_name
        return True
    
    def get_style_property(self, property_name):
        """Get current state of specific style property"""
        from world.combat.constants import STYLE_STATE_NORMAL
        return self.style_properties.get(property_name, STYLE_STATE_NORMAL)
    
    def get_available_style_properties(self):
        """Get all available style properties and their states"""
        return {prop: list(states.keys()) for prop, states in self.style_configs.items()}
    
    def validate_plate_slot_coverage(self):
        """
        Validate that plate_slot_coverage keys match plate_slots.
        
        Returns:
            tuple: (is_valid, error_message)
        """
        if not getattr(self, 'is_plate_carrier', False):
            return (True, "")  # Not a plate carrier, no validation needed
            
        plate_slots = getattr(self, 'plate_slots', [])
        slot_coverage = getattr(self, 'plate_slot_coverage', {})
        
        if not slot_coverage:
            return (True, "")  # No coverage mapping, use default behavior
            
        # Check for slots in coverage that don't exist in plate_slots
        invalid_slots = [slot for slot in slot_coverage.keys() if slot not in plate_slots]
        
        if invalid_slots:
            error_msg = f"Invalid slots in plate_slot_coverage: {', '.join(invalid_slots)}. Valid slots: {', '.join(plate_slots)}"
            return (False, error_msg)
            
        return (True, "")

    def get_current_worn_desc_with_perspective(self, looker=None, from_obj=None):
        """
        Get the current worn description with template variable processing and color integration.
        
        Args:
            looker: The character doing the looking (for perspective)
            from_obj: The object being looked at (wearer, for template variable context)
            
        Returns:
            str: Processed description with pronouns and colors
        """
        if not self.worn_desc:
            return ""
            
        # Get current style configuration
        current_desc = self.get_current_worn_desc()
        
        # Process color placeholders
        colored_desc = self._process_color_codes(current_desc)
        
        # Process template variables if we have perspective context
        if looker and from_obj and hasattr(from_obj, '_process_description_variables'):
            return from_obj._process_description_variables(colored_desc, looker, force_third_person=True)
        
        # Fallback: return without template processing
        return colored_desc
    
    def _process_color_codes(self, text):
        """
        Process color placeholder codes in text.
        
        Args:
            text (str): Text with color placeholders like {color}word|n
            
        Returns:
            str: Text with color placeholders replaced with ANSI codes
        """
        if not text:
            return text
            
        # Get color value
        color = self.color or ""
        
        # Replace color placeholder
        if color and "{color}" in text:
            color_code = COLOR_DEFINITIONS.get(color, "")
            processed = text.replace("{color}", color_code)
            return processed
        
        return text

    def at_object_creation(self):
        """
        Called once when the object is created.
        """
        # Core combat attributes
        self.db.damage = 1  # Minimal default damage
        self.db.weapon_type = "melee"  # Most objects default to melee weapons
        self.db.damage_type = "blunt"  # Default medical system injury type

        # Optional future expansion
        self.db.hands_required = 1  # Assume one-handed for now

        # Generic descriptor
        if not self.db.desc:
            self.db.desc = "It's a thing. Heavy enough to hurt if used wrong."

        # Add a boolean attribute `is_ranged` to the `Item` class
        self.db.is_ranged = False

    def return_appearance(self, looker, **kwargs):
        """
        Enhanced appearance method that shows armor information for armor items.
        
        Args:
            looker: Character looking at the item
            **kwargs: Additional appearance arguments
            
        Returns:
            str: The formatted appearance string
        """
        # Get the basic appearance first
        appearance = super().return_appearance(looker, **kwargs)
        
        # Check for stuck grenade (CRITICAL SAFETY WARNING)
        if hasattr(self, 'stuck_grenade') and self.stuck_grenade:
            grenade = self.stuck_grenade
            remaining = getattr(grenade.ndb, 'countdown_remaining', 0) if hasattr(grenade, 'ndb') else 0
            if remaining > 0:
                appearance += f"\n\n|r{'='*60}|n"
                appearance += f"\n|R!!! WARNING: LIVE GRENADE MAGNETICALLY CLAMPED TO THIS ITEM !!!|n"
                appearance += f"\n|r{'='*60}|n"
                appearance += f"\n|REXPLOSION IN {remaining} SECONDS!|n"
                appearance += f"\n|r{'='*60}|n"
            else:
                appearance += f"\n\n|rA {grenade.key} is magnetically clamped to this item.|n"
        
        # Check if this is an armor item and add armor information
        if self._is_armor_item():
            armor_info = self._get_armor_information()
            if armor_info:
                appearance += f"\n\n|w=== Armor Information ===|n\n{armor_info}"
        
        return appearance
    
    def _is_armor_item(self):
        """Check if this item has armor properties."""
        return (hasattr(self, 'armor_rating') and getattr(self, 'armor_rating', 0) > 0) or \
               (hasattr(self, 'is_plate_carrier') and getattr(self, 'is_plate_carrier', False)) or \
               hasattr(self, 'plate_type')
    
    def _get_armor_information(self):
        """Generate armor information display."""
        info_lines = []
        
        # Basic armor stats
        armor_rating = getattr(self, 'armor_rating', 0)
        armor_type = getattr(self, 'armor_type', 'generic')
        weight = getattr(self, 'weight', 0)
        
        if armor_rating > 0:
            rating_desc = self._get_rating_description(armor_rating)
            info_lines.append(f"  Protection Rating: {armor_rating} ({rating_desc})")
        
        # Armor type information
        if armor_type != 'generic':
            type_info = self._get_armor_type_info(armor_type)
            info_lines.append(f"  Armor Type: {armor_type.title()} {type_info}")
        
        # Weight
        if weight > 0:
            info_lines.append(f"  Weight: {weight} kg")
        
        # Plate carrier specific information
        if hasattr(self, 'is_plate_carrier') and getattr(self, 'is_plate_carrier', False):
            carrier_info = self._get_plate_carrier_details()
            if carrier_info:
                info_lines.extend(carrier_info)
        
        # Armor plate specific information  
        elif hasattr(self, 'plate_type'):
            plate_info = self._get_plate_details()
            if plate_info:
                info_lines.extend(plate_info)
        
        # Coverage information
        if hasattr(self, 'get_current_coverage'):
            coverage = self.get_current_coverage()
        else:
            coverage = getattr(self, 'coverage', [])
        
        if coverage:
            coverage_str = ", ".join(coverage)
            info_lines.append(f"  Coverage: {coverage_str}")
        
        # Condition
        condition = self._get_condition_info()
        if condition:
            info_lines.append(f"  Condition: {condition}")
        
        return "\n".join(info_lines)
    
    def _get_rating_description(self, rating):
        """Get descriptive text for armor rating."""
        if rating <= 1:
            return "Minimal"
        elif rating <= 3:
            return "Light"
        elif rating <= 5:
            return "Moderate"
        elif rating <= 7:
            return "Heavy"
        else:
            return "Excellent"
    
    def _get_armor_type_info(self, armor_type):
        """Get information about armor type strengths/weaknesses."""
        type_info = {
            'kevlar': "(Strong vs bullets, weak vs blades)",
            'ceramic': "(Excellent vs bullets, brittle vs blunt force)",
            'steel': "(Good vs cuts/stabs, heavy)",
            'leather': "(Flexible, moderate protection)",
            'synthetic': "(Lightweight, basic protection)"
        }
        return type_info.get(armor_type, "")
    
    def _get_plate_carrier_details(self):
        """Get plate carrier configuration details."""
        info_lines = []
        installed_plates = getattr(self, 'installed_plates', {})
        base_rating = getattr(self, 'armor_rating', 0)
        
        info_lines.append(f"  Base Protection: {base_rating}")
        
        # Show slot configuration
        total_plate_rating = 0
        total_plate_weight = 0
        
        info_lines.append(f"  Current Configuration:")
        for slot_name, plate in installed_plates.items():
            if plate:
                plate_rating = getattr(plate, 'armor_rating', 0)
                plate_weight = getattr(plate, 'weight', 0)
                total_plate_rating += plate_rating
                total_plate_weight += plate_weight
                info_lines.append(f"    {slot_name.title()} Slot: {plate.key} (+{plate_rating} protection, {plate_weight}kg)")
            else:
                info_lines.append(f"    {slot_name.title()} Slot: |y[Empty]|n")
        
        # Totals
        total_protection = base_rating + total_plate_rating
        total_weight = getattr(self, 'weight', 0) + total_plate_weight
        
        info_lines.append(f"")
        info_lines.append(f"  Total Protection: {total_protection} (Base {base_rating} + Plates {total_plate_rating})")
        info_lines.append(f"  Total Weight: {total_weight} kg")
        
        return info_lines
    
    def _get_plate_details(self):
        """Get armor plate specific details."""
        info_lines = []
        plate_type = getattr(self, 'plate_type', 'unknown')
        threat_level = getattr(self, 'threat_level', None)
        
        info_lines.append(f"  Plate Type: {plate_type.title()} plate")
        
        if threat_level:
            info_lines.append(f"  Threat Level: {threat_level}")
        
        info_lines.append(f"  Slot Compatibility: Can be installed in {plate_type} slots of plate carriers.")
        
        return info_lines
    
    def _get_condition_info(self):
        """Get armor condition information."""
        durability = getattr(self, 'armor_durability', None)
        max_durability = getattr(self, 'max_armor_durability', None)
        
        if durability is not None and max_durability is not None and max_durability > 0:
            condition_percent = durability / max_durability
            
            if condition_percent > 0.9:
                return "|gExcellent|n"
            elif condition_percent > 0.7:
                return "|GGood|n"
            elif condition_percent > 0.5:
                return "|yFair|n"
            elif condition_percent > 0.3:
                return "|YPoor|n"
            else:
                return "|rTerrible|n"
        
        return None
    
    def at_delete(self):
        """
        Called when item is deleted/destroyed.
        Handles cleanup for remote detonator explosive tracking.
        """
        # If this item is an explosive scanned by a detonator, remove it from the detonator's list
        if hasattr(self.db, 'scanned_by_detonator') and self.db.scanned_by_detonator:
            from evennia.utils.search import search_object
            detonator = search_object(f"#{self.db.scanned_by_detonator}")
            if detonator and len(detonator) > 0:
                detonator_obj = detonator[0]
                if hasattr(detonator_obj.db, 'scanned_explosives'):
                    try:
                        detonator_obj.db.scanned_explosives.remove(self.id)
                    except ValueError:
                        pass  # Already removed
        
        super().at_delete()


class SprayCanItem(Item):
    """
    Spray paint can for graffiti system.
    Contains finite paint and selectable colors.
    """
    
    def at_object_creation(self):
        """Initialize spray can with paint and color attributes."""
        super().at_object_creation()
        
        # Graffiti-specific attributes
        self.db.aerosol_level = 256  # Default aerosol capacity
        self.db.max_aerosol = 256    # Starting aerosol capacity
        self.db.current_color = "red"  # Default color
        self.db.aerosol_contents = "spraypaint"  # What's inside the can
        
        # Available ANSI colors for cycling
        self.db.available_colors = [
            "red", "green", "yellow", "blue", "magenta", "cyan", "white"
        ]
        
        # Override default description with aerosol level and contents
        if not self.db.desc:
            self.db.desc = f"A can of {self.db.aerosol_contents} with a {self.db.current_color} nozzle. It feels {'heavy' if self.db.aerosol_level > 128 else 'light' if self.db.aerosol_level > 0 else 'empty'} with {self.db.aerosol_contents}."
        
        # Combat properties for spray can as weapon
        self.db.damage = 2  # Slightly better than default item
        self.db.weapon_type = "spraycan"  # Specific weapon type for combat messages
        self.db.damage_type = "burn"  # Chemical burns from spray paint/solvent
        
    def get_display_name(self, looker, **kwargs):
        """
        Display name based on aerosol contents.
        Since cans self-destruct when empty, no need for state indicators.
        """
        aerosol_contents = self.db.aerosol_contents or "spraypaint"
        return f"can of {aerosol_contents}"
    
    def has_paint(self, amount=1):
        """
        Check if spray can has enough aerosol for operation.
        
        Args:
            amount (int): Aerosol amount needed
            
        Returns:
            bool: True if enough aerosol available
        """
        return self.db.aerosol_level >= amount
    
    def use_paint(self, amount):
        """
        Consume aerosol from the can.
        
        Args:
            amount (int): Aerosol amount to consume
            
        Returns:
            int: Actual amount consumed (may be less if running out)
        """
        if amount <= 0:
            return 0
            
        actual_used = min(amount, self.db.aerosol_level)
        self.db.aerosol_level -= actual_used
        
        # Update description based on new aerosol level
        self.db.desc = f"A can of spraypaint with a {self.db.current_color} nozzle. It feels {'heavy' if self.db.aerosol_level > 128 else 'light' if self.db.aerosol_level > 0 else 'empty'} with paint."
        
        # Delete the can if it's empty
        if self.db.aerosol_level <= 0:
            # If wielded, remove from hands first
            if self.location and hasattr(self.location, 'hands'):
                hands = self.location.hands
                for hand_name, held_item in hands.items():
                    if held_item == self:
                        hands[hand_name] = None
                        self.location.hands = hands
                        break
            
            # Delete silently - let calling code handle messaging
            self.delete()
        
        return actual_used
    
    def set_color(self, color):
        """
        Set the spray can's current color.
        
        Args:
            color (str): Color name to set
            
        Returns:
            bool: True if color was valid and set
        """
        if color.lower() in [c.lower() for c in self.db.available_colors]:
            # Find the properly cased version
            for available_color in self.db.available_colors:
                if available_color.lower() == color.lower():
                    self.db.current_color = available_color
                    # Update description with new color
                    self.db.desc = f"A can of spraypaint with a {self.db.current_color} nozzle. It feels {'heavy' if self.db.aerosol_level > 128 else 'light' if self.db.aerosol_level > 0 else 'empty'} with paint."
                    return True
        return False
    
    def get_next_color(self):
        """
        Get the next color in the cycle.
        
        Returns:
            str: Next color name
        """
        try:
            current_index = self.db.available_colors.index(self.db.current_color)
            next_index = (current_index + 1) % len(self.db.available_colors)
            return self.db.available_colors[next_index]
        except ValueError:
            # Current color not in list, return first color
            return self.db.available_colors[0]


class SolventCanItem(Item):
    """
    Solvent can for cleaning graffiti.
    Contains finite solvent for graffiti removal.
    """
    
    def at_object_creation(self):
        """Initialize solvent can with aerosol capacity."""
        super().at_object_creation()
        
        # Aerosol-specific attributes (standardized)
        self.db.aerosol_level = 256  # Default aerosol capacity (matches spray paint)
        self.db.max_aerosol = 256    # Starting aerosol capacity
        self.db.aerosol_contents = "solvent"  # What's inside the can
        
        # Override default description with contents
        if not self.db.desc:
            self.db.desc = f"A can of {self.db.aerosol_contents} for cleaning graffiti. It feels {'heavy' if self.db.aerosol_level > 128 else 'light' if self.db.aerosol_level > 0 else 'empty'} with {self.db.aerosol_contents}."
            
        # Combat properties for solvent can as weapon
        self.db.damage = 2  # Same as spray can
        self.db.weapon_type = "spraycan"  # Same weapon type as spray can
        self.db.damage_type = "burn"  # Chemical burns from solvent
        
    def get_display_name(self, looker, **kwargs):
        """
        Display name based on aerosol contents.
        Since cans self-destruct when empty, no need for state indicators.
        """
        aerosol_contents = self.db.aerosol_contents or "solvent"
        return f"can of {aerosol_contents}"
    
    def has_solvent(self, amount=1):
        """
        Check if solvent can has enough aerosol for operation.
        
        Args:
            amount (int): Aerosol amount needed
            
        Returns:
            bool: True if enough aerosol available
        """
        return self.db.aerosol_level >= amount
    
    def use_solvent(self, amount):
        """
        Consume aerosol from the can.
        
        Args:
            amount (int): Aerosol amount to consume
            
        Returns:
            int: Actual amount consumed (may be less if running out)
        """
        if amount <= 0:
            return 0
            
        actual_used = min(amount, self.db.aerosol_level)
        self.db.aerosol_level -= actual_used
        
        # Update description based on new aerosol level
        self.db.desc = f"A can of solvent for cleaning graffiti. It feels {'heavy' if self.db.aerosol_level > 128 else 'light' if self.db.aerosol_level > 0 else 'empty'} with solvent."
        
        # Delete the can if it's empty
        if self.db.aerosol_level <= 0:
            # If wielded, remove from hands first
            if self.location and hasattr(self.location, 'hands'):
                hands = self.location.hands
                for hand_name, held_item in hands.items():
                    if held_item == self:
                        hands[hand_name] = None
                        self.location.hands = hands
                        break
            
            # Delete silently - let calling code handle messaging
            self.delete()
        
        return actual_used


class RemoteDetonator(Item):
    """
    Remote detonator for explosive devices.
    
    Can scan and remotely trigger up to 20 explosives. Maintains bidirectional
    tracking with explosives - each explosive can only be scanned by one detonator
    at a time, but detonators can manage multiple explosives.
    
    Remote detonation triggers the explosive's normal pin-pull and countdown logic,
    respecting each explosive type's unique behavior (sticky grenade seeking,
    rigged explosive trap mechanics, varied fuse times).
    """
    
    def at_object_creation(self):
        """Initialize remote detonator attributes."""
        super().at_object_creation()
        
        # Scanned explosives tracking (list of dbrefs)
        self.db.scanned_explosives = []
        
        # Maximum capacity
        self.db.max_capacity = 20
        
        # Device type identifier
        self.db.device_type = "remote_detonator"
        
        # Default description if not set
        if not self.db.desc:
            self.db.desc = (
                "A compact military-grade remote detonator with a digital display "
                "showing scanned explosive devices. The device can store up to 20 "
                "explosive signatures and trigger them remotely with the press of a button. "
                "A red safety cover protects the main detonation switch."
            )
    
    def validate_scanned_list(self):
        """
        Clean up invalid explosives from scanned list.
        Removes explosives that no longer exist or are invalid.
        
        Returns:
            int: Number of explosives removed
        """
        if not self.db.scanned_explosives:
            return 0
        
        original_count = len(self.db.scanned_explosives)
        valid_explosives = []
        
        for explosive_dbref in self.db.scanned_explosives:
            from evennia.utils.search import search_object
            explosive = search_object(f"#{explosive_dbref}")
            
            # Keep if explosive exists and is valid
            if explosive and len(explosive) > 0:
                explosive_obj = explosive[0]
                if explosive_obj and hasattr(explosive_obj, 'db'):
                    valid_explosives.append(explosive_dbref)
                    
        self.db.scanned_explosives = valid_explosives
        return original_count - len(valid_explosives)
    
    def add_explosive(self, explosive):
        """
        Add explosive to scanned list with validation.
        Handles capacity limits and bidirectional linking.
        
        Args:
            explosive: Explosive object to add
            
        Returns:
            tuple: (success: bool, message: str)
        """
        # Validate capacity
        if len(self.db.scanned_explosives) >= self.db.max_capacity:
            return False, f"Detonator at maximum capacity ({self.db.max_capacity} explosives)."
        
        # Check if already scanned
        if explosive.id in self.db.scanned_explosives:
            return False, f"{explosive.key} is already scanned by this detonator."
        
        # Handle override: remove from previous detonator if any
        if hasattr(explosive.db, 'scanned_by_detonator') and explosive.db.scanned_by_detonator:
            old_detonator_dbref = explosive.db.scanned_by_detonator
            from evennia.utils.search import search_object
            old_detonator = search_object(f"#{old_detonator_dbref}")
            
            if old_detonator and len(old_detonator) > 0:
                old_det = old_detonator[0]
                if hasattr(old_det.db, 'scanned_explosives'):
                    try:
                        old_det.db.scanned_explosives.remove(explosive.id)
                    except ValueError:
                        pass  # Already removed
        
        # Add to this detonator's list
        self.db.scanned_explosives.append(explosive.id)
        
        # Set bidirectional reference
        explosive.db.scanned_by_detonator = self.id
        
        return True, f"{explosive.key} scanned successfully."
    
    def remove_explosive(self, explosive_dbref):
        """
        Remove explosive from scanned list.
        Breaks bidirectional reference.
        
        Args:
            explosive_dbref: Database ID of explosive to remove
            
        Returns:
            bool: True if removed, False if not in list
        """
        if explosive_dbref not in self.db.scanned_explosives:
            return False
        
        # Remove from list
        self.db.scanned_explosives.remove(explosive_dbref)
        
        # Clear bidirectional reference if explosive still exists
        from evennia.utils.search import search_object
        explosive = search_object(f"#{explosive_dbref}")
        if explosive and len(explosive) > 0:
            explosive_obj = explosive[0]
            if hasattr(explosive_obj.db, 'scanned_by_detonator'):
                explosive_obj.db.scanned_by_detonator = None
        
        return True
    
    def get_scanned_count(self):
        """
        Get current count of scanned explosives.
        Auto-validates list before counting.
        
        Returns:
            int: Number of valid scanned explosives
        """
        self.validate_scanned_list()
        return len(self.db.scanned_explosives)
    
    def at_delete(self):
        """
        Called when detonator is destroyed.
        Clears scanned_by_detonator reference on all linked explosives.
        """
        if self.db.scanned_explosives:
            from evennia.utils.search import search_object
            
            for explosive_dbref in self.db.scanned_explosives:
                explosive = search_object(f"#{explosive_dbref}")
                if explosive and len(explosive) > 0:
                    explosive_obj = explosive[0]
                    if hasattr(explosive_obj.db, 'scanned_by_detonator'):
                        explosive_obj.db.scanned_by_detonator = None
        
        super().at_delete()


# =============================================================================
# AMMUNITION SYSTEM
# =============================================================================

# Ammunition caliber/type definitions
AMMO_TYPES = {
    # Pistol ammunition
    "9mm": {
        "name": "9mm Parabellum",
        "category": "pistol",
        "damage_mod": 0,
        "desc_single": "a single 9mm round",
        "desc_plural": "9mm rounds",
    },
    "45acp": {
        "name": ".45 ACP",
        "category": "pistol", 
        "damage_mod": 2,
        "desc_single": "a single .45 ACP round",
        "desc_plural": ".45 ACP rounds",
    },
    "44mag": {
        "name": ".44 Magnum",
        "category": "pistol",
        "damage_mod": 4,
        "desc_single": "a single .44 Magnum round",
        "desc_plural": ".44 Magnum rounds",
    },
    "38special": {
        "name": ".38 Special",
        "category": "pistol",
        "damage_mod": 0,
        "desc_single": "a single .38 Special round",
        "desc_plural": ".38 Special rounds",
    },
    # Rifle ammunition
    "556nato": {
        "name": "5.56x45mm NATO",
        "category": "rifle",
        "damage_mod": 2,
        "desc_single": "a single 5.56 NATO round",
        "desc_plural": "5.56 NATO rounds",
    },
    "762nato": {
        "name": "7.62x51mm NATO",
        "category": "rifle",
        "damage_mod": 4,
        "desc_single": "a single 7.62 NATO round",
        "desc_plural": "7.62 NATO rounds",
    },
    "308win": {
        "name": ".308 Winchester",
        "category": "rifle",
        "damage_mod": 4,
        "desc_single": "a single .308 Winchester round",
        "desc_plural": ".308 Winchester rounds",
    },
    "50bmg": {
        "name": ".50 BMG",
        "category": "heavy",
        "damage_mod": 10,
        "desc_single": "a single .50 BMG round",
        "desc_plural": ".50 BMG rounds",
    },
    # Shotgun ammunition
    "12gauge": {
        "name": "12 Gauge",
        "category": "shotgun",
        "damage_mod": 3,
        "desc_single": "a single 12 gauge shell",
        "desc_plural": "12 gauge shells",
    },
    "12gauge_slug": {
        "name": "12 Gauge Slug",
        "category": "shotgun",
        "damage_mod": 5,
        "desc_single": "a single 12 gauge slug",
        "desc_plural": "12 gauge slugs",
    },
    # Specialty ammunition
    "flare": {
        "name": "12 Gauge Flare",
        "category": "signal",
        "damage_mod": 0,
        "desc_single": "a single 12 gauge flare cartridge",
        "desc_plural": "12 gauge flare cartridges",
    },
    "nail": {
        "name": "Framing Nail Strip",
        "category": "tool",
        "damage_mod": 0,
        "desc_single": "a strip of framing nails",
        "desc_plural": "strips of framing nails",
    },
    "fuel": {
        "name": "Incendiary Fuel Canister",
        "category": "fuel",
        "damage_mod": 0,
        "desc_single": "an incendiary fuel canister",
        "desc_plural": "incendiary fuel canisters",
    },
}

# Dark thematic descriptions for ammunition
AMMO_DARK_DESCRIPTIONS = {
    "single_bullet": [
        "Weighs as much as a human life.",
        "A small brass promise of violence.",
        "Cold to the touch. Colder in application.",
        "Someone, somewhere, cast this with purpose. Not a good one.",
        "The weight of possibility - mostly the bad kind.",
        "A question that can only be answered once.",
        "Small enough to hold. Heavy enough to end everything.",
        "The last thing some people will ever see coming.",
    ],
    "single_shell": [
        "Rattles with the sound of finality.",
        "Packed with enough hate to spread around.",
        "A shell game where everyone loses.",
        "The brass casing catches light. The contents catch flesh.",
        "Close range, wide damage, narrow chances of walking away.",
    ],
    "magazine": [
        "A spring-loaded nightmare waiting to happen.",
        "Rows of brass soldiers, eager for deployment.",
        "The mathematics of violence: capacity times intent.",
        "Heavy with potential. The bad kind.",
        "Click, lock, ready. That's all it takes.",
        "An organized queue for oblivion.",
        "Someone's last magazine is always the heaviest.",
    ],
    "clip": [
        "Metal fingers holding brass promises.",
        "Strips of organized destruction.",
        "The assembly line of entropy.",
        "Load, chamber, fire, repeat. Simple mathematics.",
    ],
    "drum": [
        "A carousel of carnage.",
        "Round and round, in and out, until everyone stops moving.",
        "The sound it makes when full is a death rattle in reverse.",
        "Capacity that exceeds most people's nightmares.",
    ],
}


class Ammunition(Item):
    """
    Base class for all ammunition types.
    
    Ammunition can exist as:
    - Single rounds (bullets, shells)
    - Magazines (detachable box magazines)
    - Clips (stripper clips, moon clips)
    - Drums (drum magazines)
    
    Dark thematic descriptions emphasize the lethal nature of ammunition.
    """
    
    # Ammo type (matches keys in AMMO_TYPES)
    ammo_type = AttributeProperty("9mm", autocreate=True)
    
    # Current round count
    current_rounds = AttributeProperty(1, autocreate=True)
    
    # Maximum capacity (for magazines/drums)
    max_rounds = AttributeProperty(1, autocreate=True)
    
    # Container type: "loose", "magazine", "clip", "drum"
    container_type = AttributeProperty("loose", autocreate=True)
    
    def at_object_creation(self):
        """Initialize ammunition with dark descriptions."""
        super().at_object_creation()
        self.db.is_ammo = True
        self._set_thematic_description()
    
    def _set_thematic_description(self):
        """Set the dark thematic description based on container type."""
        import random
        
        container = self.container_type
        if container == "loose":
            if self.ammo_type in ["12gauge", "12gauge_slug"]:
                desc_list = AMMO_DARK_DESCRIPTIONS.get("single_shell", [])
            else:
                desc_list = AMMO_DARK_DESCRIPTIONS.get("single_bullet", [])
        elif container == "magazine":
            desc_list = AMMO_DARK_DESCRIPTIONS.get("magazine", [])
        elif container == "clip":
            desc_list = AMMO_DARK_DESCRIPTIONS.get("clip", [])
        elif container == "drum":
            desc_list = AMMO_DARK_DESCRIPTIONS.get("drum", [])
        else:
            desc_list = AMMO_DARK_DESCRIPTIONS.get("single_bullet", [])
        
        if desc_list:
            self.db.thematic_line = random.choice(desc_list)
    
    def get_ammo_info(self):
        """Get ammunition type information."""
        return AMMO_TYPES.get(self.ammo_type, AMMO_TYPES["9mm"])
    
    def get_display_name(self, looker=None, **kwargs):
        """Get the display name based on count and type."""
        info = self.get_ammo_info()
        if self.current_rounds == 1:
            return info["desc_single"]
        else:
            return f"{self.current_rounds} {info['desc_plural']}"
    
    def return_appearance(self, looker, **kwargs):
        """Enhanced appearance with ammo details and dark theme."""
        info = self.get_ammo_info()
        
        # Build appearance
        appearance = f"|w{self.key}|n\n"
        
        # Container-specific description
        if self.container_type == "loose":
            if self.current_rounds == 1:
                appearance += f"\n{info['desc_single'].capitalize()}."
            else:
                appearance += f"\nA handful of {info['desc_plural']} - {self.current_rounds} rounds."
        elif self.container_type == "magazine":
            appearance += f"\nA magazine containing {info['desc_plural']}."
            appearance += f"\n|wCapacity:|n {self.current_rounds}/{self.max_rounds} rounds"
        elif self.container_type == "clip":
            appearance += f"\nA stripper clip loaded with {info['desc_plural']}."
            appearance += f"\n|wLoaded:|n {self.current_rounds}/{self.max_rounds} rounds"
        elif self.container_type == "drum":
            appearance += f"\nA drum magazine packed with {info['desc_plural']}."
            appearance += f"\n|wCapacity:|n {self.current_rounds}/{self.max_rounds} rounds"
        
        # Add caliber info
        appearance += f"\n|wCaliber:|n {info['name']}"
        
        # Add thematic line
        if hasattr(self.db, 'thematic_line') and self.db.thematic_line:
            appearance += f"\n\n|=l{self.db.thematic_line}|n"
        
        return appearance
    
    def use_rounds(self, count=1):
        """
        Consume rounds from this ammunition.
        
        Args:
            count: Number of rounds to use
            
        Returns:
            int: Actual number of rounds consumed
        """
        actual = min(count, self.current_rounds)
        self.current_rounds -= actual
        
        # Delete if empty loose ammo (not magazines)
        if self.current_rounds <= 0 and self.container_type == "loose":
            self.delete()
        
        return actual
    
    def add_rounds(self, count):
        """
        Add rounds to this ammunition container.
        
        Args:
            count: Number of rounds to add
            
        Returns:
            int: Number of rounds actually added (limited by capacity)
        """
        space = self.max_rounds - self.current_rounds
        actual = min(count, space)
        self.current_rounds += actual
        return actual
    
    def is_compatible_with(self, weapon):
        """
        Check if this ammo is compatible with a weapon.
        
        Args:
            weapon: The weapon to check compatibility with
            
        Returns:
            bool: True if compatible
        """
        if not weapon or not hasattr(weapon, 'db'):
            return False
        
        weapon_ammo_type = getattr(weapon.db, 'ammo_type', None)
        if not weapon_ammo_type:
            return False
        
        # Exact match
        if self.ammo_type == weapon_ammo_type:
            return True
        
        # Compatible ammo types (e.g., 12gauge_slug works in 12gauge weapons)
        COMPATIBLE_AMMO = {
            "12gauge": ["12gauge", "12gauge_slug"],  # Shotguns accept both buckshot and slugs
        }
        
        compatible_types = COMPATIBLE_AMMO.get(weapon_ammo_type, [])
        return self.ammo_type in compatible_types


class Magazine(Ammunition):
    """
    A detachable box magazine for firearms.
    Can be loaded into compatible weapons for quick reloading.
    """
    
    def at_object_creation(self):
        """Initialize magazine defaults."""
        self.container_type = "magazine"
        self.max_rounds = 15  # Standard pistol mag
        self.current_rounds = 15
        super().at_object_creation()


class Clip(Ammunition):
    """
    A stripper clip or speed loader for quick reloading.
    Used with revolvers and some rifles.
    """
    
    def at_object_creation(self):
        """Initialize clip defaults."""
        self.container_type = "clip"
        self.max_rounds = 6  # Standard revolver speedloader
        self.current_rounds = 6
        super().at_object_creation()


class DrumMagazine(Ammunition):
    """
    A high-capacity drum magazine.
    Heavy and bulky, but provides extended firepower.
    """
    
    def at_object_creation(self):
        """Initialize drum magazine defaults."""
        self.container_type = "drum"
        self.max_rounds = 50  # Standard drum size
        self.current_rounds = 50
        super().at_object_creation()


# =============================================================================
# WEAPON MODIFICATION SYSTEM
# =============================================================================

class WeaponMod(Item):
    """
    Base class for weapon modifications.
    
    Mods can be attached to compatible weapons using the tinkering skill.
    Each mod has a difficulty rating that determines the skill check required.
    """
    
    # Tinkering skill required (0-100 scale)
    tinkering_difficulty = AttributeProperty(25, autocreate=True)
    
    # Compatible weapon types (list of weapon_type strings)
    compatible_weapons = AttributeProperty([], autocreate=True)
    
    # Mod slot type (magazine, barrel, stock, sight, etc.)
    mod_slot = AttributeProperty("magazine", autocreate=True)
    
    # Stat modifications when attached
    stat_mods = AttributeProperty({}, autocreate=True)
    
    def at_object_creation(self):
        """Initialize weapon mod."""
        super().at_object_creation()
        self.db.is_weapon_mod = True
    
    def can_attach_to(self, weapon):
        """
        Check if this mod can be attached to a weapon.
        
        Args:
            weapon: The weapon to check
            
        Returns:
            tuple: (can_attach: bool, reason: str)
        """
        if not weapon or not hasattr(weapon, 'db'):
            return False, "Invalid weapon."
        
        weapon_type = getattr(weapon.db, 'weapon_type', None)
        if not weapon_type:
            return False, "This item cannot accept modifications."
        
        if self.compatible_weapons and weapon_type not in self.compatible_weapons:
            return False, f"This mod is not compatible with {weapon_type} weapons."
        
        # Check if slot is already occupied
        installed_mods = getattr(weapon.db, 'installed_mods', {})
        if self.mod_slot in installed_mods:
            return False, f"This weapon already has a {self.mod_slot} modification installed."
        
        return True, "Compatible."
    
    def get_tinkering_description(self):
        """Get description of difficulty for tinkering."""
        diff = self.tinkering_difficulty
        if diff <= 20:
            return "trivial (anyone can do this)"
        elif diff <= 35:
            return "simple (basic mechanical knowledge)"
        elif diff <= 50:
            return "moderate (trained technician)"
        elif diff <= 70:
            return "difficult (experienced gunsmith)"
        elif diff <= 85:
            return "very difficult (master craftsman)"
        else:
            return "nearly impossible (legendary skill required)"


class ExtendedMagazine(WeaponMod):
    """
    An extended magazine modification that increases ammo capacity.
    Relatively easy to install on most weapons.
    """
    
    def at_object_creation(self):
        """Initialize extended magazine mod."""
        super().at_object_creation()
        self.key = "extended magazine"
        self.aliases = ["ext mag", "extended mag"]
        self.db.desc = "An extended magazine base plate and spring assembly. Adds extra capacity at the cost of slightly increased weight and profile."
        
        self.mod_slot = "magazine"
        self.tinkering_difficulty = 25  # Easy - just sliding in a longer mag
        
        # Compatible with most pistol-type weapons
        self.compatible_weapons = [
            "light_pistol", "heavy_pistol", "machine_pistol",
            "light_revolver", "heavy_revolver",  # Speed loaders
        ]
        
        # Stat modifications
        self.stat_mods = {
            "ammo_capacity_bonus": 5,  # +5 rounds
        }


class DrumMagazineMod(WeaponMod):
    """
    A drum magazine modification for extreme capacity.
    Requires more skill to install and maintain.
    """
    
    def at_object_creation(self):
        """Initialize drum magazine mod."""
        super().at_object_creation()
        self.key = "drum magazine modification"
        self.aliases = ["drum mag", "drum mod"]
        self.db.desc = "A drum magazine conversion kit. Replaces the standard magazine well with a high-capacity drum feed system. Heavy, awkward, but holds an obscene amount of ammunition."
        
        self.mod_slot = "magazine"
        self.tinkering_difficulty = 55  # Moderate - requires feeding mechanism work
        
        # Compatible with automatic weapons
        self.compatible_weapons = [
            "machine_pistol", "submachine_gun", "assault_rifle",
        ]
        
        # Stat modifications
        self.stat_mods = {
            "ammo_capacity_multiplier": 3,  # Triple capacity
            "weight_penalty": 2,  # Heavier
        }


class RifleDrumMod(WeaponMod):
    """
    A heavy drum magazine for rifles and LMGs.
    Complex installation requiring advanced skills.
    """
    
    def at_object_creation(self):
        """Initialize rifle drum mod."""
        super().at_object_creation()
        self.key = "rifle drum magazine"
        self.aliases = ["rifle drum", "lmg drum"]
        self.db.desc = "A heavy-duty drum magazine designed for sustained fire from rifles and light machine guns. The installation requires significant modification to the weapon's receiver and feeding mechanism."
        
        self.mod_slot = "magazine"
        self.tinkering_difficulty = 70  # Difficult - major weapon modification
        
        # Compatible with rifle-type weapons
        self.compatible_weapons = [
            "assault_rifle", "semi-auto_rifle", "heavy_machine_gun",
        ]
        
        # Stat modifications  
        self.stat_mods = {
            "ammo_capacity_multiplier": 4,  # Quadruple capacity
            "weight_penalty": 4,  # Much heavier
        }


# =============================================================================
# SAFETYNET ACCESS DEVICES
# =============================================================================

class Wristpad(Item):
    """
    A wristpad - a sleek PDA/pipboy-like wearable device.
    Provides access to the SafetyNet intranet system with slower connection speeds.
    
    Wristpads can be worn on the wrist and provide mobile SafetyNet access.
    Connection is slower than computer terminals due to limited bandwidth.
    Shows as an accessory on the arm when worn without covering naked body parts.
    """
    
    def at_object_creation(self):
        """Initialize wristpad attributes."""
        super().at_object_creation()
        
        # SafetyNet access flag
        self.db.is_wristpad = True
        
        # Default item properties
        self.db.desc = "A compact wristpad with a flexible display screen. The device wraps around the forearm, its matte surface dotted with status LEDs and a small speaker grille. When activated, holographic displays project interface elements just above the screen. Standard municipal issue, but the firmware has clearly been modified."
        
        # Wearable on left or right arm as an accessory (thin layer, doesn't block arm)
        self.coverage = ["left_arm", "right_arm"]
        self.worn_desc = "%N is wearing a compact wristpad with a flickering display"
        
        # Light weight
        self.weight = 0.3
        
        # High layer number (worn on top, accessory layer)
        # This ensures it displays as an accessory without blocking other clothing
        self.layer = 10


class ComputerTerminal(Item):
    """
    A computer terminal - provides fast SafetyNet access.
    Typically found in fixed locations like offices, apartments, or public kiosks.
    
    Terminals provide near-instant SafetyNet access but are not portable.
    They are usually placed in rooms rather than carried.
    """
    
    def at_object_creation(self):
        """Initialize computer terminal attributes."""
        super().at_object_creation()
        
        # SafetyNet access flag
        self.db.is_computer = True
        
        # Default item properties
        self.db.desc = "A battered computer terminal with a flickering CRT monitor and a mechanical keyboard. Exposed wiring runs along its sides, patched with electrical tape and solder. Despite its appearance, the machine hums with surprising processing power. A small placard reads 'SAFETYNET ACCESS POINT' in faded municipal lettering."
        
        # Heavy, not meant to be carried
        self.weight = 25.0
        
        # Cannot be picked up by default
        self.locks.add("get:false()")


class PortableComputer(Item):
    """
    A portable computer - laptop-style device for fast SafetyNet access.
    More expensive than a wristpad but provides faster connection speeds.
    Can be carried but must be set down to use.
    """
    
    def at_object_creation(self):
        """Initialize portable computer attributes."""
        super().at_object_creation()
        
        # SafetyNet access flag
        self.db.is_computer = True
        
        # Default item properties
        self.db.desc = "A ruggedized portable computer with a reinforced case. The screen is protected by a scratch-resistant polymer, and the keyboard has been replaced with a more durable membrane type. Various ports line one edge, ready for peripheral connections. A high-gain antenna extends from the back for improved signal reception."
        
        # Moderate weight
        self.weight = 3.5


class ProxyModule(Item):
    """
    A SafetyNet proxy module that can be slotted into wristpads or computers.
    When slotted and activated via 'sn proxy', it provides +25 ICE bonus and
    evades ICE detection.
    """
    
    # Proxy module flag - identifies this as a proxy module
    is_proxy = AttributeProperty(True, autocreate=True)
    
    # Proxy type for SafetyNet integration
    proxy_type = AttributeProperty("safetynet", autocreate=True)
    
    # Active state - toggled via 'sn proxy' command
    is_active = AttributeProperty(False, autocreate=True)
    
    def at_object_creation(self):
        """Initialize proxy module attributes."""
        super().at_object_creation()
        
        self.db.is_proxy = True
        self.db.proxy_type = "safetynet"
        self.db.is_active = False
        
        # Default description
        if not self.db.desc:
            self.db.desc = "A sleek black module, roughly the size of a deck of cards. Its surface is studded with tiny LED indicators that cycle through amber and green. Circuit patterns are etched into the casing, and a connector port on one end allows it to interface with compatible devices. When powered up, a faint hum emanates from its core."
        
        # Light weight - just a module
        self.weight = 0.3


class OkamaGamebud(Item):
    """
    An Okama Gamebud - a retro handheld communication device from 1969.
    
    Originally created as a companion to the Okama Gamesphere, the Gamebud
    became popular in Kowloon Walled City due to its ability to communicate
    with other Gamebuds within the city without corporate surveillance.
    
    Easy to jailbreak and hack, they have become the preferred communication
    method for those who want to avoid ATT or Tri-Net monitoring.
    
    Commands:
    - gamebud (or gb) - View the device display
    - gamebud post=<msg> - Post to the public lobby
    - gamebud messages - Read your private messages
    - gamebud message <alias>=<msg> - Send a private message
    - gamebud alias=<name> - Change your display alias
    - gamebud color=<color> - Set your alias color
    
    Note: Aliases are stored on the device itself, so if someone steals your
    Gamebud, they can post as you!
    """
    
    def at_object_creation(self):
        """Initialize Gamebud attributes."""
        super().at_object_creation()
        
        # Gamebud access flag
        self.db.is_gamebud = True
        
        # User alias for messaging (max 10 chars)
        # Generate random alias by default - can be changed with 'gamebud alias='
        from world.gamebud.core import generate_random_alias
        from world.gamebud.constants import DEFAULT_ALIAS_COLOR
        self.db.alias = generate_random_alias()
        
        # User's chosen alias color - defaults to white
        self.db.alias_color = DEFAULT_ALIAS_COLOR
        
        # Mute state for notifications
        self.db.muted = False
        
        # Current page for message viewing
        self.db.current_page = 0
        
        # Default item properties
        self.db.desc = "Created in 1969 as a companion to the Okama Gamesphere, the Gamebud took on a life of its own in the Walled City due to its revolutionary ability to communicate with other Gamebuds within 0.002 square miles - roughly twice the size of Kowloon. Easy to jailbreak and hack, they have become the best way for the right kinds of people to communicate with others within the city, without ATT or Tri-Net breathing down their neck. It is a bubbly, hard plastic little thing with a transparent shell that fits in the palm of the hand."
        
        # Light weight - handheld device
        self.weight = 0.2

