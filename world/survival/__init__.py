"""
Survival System - Hunger, Thirst, and Intoxication

This module provides a comprehensive survival system including:
- Hunger tracking (must eat once per day)
- Thirst tracking (must drink twice per day)
- Intoxication system with tiered effects
- Nutritious food bonuses
- Starvation and dehydration effects
"""

from .core import (
    # Hunger/Thirst state
    get_survival_state,
    record_meal,
    record_drink,
    is_hungry,
    is_thirsty,
    
    # Intoxication
    add_intoxication,
    get_intoxication_level,
    get_intoxication_tier,
    process_sobering,
    clear_intoxication,
    
    # Nutrition bonus
    add_nutrition_bonus,
    has_nutrition_bonus,
    
    # Status checks
    is_starving,
    is_dehydrated,
    check_survival_effects,
    
    # Speech processing
    slur_speech,
    
    # Constants
    INTOXICATION_TIERS,
    HUNGER_MESSAGES,
    THIRST_MESSAGES,
    
    # Ambient messages
    get_random_hunger_message,
    get_random_thirst_message,
    
    # Login tracking
    update_login_tracking,
)

from .script import (
    SurvivalTickerScript,
    start_survival_ticker,
    stop_survival_ticker,
)
