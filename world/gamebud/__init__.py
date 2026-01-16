"""
Gamebud System

The Okama Gamebud is a retro communication device from 1969 that allows
peer-to-peer messaging within Kowloon Walled City. Easy to jailbreak,
these devices have become the preferred communication method for those
who want to avoid corporate surveillance.
"""

from world.gamebud.core import (
    get_gamebud_manager, 
    GamebudManager,
    start_gamebud_typing,
    cancel_gamebud_typing,
    is_gamebud_typing,
    calculate_typing_delay,
)

__all__ = [
    "get_gamebud_manager", 
    "GamebudManager",
    "start_gamebud_typing",
    "cancel_gamebud_typing",
    "is_gamebud_typing",
    "calculate_typing_delay",
]
