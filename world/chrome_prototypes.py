# =============================================================================
# CHROME/CYBERWARE PROTOTYPES
# =============================================================================
# These prototypes define cybernetic augmentations (chrome) that can be spawned
# using the spawnchrome command. Each prototype uses a shortname as the
# prototype_key for easy spawning.
#
# Usage: spawnchrome <number> <shortname>
# Example: spawnchrome 1 BS-ProbCal
# =============================================================================

# Base chrome prototype with common properties
CHROME_BASE = {
    "typeclass": "typeclasses.items.Item",
    "is_chrome": True,
    "is_medical_item": True,
    "is_physical": True,
    "tags": [("chrome", "cyberware"), ("item", "general")],
}

# =============================================================================
# HEAD CHROME
# =============================================================================

# Mind's Eye Chrome Implant
MINDSEYE = {
    "prototype_parent": "CHROME_BASE",
    "prototype_key": "mindseye",
    "key": "Mind's Eye Chrome Implant",
    "aliases": ["mindseye", "mind's eye", "minds eye", "mind eye"],
    "desc": "A small neural implant designed to rest behind the ear. This chrome grants the wearer the ability to perceive and hear the surface thoughts of those nearby, allowing for a unique form of extrasensory awareness. The implant is delicate and refined, featuring neural pathways that interface directly with the auditory cortex. Those who wear this implant often report a strange humming sensation, as if they're tuning into a frequency just below conscious hearing.",
    "chrome_slot": "head",
    "chrome_type": "internal",
    "shortname": "mindseye",
    "empathy_cost": -0.25,
    "buffs": None,
    "buff_description": "No buffs",
    "abilities": "Hear thoughts of nearby individuals",
    "can_customize": False,
    "worn_desc": None,
}

# NanoTrace Probability Calculator
NT_PROBCAL = {
    "prototype_parent": "CHROME_BASE",
    "prototype_key": "ProbCal",
    "key": "NanoTrace Probability Calculator Cranial Implant Mk. I",
    "aliases": ["probcal", "probability calculator", "nt-probcal"],
    "desc": "A NanoTrace Probability Calculator Cranial Implant Mk. I. This internal cranial implant integrates directly with the parietal lobe, enhancing mathematical reasoning and predictive modeling capabilities. The chrome housing features NanoTrace's refined design aesthetic. Neural pathways light up with statistical analysis, turning gut feelings into calculated certainties.",
    "chrome_slot": "head",
    "chrome_type": "internal",
    "shortname": "ProbCal",
    "empathy_cost": 1.5,
    "buffs": {"smarts": 2},
    "buff_description": "+2 Smarts",
    "abilities": None,
    "can_customize": False,
}

# NanoTrace Parietal Amplifier
NT_PARAMP = {
    "prototype_parent": "CHROME_BASE",
    "prototype_key": "ParAmp",
    "key": "NanoTrace Parietal Amplifier Cranial Implant Mk. I",
    "aliases": ["paramp", "parietal amplifier", "nt-paramp"],
    "desc": "A NanoTrace Parietal Amplifier Cranial Implant Mk. I. This compact internal implant boosts cognitive function through targeted neural enhancement of the parietal region. NanoTrace's refined design aesthetic is reflected in every detail of the chrome casing.",
    "chrome_slot": "head",
    "chrome_type": "internal",
    "shortname": "ParAmp",
    "empathy_cost": 0.90,
    "buffs": {"smarts": 1},
    "buff_description": "+1 Smarts",
    "abilities": None,
    "can_customize": False,
}

# BaoSteel Subdermal Skull Plating
BS_SKULL_PLATING = {
    "prototype_parent": "CHROME_BASE",
    "prototype_key": "BS-SKLPLT",
    "key": "BaoSteel Subdermal Skull Plating",
    "aliases": ["skull plating", "skull plate", "bs-sklplt", "skulplt"],
    "desc": "BaoSteel Subdermal Skull Plating - a lattice of reinforced composite material implanted beneath the skin of the skull. The hexagonal BaoSteel pattern is barely visible beneath the skin when light catches it just right. Provides significant protection to the head without external visibility.",
    "chrome_slot": "head",
    "chrome_type": "internal",
    "shortname": "BS-SKLPLT",
    "empathy_cost": 1.5,
    "buffs": {},
    "armor_bonus": {"head": 1},
    "buff_description": "+1 Armor to Head",
    "abilities": None,
    "can_customize": False,
    "incompatible_with": ["morikawa_kabuto"],
}

# NanoTrace Nerves Of Steel
NT_NERVES = {
    "prototype_parent": "CHROME_BASE",
    "prototype_key": "NT-NRV",
    "key": "NanoTrace Nerves Of Steel!",
    "aliases": ["nerves of steel", "nt-nrv", "nanotrace nerves"],
    "desc": "NanoTrace Nerves Of Steel! - a proprietary neural dampening system that reduces stress response and enhances composure under pressure. Microscopic implants distributed throughout the nervous system regulate adrenaline and cortisol, keeping you cool when others crack.",
    "chrome_slot": "head",
    "chrome_type": "internal",
    "shortname": "NT-NRV",
    "empathy_cost": 0.90,
    "buffs": {"edge": 1},
    "buff_description": "+1 Edge",
    "abilities": None,
    "can_customize": False,
}

