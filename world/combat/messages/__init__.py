import importlib
import random

from .body_parts import (
    get_impact_description,
    get_wound_description,
    get_kill_description,
    get_wound_type_for_weapon,
    format_location_for_display,
    is_vital_hit
)

# Import disguise system for proper identity display
try:
    from world.disguise.core import get_display_identity
except ImportError:
    # Fallback if disguise system not available
    def get_display_identity(character, looker):
        return (character.key if character else "Someone", True)


def get_combat_message(weapon_type, phase, attacker=None, target=None, item=None, **kwargs):
    """
    Load the appropriate combat message from a specific weapon_type module.
    Returns a dictionary with "attacker_msg", "victim_msg", and "observer_msg".

    Args:
        weapon_type (str): e.g., "unarmed", "blade"
        phase (str): One of "initiate", "hit", "miss", "kill", etc.
        attacker (Object): The attacker
        target (Object): The target
        item (Object): The weapon/item used (can be None for unarmed)
        **kwargs: Any extra variables for formatting (e.g., damage, hit_location)

    Returns:
        dict: A dictionary containing formatted "attacker_msg", "victim_msg",
              and "observer_msg" strings.
    """
    # Get display identities - what each party sees
    # Attacker sees target's identity (attacker knows who they are attacking)
    attacker_sees_target, _ = get_display_identity(target, attacker) if target and attacker else ("someone", True)
    # Victim sees attacker's disguised identity
    victim_sees_attacker, _ = get_display_identity(attacker, target) if attacker and target else ("Someone", True)
    # Observers see disguised identities of both (use None as looker for generic view)
    observer_sees_attacker, _ = get_display_identity(attacker, None) if attacker else ("Someone", True)
    observer_sees_target, _ = get_display_identity(target, None) if target else ("someone", True)
    
    # For attacker_msg, we use "You" for attacker, and what attacker sees for target
    attacker_s = attacker.key if attacker else "Someone"  # Not used in attacker_msg but kept for compatibility
    target_s_for_attacker = attacker_sees_target
    target_s_for_victim = target.key if target else "someone"  # Victim knows their own name
    attacker_s_for_victim = victim_sees_attacker
    attacker_s_for_observer = observer_sees_attacker
    target_s_for_observer = observer_sees_target
    
    item_s = item.key if item else "fists" # Default item name if None

    # Determine verb forms for fallback messages based on phase
    verb_root = phase.lower()
    attacker_verb = verb_root # For "You verb..."
    third_person_verb = f"{verb_root}s" # Default for "Someone verbs..."

    if verb_root.endswith("s") or verb_root.endswith("sh") or \
       verb_root.endswith("ch") or verb_root.endswith("x") or \
       verb_root.endswith("z"):
        third_person_verb = f"{verb_root}es"
    elif verb_root.endswith("y") and len(verb_root) > 1 and verb_root[-2].lower() not in "aeiou":
        third_person_verb = f"{verb_root[:-1]}ies"
    
    # Specific overrides for common verbs if needed
    if verb_root == "hit":
        attacker_verb = "hit"
        third_person_verb = "hits"
    elif verb_root == "miss": # "miss" -> "misses"
        attacker_verb = "miss" # "You miss"
        third_person_verb = "misses" # "Someone misses"
    # Add more overrides if other phases require special verb forms

    # Fallback message templates (using placeholders)
    fallback_template_set = {
        "attacker_msg": f"You {attacker_verb} {{target_name}} with {{item_name}}.",
        "victim_msg": f"{{attacker_name}} {third_person_verb} you with {{item_name}}.",
        "observer_msg": f"{{attacker_name}} {third_person_verb} {{target_name}} with {{item_name}}."
    }

    chosen_template_set = None
    try:
        module_path = f"world.combat.messages.{weapon_type}"
        module = importlib.import_module(module_path)
        messages_for_weapon = getattr(module, "MESSAGES", {})
        templates_for_phase = messages_for_weapon.get(phase, [])
        
        if templates_for_phase and isinstance(templates_for_phase, list):
            valid_templates = [t for t in templates_for_phase if isinstance(t, dict)]
            if valid_templates:
                chosen_template_set = random.choice(valid_templates)
    except ModuleNotFoundError:
        pass # chosen_template_set remains None, will use fallback
    except Exception as e:
        pass # chosen_template_set remains None, will use fallback

    # If no specific template was loaded (or error), use the fallback set
    if not chosen_template_set:
        chosen_template_set = fallback_template_set

    # Get hit location and generate body-part-specific content
    hit_location_raw = kwargs.get("hit_location", "chest")
    hit_location_display = format_location_for_display(hit_location_raw)
    wound_type = get_wound_type_for_weapon(weapon_type)
    
    # Generate body-part-specific descriptions for templates to use
    impact_desc = get_impact_description(hit_location_raw)
    wound_desc = get_wound_description(hit_location_raw, wound_type)
    kill_desc = get_kill_description(hit_location_raw)
    vital_hit = is_vital_hit(hit_location_raw)

    # Prepare base kwargs for formatting (without names - those are per-message)
    base_format_kwargs = {
        "item_name": item_s,
        "item": item_s,          # Alias for convenience if templates use {item}
        "phase": phase,          # Pass phase itself if templates need it
        # Body part context
        "hit_location": hit_location_display,
        "impact": impact_desc,
        "wound": wound_desc,
        "kill_desc": kill_desc,
        "vital_hit": vital_hit,
        **{k: v for k, v in kwargs.items() if k != "hit_location"}  # Other kwargs except raw hit_location
    }
    
    # Per-message format kwargs with appropriate names for each perspective
    format_kwargs_attacker = {
        **base_format_kwargs,
        "attacker_name": attacker.key if attacker else "Someone",  # Attacker knows themselves
        "target_name": target_s_for_attacker,  # What attacker sees target as
        "attacker": attacker.key if attacker else "Someone",
        "target": target_s_for_attacker,
    }
    format_kwargs_victim = {
        **base_format_kwargs,
        "attacker_name": attacker_s_for_victim,  # What victim sees attacker as (disguised)
        "target_name": target.key if target else "someone",  # Victim knows themselves
        "attacker": attacker_s_for_victim,
        "target": target.key if target else "someone",
    }
    format_kwargs_observer = {
        **base_format_kwargs,
        "attacker_name": attacker_s_for_observer,  # Disguised name
        "target_name": target_s_for_observer,  # Disguised name
        "attacker": attacker_s_for_observer,
        "target": target_s_for_observer,
    }

    final_messages = {}
    # Define which phases should be colored red for "successful hits"
    # This assumes 'hit' for grapple initiation should also be red, as per "like the initiate message"
    successful_hit_phases = [
        "initiate", # Add this line
        "hit",
        "grapple_damage_hit",
        "kill",
        "grapple_damage_kill"
        # Add any other phases that represent a "successful hit" you want red
    ]
    
    miss_phases = [
        "miss",
        "grapple_damage_miss"
        # Add any other phases that represent a "miss" you want white
    ]

    for msg_key in ["attacker_msg", "victim_msg", "observer_msg"]:
        # Select appropriate format kwargs based on message type
        if msg_key == "attacker_msg":
            format_kwargs = format_kwargs_attacker
        elif msg_key == "victim_msg":
            format_kwargs = format_kwargs_victim
        else:
            format_kwargs = format_kwargs_observer
            
        # Get template string from chosen set, or from fallback_template_set if key is missing in chosen
        template_str = chosen_template_set.get(msg_key, fallback_template_set.get(msg_key, "Error: Message template key missing."))
        try:
            formatted_msg = template_str.format(**format_kwargs)
            
            # Apply colors based on phase type
            # Assumes the template_str itself does not contain color codes for these phases.
            if phase in successful_hit_phases:
                if not (formatted_msg.startswith("|") and formatted_msg.endswith("|n")):
                    if phase == "kill" or phase == "grapple_damage_kill": # Check for kill phases
                        final_messages[msg_key] = f"|r{formatted_msg}|n" # Apply bold red for kill
                    else:
                        final_messages[msg_key] = f"|R{formatted_msg}|n" # Apply non-bold red for other successful hits
                else:
                    final_messages[msg_key] = formatted_msg # Pass through if already colored
            elif phase in miss_phases:
                if not (formatted_msg.startswith("|") and formatted_msg.endswith("|n")):
                    final_messages[msg_key] = f"|W{formatted_msg}|n" # Apply white for misses
                else:
                    final_messages[msg_key] = formatted_msg # Pass through if already colored
            else:
                final_messages[msg_key] = formatted_msg

        except KeyError as e_key:
            final_messages[msg_key] = f"(Error: Missing placeholder {e_key} in template for '{msg_key}')"
        except Exception as e_fmt:
            final_messages[msg_key] = f"(Error: Formatting issue for '{msg_key}': {e_fmt})"

    return final_messages
