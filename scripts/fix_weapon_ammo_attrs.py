"""
Script to fix existing weapons that are missing uses_ammo and is_ranged attributes.

Run with: @py from scripts.fix_weapon_ammo_attrs import fix_weapons; fix_weapons()
"""

from evennia.objects.models import ObjectDB


# Weapon types that should use ammo (from prototypes.py)
AMMO_WEAPON_TYPES = {
    # Generic weapons
    "flare_gun": ("flare", 1),
    "heavy_revolver": ("44mag", 6),
    "light_revolver": ("38special", 5),
    "machine_pistol": ("9mm", 33),
    "nail_gun": ("nail", 50),
    "flamethrower": ("fuel", 10),
    "heavy_machine_gun": ("50bmg", 100),
    "lever-action_rifle": ("308win", 8),
    "lever-action_shotgun": ("12gauge", 6),
    "semi-auto_rifle": ("762nato", 20),
    "semi-auto_shotgun": ("12gauge", 8),
    "bolt-action_rifle": ("762nato", 5),
    # Branded weapons
    "light_pistol": ("9mm", 10),
    "heavy_pistol": ("45acp", 15),
    "pump-action_shotgun": ("12gauge", 7),
    "break-action_shotgun": ("12gauge", 2),
    "assault_rifle": ("556nato", 30),
    "smg": ("9mm", 30),
    "anti-material_rifle": ("50bmg", 10),
}

# Weapon types that are ranged but don't use ammo
NO_AMMO_RANGED = ["stun_gun", "bowel_disruptor"]


def fix_weapons():
    """Fix all existing weapons with missing ammo attributes."""
    fixed_count = 0
    checked_count = 0
    
    # Find all objects with a weapon_type attribute
    all_objects = ObjectDB.objects.all()
    
    for obj in all_objects:
        weapon_type = obj.attributes.get("weapon_type")
        if not weapon_type:
            continue
            
        checked_count += 1
        changes_made = []
        
        # Check if this weapon type should use ammo
        if weapon_type in AMMO_WEAPON_TYPES:
            ammo_type, ammo_capacity = AMMO_WEAPON_TYPES[weapon_type]
            
            # Fix uses_ammo
            if not obj.attributes.get("uses_ammo"):
                obj.db.uses_ammo = True
                changes_made.append("uses_ammo=True")
            
            # Fix is_ranged
            if not obj.attributes.get("is_ranged"):
                obj.db.is_ranged = True
                changes_made.append("is_ranged=True")
            
            # Fix ammo_type if missing
            if not obj.attributes.get("ammo_type"):
                obj.db.ammo_type = ammo_type
                changes_made.append(f"ammo_type={ammo_type}")
            
            # Fix ammo_capacity if missing
            if not obj.attributes.get("ammo_capacity"):
                obj.db.ammo_capacity = ammo_capacity
                changes_made.append(f"ammo_capacity={ammo_capacity}")
            
            # Fix current_ammo if missing (set to capacity)
            if obj.attributes.get("current_ammo") is None:
                obj.db.current_ammo = ammo_capacity
                changes_made.append(f"current_ammo={ammo_capacity}")
                
        elif weapon_type in NO_AMMO_RANGED:
            # These are ranged but don't use ammo
            if not obj.attributes.get("is_ranged"):
                obj.db.is_ranged = True
                changes_made.append("is_ranged=True")
            
            if obj.attributes.get("uses_ammo") is None:
                obj.db.uses_ammo = False
                changes_made.append("uses_ammo=False")
        
        if changes_made:
            fixed_count += 1
            print(f"Fixed {obj.key} (#{obj.id}): {', '.join(changes_made)}")
    
    print(f"\nChecked {checked_count} weapons, fixed {fixed_count}.")
    return fixed_count


if __name__ == "__main__":
    fix_weapons()