# Nerves Of BaoSteel
BS_NERVES = {
    "prototype_parent": "CHROME_BASE",
    "prototype_key": "BS-NRV",
    "key": "Nerves Of BaoSteel",
    "aliases": ["nerves of baosteel", "bs-nrv", "baosteel nerves"],
    "desc": "Nerves Of BaoSteel (TM) - BaoSteel's premium neural dampening system, a significant upgrade over standard models. Advanced microsystems distributed throughout the nervous system provide enhanced stress regulation and composure. The BaoSteel logo is trademarked directly into your neural pathways.",
    "chrome_slot": "head",
    "chrome_type": "internal",
    "shortname": "BS-NRV",
    "empathy_cost": 1.5,
    "buffs": {"edge": 2},
    "buff_description": "+2 Edge",
    "abilities": None,
    "can_customize": False,
}

# MadGenTek Electroconvulsive Motor Cortex Stimulator
MGT_NRVZAP = {
    "prototype_parent": "CHROME_BASE",
    "prototype_key": "NRVZAP",
    "key": "MadGenTek Electroconvulsive Motor Cortex Stimulator",
    "aliases": ["nrvzap", "nerve zap", "motor cortex stimulator", "madgentek stimulator"],
    "desc": "A MadGenTek Electroconvulsive Motor Cortex Stimulator - an aggressive neural enhancement that delivers precisely calibrated electrical impulses to the motor cortex. The result is dramatically improved reaction time and reflexive response. Side effects may include involuntary twitching and an unsettling awareness of your own nervous system. MadGenTek: Because sometimes progress hurts.",
    "chrome_slot": "head",
    "chrome_type": "internal",
    "shortname": "NRVZAP",
    "empathy_cost": 1.5,
    "buffs": {"reflexes": 2},
    "buff_description": "+2 Reflexes",
    "abilities": None,
    "can_customize": False,
}

# NanoTrace Axon Enhancer
NT_AXON = {
    "prototype_parent": "CHROME_BASE",
    "prototype_key": "NT-AX",
    "key": "NanoTrace Axon Enhancer",
    "aliases": ["axon enhancer", "nt-ax", "nanotrace axon"],
    "desc": "A NanoTrace Axon Enhancer - microscopic neural boosters that optimize signal transmission along axon pathways. The result is measurably faster reflexes without the aggressive approach of competitors. NanoTrace believes in enhancement through refinement, not brute force.",
    "chrome_slot": "head",
    "chrome_type": "internal",
    "shortname": "NT-AX",
    "empathy_cost": 0.90,
    "buffs": {"reflexes": 1},
    "buff_description": "+1 Reflexes",
    "abilities": None,
    "can_customize": False,
}

# Morikawa Kabuto
MORIKAWA_KABUTO = {
    "prototype_parent": "CHROME_BASE",
    "prototype_key": "MK-KABUTO",
    "key": "Morikawa Kabuto",
    "aliases": ["kabuto", "morikawa kabuto", "mk-kabuto", "dragon helm"],
    "desc": "A Morikawa Kabuto - external cranial armor designed for Yakuza muscle who believe that a dragon does not hide from a mouse. The distinctive helmet integrates traditional Japanese aesthetic with modern ballistic protection. Elaborate dragon scale patterns are etched into the chrome surface, marking the wearer as someone who fears nothing and hides from no one. This piece comes already customized and cannot be further modified.",
    "worn_desc": "Their head is encased in an ornate Morikawa Kabuto, an elaborate chrome helmet with dragon scale patterns etched into its surface.",
    "chrome_slot": "head",
    "chrome_type": "external",
    "shortname": "MK-KABUTO",
    "empathy_cost": 2.5,
    "buffs": {},
    "armor_bonus": {"head": 3},
    "buff_description": "+3 Armor to Head",
    "abilities": None,
    "replaces_slot": "head",
    "can_customize": False,
    "incompatible_with": ["bs_skull_plating"],
}

# =============================================================================
# FACE CHROME
# =============================================================================

# NanoTrace Surface Wiring (Fashionware)
NT_SURFACE_WIRING = {
    "prototype_parent": "CHROME_BASE",
    "prototype_key": "NT-SW",
    "key": "NanoTrace Surface Wiring",
    "aliases": ["surface wiring", "nt-sw", "fashionware", "face wiring"],
    "desc": "NanoTrace Surface Wiring - fashionware that makes a statement. Delicate circuitry traces visible paths across the skin, the wiring for other implants worn externally as an aesthetic choice. The patterns pulse with soft bioluminescence, marking the wearer as someone who embraces their chrome rather than hiding it. Purely cosmetic, but cosmetics matter.",
    "worn_desc": "Delicate circuitry traces are visible across their face, pulsing with soft bioluminescence in intricate patterns.",
    "chrome_slot": "face",
    "chrome_type": "external",
    "shortname": "NT-SW",
    "empathy_cost": 0,
    "buffs": {},
    "buff_description": "Cosmetic",
    "abilities": "Cosmetic fashionware",
    "can_customize": True,
}

