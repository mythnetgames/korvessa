"""
SafetyNet - Kowloon Intranet Social System

A municipal safety + communications platform that was co-opted into a social
feed after deckers cracked the codebase open. Now serves as the primary
in-game social network for the residents of Kowloon.

Key Features:
- Feed-based posting with 72-hour decay
- Multiple net accounts (handles) per player
- Login state persistence
- DM system
- Hacking/ICE security mechanics
- Requires access devices (Wristpad or Computer)
"""

from world.safetynet.core import (
    SafetyNetManager,
    get_safetynet_manager,
)
from world.safetynet.utils import (
    check_access_device,
    get_connection_delay,
    generate_password,
)
