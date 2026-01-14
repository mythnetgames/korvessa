# Chrome Reference Table
# Used for chrome spawning and install logic
# Note: Chrome prototypes are now defined in world/chrome_prototypes.py
# This file provides a quick reference lookup table

CHROME_TABLE = [
    # Mind's Eye (Legacy)
    {
        "name": "Mind's Eye",
        "shortname": "mindseye",
        "buffs": "No buffs",
        "abilities": "Hear thoughts.",
        "empathy_cost": -0.25
    },
    # =============================================================================
    # HEAD CHROME
    # =============================================================================
    {
        "name": "BaoSteel NanoTrace Probability Calculator Cranial Implant Mk. I",
        "shortname": "BS-ProbCal",
        "buffs": "+2 Smarts",
        "abilities": None,
        "empathy_cost": 1.5,
        "slot": "head",
        "type": "internal"
    },
    {
        "name": "AnSteel NanoTrace Probability Calculator Cranial Implant Mk. I",
        "shortname": "AS-ProbCal",
        "buffs": "+2 Smarts",
        "abilities": None,
        "empathy_cost": 1.5,
        "slot": "head",
        "type": "internal"
    },
    {
        "name": "BaoSteel NanoTrace Parietal Amplifier Cranial Implant Mk. I",
        "shortname": "BS-ParAmp",
        "buffs": "+1 Smarts",
        "abilities": None,
        "empathy_cost": 0.90,
        "slot": "head",
        "type": "internal"
    },
    {
        "name": "AnSteel NanoTrace Parietal Amplifier Cranial Implant Mk. I",
        "shortname": "AS-ParAmp",
        "buffs": "+1 Smarts",
        "abilities": None,
        "empathy_cost": 0.90,
        "slot": "head",
        "type": "internal"
    },
    {
        "name": "BaoSteel Subdermal Skull Plating",
        "shortname": "BS-SKLPLT",
        "buffs": "+1 Armor to Head",
        "abilities": None,
        "empathy_cost": 1.5,
        "slot": "head",
        "type": "internal"
    },
    {
        "name": "NanoTrace Nerves Of Steel!",
        "shortname": "NT-NRV",
        "buffs": "+1 Edge",
        "abilities": None,
        "empathy_cost": 0.90,
        "slot": "head",
        "type": "internal"
    },
    {
        "name": "Nerves Of BaoSteel",
        "shortname": "BS-NRV",
        "buffs": "+2 Edge",
        "abilities": None,
        "empathy_cost": 1.5,
        "slot": "head",
        "type": "internal"
    },
    {
        "name": "MadGenTek Electroconvulsive Motor Cortex Stimulator",
        "shortname": "NRVZAP",
        "buffs": "+2 Reflexes",
        "abilities": None,
        "empathy_cost": 1.5,
        "slot": "head",
        "type": "internal"
    },
    {
        "name": "NanoTrace Axon Enhancer",
        "shortname": "NT-AX",
        "buffs": "+1 Reflexes",
        "abilities": None,
        "empathy_cost": 0.90,
        "slot": "head",
        "type": "internal"
    },
    {
        "name": "Morikawa Kabuto",
        "shortname": "MK-KABUTO",
        "buffs": "+3 Armor to Head",
        "abilities": None,
        "empathy_cost": 2.5,
        "slot": "head",
        "type": "external",
        "notes": "Yakuza muscle, already customized, incompatible with skull plating"
    },
    # =============================================================================
    # FACE CHROME
    # =============================================================================
    {
        "name": "NanoTrace Surface Wiring",
        "shortname": "NT-SW",
        "buffs": "Cosmetic",
        "abilities": "Cosmetic fashionware",
        "empathy_cost": 0,
        "slot": "face",
        "type": "external"
    },
    {
        "name": "BaoSteel Subdermal Facial Plating",
        "shortname": "BS-FCEPLT",
        "buffs": "+1 Armor to Face",
        "abilities": None,
        "empathy_cost": 1.5,
        "slot": "face",
        "type": "internal"
    },
    {
        "name": "Morikawa Menpo",
        "shortname": "MK-MENPO",
        "buffs": "+3 Armor to Face",
        "abilities": None,
        "empathy_cost": 2.5,
        "slot": "face",
        "type": "external",
        "notes": "Yakuza muscle, already customized, incompatible with facial plating"
    },
    # =============================================================================
    # EYE CHROME
    # =============================================================================
    {
        "name": "MadGenTek Bug Eyes",
        "shortname": "BUG-I",
        "buffs": None,
        "abilities": "5 optical slots, replaces eye slot",
        "empathy_cost": 4.0,
        "slot": "eyes",
        "type": "external",
        "notes": "Borgware"
    },
    {
        "name": "BaoSteel Cybereye Set",
        "shortname": "BS-3YE5",
        "buffs": None,
        "abilities": "2 optical slots, replaces eye slot",
        "empathy_cost": 2.0,
        "slot": "eyes",
        "type": "external"
    },
    {
        "name": "AnSteel Cybereye Set",
        "shortname": "AS-3YE5",
        "buffs": None,
        "abilities": "2 optical slots, replaces eye slot",
        "empathy_cost": 2.0,
        "slot": "eyes",
        "type": "external"
    },
    {
        "name": "BaoSteel Cybereye",
        "shortname": "BS-3YE",
        "buffs": None,
        "abilities": "1 optical slot, replaces selected eye",
        "empathy_cost": 1.0,
        "slot": "eye",
        "type": "external"
    },
    {
        "name": "AnSteel Cybereye",
        "shortname": "AS-3YE",
        "buffs": None,
        "abilities": "1 optical slot, replaces selected eye",
        "empathy_cost": 1.0,
        "slot": "eye",
        "type": "external"
    },
    {
        "name": "BaoSteel Reinforced Cybereye Set",
        "shortname": "BS-R3YE5",
        "buffs": "+1 Armor to Eyes",
        "abilities": "2 optical slots, replaces eye slot",
        "empathy_cost": 3.0,
        "slot": "eyes",
        "type": "external",
        "notes": "Cannot be customized"
    },
    {
        "name": "BaoSteel Reinforced Cybereye",
        "shortname": "BS-R3YE",
        "buffs": "+1 Armor to Applied Eye",
        "abilities": "1 optical slot, replaces applied eye",
        "empathy_cost": 2.0,
        "slot": "eye",
        "type": "external",
        "notes": "Cannot be customized"
    },
    {
        "name": "Morikawa Gaze",
        "shortname": "MK-GAZE",
        "buffs": "+3 Armor to Eyes",
        "abilities": None,
        "empathy_cost": 3.5,
        "slot": "eyes",
        "type": "external",
        "notes": "Yakuza muscle, already customized, incompatible with cybereyes"
    },
    # =============================================================================
    # EAR CHROME
    # =============================================================================
    {
        "name": "BaoSteel Cyberear Set (External)",
        "shortname": "BS-E4R5-EXT",
        "buffs": None,
        "abilities": "4 ear slots, replaces ear nakeds",
        "empathy_cost": 2.0,
        "slot": "ears",
        "type": "external"
    },
    {
        "name": "BaoSteel Cyberear Set (Internal)",
        "shortname": "BS-E4R5-INT",
        "buffs": None,
        "abilities": "4 ear slots",
        "empathy_cost": 2.0,
        "slot": "ears",
        "type": "internal"
    },
    {
        "name": "AnSteel Cyberear Set (External)",
        "shortname": "AS-E4R5-EXT",
        "buffs": None,
        "abilities": "4 ear slots, replaces ear nakeds",
        "empathy_cost": 2.0,
        "slot": "ears",
        "type": "external"
    },
    {
        "name": "AnSteel Cyberear Set (Internal)",
        "shortname": "AS-E4R5-INT",
        "buffs": None,
        "abilities": "4 ear slots",
        "empathy_cost": 2.0,
        "slot": "ears",
        "type": "internal"
    },
    # =============================================================================
    # ARM/HAND CHROME
    # =============================================================================
    {
        "name": "BaoSteel Cyberarm Set",
        "shortname": "BS-4RM5",
        "buffs": "+1 Arm Armor, +2 Body, +2 Dexterity, +2 Technique",
        "abilities": "4 module slots, replaces arms",
        "empathy_cost": 4.0,
        "slot": "arms",
        "type": "external"
    },
    {
        "name": "AnSteel Cyberarm Set",
        "shortname": "AS-4RM5",
        "buffs": "+1 Arm Armor, +2 Body, +2 Dexterity, +2 Technique",
        "abilities": "4 module slots, replaces arms",
        "empathy_cost": 4.0,
        "slot": "arms",
        "type": "external"
    },
    {
        "name": "BaoSteel Cyberarm",
        "shortname": "BS-4RM",
        "buffs": "+1 Body, +1 Dexterity, +1 Technique",
        "abilities": "2 module slots, replaces arm",
        "empathy_cost": 2.0,
        "slot": "arm",
        "type": "external"
    },
    {
        "name": "AnSteel Cyberarm",
        "shortname": "AS-4RM",
        "buffs": "+1 Body, +1 Dexterity, +1 Technique",
        "abilities": "2 module slots, replaces arm",
        "empathy_cost": 2.0,
        "slot": "arm",
        "type": "external"
    },
    # =============================================================================
    # LEG/FEET CHROME
    # =============================================================================
    {
        "name": "BaoSteel Cyberleg Set",
        "shortname": "BS-L3G5",
        "buffs": "+1 Leg Armor, +2 Body, +2 Dexterity, +2 Reflexes",
        "abilities": "4 module slots, replaces legs",
        "empathy_cost": 4.0,
        "slot": "legs",
        "type": "external"
    },
    {
        "name": "AnSteel Cyberleg Set",
        "shortname": "AS-L3G5",
        "buffs": "+1 Leg Armor, +2 Body, +2 Dexterity, +2 Reflexes",
        "abilities": "4 module slots, replaces legs",
        "empathy_cost": 4.0,
        "slot": "legs",
        "type": "external"
    },
    {
        "name": "BaoSteel Cyberleg",
        "shortname": "BS-L3G",
        "buffs": "+1 Body, +1 Dexterity, +1 Reflexes",
        "abilities": "2 module slots, replaces leg",
        "empathy_cost": 2.0,
        "slot": "leg",
        "type": "external"
    },
    {
        "name": "AnSteel Cyberleg",
        "shortname": "AS-L3G",
        "buffs": "+1 Body, +1 Dexterity, +1 Reflexes",
        "abilities": "2 module slots, replaces leg",
        "empathy_cost": 2.0,
        "slot": "leg",
        "type": "external"
    },
    {
        "name": "BaoSteel Cyberfeet Set",
        "shortname": "BS-F33T",
        "buffs": "+1 Dexterity, +1 Reflexes",
        "abilities": "Replaces feet",
        "empathy_cost": 1.0,
        "slot": "feet",
        "type": "external"
    },
    {
        "name": "AnSteel Cyberfeet Set",
        "shortname": "AS-F33T",
        "buffs": "+1 Dexterity, +1 Reflexes",
        "abilities": "Replaces feet",
        "empathy_cost": 1.0,
        "slot": "feet",
        "type": "external"
    },
    {
        "name": "BaoSteel Cyberfoot",
        "shortname": "BS-F00T",
        "buffs": None,
        "abilities": "Replaces foot",
        "empathy_cost": 0.5,
        "slot": "foot",
        "type": "external"
    },
    {
        "name": "AnSteel Cyberfoot",
        "shortname": "AS-F00T",
        "buffs": None,
        "abilities": "Replaces foot",
        "empathy_cost": 0.5,
        "slot": "foot",
        "type": "external"
    },
]