# BaoSteel Subdermal Facial Plating
BS_FACE_PLATING = {
    "prototype_parent": "CHROME_BASE",
    "prototype_key": "BS-FCEPLT",
    "key": "BaoSteel Subdermal Facial Plating",
    "aliases": ["face plating", "facial plating", "bs-fceplt", "fceplt"],
    "desc": "BaoSteel Subdermal Facial Plating - reinforced composite material implanted beneath the facial skin. The hexagonal BaoSteel lattice pattern sits just beneath the surface, barely visible in certain light. Provides protection without external visibility, though some say it gives your face an unsettling rigidity.",
    "chrome_slot": "face",
    "chrome_type": "internal",
    "shortname": "BS-FCEPLT",
    "empathy_cost": 1.5,
    "buffs": {},
    "armor_bonus": {"face": 1},
    "buff_description": "+1 Armor to Face",
    "abilities": None,
    "can_customize": False,
    "incompatible_with": ["morikawa_menpo"],
}

# Morikawa Menpo
MORIKAWA_MENPO = {
    "prototype_parent": "CHROME_BASE",
    "prototype_key": "MK-MENPO",
    "key": "Morikawa Menpo",
    "aliases": ["menpo", "morikawa menpo", "mk-menpo", "dragon mask"],
    "desc": "A Morikawa Menpo - external facial armor designed for Yakuza muscle who believe that a dragon does not hide from a mouse. The distinctive face plate integrates traditional Japanese aesthetic with modern ballistic protection. Fearsome demon or dragon features are etched into the chrome surface, marking the wearer as someone who embraces intimidation as a tool. This piece comes already customized and cannot be further modified.",
    "worn_desc": "Their face is covered by an ornate chrome faceplate, etched with fearsome demon or dragon features that project an intimidating visage.",
    "chrome_slot": "face",
    "chrome_type": "external",
    "shortname": "MK-MENPO",
    "empathy_cost": 2.5,
    "buffs": {},
    "armor_bonus": {"face": 3},
    "buff_description": "+3 Armor to Face",
    "abilities": None,
    "replaces_slot": "face",
    "can_customize": False,
    "incompatible_with": ["bs_face_plating"],
}

# =============================================================================
# EYE CHROME
# =============================================================================

# MadGenTek Bug Eyes (Borgware)
MGT_BUG_EYES = {
    "prototype_parent": "CHROME_BASE",
    "prototype_key": "BUG-I",
    "key": "MadGenTek Bug Eyes",
    "aliases": ["bug eyes", "bug-i", "madgentek eyes", "borgware eyes"],
    "desc": "MadGenTek Bug Eyes - oversized cybereyes that resemble the optical organs of an insect. Multiple faceted lenses capture light from impossible angles, feeding visual data through parallel processing channels. The effect is unsettling to observers but provides unparalleled optical versatility. Five optical module slots allow extensive customization. MadGenTek: Because seeing is believing, and you should believe in more.",
    "worn_desc": "Their eyes have been replaced with oversized cybereyes resembling insect optical organs, with multiple faceted lenses that catch light unnervingly.",
    "chrome_slot": "eyes",
    "chrome_type": "external",
    "shortname": "BUG-I",
    "empathy_cost": 4.0,
    "buffs": {},
    "buff_description": "5 optical slots, replaces eye slot",
    "abilities": "5 optical module slots",
    "optical_slots": 5,
    "replaces_slot": "eyes",
    "can_customize": True,  # Slightly customizable
}

# BaoSteel Cybereye Set
BS_CYBEREYE_SET = {
    "prototype_parent": "CHROME_BASE",
    "prototype_key": "BS-3YE5",
    "key": "BaoSteel Cybereye Set",
    "aliases": ["cybereyes", "bs-3ye5", "baosteel eyes", "cyber eyes"],
    "desc": "A BaoSteel Cybereye Set - stock standard replacement eyes with the distinctive BaoSteel optical design. The hexagonal iris pattern marks them as genuine BaoSteel product. Two optical module slots per eye allow for basic customization. Some say the BaoSteel design captures light differently, giving wearers a subtle glow in dim conditions.",
    "worn_desc": "Their eyes have been replaced with sleek chrome cybereyes bearing the distinctive BaoSteel hexagonal iris pattern.",
    "chrome_slot": "eyes",
    "chrome_type": "external",
    "shortname": "BS-3YE5",
    "empathy_cost": 2.0,
    "buffs": {},
    "buff_description": "2 optical slots, replaces eye slot",
    "abilities": "2 optical module slots",
    "optical_slots": 2,
    "replaces_slot": "eyes",
    "can_customize": True,
}

