"""
Disguise & Anonymity System

This module provides identity concealment mechanics including:
- Item-based anonymity (hoodies, masks, helmets)
- Skill-based disguises (Disguise skill profiles)
- Slip mechanics and identity revelation
- Observer memory and recognition
"""

from .core import (
    get_anonymity_descriptor,
    get_active_disguise,
    get_display_identity,
    check_item_anonymity,
    check_disguise_slip,
    trigger_slip_event,
    apply_disguise,
    break_disguise,
    adjust_anonymity_item,
    mark_identity_known,
    knows_identity,
    get_disguise_stability,
    damage_disguise_stability,
)

__all__ = [
    "get_anonymity_descriptor",
    "get_active_disguise", 
    "get_display_identity",
    "check_item_anonymity",
    "check_disguise_slip",
    "trigger_slip_event",
    "apply_disguise",
    "break_disguise",
    "adjust_anonymity_item",
    "mark_identity_known",
    "knows_identity",
    "get_disguise_stability",
    "damage_disguise_stability",
]
