BLEEDING CONDITION INSTANTIATION SEARCH RESULTS
===============================================

Search Date: January 12, 2026
Purpose: Find all places where BleedingCondition is instantiated or bleeding conditions are added

SUMMARY
=======
Total Locations Found: 12 active instantiation sites
Identified Issue: Multiple BleedingCondition instances being created in CmdAdmin test commands (5 instances)

DETAILED FINDINGS
=================

PRIMARY CONDITION CREATION SYSTEM
==================================

1. MAIN BLEEDING CONDITION CREATION FUNCTION
   File: [world/medical/conditions.py](world/medical/conditions.py#L304-L365)
   Function: `create_condition_from_damage()`
   Lines: 304-365
   
   Description: Central function that creates BleedingCondition instances based on damage type and amount.
   
   Key Logic:
   - Sharp/penetrating wounds (bullet, blade, stab, laceration, cut):
     * Threshold: 8+ damage triggers bleeding
     * Severity calculation: damage_amount // 4 (max severity 10)
     * Line 344: conditions.append(BleedingCondition(bleeding_severity, location))
     
   - Other damage types (blunt, burn, etc):
     * Threshold: 10+ damage triggers bleeding
     * Severity calculation: damage_amount // 3 (max severity 10)
     * Line 354: conditions.append(BleedingCondition(bleeding_severity, location))
   
   Armor Protection Factor: 0.0-1.0 ratio applied to reduce bleeding chance and severity
   - condition_prevention_chance = armor_protection * 100
   - Random roll: random.randint(1, 100) > condition_prevention_chance prevents bleeding
   - Severity reduction: up to 50% reduction from armor


DAMAGE APPLICATION PIPELINE
============================

2. DAMAGE APPLICATION ENTRY POINT
   File: [typeclasses/characters.py](typeclasses/characters.py#L596)
   Function: `Character.take_damage()`
   Lines: 596-660
   
   Processes:
   1. Validates damage amount (must be int > 0)
   2. Calculates armor damage reduction
   3. Calls apply_anatomical_damage()
   4. Handles death/unconsciousness state changes
   
   Called from: [world/combat/handler.py](world/combat/handler.py#L1428)
   Line 1428: target.take_damage(damage, location=hit_location, injury_type=injury_type, target_organ=target_organ)


3. ANATOMICAL DAMAGE APPLICATION
   File: [world/medical/utils.py](world/medical/utils.py#L521)
   Function: `apply_anatomical_damage()`
   Lines: 521-615
   
   Process Flow:
   1. Accesses medical_state from character
   2. Stores armor_protection ratio
   3. Distributes damage to organs in location
   4. Calls medical_state.take_organ_damage() for each organ
   
   Key Line 544: self.add_condition(condition) - adds condition to medical state


4. ORGAN DAMAGE AND CONDITION CREATION
   File: [world/medical/core.py](world/medical/core.py#L521)
   Function: `MedicalState.take_organ_damage()`
   Lines: 521-545
   
   Process Flow:
   1. Applies damage to organ directly
   2. If damage > 0, calls _create_conditions_from_damage()
   3. Iterates through returned conditions and calls add_condition() for each
   
   Lines 535-538:
   ```python
   for condition in new_conditions:
       self.add_condition(condition)
   ```


5. CONDITION ADDITION TO MEDICAL STATE
   File: [world/medical/core.py](world/medical/core.py#L573)
   Function: `MedicalState.add_condition()`
   Lines: 573-620
   
   Validation:
   - Checks if character is archived (permanently dead) - skips condition if true
   - Prevents duplicate conditions (checks if condition already in list)
   - Starts ticker for conditions that require it (requires_ticker attribute)
   
   Debug Output:
   - Line 599: "ADD_CONDITION: Added {condition.condition_type} severity {condition.severity}"
   - Line 612: "ADD_CONDITION: Starting ticker for {condition.condition_type} on {character.key}"


TEST/ADMIN INSTANTIATION SITES
==============================

6. ADMIN TEST COMMAND - CONSCIOUS SUICIDE SCENARIO
   File: [commands/CmdAdmin.py](commands/CmdAdmin.py#L422-L442)
   Lines: 422-442
   Context: CmdAdmin setdeathtrauma function
   
   REPETITIVE CODE PATTERN - 5 BleedingCondition instances created in sequence:
   
   Line 422-426: First arterial bleed
   ```python
   arterial_bleeding_1 = BleedingCondition(
       severity=10,
       location="neck"
   )
   ```
   
   Line 427-430: Second arterial bleed
   ```python
   arterial_bleeding_2 = BleedingCondition(
       severity=10,
       location="chest"
   )
   ```
   
   Line 432-435: Third arterial bleed
   ```python
   arterial_bleeding_3 = BleedingCondition(
       severity=10,
       location="abdomen"
   )
   ```
   
   Line 437-440: Fourth arterial bleed
   ```python
   arterial_bleeding_4 = BleedingCondition(
       severity=10,
       location="left_leg"
   )
   ```
   
   Line 442-445: Fifth arterial bleed (partial read, continues to line 450+)
   ```python
   arterial_bleeding_5 = BleedingCondition(
       severity=10,
       location="right_leg"
   )
   ```
   
   Analysis: This is a test command creating multiple severe arterial bleeds (10% blood loss each per tick).
   The pattern is clearly repetitive boilerplate that could be refactored with a loop.


CONDITION DESERIALIZATION
==========================

7. CONDITION LOADING FROM DATABASE
   File: [world/medical/core.py](world/medical/core.py#L705-L712)
   Function: `MedicalState.from_dict()` (line 705+)
   Line 712: condition = BleedingCondition.from_dict(condition_dict)
   
   Context: When loading persisted character state from database
   Used for character reloading/restarts only


CONDITION CLASS DEFINITION
==========================

8. BLEEDING CONDITION CLASS
   File: [world/medical/conditions.py](world/medical/conditions.py#L122)
   Line 122: class BleedingCondition(MedicalCondition):
   
   Properties:
   - requires_ticker = True (automatic ticker-based decay)
   - Natural clotting with decay_rate (default 1 per tick)
   - Location tracking
   - Blood loss rate calculation based on severity


DOCUMENTATION REFERENCES
========================

9-12. Various documentation and spec files reference BleedingCondition but don't instantiate:
   - [specs/HEALTH_AND_SUBSTANCE_SYSTEM_SPEC.md](specs/HEALTH_AND_SUBSTANCE_SYSTEM_SPEC.md#L2195)
   - Combat message templates in weapon message files (narrative only, no instantiation)


LOOPING/REPETITIVE CODE IDENTIFIED
===================================

FINDING #1: REPETITIVE ADMIN TEST CODE
Location: [commands/CmdAdmin.py](commands/CmdAdmin.py#L422-L450)
Issue: 5 sequential BleedingCondition instantiations with nearly identical code
Severity: LOW (admin test only, not production code)
Recommendation: Refactor to use list comprehension or loop

Example of current repetitive code:
```python
arterial_bleeding_1 = BleedingCondition(severity=10, location="neck")
arterial_bleeding_2 = BleedingCondition(severity=10, location="chest")
arterial_bleeding_3 = BleedingCondition(severity=10, location="abdomen")
arterial_bleeding_4 = BleedingCondition(severity=10, location="left_leg")
arterial_bleeding_5 = BleedingCondition(severity=10, location="right_leg")
```

Could be refactored to:
```python
locations = ["neck", "chest", "abdomen", "left_leg", "right_leg"]
arterial_bleeds = [BleedingCondition(severity=10, location=loc) for loc in locations]
```


PRODUCTION SYSTEM FLOW
======================

Normal Combat Damage Flow (Non-Looping):
1. Combat Handler calls take_damage() ONCE per attack
2. take_damage() calls apply_anatomical_damage() ONCE
3. apply_anatomical_damage() calls take_organ_damage() for each organ affected (1-3 organs typically)
4. take_organ_damage() calls create_condition_from_damage() ONCE per organ
5. create_condition_from_damage() CONDITIONALLY creates 1-3 BleedingCondition instances based on damage type

Result: NO PROBLEMATIC LOOPING in production code
- Each damage application creates at most 3 conditions per organ
- Multiple organs in hit location can create multiple conditions, but this is intentional
- Example: Heavy blade damage to left arm hits 4 organs (bone, muscle, blood vessel, skin) = max 12 bleeding conditions across 4 organs


ARMOR PROTECTION INTEGRATION
=============================

All BleedingCondition creation routes through create_condition_from_damage() which applies armor protection:
- armor_protection passed through character.take_damage() -> apply_anatomical_damage() -> MedicalState.take_organ_damage() -> create_condition_from_damage()
- Ratio stored in medical_state._current_armor_protection
- Used to calculate condition_prevention_chance and severity_reduction


CONDITION TICKER SYSTEM
=======================

All created BleedingConditions automatically start tickers via:
1. MedicalState.add_condition() detects requires_ticker = True
2. Calls condition.start_condition(character)
3. Ticker script runs on schedule, applies decay and vital sign changes
4. No multiple condition creation through ticker system


CONCLUSION
==========

FINDING: NO PROBLEMATIC LOOPING CREATING DUPLICATE BLEEDING CONDITIONS

The system properly:
- Creates conditions only once per damage application
- Prevents duplicates through add_condition() deduplication check
- Applies armor protection consistently across all creation routes
- Uses ticker-based system for decay (not condition creation loops)

ONLY ISSUE FOUND: Repetitive boilerplate in admin test code (CmdAdmin.py lines 422-450)
- Not a functional problem, just code quality issue
- Recommendation: Refactor to use loop/list comprehension for 5 BleedingCondition creations