# AnSteel Cybereye Set
AS_CYBEREYE_SET = {
    "prototype_parent": "CHROME_BASE",
    "prototype_key": "AS-3YE5",
    "key": "AnSteel Cybereye Set",
    "aliases": ["cybereyes", "as-3ye5", "ansteel eyes", "cyber eyes"],
    "desc": "An AnSteel Cybereye Set - stock standard replacement eyes with the distinctive AnSteel optical design. The angular iris pattern marks them as genuine AnSteel product. Two optical module slots per eye allow for basic customization. Some say the AnSteel design processes light more efficiently, though brand loyalists will argue the point endlessly.",
    "worn_desc": "Their eyes have been replaced with efficient chrome cybereyes bearing the distinctive AnSteel angular iris pattern.",
    "chrome_slot": "eyes",
    "chrome_type": "external",
    "shortname": "AS-3YE5",
    "empathy_cost": 2.0,
    "buffs": {},
    "buff_description": "2 optical slots, replaces eye slot",
    "abilities": "2 optical module slots",
    "optical_slots": 2,
    "replaces_slot": "eyes",
    "can_customize": True,
}

# BaoSteel Single Cybereye
BS_CYBEREYE = {
    "prototype_parent": "CHROME_BASE",
    "prototype_key": "BS-3YE",
    "key": "BaoSteel Cybereye",
    "aliases": ["cybereye", "bs-3ye", "baosteel eye", "cyber eye"],
    "desc": "A single BaoSteel Cybereye - a stock standard replacement eye with the distinctive BaoSteel optical design. The hexagonal iris pattern marks it as genuine BaoSteel product. One optical module slot allows for basic customization. Perfect for those who only need to replace one eye.",
    "worn_desc": "Their eye has been replaced with a sleek chrome cybereye bearing the distinctive BaoSteel hexagonal iris pattern.",
    "chrome_slot": "eye",
    "chrome_type": "external",
    "shortname": "BS-3YE",
    "empathy_cost": 1.0,
    "buffs": {},
    "buff_description": "1 optical slot, replaces selected eye",
    "abilities": "1 optical module slot",
    "optical_slots": 1,
    "replaces_slot": "eye",
    "can_customize": True,
}

# AnSteel Single Cybereye
AS_CYBEREYE = {
    "prototype_parent": "CHROME_BASE",
    "prototype_key": "AS-3YE",
    "key": "AnSteel Cybereye",
    "aliases": ["cybereye", "as-3ye", "ansteel eye", "cyber eye"],
    "desc": "A single AnSteel Cybereye - a stock standard replacement eye with the distinctive AnSteel optical design. The angular iris pattern marks it as genuine AnSteel product. One optical module slot allows for basic customization. Perfect for those who only need to replace one eye.",
    "worn_desc": "Their eye has been replaced with an efficient chrome cybereye bearing the distinctive AnSteel angular iris pattern.",
    "chrome_slot": "eye",
    "chrome_type": "external",
    "shortname": "AS-3YE",
    "empathy_cost": 1.0,
    "buffs": {},
    "buff_description": "1 optical slot, replaces selected eye",
    "abilities": "1 optical module slot",
    "optical_slots": 1,
    "replaces_slot": "eye",
    "can_customize": True,
}

# BaoSteel Reinforced Cybereye Set
BS_REINFORCED_CYBEREYE_SET = {
    "prototype_parent": "CHROME_BASE",
    "prototype_key": "BS-R3YE5",
    "key": "BaoSteel Reinforced Cybereye Set",
    "aliases": ["reinforced cybereyes", "bs-r3ye5", "armored eyes", "reinforced eyes"],
    "desc": "A BaoSteel Reinforced Cybereye Set - armored replacement eyes with enhanced ballistic protection. The patent is held exclusively by BaoSteel. The reinforced housing reduces optical slot capacity but provides meaningful protection against ocular trauma. The distinctive hexagonal reinforcement pattern is visible in the iris.",
    "worn_desc": "Their eyes have been replaced with heavily armored chrome cybereyes with reinforced hexagonal patterning, designed for serious combat.",
    "chrome_slot": "eyes",
    "chrome_type": "external",
    "shortname": "BS-R3YE5",
    "empathy_cost": 3.0,
    "buffs": {},
    "armor_bonus": {"eyes": 1},
    "buff_description": "+1 Armor to Eyes, 2 optical slots",
    "abilities": "2 optical module slots",
    "optical_slots": 2,
    "replaces_slot": "eyes",
    "can_customize": False,
}

# BaoSteel Reinforced Single Cybereye
BS_REINFORCED_CYBEREYE = {
    "prototype_parent": "CHROME_BASE",
    "prototype_key": "BS-R3YE",
    "key": "BaoSteel Reinforced Cybereye",
    "aliases": ["reinforced cybereye", "bs-r3ye", "armored eye", "reinforced eye"],
    "desc": "A single BaoSteel Reinforced Cybereye - an armored replacement eye with enhanced ballistic protection. The patent is held exclusively by BaoSteel. The reinforced housing provides protection against ocular trauma while maintaining basic optical functionality. One module slot available.",
    "worn_desc": "Their eye has been replaced with an armored chrome cybereye, heavily reinforced for combat protection.",
    "chrome_slot": "eye",
    "chrome_type": "external",
    "shortname": "BS-R3YE",
    "empathy_cost": 2.0,
    "buffs": {},
    "armor_bonus": {"eye": 1},
    "buff_description": "+1 Armor to Applied Eye, 1 optical slot",
    "abilities": "1 optical module slot",
    "optical_slots": 1,
    "replaces_slot": "eye",
    "can_customize": False,
}

# Morikawa Gaze
MORIKAWA_GAZE = {
    "prototype_parent": "CHROME_BASE",
    "prototype_key": "MK-GAZE",
    "key": "Morikawa Gaze",
    "aliases": ["gaze", "morikawa gaze", "mk-gaze", "dragon eyes"],
    "desc": "Morikawa Gaze - external eye armor designed for Yakuza muscle who believe that a dragon does not hide from a mouse. Heavy chrome plating surrounds the optical organs, providing substantial protection while projecting an intimidating visage. The distinctive dragon-scale pattern marks the wearer as someone who has chosen to see the world through armored eyes. Incompatible with cybereyes. This piece comes already customized.",
    "worn_desc": "Their eyes are shielded behind heavy chrome armor, with distinctive dragon-scale patterns etched into the plating.",
    "chrome_slot": "eyes",
    "chrome_type": "external",
    "shortname": "MK-GAZE",
    "empathy_cost": 3.5,
    "buffs": {},
    "armor_bonus": {"eyes": 3},
    "buff_description": "+3 Armor to Eyes",
    "abilities": None,
    "replaces_slot": "eyes",
    "can_customize": False,
    "incompatible_with": ["cybereyes"],
}

# =============================================================================
# EAR CHROME
# =============================================================================

# BaoSteel Cyberear Set (External)
BS_CYBEREAR_SET_EXT = {
    "prototype_parent": "CHROME_BASE",
    "prototype_key": "BS-E4R5-EXT",
    "key": "BaoSteel Cyberear Set (External)",
    "aliases": ["cyberears", "bs-e4r5", "baosteel ears", "cyber ears external"],
    "desc": "A BaoSteel Cyberear Set (External) - stock standard replacement ears with the distinctive BaoSteel internal design, worn externally. The hexagonal pattern in the chrome housing marks them as genuine BaoSteel product. Four audio module slots allow for extensive customization. External models replace ear nakeds but can be customized aesthetically.",
    "worn_desc": "Their ears have been replaced with external chrome cyberears bearing the distinctive BaoSteel hexagonal patterning.",
    "chrome_slot": "ears",
    "chrome_type": "external",
    "shortname": "BS-E4R5-EXT",
    "empathy_cost": 2.0,
    "buffs": {},
    "buff_description": "4 ear slots, replaces ear nakeds",
    "abilities": "4 audio module slots",
    "audio_slots": 4,
    "replaces_slot": "ears",
    "can_customize": True,
}

# BaoSteel Cyberear Set (Internal)
BS_CYBEREAR_SET_INT = {
    "prototype_parent": "CHROME_BASE",
    "prototype_key": "BS-E4R5-INT",
    "key": "BaoSteel Cyberear Set (Internal)",
    "aliases": ["cyberears", "bs-e4r5-int", "baosteel ears internal", "cyber ears internal"],
    "desc": "A BaoSteel Cyberear Set (Internal) - stock standard replacement ears with the distinctive BaoSteel internal design, implanted beneath the skin. The internal components are invisible from outside but provide the same audio enhancement capabilities. Four audio module slots allow for extensive customization.",
    "chrome_slot": "ears",
    "chrome_type": "internal",
    "shortname": "BS-E4R5-INT",
    "empathy_cost": 2.0,
    "buffs": {},
    "buff_description": "4 ear slots",
    "abilities": "4 audio module slots",
    "audio_slots": 4,
    "can_customize": False,
}

# AnSteel Cyberear Set (External)
AS_CYBEREAR_SET_EXT = {
    "prototype_parent": "CHROME_BASE",
    "prototype_key": "AS-E4R5-EXT",
    "key": "AnSteel Cyberear Set (External)",
    "aliases": ["cyberears", "as-e4r5", "ansteel ears", "cyber ears external"],
    "desc": "An AnSteel Cyberear Set (External) - stock standard replacement ears with the distinctive AnSteel internal design, worn externally. The angular pattern in the chrome housing marks them as genuine AnSteel product. Four audio module slots allow for extensive customization. External models replace ear nakeds but can be customized aesthetically.",
    "worn_desc": "Their ears have been replaced with external chrome cyberears bearing the distinctive AnSteel angular patterning.",
    "chrome_slot": "ears",
    "chrome_type": "external",
    "shortname": "AS-E4R5-EXT",
    "empathy_cost": 2.0,
    "buffs": {},
    "buff_description": "4 ear slots, replaces ear nakeds",
    "abilities": "4 audio module slots",
    "audio_slots": 4,
    "replaces_slot": "ears",
    "can_customize": True,
}

# AnSteel Cyberear Set (Internal)
AS_CYBEREAR_SET_INT = {
    "prototype_parent": "CHROME_BASE",
    "prototype_key": "AS-E4R5-INT",
    "key": "AnSteel Cyberear Set (Internal)",
    "aliases": ["cyberears", "as-e4r5-int", "ansteel ears internal", "cyber ears internal"],
    "desc": "An AnSteel Cyberear Set (Internal) - stock standard replacement ears with the distinctive AnSteel internal design, implanted beneath the skin. The internal components are invisible from outside but provide the same audio enhancement capabilities. Four audio module slots allow for extensive customization.",
    "chrome_slot": "ears",
    "chrome_type": "internal",
    "shortname": "AS-E4R5-INT",
    "empathy_cost": 2.0,
    "buffs": {},
    "buff_description": "4 ear slots",
    "abilities": "4 audio module slots",
    "audio_slots": 4,
    "can_customize": False,
}

# =============================================================================
# ARM/HAND CHROME
# =============================================================================

# BaoSteel Cyberarm Set
BS_CYBERARM_SET = {
    "prototype_parent": "CHROME_BASE",
    "prototype_key": "BS-4RM5",
    "key": "BaoSteel Cyberarm Set",
    "aliases": ["cyberarms", "bs-4rm5", "baosteel arms", "cyber arms"],
    "desc": "A BaoSteel Cyberarm Set - a matched pair of stock standard full cyberarm replacements with the distinctive BaoSteel muscle design. The hexagonal myomer bundles and chrome plating mark them as genuine BaoSteel product. Replaces lost or damaged limbs with enhanced mechanical alternatives. Four module slots allow for extensive customization. The artificial muscles provide significant strength and dexterity improvements.",
    "worn_desc": "Their arms have been replaced with sleek chrome cyberarms, the hexagonal myomer bundles of BaoSteel engineering clearly visible beneath polished chrome plating.",
    "chrome_slot": "arms",
    "chrome_type": "external",
    "shortname": "BS-4RM5",
    "empathy_cost": 4.0,
    "buffs": {"body": 2, "dexterity": 2, "technique": 2},
    "armor_bonus": {"arms": 1},
    "buff_description": "+1 Arm Armor, +2 Body, +2 Dexterity, +2 Technique",
    "abilities": "4 module slots, replaces arms",
    "module_slots": 4,
    "replaces_slot": "arms",
    "can_customize": True,
}

# AnSteel Cyberarm Set
AS_CYBERARM_SET = {
    "prototype_parent": "CHROME_BASE",
    "prototype_key": "AS-4RM5",
    "key": "AnSteel Cyberarm Set",
    "aliases": ["cyberarms", "as-4rm5", "ansteel arms", "cyber arms"],
    "desc": "An AnSteel Cyberarm Set - a matched pair of stock standard full cyberarm replacements with the distinctive AnSteel muscle design. The angular myomer bundles and sleek chrome plating mark them as genuine AnSteel product. Replaces lost or damaged limbs with enhanced mechanical alternatives. Four module slots allow for extensive customization. The artificial muscles provide significant strength and dexterity improvements.",
    "worn_desc": "Their arms have been replaced with sleek chrome cyberarms, the angular myomer bundles of AnSteel engineering clearly visible beneath polished chrome.",
    "chrome_slot": "arms",
    "chrome_type": "external",
    "shortname": "AS-4RM5",
    "empathy_cost": 4.0,
    "buffs": {"body": 2, "dexterity": 2, "technique": 2},
    "armor_bonus": {"arms": 1},
    "buff_description": "+1 Arm Armor, +2 Body, +2 Dexterity, +2 Technique",
    "abilities": "4 module slots, replaces arms",
    "module_slots": 4,
    "replaces_slot": "arms",
    "can_customize": True,
}

# BaoSteel Single Cyberarm
BS_CYBERARM = {
    "prototype_parent": "CHROME_BASE",
    "prototype_key": "BS-4RM",
    "key": "BaoSteel Cyberarm",
    "aliases": ["cyberarm", "bs-4rm", "baosteel arm", "cyber arm"],
    "desc": "A single BaoSteel Cyberarm - a stock standard full cyberarm replacement with the distinctive BaoSteel muscle design. The hexagonal myomer bundles and chrome plating mark it as genuine BaoSteel product. Replaces a lost or damaged limb with an enhanced mechanical alternative. Two module slots allow for customization.",
    "worn_desc": "Their arm has been replaced with a sleek chrome cyberarm, the hexagonal BaoSteel myomer bundles visible beneath the plating.",
    "chrome_slot": "arm",
    "chrome_type": "external",
    "shortname": "BS-4RM",
    "empathy_cost": 2.0,
    "buffs": {"body": 1, "dexterity": 1, "technique": 1},
    "buff_description": "+1 Body, +1 Dexterity, +1 Technique",
    "abilities": "2 module slots, replaces arm",
    "module_slots": 2,
    "replaces_slot": "arm",
    "can_customize": True,
}

# AnSteel Single Cyberarm
AS_CYBERARM = {
    "prototype_parent": "CHROME_BASE",
    "prototype_key": "AS-4RM",
    "key": "AnSteel Cyberarm",
    "aliases": ["cyberarm", "as-4rm", "ansteel arm", "cyber arm"],
    "desc": "A single AnSteel Cyberarm - a stock standard full cyberarm replacement with the distinctive AnSteel muscle design. The angular myomer bundles and sleek chrome plating mark it as genuine AnSteel product. Replaces a lost or damaged limb with an enhanced mechanical alternative. Two module slots allow for customization.",
    "worn_desc": "Their arm has been replaced with a sleek chrome cyberarm, the angular AnSteel myomer bundles visible beneath the plating.",
    "chrome_slot": "arm",
    "chrome_type": "external",
    "shortname": "AS-4RM",
    "empathy_cost": 2.0,
    "buffs": {"body": 1, "dexterity": 1, "technique": 1},
    "buff_description": "+1 Body, +1 Dexterity, +1 Technique",
    "abilities": "2 module slots, replaces arm",
    "module_slots": 2,
    "replaces_slot": "arm",
    "can_customize": True,
}

# =============================================================================
# LEG/FEET CHROME
# =============================================================================

# BaoSteel Cyberleg Set
BS_CYBERLEG_SET = {
    "prototype_parent": "CHROME_BASE",
    "prototype_key": "BS-L3G5",
    "key": "BaoSteel Cyberleg Set",
    "aliases": ["cyberlegs", "bs-l3g5", "baosteel legs", "cyber legs"],
    "desc": "A BaoSteel Cyberleg Set - a matched pair of stock standard full cyberleg replacements complete with thighs, lower legs, and feet. The distinctive BaoSteel muscle design features hexagonal myomer bundles and chrome plating. Replaces lost or damaged limbs with enhanced mechanical alternatives. Four module slots allow for extensive customization. The artificial muscles provide significant strength, dexterity, and reflex improvements.",
    "worn_desc": "Their legs have been replaced with powerful chrome cyberlegs, the hexagonal BaoSteel myomer bundles clearly visible through the polished chrome.",
    "chrome_slot": "legs",
    "chrome_type": "external",
    "shortname": "BS-L3G5",
    "empathy_cost": 4.0,
    "buffs": {"body": 2, "dexterity": 2, "reflexes": 2},
    "armor_bonus": {"legs": 1},
    "buff_description": "+1 Leg Armor, +2 Body, +2 Dexterity, +2 Reflexes",
    "abilities": "4 module slots, replaces legs",
    "module_slots": 4,
    "replaces_slot": "legs",
    "can_customize": True,
}

# AnSteel Cyberleg Set
AS_CYBERLEG_SET = {
    "prototype_parent": "CHROME_BASE",
    "prototype_key": "AS-L3G5",
    "key": "AnSteel Cyberleg Set",
    "aliases": ["cyberlegs", "as-l3g5", "ansteel legs", "cyber legs"],
    "desc": "An AnSteel Cyberleg Set - a matched pair of stock standard full cyberleg replacements complete with thighs, lower legs, and feet. The distinctive AnSteel muscle design features angular myomer bundles and sleek chrome plating. Replaces lost or damaged limbs with enhanced mechanical alternatives. Four module slots allow for extensive customization. The artificial muscles provide significant strength, dexterity, and reflex improvements.",
    "worn_desc": "Their legs have been replaced with powerful chrome cyberlegs, the angular AnSteel myomer bundles clearly visible through the polished chrome.",
    "chrome_slot": "legs",
    "chrome_type": "external",
    "shortname": "AS-L3G5",
    "empathy_cost": 4.0,
    "buffs": {"body": 2, "dexterity": 2, "reflexes": 2},
    "armor_bonus": {"legs": 1},
    "buff_description": "+1 Leg Armor, +2 Body, +2 Dexterity, +2 Reflexes",
    "abilities": "4 module slots, replaces legs",
    "module_slots": 4,
    "replaces_slot": "legs",
    "can_customize": True,
}

# BaoSteel Single Cyberleg
BS_CYBERLEG = {
    "prototype_parent": "CHROME_BASE",
    "prototype_key": "BS-L3G",
    "key": "BaoSteel Cyberleg",
    "aliases": ["cyberleg", "bs-l3g", "baosteel leg", "cyber leg"],
    "desc": "A single BaoSteel Cyberleg - a stock standard full cyberleg replacement complete with thigh, lower leg, and foot. The distinctive BaoSteel muscle design features hexagonal myomer bundles and chrome plating. Replaces a lost or damaged limb with an enhanced mechanical alternative. Two module slots allow for customization.",
    "worn_desc": "Their leg has been replaced with a powerful chrome cyberleg, the hexagonal BaoSteel myomer bundles visible through the plating.",
    "chrome_slot": "leg",
    "chrome_type": "external",
    "shortname": "BS-L3G",
    "empathy_cost": 2.0,
    "buffs": {"body": 1, "dexterity": 1, "reflexes": 1},
    "buff_description": "+1 Body, +1 Dexterity, +1 Reflexes",
    "abilities": "2 module slots, replaces leg",
    "module_slots": 2,
    "replaces_slot": "leg",
    "can_customize": True,
}

# AnSteel Single Cyberleg
AS_CYBERLEG = {
    "prototype_parent": "CHROME_BASE",
    "prototype_key": "AS-L3G",
    "key": "AnSteel Cyberleg",
    "aliases": ["cyberleg", "as-l3g", "ansteel leg", "cyber leg"],
    "desc": "A single AnSteel Cyberleg - a stock standard full cyberleg replacement complete with thigh, lower leg, and foot. The distinctive AnSteel muscle design features angular myomer bundles and sleek chrome plating. Replaces a lost or damaged limb with an enhanced mechanical alternative. Two module slots allow for customization.",
    "worn_desc": "Their leg has been replaced with a powerful chrome cyberleg, the angular AnSteel myomer bundles visible through the plating.",
    "chrome_slot": "leg",
    "chrome_type": "external",
    "shortname": "AS-L3G",
    "empathy_cost": 2.0,
    "buffs": {"body": 1, "dexterity": 1, "reflexes": 1},
    "buff_description": "+1 Body, +1 Dexterity, +1 Reflexes",
    "abilities": "2 module slots, replaces leg",
    "module_slots": 2,
    "replaces_slot": "leg",
    "can_customize": True,
}

# BaoSteel Cyberfeet Set
BS_CYBERFEET_SET = {
    "prototype_parent": "CHROME_BASE",
    "prototype_key": "BS-F33T",
    "key": "BaoSteel Cyberfeet Set",
    "aliases": ["cyberfeet", "bs-f33t", "baosteel feet", "cyber feet"],
    "desc": "A BaoSteel Cyberfeet Set - a matched pair of stock standard cyberfoot replacements. The distinctive BaoSteel design features hexagonal joint articulation and chrome plating. Replaces lost or damaged feet with enhanced mechanical alternatives. The artificial joints provide improved dexterity and reflex response.",
    "worn_desc": "Their feet have been replaced with sleek chrome cyberfeet, the hexagonal joint articulation of BaoSteel engineering visible.",
    "chrome_slot": "feet",
    "chrome_type": "external",
    "shortname": "BS-F33T",
    "empathy_cost": 1.0,
    "buffs": {"dexterity": 1, "reflexes": 1},
    "buff_description": "+1 Dexterity, +1 Reflexes",
    "abilities": "Replaces feet",
    "replaces_slot": "feet",
    "can_customize": True,
}

# AnSteel Cyberfeet Set
AS_CYBERFEET_SET = {
    "prototype_parent": "CHROME_BASE",
    "prototype_key": "AS-F33T",
    "key": "AnSteel Cyberfeet Set",
    "aliases": ["cyberfeet", "as-f33t", "ansteel feet", "cyber feet"],
    "desc": "An AnSteel Cyberfeet Set - a matched pair of stock standard cyberfoot replacements. The distinctive AnSteel design features angular joint articulation and sleek chrome plating. Replaces lost or damaged feet with enhanced mechanical alternatives. The artificial joints provide improved dexterity and reflex response.",
    "worn_desc": "Their feet have been replaced with sleek chrome cyberfeet, the angular joint articulation of AnSteel engineering visible.",
    "chrome_slot": "feet",
    "chrome_type": "external",
    "shortname": "AS-F33T",
    "empathy_cost": 1.0,
    "buffs": {"dexterity": 1, "reflexes": 1},
    "buff_description": "+1 Dexterity, +1 Reflexes",
    "abilities": "Replaces feet",
    "replaces_slot": "feet",
    "can_customize": True,
}

# BaoSteel Single Cyberfoot
BS_CYBERFOOT = {
    "prototype_parent": "CHROME_BASE",
    "prototype_key": "BS-F00T",
    "key": "BaoSteel Cyberfoot",
    "aliases": ["cyberfoot", "bs-f00t", "baosteel foot", "cyber foot"],
    "desc": "A single BaoSteel Cyberfoot - a stock standard cyberfoot replacement. The distinctive BaoSteel design features hexagonal joint articulation and chrome plating. Replaces a lost or damaged foot with an enhanced mechanical alternative.",
    "worn_desc": "Their foot has been replaced with a sleek chrome cyberfoot, the hexagonal BaoSteel joint articulation visible.",
    "chrome_slot": "foot",
    "chrome_type": "external",
    "shortname": "BS-F00T",
    "empathy_cost": 0.5,
    "buffs": {},
    "buff_description": "Replaces foot",
    "abilities": "Replaces foot",
    "replaces_slot": "foot",
    "can_customize": True,
}

# AnSteel Single Cyberfoot
AS_CYBERFOOT = {
    "prototype_parent": "CHROME_BASE",
    "prototype_key": "AS-F00T",
    "key": "AnSteel Cyberfoot",
    "aliases": ["cyberfoot", "as-f00t", "ansteel foot", "cyber foot"],
    "desc": "A single AnSteel Cyberfoot - a stock standard cyberfoot replacement. The distinctive AnSteel design features angular joint articulation and sleek chrome plating. Replaces a lost or damaged foot with an enhanced mechanical alternative.",
    "worn_desc": "Their foot has been replaced with a sleek chrome cyberfoot, the angular AnSteel joint articulation visible.",
    "chrome_slot": "foot",
    "chrome_type": "external",
    "shortname": "AS-F00T",
    "empathy_cost": 0.5,
    "buffs": {},
    "buff_description": "Replaces foot",
    "abilities": "Replaces foot",
    "replaces_slot": "foot",
    "can_customize": True,
}
