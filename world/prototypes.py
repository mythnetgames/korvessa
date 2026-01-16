# =============================================================================
# CHROME/CYBERWARE PROTOTYPES
# =============================================================================

MINDS_EYE_CHROME = {
    "prototype_key": "mindseye",
    "key": "Mindseye Chrome",
    "typeclass": "typeclasses.items.Item",
    "desc": "A small neural implant behind the ear, rumored to let you hear thoughts.",
    "shortname": "mindseye",
    "empathy_cost": -0.25,
    "abilities": "Hear thoughts.",
    "buffs": "No buffs",
    "tags": [("chrome", "cyberware")],
}
"""
Prototypes

A prototype is a simple way to create individualized instances of a
given typeclass. It is dictionary with specific key names.

For example, you might have a Sword typeclass that implements everything a
Sword would need to do. The only difference between different individual Swords
would be their key, description and some Attributes. The Prototype system
allows to create a range of such Swords with only minor variations. Prototypes
can also inherit and combine together to form entire hierarchies (such as
giving all Sabres and all Broadswords some common properties). Note that bigger
variations, such as custom commands or functionality belong in a hierarchy of
typeclasses instead.

A prototype can either be a dictionary placed into a global variable in a
python module (a 'module-prototype') or stored in the database as a dict on a
special Script (a db-prototype). The former can be created just by adding dicts
to modules Evennia looks at for prototypes, the latter is easiest created
in-game via the `olc` command/menu.

Prototypes are read and used to create new objects with the `spawn` command
or directly via `evennia.spawn` or the full path `evennia.prototypes.spawner.spawn`.

A prototype dictionary have the following keywords:

Possible keywords are:
- `prototype_key` - the name of the prototype. This is required for db-prototypes,
  for module-prototypes, the global variable name of the dict is used instead
- `prototype_parent` - string pointing to parent prototype if any. Prototype inherits
  in a similar way as classes, with children overriding values in their parents.
- `key` - string, the main object identifier.
- `typeclass` - string, if not set, will use `settings.BASE_OBJECT_TYPECLASS`.
- `location` - this should be a valid object or #dbref.
- `home` - valid object or #dbref.
- `destination` - only valid for exits (object or #dbref).
- `permissions` - string or list of permission strings.
- `locks` - a lock-string to use for the spawned object.
- `aliases` - string or list of strings.
- `attrs` - Attributes, expressed as a list of tuples on the form `(attrname, value)`,
  `(attrname, value, category)`, or `(attrname, value, category, locks)`. If using one
   of the shorter forms, defaults are used for the rest.
- `tags` - Tags, as a list of tuples `(tag,)`, `(tag, category)` or `(tag, category, data)`.
-  Any other keywords are interpreted as Attributes with no category or lock.
   These will internally be added to `attrs` (equivalent to `(attrname, value)`.

See the `spawn` command and `evennia.prototypes.spawner.spawn` for more info.

"""

# =============================================================================
# EXPLOSIVE PROTOTYPES FOR THROW COMMAND TESTING
# =============================================================================

# Base explosive prototype with common properties
EXPLOSIVE_BASE = {
    "typeclass": "typeclasses.items.Item",
    "desc": "A military-grade explosive device with a pin-pull mechanism.",
    "is_explosive": True,
    "requires_pin": True,
    "pin_pulled": False,
    "chain_trigger": True,
    "dud_chance": 0.05,  # 5% chance to fail
    "damage_type": "laceration",  # Fragmentation/shrapnel wounds
    "scanned_by_detonator": None,  # Remote detonator tracking
}

# Standard fragmentation grenade
FRAG_GRENADE = {
    "prototype_parent": "EXPLOSIVE_BASE",
    "key": "HDG M67 fragmentation grenade",
    "aliases": ["grenade", "frag", "m67", "hdg grenade", "frag grenade"],
    "desc": "A Helios Defense Group M67 fragmentation grenade - the standard-issue antipersonnel explosive used by military forces across human space. The body is a sphere of notched steel designed to fragment into hundreds of lethal shards upon detonation, encased in an olive drab coating. A spoon-style safety lever is held down by a pin that must be pulled to arm the fuse. Once the pin is pulled and the spoon released, you have approximately 8 seconds before detonation - enough time to throw it, not enough time to reconsider. The M67's blast radius extends fifteen meters, with the fragmentation pattern deadly within five. HDG has manufactured this design unchanged for over a century because some problems require the same solution regardless of the era: aggressive, indiscriminate violence delivered by a sphere you can hold in your hand.",
    "fuse_time": 8,
    "blast_damage": 25,
}

# Shorter fuse tactical grenade
TACTICAL_GRENADE = {
    "prototype_parent": "EXPLOSIVE_BASE", 
    "key": "tactical grenade",
    "aliases": ["tac grenade", "tactical"],
    "desc": "A tactical grenade with a shorter 5-second fuse for close-quarters combat.",
    "fuse_time": 5,
    "blast_damage": 20,
    "dud_chance": 0.02,  # More reliable
}

# High-damage demo charge
DEMO_CHARGE = {
    "prototype_parent": "EXPLOSIVE_BASE",
    "key": "HDG DX-15 demolition charge", 
    "aliases": ["charge", "demo", "dx-15", "dx15", "hdg demo", "demo charge", "c4"],
    "desc": "A Helios Defense Group DX-15 demolition charge - military-grade plastic explosive in a standardized one-kilogram block. The putty-like compound is stable enough to survive drops, fire, and even small-arms fire, but detonates with devastating force when triggered by the integrated electric blasting cap. The tan-colored explosive can be molded to fit against structural weak points, and the adhesive backing ensures it stays exactly where you place it. A digital timer/detonator is embedded in the block, offering settings from 10 seconds to 24 hours - though combat engineers rarely use anything longer than the minimum. When absolute structural destruction is required, whether it's breaching reinforced doors, collapsing tunnels, or eliminating hardened positions, the DX-15 delivers predictable, overwhelming force. HDG's technical documentation carefully avoids mentioning that this is the same compound used in shaped charges, improvised devices, and enough war crimes to fill a database.",
    "fuse_time": 10,
    "blast_damage": 40,
    "dud_chance": 0.01,  # Very reliable
}

# Flashbang (non-lethal)
FLASHBANG = {
    "prototype_parent": "EXPLOSIVE_BASE",
    "key": "flashbang",
    "aliases": ["flash", "stun grenade"],
    "desc": "A non-lethal stun grenade that produces a blinding flash and deafening bang.",
    "fuse_time": 6,
    "blast_damage": 5,  # Minimal damage, mainly stunning
    "dud_chance": 0.10,  # 10% dud chance
    "damage_type": "blunt",  # Concussion/pressure wave damage
}

# Smoke grenade (minimal damage)
SMOKE_GRENADE = {
    "prototype_parent": "EXPLOSIVE_BASE",
    "key": "smoke grenade",
    "aliases": ["smoke"],
    "desc": "A smoke grenade that creates a thick concealing cloud. Minimal explosive force.",
    "fuse_time": 4,
    "blast_damage": 2,  # Very low damage
    "dud_chance": 0.15,  # Higher dud chance
    "damage_type": "burn",  # Chemical irritation from smoke
}

# =============================================================================
# STICKY GRENADE PROTOTYPE (magnetic adhesion system)
# =============================================================================

# SPDR M9 - Spider-class magnetic adhesion grenade (repurposed mining tech)
STICKY_GRENADE = {
    "prototype_parent": "EXPLOSIVE_BASE",
    "key": "SPDR M9 grenade",
    "aliases": ["spdr", "spider grenade", "m9", "sticky grenade", "sticky"],
    "desc": "A SPDR M9 'Spider' - originally designed for breaching and clearing metallic ore deposits in asteroid mining operations. A compact black sphere bristling with eight telescoping articulated legs that extend on deployment. The moment it's thrown, tiny servos activate and the legs begin seeking ferrous metal surfaces with the single-minded purpose of industrial demolition equipment. Once proximity is achieved, powerful electromagnets pulse through the leg tips, causing them to skitter and latch onto the target with frightening precision. The magnetic adhesion is so strong that removing the stuck surface is the only way to separate yourself from the device. A soft blue LED pulses faster as detonation approaches. What was once a tool for breaking apart ore-rich asteroids has found a darker purpose in combat scenarios.",
    "fuse_time": 10,  # Longer fuse for tactical use
    "blast_damage": 30,
    "dud_chance": 0.02,  # Industrial reliability standards
    "damage_type": "laceration",
    # Sticky grenade specific attributes
    "is_sticky": True,
    "magnetic_strength": 8,  # 0-10 scale, determines stick threshold (mining-grade electromagnets)
    "stuck_to_armor": None,  # Reference to armor it's stuck to (runtime)
    "stuck_to_location": None,  # Body location where it's stuck (runtime)
}

# =============================================================================
# REMOTE DETONATOR PROTOTYPE
# =============================================================================

REMOTE_DETONATOR = {
    "key": "VECTOR UEM-3 detonator",
    "aliases": ["vector", "uem3", "uem-3", "detonator", "remote", "trigger"],
    "typeclass": "typeclasses.items.RemoteDetonator",
    "desc": "A VECTOR UEM-3 (Universal Explosive Module, Series 3) - a compact military-grade remote detonator with a matte black finish and angular, utilitarian design. Its digital display shows scanned explosive device signatures in crisp amber text. The device can store up to 20 explosive signatures simultaneously and trigger them remotely with surgical precision. A prominent red safety cover protects the main detonation switch, while smaller buttons below handle scanning and memory management. The VECTOR logo is subtly embossed on the casing, along with the serial number and dire warnings about unauthorized use.",
    "tags": [
        ("item", "general"),
        ("tool", "category"),
    ],
    "attrs": [
        ("scanned_explosives", []),  # List of explosive dbrefs
        ("max_capacity", 20),        # Maximum capacity
        ("device_type", "remote_detonator"),
    ]
}

# =============================================================================
# MELEE WEAPON PROTOTYPES (for grenade deflection testing)
# =============================================================================

# Base melee weapon
MELEE_WEAPON_BASE = {
    "prototype_key": "melee_weapon_base",
    "key": "melee weapon",
    "typeclass": "typeclasses.items.Item",
    "desc": "A weapon designed for close combat.",
    "tags": [
        ("weapon", "type"),
        ("melee", "category"),
        ("item", "general")
    ],
    "attrs": [
        ("is_ranged", False),  # Explicitly melee (though this is the default)
    ]
}

# Sword (standard deflection)
SWORD = {
    "prototype_parent": "MELEE_WEAPON_BASE",
    "key": "sword",
    "aliases": ["blade"],
    "desc": "A well-balanced sword. Good for both combat and deflecting projectiles.",
    "damage": 10,
    "weapon_type": "long_sword",  # Using existing message type
    "damage_type": "cut",  # Medical system injury type
    "hands_required": 2,
}

# Baseball bat (enhanced deflection)
BASEBALL_BAT = {
    "prototype_parent": "MELEE_WEAPON_BASE",
    "key": "baseball bat",
    "aliases": ["bat"],
    "desc": "A wooden baseball bat. Perfect for batting away incoming objects!",
    "damage": 8,
    "deflection_bonus": 0.30,  # +6 to deflection threshold (0.30 * 20)
    "weapon_type": "baseball_bat",  # Using existing message type
    "damage_type": "blunt",  # Medical system injury type
    "hands_required": 2,
}

# Staff (good deflection)
STAFF = {
    "prototype_parent": "MELEE_WEAPON_BASE",
    "key": "staff",
    "aliases": ["quarterstaff", "bo"],
    "desc": "A long wooden staff. Its reach makes it excellent for deflecting projectiles.",
    "damage": 7,
    "deflection_bonus": 0.10,  # +2 to deflection threshold (0.10 * 20)
    "weapon_type": "staff",  # Using existing message type
    "damage_type": "blunt",  # Medical system injury type
    "hands_required": 2,
}

# Tennis Racket (excellent deflection!)
TENNIS_RACKET = {
    "prototype_parent": "MELEE_WEAPON_BASE",
    "key": "tennis racket",
    "aliases": ["racket", "racquet"],
    "desc": "A professional tennis racket with tight strings and a lightweight frame. Perfect for returning serves... and grenades!",
    "damage": 5,  # Lower damage but amazing deflection
    "deflection_bonus": 0.50,  # +10 to deflection threshold (0.50 * 20) - BEST deflection weapon!
    "weapon_type": "tennis_racket",
    "damage_type": "blunt",  # Medical system injury type
    "hands": 1,
}

# Katana (legendary weapon of the samurai soul)
KATANA = {
    "prototype_parent": "MELEE_WEAPON_BASE",
    "key": "katana",
    "aliases": ["sword", "blade", "japanese sword", "nihonto", "samurai sword"],
    "desc": "A legendary nihonto katana forged by a master swordsmith in the ancient traditions of the samurai. The curved, single-edged blade bears the distinctive hamon temper line like frozen lightning captured in tamahagane steel. Its razor-sharp ha (cutting edge) whispers promises of iai-jutsu and the Way of the Sword, while the sacred geometry of its curvature channels the very essence of bushido. The ray-skin wrapped tsuka handle, bound with silk ito in traditional diamond patterns, fits perfectly in the hand as if forged for your soul alone. This is not merely a weapon—it is the steel incarnation of honor, discipline, and the indomitable spirit of the warrior. To wield it is to walk the path of the samurai, where each cut carries the weight of a thousand generations of swordmasters. The blade seems to hum with latent spiritual energy, as if it remembers every duel, every moment of perfect technique, every drop of blood spilled in service to the code. In the right hands, this katana transcends mere metal to become an extension of one's very being—the soul made manifest in folded steel.",
    "damage": 14,
    "deflection_bonus": 0.25,  # +5 to deflection threshold (excellent for parrying)
    "weapon_type": "katana",  # Using existing katana message type
    "damage_type": "cut",  # Medical system injury type
    "hands_required": 2,
}

# Dagger (poor deflection)
DAGGER = {
    "prototype_parent": "MELEE_WEAPON_BASE",
    "key": "dagger",
    "aliases": ["knife"],
    "desc": "A small, sharp dagger. Not ideal for deflecting larger objects.",
    "damage": 6,
    "deflection_bonus": -0.05,  # -1 to deflection threshold (penalty)
    "weapon_type": "knife",  # Using existing message type
    "damage_type": "stab",  # Medical system injury type
}

# Brass Knuckles (brawling weapon)
BRASS_KNUCKLES = {
    "prototype_parent": "MELEE_WEAPON_BASE",
    "key": "pair of brass knuckles",
    "aliases": ["knuckles", "brass", "knucks", "brass knuckles"],
    "desc": "A pair of brass knuckles, one for each fist. The weight feels right in your hands, cold and purposeful. Each ring has been used enough to show scratches and dents from countless encounters. Simple, brutal, effective.",
    "damage": 9,
    "deflection_bonus": 0.05,  # +1 to deflection threshold (hands-on defense)
    "weapon_type": "brass_knuckles",  # Custom message type for brass knuckles
    "damage_type": "blunt",  # Medical system injury type
    "hands_required": 2,
}

# Tessen (iron war fan)
FIGHTING_FAN = {
    "prototype_parent": "MELEE_WEAPON_BASE",
    "key": "fighting fan",
    "aliases": ["tessen", "iron fan", "fighting fan", "battle fan"],
    "desc": "A tessen war fan - deceptively elegant with its iron ribs concealed beneath decorative lacquer and silk panels. What appears to be a courtly accessory unfolds into a bladed weapon, each metal spine sharpened along its edge. The hinged ribs lock into position with a practiced snap, transforming ornament into armament. Favored by those who understood that the deadliest weapons are the ones your opponent doesn't see coming.",
    "damage": 7,
    "deflection_bonus": 0.15,  # +3 to deflection threshold (good defensive weapon)
    "weapon_type": "tessen",
    "damage_type": "cut",  # Medical system injury type
}

# Chainsaw (devastating damage, no deflection)
CHAINSAW = {
    "prototype_parent": "MELEE_WEAPON_BASE",
    "key": "chainsaw",
    "aliases": ["saw", "power saw"],
    "desc": "A gas-powered chainsaw with razor-sharp teeth. The engine sputters and growls, hungry for violence. Its mechanical brutality leaves no room for finesse.",
    "damage": 25,  # Extremely high damage
    "deflection_bonus": -0.50,  # -10 to deflection threshold (major penalty - chainsaws are terrible for defense)
    "weapon_type": "chainsaw",  # Using our newly converted message type
    "damage_type": "laceration",  # Medical system injury type
}

# =============================================================================
# BLADES SKILL WEAPONS
# =============================================================================

# Bokken (wooden practice sword)
BOKKEN = {
    "prototype_parent": "MELEE_WEAPON_BASE",
    "key": "bokken",
    "aliases": ["wooden sword", "practice sword"],
    "desc": "A solid oak bokken - the traditional wooden training sword of Japanese martial arts. Despite being made of wood, a properly swung bokken can break bones and crack skulls. The smooth grain shows wear from countless practice sessions.",
    "damage": 6,
    "deflection_bonus": 0.15,
    "weapon_type": "bokken",
    "damage_type": "blunt",
}

# Box Cutter
BOX_CUTTER = {
    "prototype_parent": "MELEE_WEAPON_BASE",
    "key": "box cutter",
    "aliases": ["utility knife", "razor blade"],
    "desc": "A retractable box cutter with a fresh blade. The yellow plastic handle is worn smooth from use. Small, concealable, and surprisingly effective in close quarters.",
    "damage": 4,
    "deflection_bonus": -0.10,
    "weapon_type": "box_cutter",
    "damage_type": "cut",
}

# Claymore
CLAYMORE = {
    "prototype_parent": "MELEE_WEAPON_BASE",
    "key": "claymore",
    "aliases": ["great sword", "two-handed sword"],
    "desc": "A massive Scottish claymore with a cruciform hilt and leather-wrapped grip. The blade stretches nearly five feet, meant for sweeping strikes that keep enemies at distance. The weight demands respect and strength.",
    "damage": 18,
    "deflection_bonus": 0.20,
    "weapon_type": "claymore",
    "damage_type": "cut",
    "hands_required": 2,
}

# Combat Knife
COMBAT_KNIFE = {
    "prototype_parent": "MELEE_WEAPON_BASE",
    "key": "combat knife",
    "aliases": ["tactical knife", "fighting knife"],
    "desc": "A military-grade combat knife with a blackened blade and serrated spine. The handle is wrapped in paracord for grip, and the pommel is weighted for striking. Built to kill, not to cut boxes.",
    "damage": 8,
    "deflection_bonus": 0.05,
    "weapon_type": "combat_knife",
    "damage_type": "stab",
}

# Cutlass
CUTLASS = {
    "prototype_parent": "MELEE_WEAPON_BASE",
    "key": "cutlass",
    "aliases": ["pirate sword", "saber"],
    "desc": "A curved cutlass with a brass basket guard. The blade shows salt-air corrosion and old nicks, but the edge is freshly honed. Balanced for slashing in tight quarters.",
    "damage": 10,
    "deflection_bonus": 0.15,
    "weapon_type": "cutlass",
    "damage_type": "cut",
}

# Falchion
FALCHION = {
    "prototype_parent": "MELEE_WEAPON_BASE",
    "key": "falchion",
    "aliases": ["chopping sword", "cleaving sword"],
    "desc": "A heavy falchion with a single-edged blade that widens toward the tip. Built for chopping through armor and bone alike. The weight is concentrated forward for devastating cuts.",
    "damage": 12,
    "deflection_bonus": 0.10,
    "weapon_type": "falchion",
    "damage_type": "cut",
}

# Gladius
GLADIUS = {
    "prototype_parent": "MELEE_WEAPON_BASE",
    "key": "gladius",
    "aliases": ["roman sword", "short sword"],
    "desc": "A reproduction Roman gladius with a leaf-shaped blade. Designed for stabbing in close formation combat. The edge is secondary to the point, which finds gaps in armor with surgical precision.",
    "damage": 9,
    "deflection_bonus": 0.10,
    "weapon_type": "gladius",
    "damage_type": "stab",
}

# Glass Shard
GLASS_SHARD = {
    "prototype_parent": "MELEE_WEAPON_BASE",
    "key": "glass shard",
    "aliases": ["broken glass", "glass shiv"],
    "desc": "A wicked shard of broken glass wrapped at one end with cloth tape. Cuts the wielder almost as easily as the victim. Desperate, ugly, effective.",
    "damage": 5,
    "deflection_bonus": -0.15,
    "weapon_type": "glass_shard",
    "damage_type": "cut",
}

# Kukri
KUKRI = {
    "prototype_parent": "MELEE_WEAPON_BASE",
    "key": "kukri",
    "aliases": ["gurkha knife", "khukuri"],
    "desc": "A traditional Nepalese kukri with its distinctive inward-curved blade. The weight is forward, designed for powerful chopping strikes. Gurkha regiments made this blade legendary.",
    "damage": 11,
    "deflection_bonus": 0.05,
    "weapon_type": "kukri",
    "damage_type": "cut",
}

# Machete
MACHETE = {
    "prototype_parent": "MELEE_WEAPON_BASE",
    "key": "machete",
    "aliases": ["brush cutter", "cane knife"],
    "desc": "A long-bladed machete with a wooden handle. Originally meant for clearing brush, it's found equal utility clearing paths through crowds. The blade is stained with rust and other things.",
    "damage": 10,
    "deflection_bonus": 0.05,
    "weapon_type": "machete",
    "damage_type": "cut",
}

# Meat Cleaver
MEAT_CLEAVER = {
    "prototype_parent": "MELEE_WEAPON_BASE",
    "key": "meat cleaver",
    "aliases": ["cleaver", "butcher knife"],
    "desc": "A heavy rectangular meat cleaver from a butcher's block. The blade is thick steel, built to chop through bone. In a pinch, it chops through other things just as well.",
    "damage": 9,
    "deflection_bonus": 0.0,
    "weapon_type": "meat_cleaver",
    "damage_type": "cut",
}

# Mirror Shard
MIRROR_SHARD = {
    "prototype_parent": "MELEE_WEAPON_BASE",
    "key": "mirror shard",
    "aliases": ["broken mirror", "mirror shiv"],
    "desc": "A triangular piece of broken mirror, the reflective coating fragmenting your image as you grip it. Someone stares back at you from its surface. Maybe it's you. Maybe it isn't anymore.",
    "damage": 5,
    "deflection_bonus": -0.15,
    "weapon_type": "mirror_shard",
    "damage_type": "cut",
}

# Rapier
RAPIER = {
    "prototype_parent": "MELEE_WEAPON_BASE",
    "key": "rapier",
    "aliases": ["fencing sword", "epee"],
    "desc": "An elegant rapier with a swept hilt and wire-wrapped grip. The blade is impossibly thin but remarkably rigid, designed for precise thrusts that slip between ribs. A duelist's weapon.",
    "damage": 9,
    "deflection_bonus": 0.15,
    "weapon_type": "rapier",
    "damage_type": "stab",
}

# Scalpel
SCALPEL = {
    "prototype_parent": "MELEE_WEAPON_BASE",
    "key": "scalpel",
    "aliases": ["surgical blade", "medical knife"],
    "desc": "A surgical scalpel with a disposable blade. The edge is impossibly sharp, meant to part flesh with minimal trauma. In combat, it trades reach for precision cuts.",
    "damage": 3,
    "deflection_bonus": -0.15,
    "weapon_type": "scalpel",
    "damage_type": "cut",
}

# Scimitar
SCIMITAR = {
    "prototype_parent": "MELEE_WEAPON_BASE",
    "key": "scimitar",
    "aliases": ["curved sword", "shamshir"],
    "desc": "A sweeping scimitar with an elegantly curved blade. The design maximizes cutting power in cavalry slashes, drawing across the target. The edge whispers through the air.",
    "damage": 11,
    "deflection_bonus": 0.10,
    "weapon_type": "scimitar",
    "damage_type": "cut",
}

# Shiv
SHIV = {
    "prototype_parent": "MELEE_WEAPON_BASE",
    "key": "shiv",
    "aliases": ["prison knife", "homemade knife"],
    "desc": "A crude shiv fashioned from sharpened metal. The handle is wrapped in torn cloth. It's ugly, it's simple, and it's ended more lives in dark corners than fancy swords ever will.",
    "damage": 5,
    "deflection_bonus": -0.10,
    "weapon_type": "shiv",
    "damage_type": "stab",
}

# Small Knife
SMALL_KNIFE = {
    "prototype_parent": "MELEE_WEAPON_BASE",
    "key": "small knife",
    "aliases": ["pocket knife", "folding knife"],
    "desc": "A small folding knife with a three-inch blade. Nothing fancy, nothing tactical - just a working knife that happens to fit in a pocket and opens with a satisfying click.",
    "damage": 4,
    "deflection_bonus": -0.10,
    "weapon_type": "small_knife",
    "damage_type": "stab",
}

# Straight Razor
STRAIGHT_RAZOR = {
    "prototype_parent": "MELEE_WEAPON_BASE",
    "key": "straight razor",
    "aliases": ["cutthroat razor", "barber razor"],
    "desc": "An old-fashioned straight razor with a bone handle. The blade folds into the handle with a menacing click. Originally for shaving, but the edge doesn't care what it cuts.",
    "damage": 4,
    "deflection_bonus": -0.15,
    "weapon_type": "straight_razor",
    "damage_type": "cut",
}

# =============================================================================
# MELEE SKILL WEAPONS (blunt weapons, improvised, tools)
# =============================================================================

# Baton
BATON = {
    "prototype_parent": "MELEE_WEAPON_BASE",
    "key": "baton",
    "aliases": ["club", "billy club"],
    "desc": "A solid metal baton with a rubberized grip. Standard issue for security and law enforcement. Extended, it's about two feet of pain compliance.",
    "damage": 7,
    "deflection_bonus": 0.10,
    "weapon_type": "baton",
    "damage_type": "blunt",
}

# Battle Axe
BATTLE_AXE = {
    "prototype_parent": "MELEE_WEAPON_BASE",
    "key": "battle axe",
    "aliases": ["war axe", "viking axe"],
    "desc": "A proper battle axe with a crescent-shaped head on a long haft. The weight demands two hands, but the devastation it delivers justifies the commitment.",
    "damage": 16,
    "deflection_bonus": 0.05,
    "weapon_type": "battle_axe",
    "damage_type": "cut",
    "hands_required": 2,
}

# Blowtorch
BLOWTORCH = {
    "prototype_parent": "MELEE_WEAPON_BASE",
    "key": "blowtorch",
    "aliases": ["torch", "welding torch"],
    "desc": "A handheld blowtorch with a blue-hot flame. Meant for welding and cutting metal. The tank sloshes with propane, and the igniter clicks with promise.",
    "damage": 8,
    "deflection_bonus": -0.20,
    "weapon_type": "blowtorch",
    "damage_type": "burn",
}

# Brick
BRICK = {
    "prototype_parent": "MELEE_WEAPON_BASE",
    "key": "brick",
    "aliases": ["red brick", "building brick"],
    "desc": "A standard red construction brick. Heavy, rough, and absolutely final when applied to someone's skull. The simplest weapon is often the most effective.",
    "damage": 6,
    "deflection_bonus": -0.05,
    "weapon_type": "brick",
    "damage_type": "blunt",
}

# Broken Bottle
BROKEN_BOTTLE = {
    "prototype_parent": "MELEE_WEAPON_BASE",
    "key": "broken bottle",
    "aliases": ["bottle", "glass bottle"],
    "desc": "A broken bottle with jagged edges. The neck makes a convenient handle while the shattered base becomes a crown of glass teeth. Classic bar fight weaponry.",
    "damage": 5,
    "deflection_bonus": -0.10,
    "weapon_type": "broken_bottle",
    "damage_type": "cut",
}

# Catchpole
CATCHPOLE = {
    "prototype_parent": "MELEE_WEAPON_BASE",
    "key": "catchpole",
    "aliases": ["catch pole", "control pole"],
    "desc": "A long pole with a loop of cable at the end, normally used for animal control. The loop can restrain a neck surprisingly well, regardless of species.",
    "damage": 4,
    "deflection_bonus": 0.10,
    "weapon_type": "catchpole",
    "damage_type": "blunt",
    "hands_required": 2,
}

# Chain
CHAIN = {
    "prototype_parent": "MELEE_WEAPON_BASE",
    "key": "chain",
    "aliases": ["heavy chain", "bike chain"],
    "desc": "A length of heavy chain, about three feet long. Each link is solid steel. Swung with intent, it wraps around limbs and crushes bone.",
    "damage": 8,
    "deflection_bonus": 0.05,
    "weapon_type": "chain",
    "damage_type": "blunt",
}

# Cricket Bat
CRICKET_BAT = {
    "prototype_parent": "MELEE_WEAPON_BASE",
    "key": "cricket bat",
    "aliases": ["bat", "willow bat"],
    "desc": "A traditional cricket bat made of willow wood. The flat striking surface is perfect for hitting things - balls, heads, whatever needs hitting.",
    "damage": 8,
    "deflection_bonus": 0.25,
    "weapon_type": "cricket_bat",
    "damage_type": "blunt",
    "hands_required": 2,
}

# Crowbar
CROWBAR = {
    "prototype_parent": "MELEE_WEAPON_BASE",
    "key": "crowbar",
    "aliases": ["pry bar", "iron bar"],
    "desc": "A heavy steel crowbar with a curved claw at one end. Originally designed for prying open crates and doors, it pries open other things equally well.",
    "damage": 9,
    "deflection_bonus": 0.10,
    "weapon_type": "crowbar",
    "damage_type": "blunt",
}

# Fire Axe
FIRE_AXE = {
    "prototype_parent": "MELEE_WEAPON_BASE",
    "key": "fire axe",
    "aliases": ["axe", "emergency axe"],
    "desc": "A red-painted fire axe pulled from an emergency case. The blade is sharp, the handle is fiberglass, and the weight is perfect for breaching doors - or skulls.",
    "damage": 14,
    "deflection_bonus": 0.05,
    "weapon_type": "fire_axe",
    "damage_type": "cut",
    "hands_required": 2,
}

# Flare
FLARE = {
    "prototype_parent": "MELEE_WEAPON_BASE",
    "key": "flare",
    "aliases": ["road flare", "emergency flare"],
    "desc": "A lit road flare spitting red sparks. The chemical burn is intense enough to melt synthetic fabric. As a weapon, it's more psychological than practical - but burns are burns.",
    "damage": 4,
    "deflection_bonus": -0.15,
    "weapon_type": "flare",
    "damage_type": "burn",
}

# Garden Shears
GARDEN_SHEARS = {
    "prototype_parent": "MELEE_WEAPON_BASE",
    "key": "garden shears",
    "aliases": ["shears", "pruning shears"],
    "desc": "Heavy-duty garden shears meant for trimming branches. The blades are long and slightly curved, with enough leverage to cut through surprisingly thick... branches.",
    "damage": 7,
    "deflection_bonus": -0.05,
    "weapon_type": "garden_shears",
    "damage_type": "cut",
    "hands_required": 2,
}

# Hammer
HAMMER = {
    "prototype_parent": "MELEE_WEAPON_BASE",
    "key": "hammer",
    "aliases": ["claw hammer", "framing hammer"],
    "desc": "A standard claw hammer with a fiberglass handle. The head is weighted for driving nails. The claw is curved for pulling them out. Both ends work on people.",
    "damage": 7,
    "deflection_bonus": 0.0,
    "weapon_type": "hammer",
    "damage_type": "blunt",
}

# Hatchet
HATCHET = {
    "prototype_parent": "MELEE_WEAPON_BASE",
    "key": "hatchet",
    "aliases": ["small axe", "hand axe"],
    "desc": "A compact hatchet with a leather-wrapped handle. Designed for light chopping and camping tasks. The blade is sharp enough for finer work than a full axe allows.",
    "damage": 9,
    "deflection_bonus": 0.0,
    "weapon_type": "hatchet",
    "damage_type": "cut",
}

# Ice Pick
ICE_PICK = {
    "prototype_parent": "MELEE_WEAPON_BASE",
    "key": "ice pick",
    "aliases": ["pick", "awl"],
    "desc": "An old-fashioned ice pick with a wooden handle and steel spike. Originally meant for chipping ice blocks. The point finds other uses in dark alleys.",
    "damage": 6,
    "deflection_bonus": -0.10,
    "weapon_type": "ice_pick",
    "damage_type": "stab",
}

# Improvised Shield
IMPROVISED_SHIELD = {
    "prototype_parent": "MELEE_WEAPON_BASE",
    "key": "improvised shield",
    "aliases": ["makeshift shield", "riot shield"],
    "desc": "A large piece of scrap metal or plastic fashioned into a crude shield. The edges are rough and the grip is uncomfortable, but it stops incoming attacks.",
    "damage": 4,
    "deflection_bonus": 0.40,
    "weapon_type": "improvised_shield",
    "damage_type": "blunt",
}

# Large Axe
LARGE_AXE = {
    "prototype_parent": "MELEE_WEAPON_BASE",
    "key": "large axe",
    "aliases": ["wood axe", "splitting axe"],
    "desc": "A heavy wood-splitting axe with a long handle. The wedge-shaped head is built for cleaving logs. It cleaves other things with equal enthusiasm.",
    "damage": 13,
    "deflection_bonus": 0.05,
    "weapon_type": "large_axe",
    "damage_type": "cut",
    "hands_required": 2,
}

# Large Shield
LARGE_SHIELD = {
    "prototype_parent": "MELEE_WEAPON_BASE",
    "key": "large shield",
    "aliases": ["tower shield", "riot shield"],
    "desc": "A proper large shield offering full torso coverage. Heavy and cumbersome, but it turns you into a walking wall. The edge can be used to bash.",
    "damage": 5,
    "deflection_bonus": 0.50,
    "weapon_type": "large_shield",
    "damage_type": "blunt",
}

# Meat Hook
MEAT_HOOK = {
    "prototype_parent": "MELEE_WEAPON_BASE",
    "key": "meat hook",
    "aliases": ["hook", "butcher hook"],
    "desc": "A curved steel meat hook stained with old blood. The point is sharp enough to pierce, and the curve ensures whatever it catches doesn't come free easily.",
    "damage": 8,
    "deflection_bonus": -0.05,
    "weapon_type": "meat_hook",
    "damage_type": "stab",
}

# Metal Club
METAL_CLUB = {
    "prototype_parent": "MELEE_WEAPON_BASE",
    "key": "metal club",
    "aliases": ["pipe club", "iron club"],
    "desc": "A solid piece of metal shaped into a crude club. No elegance, no subtlety - just weight and violence in a convenient package.",
    "damage": 9,
    "deflection_bonus": 0.05,
    "weapon_type": "metal_club",
    "damage_type": "blunt",
}

# Nail Bat
NAIL_BAT = {
    "prototype_parent": "MELEE_WEAPON_BASE",
    "key": "nail bat",
    "aliases": ["spiked bat", "nailed bat"],
    "desc": "A baseball bat studded with rusty nails. The wood is wrapped in duct tape for grip, and each nail promises tetanus along with trauma.",
    "damage": 11,
    "deflection_bonus": 0.15,
    "weapon_type": "nail_bat",
    "damage_type": "blunt",
    "hands_required": 2,
}

# Nailed Board
NAILED_BOARD = {
    "prototype_parent": "MELEE_WEAPON_BASE",
    "key": "nailed board",
    "aliases": ["board with nails", "spiked board"],
    "desc": "A rough wooden board with nails driven through it. The nails stick out at various angles, bent but sharp. Primitive, brutal, effective.",
    "damage": 8,
    "deflection_bonus": 0.0,
    "weapon_type": "nailed_board",
    "damage_type": "blunt",
}

# Nightstick
NIGHTSTICK = {
    "prototype_parent": "MELEE_WEAPON_BASE",
    "key": "nightstick",
    "aliases": ["police baton", "truncheon"],
    "desc": "A wooden nightstick with a side handle. Classic law enforcement issue, designed for controlling suspects. The weight is perfectly balanced for repeated strikes.",
    "damage": 7,
    "deflection_bonus": 0.15,
    "weapon_type": "nightstick",
    "damage_type": "blunt",
}

# Pipe
PIPE = {
    "prototype_parent": "MELEE_WEAPON_BASE",
    "key": "pipe",
    "aliases": ["metal pipe", "lead pipe"],
    "desc": "A length of metal pipe, probably from some plumbing. Heavy, sturdy, and anonymous - the kind of weapon that could have come from anywhere and leaves no distinctive marks.",
    "damage": 8,
    "deflection_bonus": 0.10,
    "weapon_type": "pipe",
    "damage_type": "blunt",
}

# Pipe Wrench
PIPE_WRENCH = {
    "prototype_parent": "MELEE_WEAPON_BASE",
    "key": "pipe wrench",
    "aliases": ["wrench", "plumber's wrench"],
    "desc": "A heavy pipe wrench with adjustable jaws. The weight is concentrated in the head, making it swing like a mace. Plumbers know - this is the real tool of the trade.",
    "damage": 10,
    "deflection_bonus": 0.05,
    "weapon_type": "pipe_wrench",
    "damage_type": "blunt",
}

# Pool Cue
POOL_CUE = {
    "prototype_parent": "MELEE_WEAPON_BASE",
    "key": "pool cue",
    "aliases": ["cue stick", "billiard cue"],
    "desc": "A two-piece pool cue screwed together. The wood is polished smooth, tapering to a fine point. Break it over someone's back and you have two weapons.",
    "damage": 6,
    "deflection_bonus": 0.10,
    "weapon_type": "pool_cue",
    "damage_type": "blunt",
    "hands_required": 2,
}

# Rebar
REBAR = {
    "prototype_parent": "MELEE_WEAPON_BASE",
    "key": "rebar",
    "aliases": ["reinforcing bar", "steel rod"],
    "desc": "A length of construction rebar with ridged surfaces for gripping concrete. The ridges also grip flesh quite effectively. About three feet of solid steel.",
    "damage": 9,
    "deflection_bonus": 0.10,
    "weapon_type": "rebar",
    "damage_type": "blunt",
}

# Screwdriver
SCREWDRIVER = {
    "prototype_parent": "MELEE_WEAPON_BASE",
    "key": "screwdriver",
    "aliases": ["flathead", "phillips"],
    "desc": "A long screwdriver with a hardened steel shaft. The grip is rubberized for comfort. The point is meant for turning screws, but anatomy has screws of its own.",
    "damage": 5,
    "deflection_bonus": -0.10,
    "weapon_type": "screwdriver",
    "damage_type": "stab",
}

# Shovel
SHOVEL = {
    "prototype_parent": "MELEE_WEAPON_BASE",
    "key": "shovel",
    "aliases": ["spade", "entrenching tool"],
    "desc": "A standard garden shovel with a steel blade and wooden handle. It digs graves before and after use. The edge isn't sharp, but edge doesn't matter at this speed.",
    "damage": 10,
    "deflection_bonus": 0.10,
    "weapon_type": "shovel",
    "damage_type": "blunt",
    "hands_required": 2,
}

# Sledgehammer
SLEDGEHAMMER = {
    "prototype_parent": "MELEE_WEAPON_BASE",
    "key": "sledgehammer",
    "aliases": ["maul", "heavy hammer"],
    "desc": "A ten-pound sledgehammer with a fiberglass handle. Built for demolition work. The head moves slow but carries enough momentum to end arguments permanently.",
    "damage": 15,
    "deflection_bonus": -0.10,
    "weapon_type": "sledgehammer",
    "damage_type": "blunt",
    "hands_required": 2,
}

# Small Axe
SMALL_AXE = {
    "prototype_parent": "MELEE_WEAPON_BASE",
    "key": "small axe",
    "aliases": ["camp axe", "boy scout axe"],
    "desc": "A small camp axe with a short handle. Compact enough to carry easily, heavy enough to do damage. The head is slightly rusted but the edge is keen.",
    "damage": 8,
    "deflection_bonus": 0.0,
    "weapon_type": "small_axe",
    "damage_type": "cut",
}

# Small Shield
SMALL_SHIELD = {
    "prototype_parent": "MELEE_WEAPON_BASE",
    "key": "small shield",
    "aliases": ["buckler", "round shield"],
    "desc": "A small round shield meant for parrying and punching. Light enough to maneuver quickly, solid enough to deflect blows. The boss can be used to strike.",
    "damage": 4,
    "deflection_bonus": 0.30,
    "weapon_type": "small_shield",
    "damage_type": "blunt",
}

# Stake
STAKE = {
    "prototype_parent": "MELEE_WEAPON_BASE",
    "key": "stake",
    "aliases": ["wooden stake", "tent stake"],
    "desc": "A sharpened wooden stake about a foot long. Originally for securing tents or fencing. The point is crude but effective against anything with a chest cavity.",
    "damage": 6,
    "deflection_bonus": -0.10,
    "weapon_type": "stake",
    "damage_type": "stab",
}

# Tire Iron
TIRE_IRON = {
    "prototype_parent": "MELEE_WEAPON_BASE",
    "key": "tire iron",
    "aliases": ["lug wrench", "wheel brace"],
    "desc": "A heavy tire iron with a bent end for leverage. Every car has one. Every driver has considered using it for something other than changing tires.",
    "damage": 8,
    "deflection_bonus": 0.10,
    "weapon_type": "tire_iron",
    "damage_type": "blunt",
}

# Whip
WHIP = {
    "prototype_parent": "MELEE_WEAPON_BASE",
    "key": "whip",
    "aliases": ["bullwhip", "leather whip"],
    "desc": "A braided leather whip about eight feet long. The tip moves faster than sound when cracked. Leaves welts that last for weeks and scars that last longer.",
    "damage": 6,
    "deflection_bonus": 0.05,
    "weapon_type": "whip",
    "damage_type": "blunt",
}

# =============================================================================
# PISTOL SKILL WEAPONS
# =============================================================================

# Flare Gun
FLARE_GUN = {
    "prototype_parent": "RANGED_WEAPON_BASE",
    "key": "flare gun",
    "aliases": ["signal gun", "distress pistol"],
    "desc": "An orange plastic flare gun meant for signaling distress. The 12-gauge flare it fires can also signal distress in a more direct way when aimed at someone.",
    "damage": 10,
    "attrs": [
        ("weapon_type", "flare_gun"),
        ("damage_type", "burn"),
        ("hands_required", 1),
        ("is_ranged", True),
        ("uses_ammo", True),
        ("ammo_type", "flare"),
        ("ammo_capacity", 1),
        ("current_ammo", 1),
    ]
}

# Heavy Revolver
HEAVY_REVOLVER = {
    "prototype_parent": "RANGED_WEAPON_BASE",
    "key": "heavy revolver",
    "aliases": ["magnum", "44 magnum", "wheel gun"],
    "desc": "A massive double-action revolver with a six-inch barrel. The cylinder holds six rounds of ammunition that could stop a charging bear. The recoil requires commitment.",
    "damage": 20,
    "attrs": [
        ("weapon_type", "heavy_revolver"),
        ("damage_type", "bullet"),
        ("hands_required", 1),
        ("is_ranged", True),
        ("uses_ammo", True),
        ("ammo_type", "44mag"),
        ("ammo_capacity", 6),
        ("current_ammo", 6),
    ]
}

# Light Revolver
LIGHT_REVOLVER = {
    "prototype_parent": "RANGED_WEAPON_BASE",
    "key": "light revolver",
    "aliases": ["snubnose", "pocket revolver", "38 special"],
    "desc": "A compact revolver with a snub-nosed barrel. Five shots, no safety, and small enough to hide almost anywhere. The classic backup piece.",
    "damage": 10,
    "attrs": [
        ("weapon_type", "light_revolver"),
        ("damage_type", "bullet"),
        ("hands_required", 1),
        ("is_ranged", True),
        ("uses_ammo", True),
        ("ammo_type", "38special"),
        ("ammo_capacity", 5),
        ("current_ammo", 5),
    ]
}

# Machine Pistol
MACHINE_PISTOL = {
    "prototype_parent": "RANGED_WEAPON_BASE",
    "key": "machine pistol",
    "aliases": ["auto pistol", "glock 18"],
    "desc": "A compact machine pistol with a extended magazine and folding stock. The selector switch offers semi-auto and full-auto fire. Accuracy suffers, but volume compensates.",
    "damage": 9,
    "attrs": [
        ("weapon_type", "machine_pistol"),
        ("damage_type", "bullet"),
        ("hands_required", 1),
        ("is_ranged", True),
        ("uses_ammo", True),
        ("ammo_type", "9mm"),
        ("ammo_capacity", 33),
        ("current_ammo", 33),
    ]
}

# Nail Gun
NAIL_GUN = {
    "prototype_parent": "RANGED_WEAPON_BASE",
    "key": "nail gun",
    "aliases": ["pneumatic nailer", "framing nailer"],
    "desc": "A pneumatic nail gun with a full magazine of 3-inch framing nails. Construction safety protocols exist for good reason. This is that reason.",
    "damage": 8,
    "attrs": [
        ("weapon_type", "nail_gun"),
        ("damage_type", "stab"),
        ("hands_required", 1),
        ("is_ranged", True),
        ("uses_ammo", True),
        ("ammo_type", "nail"),
        ("ammo_capacity", 50),
        ("current_ammo", 50),
    ]
}

# Stun Gun
STUN_GUN = {
    "prototype_parent": "RANGED_WEAPON_BASE",
    "key": "stun gun",
    "aliases": ["taser", "electroshock"],
    "desc": "A handheld stun gun that fires two barbed probes trailing thin wires. The electrical discharge causes immediate muscle lockup. Range is limited, but so is target resistance.",
    "damage": 5,
    "attrs": [
        ("weapon_type", "stun_gun"),
        ("damage_type", "burn"),
        ("hands_required", 1),
        ("is_ranged", True),
        ("uses_ammo", False),  # Electric, doesn't use conventional ammo
    ]
}

# =============================================================================
# RIFLE SKILL WEAPONS
# =============================================================================

# Bowel Disruptor
BOWEL_DISRUPTOR = {
    "prototype_parent": "RANGED_WEAPON_BASE",
    "key": "bowel disruptor",
    "aliases": ["disruptor", "sonic rifle"],
    "desc": "A bulky weapon that emits focused infrasound waves. The effect on human bowels is as advertised. Banned by most conventions. Available at better arms dealers.",
    "damage": 15,
    "attrs": [
        ("weapon_type", "bowel_disruptor"),
        ("damage_type", "blunt"),
        ("is_ranged", True),
        ("uses_ammo", False),  # Energy weapon
    ]
}

# Flamethrower
FLAMETHROWER = {
    "prototype_parent": "RANGED_WEAPON_BASE",
    "key": "flamethrower",
    "aliases": ["flame thrower", "fire sprayer"],
    "desc": "A backpack-mounted flamethrower with a long nozzle and pilot light. The fuel tank gurgles ominously. The stream of burning gel sticks to everything it touches.",
    "damage": 18,
    "attrs": [
        ("weapon_type", "flamethrower"),
        ("damage_type", "burn"),
        ("is_ranged", True),
        ("uses_ammo", True),
        ("ammo_type", "fuel"),
        ("ammo_capacity", 10),
        ("current_ammo", 10),
    ]
}

# Heavy Machine Gun
HEAVY_MACHINE_GUN = {
    "prototype_parent": "RANGED_WEAPON_BASE",
    "key": "heavy machine gun",
    "aliases": ["HMG", "mounted gun", "50 cal"],
    "desc": "A heavy machine gun designed for vehicle or tripod mounting. The belt feed allows sustained fire, and the caliber allows sustained devastation. Portable only in the most generous sense.",
    "damage": 30,
    "attrs": [
        ("weapon_type", "heavy_machine_gun"),
        ("damage_type", "bullet"),
        ("is_ranged", True),
        ("uses_ammo", True),
        ("ammo_type", "50bmg"),
        ("ammo_capacity", 100),
        ("current_ammo", 100),
    ]
}

# Lever-Action Rifle
LEVER_ACTION_RIFLE = {
    "prototype_parent": "RANGED_WEAPON_BASE",
    "key": "lever-action rifle",
    "aliases": ["lever rifle", "winchester", "cowboy rifle"],
    "desc": "A classic lever-action rifle with a tubular magazine under the barrel. The lever cycles with a satisfying mechanical precision. Frontier technology that never stopped being effective.",
    "damage": 18,
    "attrs": [
        ("weapon_type", "lever-action_rifle"),
        ("damage_type", "bullet"),
        ("is_ranged", True),
        ("uses_ammo", True),
        ("ammo_type", "308win"),
        ("ammo_capacity", 8),
        ("current_ammo", 8),
    ]
}

# Lever-Action Shotgun
LEVER_ACTION_SHOTGUN = {
    "prototype_parent": "RANGED_WEAPON_BASE",
    "key": "lever-action shotgun",
    "aliases": ["lever shotgun", "mare's leg"],
    "desc": "A compact lever-action shotgun with a shortened stock. The lever cycles 12-gauge shells with cowboy style. Fast, loud, and devastating at close range.",
    "damage": 18,
    "attrs": [
        ("weapon_type", "lever-action_shotgun"),
        ("damage_type", "bullet"),
        ("is_ranged", True),
        ("uses_ammo", True),
        ("ammo_type", "12gauge"),
        ("ammo_capacity", 6),
        ("current_ammo", 6),
    ]
}

# Semi-Auto Rifle
SEMI_AUTO_RIFLE = {
    "prototype_parent": "RANGED_WEAPON_BASE",
    "key": "semi-auto rifle",
    "aliases": ["battle rifle", "carbine"],
    "desc": "A semi-automatic rifle with a detachable magazine. One trigger pull, one shot, as fast as you can pull. The receiver is stamped with military proof marks.",
    "damage": 16,
    "attrs": [
        ("weapon_type", "semi-auto_rifle"),
        ("damage_type", "bullet"),
        ("is_ranged", True),
        ("uses_ammo", True),
        ("ammo_type", "762nato"),
        ("ammo_capacity", 20),
        ("current_ammo", 20),
    ]
}

# Semi-Auto Shotgun
SEMI_AUTO_SHOTGUN = {
    "prototype_parent": "RANGED_WEAPON_BASE",
    "key": "semi-auto shotgun",
    "aliases": ["auto shotgun", "combat shotgun"],
    "desc": "A semi-automatic shotgun with gas operation and an extended magazine. Each trigger pull chambers a fresh shell automatically. Volume of fire meets close-range devastation.",
    "damage": 18,
    "attrs": [
        ("weapon_type", "semi-auto_shotgun"),
        ("damage_type", "bullet"),
        ("is_ranged", True),
        ("uses_ammo", True),
        ("ammo_type", "12gauge"),
        ("ammo_capacity", 8),
        ("current_ammo", 8),
    ]
}

# Sniper Rifle
SNIPER_RIFLE = {
    "prototype_parent": "RANGED_WEAPON_BASE",
    "key": "sniper rifle",
    "aliases": ["precision rifle", "marksman rifle"],
    "desc": "A precision rifle with a heavy barrel, bipod, and high-powered scope. Built for one shot, one kill at extreme range. The bolt action is glass-smooth.",
    "damage": 28,
    "attrs": [
        ("weapon_type", "bolt-action_rifle"),
        ("damage_type", "bullet"),
        ("is_ranged", True),
        ("uses_ammo", True),
        ("ammo_type", "762nato"),
        ("ammo_capacity", 5),
        ("current_ammo", 5),
    ]
}

# =============================================================================
# BRAWLING SKILL WEAPONS
# =============================================================================

# Tiger Claws (moved to Martial Arts as it requires trained technique)

# =============================================================================
# MARTIAL ARTS SKILL WEAPONS
# =============================================================================

# Nunchaku
NUNCHAKU = {
    "prototype_parent": "MELEE_WEAPON_BASE",
    "key": "nunchaku",
    "aliases": ["nunchucks", "chain sticks"],
    "desc": "A pair of wooden batons connected by a short chain. The weapon requires training to use effectively without striking yourself. In skilled hands, they're a blur of controlled chaos.",
    "damage": 8,
    "deflection_bonus": 0.15,
    "weapon_type": "nunchaku",
    "damage_type": "blunt",
    "hands_required": 2,
}

# Tiger Claws
TIGER_CLAWS = {
    "prototype_parent": "MELEE_WEAPON_BASE",
    "key": "tiger claws",
    "aliases": ["bagh nakh", "claw weapon"],
    "desc": "A set of curved metal claws worn over the fingers like brass knuckles. The blades extend from between the knuckles, turning each punch into a raking slash.",
    "damage": 10,
    "deflection_bonus": 0.0,
    "weapon_type": "tiger_claws",
    "damage_type": "cut",
}

# =============================================================================
# THROWING WEAPON PROTOTYPES
# =============================================================================

# Base throwing weapon
THROWING_WEAPON_BASE = {
    "prototype_key": "throwing_weapon_base",
    "key": "throwing weapon",
    "typeclass": "typeclasses.items.Item",
    "desc": "A weapon designed for throwing.",
    "tags": [
        ("weapon", "type"),
        ("throwing", "category"),
        ("item", "general")
    ],
    "attrs": [
        ("is_ranged", True),  # Throwing weapons are ranged weapons
        ("is_explosive", False),
        ("is_throwing_weapon", True),  # Dedicated throwing weapon - uses attack command
    ]
}

# Throwing knife
THROWING_KNIFE = {
    "prototype_parent": "THROWING_WEAPON_BASE",
    "key": "throwing knife",
    "aliases": ["knife", "blade"],
    "desc": "A balanced knife designed for throwing. Sharp and deadly.",
    "damage": 8,
    "attrs": [
        ("weapon_type", "throwing_knife"),
        ("damage_type", "stab"),  # Medical system injury type
    ]
}

# Throwing axe
THROWING_AXE = {
    "prototype_parent": "THROWING_WEAPON_BASE", 
    "key": "throwing axe",
    "aliases": ["axe", "hatchet"],
    "desc": "A heavy axe perfect for throwing. Deals significant damage on impact.",
    "damage": 12,
    "attrs": [
        ("weapon_type", "throwing_axe"),
        ("damage_type", "cut"),  # Medical system injury type
    ]
}

# Shuriken
SHURIKEN = {
    "prototype_parent": "THROWING_WEAPON_BASE",
    "key": "shuriken",
    "aliases": ["star", "ninja star"],
    "desc": "A traditional throwing star. Light and precise.",
    "damage": 6,
    "attrs": [
        ("weapon_type", "shuriken"),
        ("damage_type", "laceration"),  # Medical system injury type
    ]
}

# =============================================================================
# RANGED WEAPON PROTOTYPES (firearms and projectile weapons)
# =============================================================================

# Base ranged weapon
RANGED_WEAPON_BASE = {
    "prototype_key": "ranged_weapon_base",
    "key": "ranged weapon",
    "typeclass": "typeclasses.items.Item",
    "desc": "A weapon designed for ranged combat.",
    "tags": [
        ("weapon", "type"),
        ("ranged", "category"),
        ("item", "general")
    ],
    "attrs": [
        ("is_ranged", True),  # Ranged weapons
        ("hands_required", 2),  # Most firearms require two hands
        ("deflection_bonus", 0.0),  # Base deflection capability
        # Ammunition system attributes
        ("uses_ammo", True),  # Whether this weapon uses ammunition
        ("ammo_type", "9mm"),  # Default ammo type (should be overridden)
        ("ammo_capacity", 10),  # Magazine/chamber capacity
        ("current_ammo", 10),  # Current loaded rounds
        ("installed_mods", {}),  # Installed weapon modifications
    ]
}

# Light pistol (existing message type)
LIGHT_PISTOL = {
    "prototype_parent": "RANGED_WEAPON_BASE",
    "key": "PAM Model 6 pistol",
    "aliases": ["pistol", "model 6", "m6", "pam pistol", "pam m6", "handgun", "9mm"],
    "desc": "A Pioneer Arms Manufacturing Model 6 pistol in 9mm - the ubiquitous sidearm of frontier colonies across human space. The polymer frame keeps weight down while the slide is precision-machined steel with a corrosion-resistant finish that stands up to harsh planetary environments. Fixed three-dot sights are robust and simple, requiring no batteries or adjustment. The trigger is heavy but predictable, designed for reliability over refinement. No frills, no unnecessary features - just a working person's pistol that starts every time and keeps running through dust, mud, and neglect. You'll find Model 6s in the holsters of security guards, cargo haulers, and frontier marshals across a thousand worlds. It's not the best pistol ever made, but it might be the most common.",
    "damage": 12,
    "attrs": [
        ("weapon_type", "light_pistol"),
        ("damage_type", "bullet"),  # Medical system injury type
        ("hands_required", 1),  # Pistols can be fired one-handed
        ("is_ranged", True),
        ("uses_ammo", True),
        ("ammo_type", "9mm"),
        ("ammo_capacity", 15),
        ("current_ammo", 15),
    ]
}

# Heavy pistol (existing message type) 
HEAVY_PISTOL = {
    "prototype_parent": "RANGED_WEAPON_BASE",
    "key": "HDG M88 tactical pistol",
    "aliases": ["M88", "m88", "hdg pistol", "tactical pistol", "heavy pistol", "magnum"],
    "desc": "A Helios Defense Group M88 tactical pistol chambered in 10mm caseless - maintaining ammunition commonality across HDG's entire product line. Unlike the compact VP9 or battle rifle M4RA, the M88 is built as a dedicated sidearm with refined ergonomics. The slide is machined from stainless steel with aggressive forward serrations and a loaded chamber indicator. The polymer frame features interchangeable backstraps and an integrated accessory rail. The match-grade barrel extends slightly beyond the slide, housed in a subtle compensator that controls muzzle rise during rapid fire. Night sights come standard, and the trigger breaks clean at four pounds. While the 10mm caseless round is somewhat overpowered for a pistol platform, the M88's robust construction handles it without complaint - and when you need a sidearm that hits like a rifle, HDG delivers.",
    "damage": 18,
    "attrs": [
        ("weapon_type", "heavy_pistol"),
        ("damage_type", "bullet"),  # Medical system injury type
        ("hands_required", 1),  # Can be fired one-handed but difficult
        ("is_ranged", True),
        ("uses_ammo", True),
        ("ammo_type", "45acp"),
        ("ammo_capacity", 12),
        ("current_ammo", 12),
    ]
}

# Pump-action shotgun (existing message type)
PUMP_SHOTGUN = {
    "prototype_parent": "RANGED_WEAPON_BASE", 
    "key": "PAM Defender shotgun",
    "aliases": ["shotgun", "pump", "defender", "pam shotgun", "scattergun"],
    "desc": "A Pioneer Arms Manufacturing Defender pump-action shotgun in 12-gauge - found in homesteads, outposts, and frontier settlements galaxy-wide. The action is smooth and forgiving, designed to cycle even with cheap ammunition or light hand loads. The barrel is chrome-lined and the receiver is a single piece of investment-cast steel that could probably survive re-entry. Wood furniture shows honest wear, and the corn-cob forend fits hands in work gloves as easily as bare skin. An extended magazine tube holds seven shells, and the distinctive *chk-chk* of the pump is a sound that says 'property defended' in any language. Whether it's hostile wildlife, claim jumpers, or something worse in the dark, the Defender has protected three generations of colonists.",
    "damage": 20,
    "attrs": [
        ("weapon_type", "pump-action_shotgun"),
        ("damage_type", "bullet"),  # Medical system injury type
        ("is_ranged", True),
        ("uses_ammo", True),
        ("ammo_type", "12gauge"),
        ("ammo_capacity", 7),
        ("current_ammo", 7),
    ]
}

# Break-action shotgun (existing message type)
BREAK_SHOTGUN = {
    "prototype_parent": "RANGED_WEAPON_BASE",
    "key": "PAM Reaper shotgun", 
    "aliases": ["reaper", "double-barrel", "coach gun", "pam reaper", "break shotgun", "boomstick"],
    "desc": "A Pioneer Arms Manufacturing Reaper - the double-barrel 12-gauge that earned its name in blood across a hundred frontier wars. The design is over four centuries old and hasn't needed improvement since. Two barrels, two triggers, two shells - everything else is just luxury. The barrels are chromed and the action is precisely fitted, breaking open with a satisfying mechanical *clack* and ejecting spent shells with authority. Checkered walnut stock and forend show the patina of hard use and generational transfer. At close range, both barrels fired simultaneously will stop anything that walks, crawls, or flies - and the Reaper has proven it against claim jumpers, pirates, hostile fauna, and things with too many limbs to count. When colonists need a last line of defense, they reach for the Reaper. The name isn't marketing - it's a reputation earned in the dirt.",
    "damage": 25,
    "attrs": [
        ("weapon_type", "break-action_shotgun"),
        ("damage_type", "bullet"),  # Medical system injury type
        ("is_ranged", True),
        ("uses_ammo", True),
        ("ammo_type", "12gauge"),
        ("ammo_capacity", 2),
        ("current_ammo", 2),
    ]
}

# Bolt-action rifle (existing message type)
BOLT_RIFLE = {
    "prototype_parent": "RANGED_WEAPON_BASE",
    "key": "PAM Pathfinder rifle",
    "aliases": ["rifle", "pathfinder", "pam rifle", "bolt-action", "bolt rifle"],
    "desc": "A Pioneer Arms Manufacturing Pathfinder bolt-action rifle chambered in 7.62x51mm - the working rifle of choice for frontier scouts, hunters, and anyone who needs to reach out past the fence line. The action is a controlled-feed design that's smooth as glass and utterly reliable. The barrel is free-floated and cold-hammer-forged, capable of sub-MOA accuracy with quality ammunition. The synthetic stock is textured for grip and impervious to weather, while the steel receiver wears a matte finish that won't glare in harsh sunlight. A detachable box magazine holds five rounds, and the trigger adjusts from two to four pounds. Whether you're harvesting local fauna, defending livestock from predators, or putting down threats at distance, the Pathfinder delivers first-shot hits when it counts.",
    "damage": 22,
    "attrs": [
        ("weapon_type", "bolt-action_rifle"),
        ("damage_type", "bullet"),  # Medical system injury type
        ("is_ranged", True),
        ("uses_ammo", True),
        ("ammo_type", "762nato"),
        ("ammo_capacity", 5),
        ("current_ammo", 5),
    ]
}

# Anti-material rifle (existing message type)  
ANTI_MATERIAL_RIFLE = {
    "prototype_parent": "RANGED_WEAPON_BASE",
    "key": "HDG M82A3 anti-material rifle",
    "aliases": ["AMR", "M82A3", "anti-material rifle", "m82a3", "hdg amr"],
    "desc": "A Helios Defense Group M82A3 anti-material rifle chambered in 12.7x99mm. This massive weapon features a fluted bull barrel with an integrated muzzle brake that redirects gases upward to reduce felt recoil. The upper receiver is machined from a single billet of aircraft-grade aluminum, with a full-length Picatinny rail mounting a variable-power optic. A heavy-duty bipod clamps to the reinforced front rail section, and the buttstock incorporates a hydraulic recoil buffer and adjustable cheek rest. The entire system weighs nearly thirty pounds unloaded, and the carrying handle suggests HDG knows this weapon spends more time being transported than fired. Built to eliminate light vehicles, hardened positions, and targets at extreme range.",
    "damage": 35,
    "attrs": [
        ("weapon_type", "anti-material_rifle"),
        ("damage_type", "bullet"),  # Medical system injury type
        ("hands_required", 2),  # Requires bipod/support
        ("is_ranged", True),
        ("uses_ammo", True),
        ("ammo_type", "50bmg"),
        ("ammo_capacity", 10),
        ("current_ammo", 10),
    ]
}

# Assault rifle (if you have assault rifle messages)
ASSAULT_RIFLE = {
    "prototype_parent": "RANGED_WEAPON_BASE",
    "key": "HDG M4RA pulse rifle", 
    "aliases": ["rifle", "M4RA", "pulse rifle", "pulse", "m4ra", "hdg"],
    "desc": "A Helios Defense Group M4RA pulse rifle chambered in 10mm caseless. The weapon's distinctive profile features a long barrel shroud with integrated electronic ammunition counter displaying in crisp amber numerals. The receiver is matte black composite with aggressive texturing, while the skeletal stock telescopes for compact carry. A charging handle protrudes from the right side of the upper receiver, and the trigger guard has been enlarged for gloved operation. The foregrip is ribbed polymer with heat-dissipation vents running along its length. Rail systems run along the top and sides of the handguard, currently mounting only iron sights but capable of accepting various optics and accessories. The whole assembly has the brutal, utilitarian aesthetic of military hardware designed for reliability under the worst possible conditions.",
    "damage": 15,
    "attrs": [
        ("weapon_type", "assault_rifle"),  # May need to create message file
        ("damage_type", "bullet"),  # Medical system injury type
        ("is_ranged", True),
        ("uses_ammo", True),
        ("ammo_type", "556nato"),
        ("ammo_capacity", 30),
        ("current_ammo", 30),
    ]
}

# SMG/Submachine gun
SMG = {
    "prototype_parent": "RANGED_WEAPON_BASE",
    "key": "HDG VP9 submachine gun",
    "aliases": ["SMG", "VP9", "vp9", "hdg smg", "submachine gun", "machine pistol"],
    "desc": "A Helios Defense Group VP9 submachine gun in 10mm caseless - the same ammunition as the M4RA rifle, allowing for simplified logistics in the field. The weapon is built around a compact bullpup design that keeps overall length minimal while maintaining a full-length barrel for accuracy. The polymer chassis is reinforced with internal steel rails, and the top-mounted charging handle can be swapped for left or right-hand operation. A folding vertical foregrip provides control during full-auto bursts, while the collapsible wire stock locks into three positions. The fire selector offers semi-auto, three-round burst, and full-auto modes. Compact, reliable, and sharing ammunition with half of HDG's product line - the VP9 excels in close-quarters engagements.",
    "damage": 10,
    "attrs": [
        ("weapon_type", "smg"),  # May need to create message file
        ("damage_type", "bullet"),  # Medical system injury type
        ("hands_required", 1),  # Can be fired one-handed
        ("is_ranged", True),
        ("uses_ammo", True),
        ("ammo_type", "9mm"),
        ("ammo_capacity", 30),
        ("current_ammo", 30),
    ]
}

# =============================================================================
# UTILITY OBJECT PROTOTYPES (for non-combat throwing)
# =============================================================================

# Keys for testing utility throws
KEYRING = {
    "key": "keyring",
    "aliases": ["keys", "ring"],
    "desc": "A ring of various keys. Useful for testing throwing mechanics.",
    "typeclass": "typeclasses.objects.Object",
}

# Rock for testing
ROCK = {
    "key": "rock",
    "aliases": ["stone"],
    "desc": "A smooth throwing rock. Perfect for testing directional throws.",
    "typeclass": "typeclasses.objects.Object",
}

# Bottle for testing
BOTTLE = {
    "key": "bottle",
    "aliases": ["glass bottle"],
    "desc": "An empty glass bottle. Makes a satisfying crash when thrown.",
    "typeclass": "typeclasses.objects.Object",
}

# =============================================================================
# GRAFFITI SYSTEM PROTOTYPES
# =============================================================================

# Base spray paint can
SPRAYPAINT_CAN = {
    "prototype_key": "spraypaint_can",
    "key": "can of",
    "aliases": ["can", "paint", "spray", "spraycan", "spraypaint"],
    "typeclass": "typeclasses.items.SprayCanItem", 
    "desc": "A can of spraypaint with a red nozzle. It feels heavy with paint.",
    "attrs": [
        ("aerosol_level", 256),
        ("max_aerosol", 256),
        ("current_color", "red"),
        ("aerosol_contents", "spraypaint"),
        ("damage", 2),
        ("weapon_type", "spraycan"),
        ("damage_type", "burn"),  # Medical system injury type - chemical burn
        ("hands_required", 1)
    ],
    "tags": [
        ("graffiti", "type"),
        ("spray_can", "category"),
        ("item", "general")
    ]
}

# Solvent can for cleaning graffiti
SOLVENT_CAN = {
    "prototype_key": "solvent_can",
    "key": "can of",
    "aliases": ["solvent", "cleaner", "cleaning_can", "can"],
    "typeclass": "typeclasses.items.SolventCanItem",
    "desc": "A can of solvent for cleaning graffiti. It feels heavy with solvent.", 
    "attrs": [
        ("aerosol_level", 256),
        ("max_aerosol", 256),
        ("aerosol_contents", "solvent"),
        ("damage", 2),
        ("weapon_type", "spraycan"), 
        ("damage_type", "burn"),  # Medical system injury type - chemical burn
        ("hands_required", 1)
    ],
    "tags": [
        ("graffiti", "type"),
        ("solvent_can", "category"),
        ("item", "general")
    ]
}

# =============================================================================
# CLOTHING SYSTEM PROTOTYPES
# =============================================================================
"""
Clothing System Implementation Notes:

Phase 1 & 2 COMPLETE: Core infrastructure with dynamic styling and appearance integration
- Attribute-based clothing detection (coverage, layer, worn_desc)
- Multi-property styling system (adjustable + closure combinations)
- Coverage-based visibility masking of longdesc locations
- Inventory integration showing style states

LAYERING SYSTEM:
Layer 0: Direct skin contact (underwear, thin socks)
Layer 1: Base clothing (t-shirts, tactical undergarments)
Layer 2: Regular clothing (jeans, hoodies, regular shirts)
Layer 3: Footwear (boots, shoes - doesn't conflict with pants)
Layer 4: Light armor (plate carriers, kevlar vests)
Layer 5: Heavy armor (future: full plate, power armor)
Layer 6: Outer layers (future: coats, cloaks, ponchos)

FUTURE EXPANSION POSSIBILITIES:
- Phase 3: Advanced layer conflict resolution, staff targeting commands
- Material Physics: Durability, weather resistance, cleaning requirements
- Fashion Systems: NPC reactions based on clothing combinations/appropriateness
- Condition Tracking: Wear states, stains, damage affecting appearance/stats
- Social Mechanics: Dress codes, cultural clothing significance
- Seasonal Systems: Temperature comfort, weather protection
- Economic Integration: Clothing value, fashion trends affecting prices
- Magical Clothing: Enchantments, transformation items, stat bonuses

Current prototypes are proof-of-concept focusing on core mechanics.
"""

# Epic coder socks with dynamic styling capabilities
CODER_SOCKS = {
    "prototype_key": "CODER_SOCKS",
    "key": "rainbow coding socks",
    "aliases": ["socks", "coding socks", "rainbow socks"],
    "typeclass": "typeclasses.items.Item",
    "desc": "These magnificent thigh-high socks feature a gradient rainbow pattern with tiny pixelated hearts and coffee cups. The fabric shimmers with an almost magical quality, and they seem to pulse gently with RGB lighting effects. Every serious coder knows these provide +10 to programming ability.",
    "attrs": [
        # Basic clothing attributes
        ("coverage", ["left_foot", "right_foot", "left_shin", "right_shin", "left_thigh", "right_thigh"]),
        ("worn_desc", "Electric {color}rainbow|n coding socks stretching up {their} thighs, {their} prismatic patterns pulsing with soft bioluminescent threads that seem to respond to neural activity"),
        ("layer", 0),  # Direct skin contact layer (underwear, thin socks)
        ("color", "bright_magenta"),
        ("material", "synthetic"),
        ("weight", 0.2),  # Very light
        
        # Style configuration for incredible transformation power
        ("style_configs", {
            "adjustable": {
                "normal": {
                    "coverage_mod": [],
                    "desc_mod": ""  # Use base worn_desc
                },
                "rolled": {
                    "coverage_mod": ["-left_thigh", "-right_thigh"],  # Rolled down to knee-high
                    "desc_mod": "Electric {color}rainbow|n coding socks bunched down around {their} knees, {their} compressed RGB fibers creating intense aurora-like cascades that paint the calves in shifting spectral light"
                }
            },
            "closure": {
                "zipped": {
                    "coverage_mod": [],
                    "desc_mod": "Electric {color}rainbow|n coding socks stretching up {their} thighs, {their} LED matrices blazing at maximum intensity like fiber-optic constellations mapping the topology of pure computational ecstasy"
                },
                "unzipped": {
                    "coverage_mod": [],
                    "desc_mod": "Electric {color}rainbow|n coding socks stretching up {their} thighs, {their} bioluminescent patterns dimmed to a gentle ambient pulse that whispers of late-night debugging sessions and caffeine dreams"
                }
            }
        }),
        
        # Initial style state - full power mode!
        ("style_properties", {
            "adjustable": "normal",  # Full thigh-high
            "closure": "zipped"      # LEDs on full blast
        })
        
        # Future: combat stats for style-based intimidation, coder stat bonuses
        # Future tags: material properties, rarity systems, specialty gear recognition
    ],
    # Future: tags for NPC coder recognition, RGB lighting systems, legendary item mechanics  
    # "tags": [("clothing", "type"), ("socks", "category"), ("coder_gear", "specialty")]
}

# Stylish developer hoodie with hood functionality
DEV_HOODIE = {
    "prototype_key": "DEV_HOODIE", 
    "key": "black developer hoodie",
    "aliases": ["hoodie", "dev hoodie", "black hoodie"],
    "typeclass": "typeclasses.items.Item",
    "desc": "A jet-black hoodie with 'rm -rf /' printed in small, ominous green text on the chest. The fabric is impossibly soft, and the hood seems designed to cast perfect dramatic shadows. Tiny LED threads are woven throughout, creating a subtle matrix-like pattern when activated.",
    "attrs": [
        # Clothing attributes
        ("coverage", ["chest", "back", "abdomen", "left_arm", "right_arm"]),
        ("worn_desc", "A menacing {color}black|n developer hoodie draped loose and open, the cryptic green 'rm -rf /' text glowing with malevolent promise while embedded LED threads create subtle data-stream patterns across {their} fabric"),
        ("layer", 2),  # Regular clothing layer
        ("color", "black"),
        ("material", "cotton"),
        ("weight", 1.8),  # Moderate weight
        
        # Advanced styling - hood and LED modes
        ("style_configs", {
            "adjustable": {
                "normal": {
                    "coverage_mod": [],
                    "desc_mod": ""
                },
                "rolled": {
                    "coverage_mod": ["+head"],  # Hood up adds head coverage
                    "desc_mod": "A menacing {color}black|n developer hoodie with the hood pulled up like digital shadow incarnate, casting {their} face into mysterious darkness while green command-line text pulses ominously across {their} chest like a hacker's heartbeat"
                }
            },
            "closure": {
                "zipped": {
                    "coverage_mod": [],
                    "desc_mod": "A menacing {color}black|n developer hoodie zipped tight against the digital cold, LED matrix patterns cascading across the fabric like endless streams of compiled consciousness while 'rm -rf /' glows with quiet menace"
                },
                "unzipped": {
                    "coverage_mod": ["-chest"],  # Unzipped shows what's underneath
                    "desc_mod": "A menacing {color}black|n developer hoodie hanging open in calculated carelessness, revealing whatever lies beneath while {their} forbidden command-line incantation pulses with green malevolence against the darkness"
                }
            }
        }),
        
        ("style_properties", {
            "adjustable": "normal",    # Hood down initially  
            "closure": "unzipped"      # Casual mode
        })
        
        # Future: intimidation mechanics, focus bonuses, developer culture systems
        # Future tags: LED features, professional gear, meeting avoidance mechanics
    ],
    # Future: tags for developer NPC interactions, LED systems, professional contexts
    # "tags": [("clothing", "type"), ("hoodie", "category"), ("developer_gear", "specialty")]
}

# Classic blue jeans with functional styling
BLUE_JEANS = {
    "prototype_key": "BLUE_JEANS",
    "key": "blue jeans",
    "aliases": ["jeans", "pants", "denim"],
    "typeclass": "typeclasses.items.Item",
    "desc": "A classic pair of medium-wash blue jeans with a comfortable fit. The denim is soft from years of wear, with subtle fading at the knees and pockets. Five-pocket styling with sturdy copper rivets at stress points.",
    
    "attrs": [
        ("category", "clothing"),
        ("worn_desc", "Battle-tested {color}denim|n jeans that cling to {their} form with urban authority, {their} faded indigo surface scarred by countless encounters with concrete and circumstance"),
        ("coverage", ["groin", "left_thigh", "right_thigh", "left_shin", "right_shin"]),
        ("layer", 2),  # Regular clothing layer
        ("color", "blue"),
        ("material", "denim"),
        ("weight", 1.5),  # Moderate weight
        
        ("style_configs", {
            "adjustable": {
                "normal": {
                    "coverage_mod": [],
                    "desc_mod": ""  # Use base worn_desc
                },
                "rolled": {
                    "coverage_mod": ["-left_shin", "-right_shin"],
                    "desc_mod": "Battle-tested {color}denim|n jeans with cuffs deliberately rolled up to mid-calf in street-smart defiance, exposing {their} scarred ankles and the promise of swift movement when the situation demands it"
                }
            },
            "closure": {
                "zipped": {
                    "coverage_mod": [],
                    "desc_mod": ""  # Use base worn_desc
                },
                "unzipped": {
                    "coverage_mod": ["-groin"],
                    "desc_mod": "Battle-tested {color}denim|n jeans hanging loose with dangerous nonchalance, {their} undone fly creating a calculated statement of rebellion against the oppressive tyranny of proper dress codes"
                }
            }
        }),
        
        ("style_properties", {
            "adjustable": "normal",
            "closure": "zipped"
        })
        
        # Future: durability/wear system, comfort affects stats, style bonuses
        # Future tags: material properties, fashion categories, condition tracking
    ],
    # Future: tags for material physics, fashion systems, NPC reactions
    # "tags": [("clothing", "type"), ("pants", "category"), ("denim", "material")]
}

# Simple cotton t-shirt 
COTTON_TSHIRT = {
    "prototype_key": "COTTON_TSHIRT",
    "key": "white cotton t-shirt",
    "aliases": ["shirt", "t-shirt", "tshirt", "tee"],
    "typeclass": "typeclasses.items.Item", 
    "desc": "A simple white cotton t-shirt with a classic crew neck. The fabric is soft and breathable, perfect for everyday wear. The shoulders and hem show the clean lines of quality construction.",
    
    "attrs": [
        ("category", "clothing"),
        ("worn_desc", "A deceptively simple {color}white|n cotton t-shirt that seems to absorb and reflect the ambient light of {their} urban environment, its clean lines and perfect fit suggesting either careful maintenance or recent acquisition"),
        ("coverage", ["chest", "back", "abdomen"]),
        ("layer", 1),  # Base clothing layer (worn under hoodies/jackets)
        ("color", "white"),
        ("material", "cotton"),
        ("weight", 0.4),  # Light weight
        
        ("style_configs", {
            "adjustable": {
                "normal": {
                    "coverage_mod": [],
                    "desc_mod": ""  # Use base worn_desc
                },
                "rolled": {
                    "coverage_mod": ["-abdomen"],
                    "desc_mod": "A deceptively simple {color}white|n cotton t-shirt deliberately rolled up at the hem to expose {their} midriff, the casual gesture somehow managing to convey both vulnerability and confident defiance of conventional modesty"
                }
            }
        }),
        
        ("style_properties", {
            "adjustable": "normal"
        })
        
        # Future: fabric physics, stain resistance, NPC fashion reactions  
        # Future tags: material breathability, wash cycles, social contexts
    ],
    # Future: tags for clothing care systems, fashion mechanics, NPC interactions
    # "tags": [("clothing", "type"), ("shirt", "category"), ("cotton", "material")]
}

# Tactical leather combat boots with lacing
COMBAT_BOOTS = {
    "prototype_key": "COMBAT_BOOTS",
    "key": "black leather combat boots",
    "aliases": ["boots", "combat boots", "leather boots"],
    "typeclass": "typeclasses.items.Item",
    "desc": "Heavy-duty black leather combat boots with steel-reinforced toes and deep tread soles. The leather is scuffed from use but well-maintained, with military-style speed lacing running up to mid-calf. Perfect for urban warfare or intimidating accountants.",
    
    "attrs": [
        ("category", "clothing"),
        ("worn_desc", "Imposing {color}black leather|n combat boots laced with military precision, {their} steel-reinforced toes and deep-tread soles speaking of {their} owner's serious intent while weathered leather tells stories of urban warfare and late-night foot chases"),
        ("coverage", ["left_foot", "right_foot", "left_shin", "right_shin"]),
        ("layer", 3),  # Footwear layer (doesn't conflict with pants)
        ("color", "black"),
        ("material", "leather"),
        
        ("style_configs", {
            "closure": {
                "zipped": {
                    "coverage_mod": [],
                    "desc_mod": ""  # Use base worn_desc (laced tight)
                },
                "unzipped": {
                    "coverage_mod": ["-left_shin", "-right_shin"],
                    "desc_mod": "Imposing {color}black leather|n combat boots with speed-laces hanging in deliberate disarray, {their} unlaced tongues flopping open to reveal glimpses of tactical readiness beneath the facade of casual indifference"
                }
            }
        }),
        
        ("style_properties", {
            "closure": "zipped"  # Laced tight by default
        })
        
        # Future: armor rating, movement speed modifiers, intimidation bonuses
        # Future tags: leather durability, tactical gear, weather resistance
    ],
    # Future: tags for combat systems, material physics, professional contexts  
    # "tags": [("clothing", "type"), ("boots", "category"), ("leather", "material")]
}


# =============================================================================
# ARMOR PROTOTYPES (CLOTHING WITH ARMOR ATTRIBUTES)
# =============================================================================

# =============================================================================
# TACTICAL UNIFORM BASE LAYERS (Light Protection)
# =============================================================================

# Tactical Jumpsuit - Base layer with minimal protection
TACTICAL_JUMPSUIT = {
    "key": "tactical jumpsuit",
    "aliases": ["jumpsuit", "coveralls", "tactical suit"],
    "typeclass": "typeclasses.items.Item",
    "desc": "A form-fitting tactical jumpsuit made from reinforced synthetic weave. Provides minimal protection while maintaining maximum mobility and comfort.",
    "attrs": [
        # Clothing attributes
        ("coverage", ["chest", "back", "abdomen", "groin", "left_arm", "right_arm", "left_thigh", "right_thigh", "left_shin", "right_shin", "left_foot", "right_foot"]),
        ("worn_desc", "A sleek {color}black|n tactical jumpsuit that hugs their form like a second skin, its reinforced synthetic weave providing minimal protection while prioritizing mobility and tactical flexibility"),
        ("layer", 1),  # Base clothing layer (worn under armor)
        ("color", "black"),
        ("material", "synthetic"),
        ("weight", 1.8),  # Lightweight
        
        # Minimal armor
        ("armor_rating", 1),
        ("armor_type", "synthetic"),
        ("armor_durability", 20),
        ("max_armor_durability", 20),
        ("base_armor_rating", 1),
        
        # Sticky grenade properties (synthetic fabric - no metal)
        ("metal_level", 0),      # No metal content
        ("magnetic_level", 0),   # No magnetic response
    ],
}

# Tactical Pants - Alternative to jumpsuit
TACTICAL_PANTS = {
    "key": "tactical pants",
    "aliases": ["pants", "tactical trousers", "combat pants"],
    "typeclass": "typeclasses.items.Item",
    "desc": "Heavy-duty tactical pants with reinforced knees and multiple cargo pockets. Made from ripstop fabric with minimal ballistic protection.",
    "attrs": [
        # Clothing attributes
        ("coverage", ["groin", "left_thigh", "right_thigh", "left_shin", "right_shin"]),
        ("worn_desc", "Durable {color}black|n tactical pants with reinforced knees and cargo pockets, their ripstop fabric providing minimal protection while maintaining tactical functionality"),
        ("layer", 1),  # Base clothing layer (worn under armor)
        ("color", "black"),
        ("material", "synthetic"),
        ("weight", 1.2),
        
        # Minimal armor
        ("armor_rating", 1),
        ("armor_type", "synthetic"),
        ("armor_durability", 20),
        ("max_armor_durability", 20),
        ("base_armor_rating", 1),
        
        # Sticky grenade properties (synthetic fabric - no metal)
        ("metal_level", 0),      # No metal content
        ("magnetic_level", 0),   # No magnetic response
    ],
}

# Tactical Shirt - Upper body base layer
TACTICAL_SHIRT = {
    "key": "tactical shirt",
    "aliases": ["shirt", "tactical tee", "combat shirt"],
    "typeclass": "typeclasses.items.Item",
    "desc": "A tactical shirt with moisture-wicking fabric and reinforced shoulders. Designed to be worn under armor systems.",
    "attrs": [
        # Clothing attributes
        ("coverage", ["chest", "back", "abdomen", "left_arm", "right_arm"]),
        ("worn_desc", "A practical {color}black|n tactical shirt with moisture-wicking fabric, its reinforced shoulders and minimal protection designed to serve as a foundation for armor systems"),
        ("layer", 1),  # Base clothing layer (worn under armor)
        ("color", "black"),
        ("material", "synthetic"),
        ("weight", 0.8),
        
        # Minimal armor
        ("armor_rating", 1),
        ("armor_type", "synthetic"),
        ("armor_durability", 20),
        ("max_armor_durability", 20),
        ("base_armor_rating", 1),
        
        # Sticky grenade properties (synthetic fabric - no metal)
        ("metal_level", 0),      # No metal content
        ("magnetic_level", 0),   # No magnetic response
    ],
}

# =============================================================================
# MODULAR PLATE CARRIER SYSTEM
# =============================================================================

# Basic Plate Carrier - Modular platform
PLATE_CARRIER = {
    "key": "plate carrier",
    "aliases": ["carrier", "vest", "tactical vest"],
    "typeclass": "typeclasses.items.Item",
    "desc": "A modular plate carrier system with front and back plate pockets, side plate slots, and tactical webbing. Designed to accept ballistic plates for customizable protection levels.",
    "attrs": [
        # Clothing attributes
        ("coverage", ["chest", "back", "abdomen"]),
        ("worn_desc", "A professional {color}tan|n plate carrier with tactical webbing and modular plate pockets, its adjustable straps and MOLLE system creating a foundation for serious ballistic protection"),
        ("layer", 4),  # Light armor layer
        ("color", "tan"),
        ("material", "nylon"),
        ("weight", 2.5),  # Just the carrier itself
        
        # Base protection (carrier only)
        ("armor_rating", 2),        # Minimal protection without plates
        ("armor_type", "synthetic"), # Basic synthetic protection
        ("armor_durability", 40),
        ("max_armor_durability", 40),
        ("base_armor_rating", 2),
        
        # Plate carrier system
        ("is_plate_carrier", True),
        ("plate_slots", ["front", "back", "left_side", "right_side"]),
        ("installed_plates", {}),   # Empty initially
        ("plate_slot_coverage", {
            "front": ["chest"],
            "back": ["back"],
            "left_side": ["abdomen"],
            "right_side": ["abdomen"]
        }),
        
        # Style system for tactical adjustments
        ("style_configs", {
            "adjustable": {
                "normal": {"coverage_mod": [], "desc_mod": ""},
                "rolled": {"coverage_mod": ["-abdomen"], "desc_mod": "A professional {color}tan|n plate carrier with the lower section rolled up for improved mobility, its tactical webbing still providing modular attachment points"}
            }
        }),
        ("style_properties", {"adjustable": "normal"}),
        
        # Sticky grenade properties (nylon carrier - minimal metal from buckles/clips)
        ("metal_level", 1),      # Minimal metal (buckles, clips)
        ("magnetic_level", 1),   # Minimal magnetic (some steel hardware)
    ],
}

# =============================================================================
# ARMOR PLATES (For Plate Carriers)
# =============================================================================

# =============================================================================
# ARMOR PLATES (For Plate Carriers)
# Universal fit - trade protection for weight/durability
# =============================================================================

# Lightweight Plate - Mobility focused
LIGHTWEIGHT_PLATE = {
    "key": "lightweight plate",
    "aliases": ["light plate", "mobility plate", "composite plate"],
    "typeclass": "typeclasses.items.Item",
    "desc": "A lightweight composite armor plate prioritizing mobility. Sacrifices some protection for reduced weight, ideal for fast response scenarios.",
    "attrs": [
        # Not worn directly - installed in carriers
        ("coverage", []),
        ("layer", 0),  # Not a clothing layer
        ("weight", 1.8),  # Lightest option
        ("material", "composite"),
        
        # Plate properties
        ("is_armor_plate", True),
        ("plate_class", "lightweight"),  # Instead of size
        ("armor_rating", 5),        # Lower protection
        ("armor_type", "composite"),
        ("armor_durability", 100),  # Lower durability
        ("max_armor_durability", 100),
        ("base_armor_rating", 5),
        
        # Sticky grenade properties (composite - some metal, non-magnetic)
        ("metal_level", 4),      # Some metal content (aluminum backing)
        ("magnetic_level", 0),   # Non-magnetic (aluminum/composite)
    ],
}

# Standard Plate - Balanced protection
STANDARD_PLATE = {
    "key": "standard plate",
    "aliases": ["plate", "ballistic plate", "armor plate", "ceramic plate"],
    "typeclass": "typeclasses.items.Item",
    "desc": "A standard ballistic plate made from advanced ceramic composite. Offers excellent protection against rifle rounds while maintaining reasonable weight.",
    "attrs": [
        # Not worn directly - installed in carriers
        ("coverage", []),
        ("layer", 0),  # Not a clothing layer
        ("weight", 3.2),  # Balanced weight
        ("material", "ceramic"),
        
        # Plate properties
        ("is_armor_plate", True),
        ("plate_class", "standard"),  # Instead of size
        ("armor_rating", 7),        # Good protection
        ("armor_type", "ceramic"),
        ("armor_durability", 140),
        ("max_armor_durability", 140),
        ("base_armor_rating", 7),
        
        # Sticky grenade properties (ceramic with steel backing)
        ("metal_level", 6),      # Moderate metal (steel backing plate)
        ("magnetic_level", 5),   # Moderate magnetic (steel backing)
    ],
}

# Reinforced Plate - Maximum protection
REINFORCED_PLATE = {
    "key": "reinforced plate",
    "aliases": ["heavy plate", "steel plate", "assault plate"],
    "typeclass": "typeclasses.items.Item",
    "desc": "A heavy reinforced steel ballistic plate offering maximum protection. Significantly heavier than alternatives but nearly indestructible in combat scenarios.",
    "attrs": [
        ("coverage", []),
        ("layer", 0),
        ("weight", 8.5),  # Heaviest option
        ("material", "steel"),
        
        ("is_armor_plate", True),
        ("plate_class", "reinforced"),  # Instead of size
        ("armor_rating", 9),        # Maximum protection
        ("armor_type", "steel"),
        ("armor_durability", 180),  # Highest durability
        ("max_armor_durability", 180),
        ("base_armor_rating", 9),
        
        # Sticky grenade properties (solid steel plate - HIGHLY magnetic)
        ("metal_level", 10),     # Maximum metal content (solid steel)
        ("magnetic_level", 10),  # Maximum magnetic (ferrous steel)
    ],
}

# High-Performance Trauma Plate - Specialist option
CERAMIC_PLATES = {
    "key": "trauma plate",
    "aliases": ["ceramic plate", "trauma insert", "ceramic insert"],
    "typeclass": "typeclasses.items.Item",
    "desc": "An advanced ceramic trauma plate using cutting-edge materials. Extremely effective against high-velocity rounds but brittle - shatters after absorbing significant damage.",
    "attrs": [
        # Not worn directly - installed in carriers
        ("coverage", []),
        ("layer", 0),  # Not a clothing layer
        ("weight", 4.0),  # Heavy ceramic
        ("material", "ceramic"),
        
        # Plate properties
        ("is_armor_plate", True),
        ("plate_class", "trauma"),  # Specialist class
        ("armor_rating", 10),       # Maximum protection
        ("armor_type", "ceramic"),  # Excellent vs bullets, degrades quickly
        ("armor_durability", 50),   # Low durability - shatters after absorbing damage
        ("max_armor_durability", 50),
        ("base_armor_rating", 10),
        
        # Sticky grenade properties (advanced ceramic - minimal magnetic)
        ("metal_level", 3),      # Minimal metal (titanium backing)
        ("magnetic_level", 0),   # Non-magnetic (ceramic/titanium)
    ],
}

# =============================================================================
# LEGACY ARMOR (Updated with Weight)
# =============================================================================

# Tactical Kevlar Vest - Excellent bullet protection
KEVLAR_VEST = {
    "prototype_parent": "MELEE_WEAPON_BASE",  # Base item properties
    "key": "kevlar vest",
    "aliases": ["vest", "body armor", "bulletproof vest"],
    "typeclass": "typeclasses.items.Item",
    "desc": "A lightweight tactical kevlar vest with trauma plates. Designed to stop bullets while maintaining mobility.",
    "attrs": [
        # Clothing attributes
        ("coverage", ["chest", "back", "abdomen"]),
        ("worn_desc", "A professional {color}black|n kevlar vest with trauma plates, its tactical webbing and ballistic panels speaking of serious protection against projectile threats"),
        ("layer", 4),  # Light armor layer
        ("color", "black"),
        ("material", "kevlar"),
        ("weight", 4.5),  # Moderate weight
        
        # Armor attributes
        ("armor_rating", 8),        # High armor rating
        ("armor_type", "kevlar"),   # Excellent vs bullets, poor vs stabs
        ("armor_durability", 160),  # Rating * 20
        ("max_armor_durability", 160),
        ("base_armor_rating", 8),
        
        # Combat stats
        ("deflection_bonus", -0.05),  # Slight penalty to deflection (bulky)
        
        # Sticky grenade properties (kevlar with steel trauma plates)
        ("metal_level", 7),      # High metal (embedded steel plates)
        ("magnetic_level", 6),   # High magnetic (steel trauma plates)
    ],
}

# =============================================================================
# BEE HIVE ARMORED COVERALL - Swarm-Themed Tactical Armor
# =============================================================================

BEE_HIVE_COVERALL = {
    "key": "HIVE-MIND Mark VII coverall",
    "aliases": ["hive coverall", "bee armor", "hive-mind", "swarm suit", "bee suit"],
    "typeclass": "typeclasses.items.Item",
    "desc": (
        "A HIVE-MIND Mark VII tactical coverall that defies conventional armor design philosophy with its revolutionary bio-mimetic approach. "
        "The entire surface is covered in thousands of hexagonal ceramic composite cells arranged in a perfect honeycomb lattice, each cell "
        "independently articulated on microscopic servo-actuators that create a constantly shifting, organic movement across the armor's surface. "
        "The base color is a deep amber-gold that seems to glow from within, overlaid with bold black striping patterns that flow across the torso, "
        "arms, and legs in asymmetric warning coloration that triggers primal recognition responses in observers.\n\n"
        "Embedded bioluminescent fibers pulse gently beneath the hexagonal cells, creating the illusion of thousands of worker bees moving just "
        "beneath the surface—an effect that becomes more pronounced in low light, where the entire suit seems to writhe with insectile life. "
        "The collar area features raised ridges that mimic the segmented thorax of a bee, while the back incorporates subtle wing-like panels "
        "that serve both aesthetic and heat-dissipation purposes.\n\n"
        "Most unsettling are the micro-speakers distributed throughout the suit's surface, which emit a constant low-frequency buzz that can be "
        "felt in the bones more than heard—a psychological warfare tool that triggers instinctive flight responses in those nearby. The manufacturer's "
        "documentation suggests this 'harmonic resonance system' was inspired by defensive bee swarm behavior, creating an auditory territoriality "
        "field that makes opponents unconsciously maintain distance.\n\n"
        "The armor's smart-material construction allows the hexagonal cells to lock rigid on impact, distributing force across the entire lattice "
        "structure like a hive distributing the workload among workers. Each cell can also independently adjust its angle to deflect incoming "
        "projectiles, creating a surface that seems to flow and redirect attacks rather than simply absorb them. The overall effect is of wearing "
        "a living colony—beautiful, alien, and deeply disturbing in its implication that the wearer has merged with the swarm."
    ),
    "attrs": [
        # Clothing attributes - full body coverage like jumpsuit
        ("coverage", ["chest", "back", "abdomen", "groin", "left_arm", "right_arm", "left_thigh", "right_thigh", "left_shin", "right_shin"]),
        ("worn_desc", (
            "A mesmerizing HIVE-MIND Mark VII coverall coating {their} form in thousands of articulating hexagonal amber-and-black cells "
            "that ripple and shift like a living bee colony, the constant low-frequency buzz emanating from its surface making the air "
            "itself seem to vibrate with barely-contained aggression while bioluminescent patterns pulse beneath the honeycomb lattice "
            "like worker bees moving through dark corridors"
        )),
        ("layer", 4),  # Light armor layer (same as plate carrier/kevlar)
        ("color", "amber"),  # Amber-gold primary color
        ("material", "ceramic_composite"),  # Advanced materials
        ("weight", 6.8),  # Heavier than kevlar, lighter than steel plate
        
        # Armor attributes - excellent distributed protection
        ("armor_rating", 7),        # Very good protection (between kevlar and steel)
        ("armor_type", "ceramic"),  # Ceramic composite - excellent vs projectiles
        ("armor_durability", 140),  # Rating * 20
        ("max_armor_durability", 140),
        ("base_armor_rating", 7),
        
        # Combat stats - the hexagonal lattice has interesting properties
        ("deflection_bonus", 0.15),  # +3 to deflection (cells redirect impacts!)
        
        # Sticky grenade properties (ceramic composite with minimal metal framework)
        ("metal_level", 3),      # Low metal (internal framework only)
        ("magnetic_level", 0),   # Non-magnetic (ceramic/titanium construction)
        
        # Style system for bee armor
        ("style_configs", {
            "adjustable": {
                "normal": {
                    "coverage_mod": [],
                    "desc_mod": ""  # Use base worn_desc
                },
                "rolled": {
                    "coverage_mod": ["-left_shin", "-right_shin"],
                    "desc_mod": (
                        "A mesmerizing HIVE-MIND Mark VII coverall with lower sections rolled up to expose {their} calves, "
                        "the exposed hexagonal cells at the roll line still pulsing with bioluminescent patterns as if "
                        "the hive extends beyond what's visible, worker bees still toiling in phantom corridors"
                    )
                }
            },
            "closure": {
                "zipped": {
                    "coverage_mod": [],
                    "desc_mod": ""  # Use base worn_desc - sealed and buzzing
                },
                "unzipped": {
                    "coverage_mod": ["-chest", "-abdomen"],
                    "desc_mod": (
                        "A mesmerizing HIVE-MIND Mark VII coverall hanging partially open to reveal {their} torso beneath, "
                        "the separated hexagonal cells along the zipper line reorganizing themselves in real-time like "
                        "a hive adapting to structural damage, their golden bioluminescence dimmed but still pulsing "
                        "with patient, insectile purpose"
                    )
                }
            }
        }),
        
        ("style_properties", {
            "adjustable": "normal",
            "closure": "zipped"  # Fully sealed for maximum swarm effect
        })
    ],
}

# Steel Plate Armor - Medieval style, excellent all-around protection
PLATE_MAIL = {
    "prototype_parent": "MELEE_WEAPON_BASE",
    "key": "plate mail",
    "aliases": ["steel plate mail", "steel plate armor", "plate armor", "steel armor"],
    "typeclass": "typeclasses.items.Item", 
    "desc": "Heavy steel plate armor forged in overlapping segments. Provides excellent protection but restricts movement significantly.",
    "attrs": [
        # Clothing attributes
        ("coverage", ["chest", "back", "abdomen", "left_arm", "right_arm"]),
        ("worn_desc", "Imposing {color}steel|n plate armor that encases their torso and arms in overlapping metal segments, each piece precisely fitted and articulated for maximum protection while maintaining combat mobility"),
        ("layer", 3),
        ("color", "bright_white"),  # Polished steel
        ("material", "steel"),
        ("weight", 25.0),  # Very heavy
        
        # Armor attributes
        ("armor_rating", 10),       # Maximum armor rating
        ("armor_type", "steel"),    # Excellent vs everything except fire/chemicals
        ("armor_durability", 200),  # Rating * 20
        ("max_armor_durability", 200),
        ("base_armor_rating", 10),
        
        # Combat penalties
        ("deflection_bonus", -0.15),  # Significant deflection penalty (very bulky)
        
        # Sticky grenade properties (solid steel plate armor - MAXIMUM)
        ("metal_level", 10),     # Maximum metal (solid steel plates)
        ("magnetic_level", 10),  # Maximum magnetic (ferrous steel)
    ],
}

# Leather Jacket - Light armor, good vs cuts
ARMORED_LEATHER_JACKET = {
    "prototype_parent": "MELEE_WEAPON_BASE",
    "key": "armored leather jacket",
    "aliases": ["jacket", "leather armor", "biker jacket"],
    "typeclass": "typeclasses.items.Item",
    "desc": "A heavy leather jacket reinforced with steel studs and padding. Provides moderate protection while maintaining style.",
    "attrs": [
        # Clothing attributes  
        ("coverage", ["chest", "back", "abdomen", "left_arm", "right_arm"]),
        ("worn_desc", "A reinforced {color}black leather|n jacket studded with steel reinforcements, its thick hide and metal accents providing street-smart protection without sacrificing the rebellious aesthetic of urban warfare"),
        ("layer", 2),
        ("color", "black"),
        ("material", "leather"),
        ("weight", 3.2),  # Moderate weight
        
        # Style system for leather jacket
        ("style_configs", {
            "closure": {
                "zipped": {
                    "coverage_mod": [],
                    "desc_mod": "A reinforced {color}black leather|n jacket zipped tight and studded with steel reinforcements, its thick hide creating a defensive shell around their torso"
                },
                "unzipped": {
                    "coverage_mod": ["-chest", "-abdomen"],
                    "desc_mod": "A reinforced {color}black leather|n jacket hanging open to reveal whatever lies beneath, steel studs and thick hide still providing partial protection to their back and arms"
                }
            }
        }),
        ("style_properties", {"closure": "zipped"}),
        
        # Armor attributes
        ("armor_rating", 5),        # Moderate armor rating
        ("armor_type", "leather"),  # Good vs cuts, poor vs bullets
        ("armor_durability", 100),  # Rating * 20
        ("max_armor_durability", 100),
        ("base_armor_rating", 5),
        
        # Combat stats
        ("deflection_bonus", 0.05),  # Slight deflection bonus (flexible)
        
        # Sticky grenade properties (leather with decorative studs)
        ("metal_level", 2),      # Minimal metal (some decorative studs)
        ("magnetic_level", 1),   # Minimal magnetic (small steel studs)
    ],
}

# Combat Helmet - Head protection (skull/crown only, face exposed)
COMBAT_HELMET = {
    "prototype_parent": "MELEE_WEAPON_BASE",
    "key": "combat helmet",
    "aliases": ["helmet", "tactical helmet"],
    "typeclass": "typeclasses.items.Item",
    "desc": "A military-grade combat helmet with ballistic protection for the skull. The open-face design provides excellent visibility and hearing while protecting the crown and sides of the head.",
    "attrs": [
        # Clothing attributes
        ("coverage", ["head", "left_ear", "right_ear"]),  # Protects skull and ears, but face/eyes/jaw exposed
        ("worn_desc", "A menacing {color}matte black|n tactical helmet with ballistic protection, its angular design and integrated electronics creating an intimidating visage of military precision"),
        ("layer", 2),
        ("color", "black"),
        ("material", "kevlar"),
        ("weight", 1.8),  # Light weight
        
        # Armor attributes
        ("armor_rating", 7),        # High head protection
        ("armor_type", "kevlar"),   # Good vs bullets
        ("armor_durability", 20),   # Moderate durability
        ("max_armor_durability", 20),
        ("base_armor_rating", 7),
        
        # Sticky grenade properties (kevlar with composite shell)
        ("metal_level", 3),      # Low metal (mounting hardware)
        ("magnetic_level", 2),   # Low magnetic (minimal steel clips)
    ],
}

# Ceramic Trauma Plates - Insert armor for vests
CERAMIC_PLATES = {
    "key": "ceramic trauma plates",
    "aliases": ["plates", "trauma plates", "ceramic insert", "ceramic plate"],
    "typeclass": "typeclasses.items.Item",
    "desc": "Advanced ceramic trauma plates designed to be inserted into tactical vests. Extremely effective against high-velocity rounds but brittle.",
    "attrs": [
        # Not worn directly - installed in carriers
        ("coverage", []),
        ("layer", 0),  # Not a clothing layer
        ("weight", 4.0),  # Heavy ceramic
        ("material", "ceramic"),
        
        # Plate properties
        ("is_armor_plate", True),
        ("plate_size", "medium"),
        ("armor_rating", 10),       # Maximum protection
        ("armor_type", "ceramic"),  # Excellent vs bullets, degrades quickly
        ("armor_durability", 50),   # Low durability - shatters after absorbing damage
        ("max_armor_durability", 50),
        ("base_armor_rating", 10),
    ],
}

# =============================================================================
# TIERED ARMOR SYSTEM - Mix and Match Protection
# =============================================================================
# 5 Tiers: Scrap (1-2), Makeshift (3-4), Standard (5-6), Reinforced (7-8), Military (9-10)
# 5 Slots: Head, Torso, Arms, Legs, Feet
# Spawn individual pieces or full sets (e.g., @spawn SCRAP_ARMOR_SET)
# =============================================================================

# Base armor prototype for spawn permissions
TIERED_ARMOR_BASE = {
    "typeclass": "typeclasses.items.Item",
    "prototype_locks": "spawn:perm(Builder);edit:perm(Admin)",
}

# =============================================================================
# TIER 1: SCRAP ARMOR (Rating 2) - Improvised from junk and scraps
# =============================================================================

SCRAP_HELMET = {
    "prototype_parent": "TIERED_ARMOR_BASE",
    "key": "scrap helmet",
    "aliases": ["scrap head", "junk helmet", "improvised helmet"],
    "desc": "A crude helmet cobbled together from scrap metal and leather scraps. Dented panels are held together with wire and rivets. It's ugly, but it might save your skull.",
    "attrs": [
        ("coverage", ["head"]),
        ("worn_desc", "A battered {color}rust-brown|n scrap helmet held together with wire and rivets, its dented metal panels offering crude but functional protection"),
        ("layer", 3),
        ("color", "rust"),
        ("material", "scrap_metal"),
        ("weight", 1.2),
        ("armor_rating", 2),
        ("armor_type", "steel"),
        ("armor_durability", 40),
        ("max_armor_durability", 40),
        ("base_armor_rating", 2),
        ("armor_tier", "scrap"),
        ("metal_level", 6),
        ("magnetic_level", 5),
    ],
}

SCRAP_VEST = {
    "prototype_parent": "TIERED_ARMOR_BASE",
    "key": "scrap vest",
    "aliases": ["scrap torso", "junk vest", "improvised vest"],
    "desc": "A vest of overlapping scrap metal plates sewn onto a leather backing. The mismatched panels clank together when you move, but they'll stop a knife.",
    "attrs": [
        ("coverage", ["chest", "back", "abdomen"]),
        ("worn_desc", "A clanking {color}rust-brown|n scrap vest made of overlapping metal plates on leather backing, its mismatched panels offering street-level protection"),
        ("layer", 3),
        ("color", "rust"),
        ("material", "scrap_metal"),
        ("weight", 4.5),
        ("armor_rating", 2),
        ("armor_type", "steel"),
        ("armor_durability", 40),
        ("max_armor_durability", 40),
        ("base_armor_rating", 2),
        ("armor_tier", "scrap"),
        ("deflection_bonus", -0.05),
        ("metal_level", 7),
        ("magnetic_level", 6),
    ],
}

SCRAP_BRACERS = {
    "prototype_parent": "TIERED_ARMOR_BASE",
    "key": "scrap bracers",
    "aliases": ["scrap arms", "junk bracers", "improvised bracers"],
    "desc": "Crude arm guards fashioned from scrap metal strips and leather straps. The edges are rough and the fit is poor, but they'll deflect a blade.",
    "attrs": [
        ("coverage", ["left_arm", "right_arm"]),
        ("worn_desc", "Crude {color}rust-brown|n scrap bracers wrapped around {their} forearms, rough metal strips offering basic protection against glancing blows"),
        ("layer", 3),
        ("color", "rust"),
        ("material", "scrap_metal"),
        ("weight", 1.8),
        ("armor_rating", 2),
        ("armor_type", "steel"),
        ("armor_durability", 40),
        ("max_armor_durability", 40),
        ("base_armor_rating", 2),
        ("armor_tier", "scrap"),
        ("metal_level", 5),
        ("magnetic_level", 4),
    ],
}

SCRAP_GREAVES = {
    "prototype_parent": "TIERED_ARMOR_BASE",
    "key": "scrap greaves",
    "aliases": ["scrap legs", "junk greaves", "improvised greaves"],
    "desc": "Leg armor made from salvaged metal sheets strapped to leather padding. The straps are fraying and the metal is dented, but it's better than nothing.",
    "attrs": [
        ("coverage", ["left_thigh", "right_thigh", "left_shin", "right_shin"]),
        ("worn_desc", "Battered {color}rust-brown|n scrap greaves strapped to {their} legs, salvaged metal sheets offering crude protection from knee to thigh"),
        ("layer", 3),
        ("color", "rust"),
        ("material", "scrap_metal"),
        ("weight", 3.2),
        ("armor_rating", 2),
        ("armor_type", "steel"),
        ("armor_durability", 40),
        ("max_armor_durability", 40),
        ("base_armor_rating", 2),
        ("armor_tier", "scrap"),
        ("metal_level", 6),
        ("magnetic_level", 5),
    ],
}

SCRAP_BOOTS = {
    "prototype_parent": "TIERED_ARMOR_BASE",
    "key": "scrap boots",
    "aliases": ["scrap feet", "junk boots", "improvised boots"],
    "desc": "Heavy boots reinforced with scrap metal plates over the toes and ankles. They're clunky and loud, but they'll protect your feet from debris and blows.",
    "attrs": [
        ("coverage", ["left_foot", "right_foot"]),
        ("worn_desc", "Clunky {color}rust-brown|n scrap boots with metal plates protecting toes and ankles, their heavy construction trading stealth for durability"),
        ("layer", 3),
        ("color", "rust"),
        ("material", "scrap_metal"),
        ("weight", 2.0),
        ("armor_rating", 2),
        ("armor_type", "steel"),
        ("armor_durability", 40),
        ("max_armor_durability", 40),
        ("base_armor_rating", 2),
        ("armor_tier", "scrap"),
        ("metal_level", 5),
        ("magnetic_level", 4),
    ],
}

# =============================================================================
# TIER 2: MAKESHIFT ARMOR (Rating 4) - Crafted from available materials
# =============================================================================

MAKESHIFT_HELMET = {
    "prototype_parent": "TIERED_ARMOR_BASE",
    "key": "makeshift helmet",
    "aliases": ["leather helmet", "padded helmet", "crafted helmet"],
    "desc": "A helmet constructed from layered leather and padding with a few metal reinforcements at key points. Not pretty, but competently made.",
    "attrs": [
        ("coverage", ["head"]),
        ("worn_desc", "A functional {color}dark brown|n makeshift helmet of layered leather and padding, metal reinforcements at the crown and temples providing reasonable protection"),
        ("layer", 3),
        ("color", "brown"),
        ("material", "leather"),
        ("weight", 1.0),
        ("armor_rating", 4),
        ("armor_type", "leather"),
        ("armor_durability", 80),
        ("max_armor_durability", 80),
        ("base_armor_rating", 4),
        ("armor_tier", "makeshift"),
        ("metal_level", 3),
        ("magnetic_level", 2),
    ],
}

MAKESHIFT_VEST = {
    "prototype_parent": "TIERED_ARMOR_BASE",
    "key": "makeshift vest",
    "aliases": ["leather vest", "padded vest", "crafted vest"],
    "desc": "A vest of thick, layered leather with quilted padding beneath. Metal studs reinforce vital areas. Flexible enough for movement while offering decent protection.",
    "attrs": [
        ("coverage", ["chest", "back", "abdomen"]),
        ("worn_desc", "A well-crafted {color}dark brown|n makeshift vest of layered leather and quilted padding, metal studs reinforcing vital areas while maintaining flexibility"),
        ("layer", 3),
        ("color", "brown"),
        ("material", "leather"),
        ("weight", 3.5),
        ("armor_rating", 4),
        ("armor_type", "leather"),
        ("armor_durability", 80),
        ("max_armor_durability", 80),
        ("base_armor_rating", 4),
        ("armor_tier", "makeshift"),
        ("deflection_bonus", 0.0),
        ("metal_level", 3),
        ("magnetic_level", 2),
    ],
}

MAKESHIFT_BRACERS = {
    "prototype_parent": "TIERED_ARMOR_BASE",
    "key": "makeshift bracers",
    "aliases": ["leather bracers", "padded bracers", "crafted bracers"],
    "desc": "Arm guards of thick leather with metal strips riveted along the forearm. The fit is snug and the construction solid.",
    "attrs": [
        ("coverage", ["left_arm", "right_arm"]),
        ("worn_desc", "Sturdy {color}dark brown|n makeshift bracers of thick leather with riveted metal strips, protecting {their} forearms without restricting movement"),
        ("layer", 3),
        ("color", "brown"),
        ("material", "leather"),
        ("weight", 1.4),
        ("armor_rating", 4),
        ("armor_type", "leather"),
        ("armor_durability", 80),
        ("max_armor_durability", 80),
        ("base_armor_rating", 4),
        ("armor_tier", "makeshift"),
        ("metal_level", 3),
        ("magnetic_level", 2),
    ],
}

MAKESHIFT_GREAVES = {
    "prototype_parent": "TIERED_ARMOR_BASE",
    "key": "makeshift greaves",
    "aliases": ["leather greaves", "padded greaves", "crafted greaves"],
    "desc": "Leg armor of layered leather panels with metal knee guards. The straps are properly fitted and the padding is adequate for extended wear.",
    "attrs": [
        ("coverage", ["left_thigh", "right_thigh", "left_shin", "right_shin"]),
        ("worn_desc", "Well-fitted {color}dark brown|n makeshift greaves of layered leather panels, metal knee guards offering extra protection at vulnerable joints"),
        ("layer", 3),
        ("color", "brown"),
        ("material", "leather"),
        ("weight", 2.6),
        ("armor_rating", 4),
        ("armor_type", "leather"),
        ("armor_durability", 80),
        ("max_armor_durability", 80),
        ("base_armor_rating", 4),
        ("armor_tier", "makeshift"),
        ("metal_level", 3),
        ("magnetic_level", 2),
    ],
}

MAKESHIFT_BOOTS = {
    "prototype_parent": "TIERED_ARMOR_BASE",
    "key": "makeshift boots",
    "aliases": ["leather boots", "padded boots", "crafted boots"],
    "desc": "Heavy leather boots with reinforced toes and ankle support. Metal plates protect the top of the foot. Comfortable enough for long wear.",
    "attrs": [
        ("coverage", ["left_foot", "right_foot"]),
        ("worn_desc", "Sturdy {color}dark brown|n makeshift boots with reinforced toes and metal plates, offering reliable foot protection without excessive weight"),
        ("layer", 3),
        ("color", "brown"),
        ("material", "leather"),
        ("weight", 1.6),
        ("armor_rating", 4),
        ("armor_type", "leather"),
        ("armor_durability", 80),
        ("max_armor_durability", 80),
        ("base_armor_rating", 4),
        ("armor_tier", "makeshift"),
        ("metal_level", 3),
        ("magnetic_level", 2),
    ],
}

# =============================================================================
# TIER 3: STANDARD ARMOR (Rating 6) - Professional-grade protection
# =============================================================================

STANDARD_HELMET = {
    "prototype_parent": "TIERED_ARMOR_BASE",
    "key": "standard helmet",
    "aliases": ["riot helmet", "security helmet", "tactical head"],
    "desc": "A professional-grade security helmet with a polycarbonate shell and impact-absorbing liner. Standard issue for corporate security forces.",
    "attrs": [
        ("coverage", ["head"]),
        ("worn_desc", "A professional {color}matte black|n standard helmet with a polycarbonate shell, its impact-absorbing liner and adjustable straps marking it as corporate security gear"),
        ("layer", 3),
        ("color", "black"),
        ("material", "composite"),
        ("weight", 1.4),
        ("armor_rating", 6),
        ("armor_type", "composite"),
        ("armor_durability", 120),
        ("max_armor_durability", 120),
        ("base_armor_rating", 6),
        ("armor_tier", "standard"),
        ("metal_level", 2),
        ("magnetic_level", 1),
    ],
}

STANDARD_VEST = {
    "prototype_parent": "TIERED_ARMOR_BASE",
    "key": "standard vest",
    "aliases": ["security vest", "tactical vest", "body armor"],
    "desc": "A professional body armor vest with layered ballistic fabric and trauma padding. Standard issue for security contractors and law enforcement.",
    "attrs": [
        ("coverage", ["chest", "back", "abdomen"]),
        ("worn_desc", "A professional {color}matte black|n standard vest of layered ballistic fabric, its trauma padding and modular design marking it as serious protective equipment"),
        ("layer", 3),
        ("color", "black"),
        ("material", "kevlar"),
        ("weight", 4.0),
        ("armor_rating", 6),
        ("armor_type", "kevlar"),
        ("armor_durability", 120),
        ("max_armor_durability", 120),
        ("base_armor_rating", 6),
        ("armor_tier", "standard"),
        ("deflection_bonus", -0.02),
        ("metal_level", 2),
        ("magnetic_level", 1),
    ],
}

STANDARD_BRACERS = {
    "prototype_parent": "TIERED_ARMOR_BASE",
    "key": "standard bracers",
    "aliases": ["security bracers", "tactical bracers", "arm guards"],
    "desc": "Professional arm guards with hard composite shells over impact-absorbing padding. Articulated joints allow full range of motion.",
    "attrs": [
        ("coverage", ["left_arm", "right_arm"]),
        ("worn_desc", "Professional {color}matte black|n standard bracers with hard composite shells, articulated joints allowing full arm mobility while providing solid protection"),
        ("layer", 3),
        ("color", "black"),
        ("material", "composite"),
        ("weight", 1.6),
        ("armor_rating", 6),
        ("armor_type", "composite"),
        ("armor_durability", 120),
        ("max_armor_durability", 120),
        ("base_armor_rating", 6),
        ("armor_tier", "standard"),
        ("metal_level", 2),
        ("magnetic_level", 1),
    ],
}

STANDARD_GREAVES = {
    "prototype_parent": "TIERED_ARMOR_BASE",
    "key": "standard greaves",
    "aliases": ["security greaves", "tactical greaves", "leg guards"],
    "desc": "Professional leg armor with composite shin guards and articulated knee protection. Designed for extended tactical operations.",
    "attrs": [
        ("coverage", ["left_thigh", "right_thigh", "left_shin", "right_shin"]),
        ("worn_desc", "Professional {color}matte black|n standard greaves with composite shin guards, articulated knee protection allowing mobility during tactical operations"),
        ("layer", 3),
        ("color", "black"),
        ("material", "composite"),
        ("weight", 2.8),
        ("armor_rating", 6),
        ("armor_type", "composite"),
        ("armor_durability", 120),
        ("max_armor_durability", 120),
        ("base_armor_rating", 6),
        ("armor_tier", "standard"),
        ("metal_level", 2),
        ("magnetic_level", 1),
    ],
}

STANDARD_BOOTS = {
    "prototype_parent": "TIERED_ARMOR_BASE",
    "key": "standard boots",
    "aliases": ["security boots", "tactical boots", "combat boots"],
    "desc": "Professional tactical boots with composite toe caps and ankle support. Designed for both protection and all-day comfort in the field.",
    "attrs": [
        ("coverage", ["left_foot", "right_foot"]),
        ("worn_desc", "Professional {color}matte black|n standard boots with composite toe caps and reinforced ankles, their tactical design balancing protection with field comfort"),
        ("layer", 3),
        ("color", "black"),
        ("material", "composite"),
        ("weight", 1.8),
        ("armor_rating", 6),
        ("armor_type", "composite"),
        ("armor_durability", 120),
        ("max_armor_durability", 120),
        ("base_armor_rating", 6),
        ("armor_tier", "standard"),
        ("metal_level", 2),
        ("magnetic_level", 1),
    ],
}

# =============================================================================
# TIER 4: REINFORCED ARMOR (Rating 8) - Heavy-duty protection
# =============================================================================

REINFORCED_HELMET = {
    "prototype_parent": "TIERED_ARMOR_BASE",
    "key": "reinforced helmet",
    "aliases": ["assault helmet", "heavy helmet", "armored helmet"],
    "desc": "A heavy-duty assault helmet with layered ceramic-composite construction. The kind of headgear worn by breach teams and frontline operators.",
    "attrs": [
        ("coverage", ["head", "left_ear", "right_ear"]),
        ("worn_desc", "A menacing {color}gunmetal|n reinforced helmet with layered ceramic-composite construction, its heavy-duty design offering serious ballistic protection"),
        ("layer", 3),
        ("color", "gunmetal"),
        ("material", "ceramic"),
        ("weight", 2.2),
        ("armor_rating", 8),
        ("armor_type", "ceramic"),
        ("armor_durability", 160),
        ("max_armor_durability", 160),
        ("base_armor_rating", 8),
        ("armor_tier", "reinforced"),
        ("metal_level", 4),
        ("magnetic_level", 2),
    ],
}

REINFORCED_VEST = {
    "prototype_parent": "TIERED_ARMOR_BASE",
    "key": "reinforced vest",
    "aliases": ["assault vest", "heavy vest", "armored vest"],
    "desc": "A heavy-duty tactical vest with integrated ceramic trauma plates and multi-layer ballistic fabric. Designed to stop rifle rounds.",
    "attrs": [
        ("coverage", ["chest", "back", "abdomen"]),
        ("worn_desc", "A heavy {color}gunmetal|n reinforced vest with integrated ceramic plates, its multi-layer construction designed to stop serious threats"),
        ("layer", 4),
        ("color", "gunmetal"),
        ("material", "ceramic"),
        ("weight", 6.5),
        ("armor_rating", 8),
        ("armor_type", "ceramic"),
        ("armor_durability", 160),
        ("max_armor_durability", 160),
        ("base_armor_rating", 8),
        ("armor_tier", "reinforced"),
        ("deflection_bonus", -0.05),
        ("metal_level", 5),
        ("magnetic_level", 3),
    ],
}

REINFORCED_BRACERS = {
    "prototype_parent": "TIERED_ARMOR_BASE",
    "key": "reinforced bracers",
    "aliases": ["assault bracers", "heavy bracers", "armored bracers"],
    "desc": "Heavy arm guards with ceramic-composite plates over ballistic fabric. Each bracer has an integrated forearm shield for blocking.",
    "attrs": [
        ("coverage", ["left_arm", "right_arm", "left_hand", "right_hand"]),
        ("worn_desc", "Heavy {color}gunmetal|n reinforced bracers with ceramic-composite plates, integrated forearm shields providing active defense capability"),
        ("layer", 3),
        ("color", "gunmetal"),
        ("material", "ceramic"),
        ("weight", 2.4),
        ("armor_rating", 8),
        ("armor_type", "ceramic"),
        ("armor_durability", 160),
        ("max_armor_durability", 160),
        ("base_armor_rating", 8),
        ("armor_tier", "reinforced"),
        ("deflection_bonus", 0.05),
        ("metal_level", 4),
        ("magnetic_level", 2),
    ],
}

REINFORCED_GREAVES = {
    "prototype_parent": "TIERED_ARMOR_BASE",
    "key": "reinforced greaves",
    "aliases": ["assault greaves", "heavy greaves", "armored greaves"],
    "desc": "Heavy leg armor with ceramic-composite plating over the thighs, knees, and shins. Articulated joints preserve mobility despite the weight.",
    "attrs": [
        ("coverage", ["left_thigh", "right_thigh", "left_shin", "right_shin"]),
        ("worn_desc", "Heavy {color}gunmetal|n reinforced greaves with ceramic-composite plating, articulated joints preserving mobility despite {their} substantial protection"),
        ("layer", 3),
        ("color", "gunmetal"),
        ("material", "ceramic"),
        ("weight", 4.2),
        ("armor_rating", 8),
        ("armor_type", "ceramic"),
        ("armor_durability", 160),
        ("max_armor_durability", 160),
        ("base_armor_rating", 8),
        ("armor_tier", "reinforced"),
        ("metal_level", 4),
        ("magnetic_level", 2),
    ],
}

REINFORCED_BOOTS = {
    "prototype_parent": "TIERED_ARMOR_BASE",
    "key": "reinforced boots",
    "aliases": ["assault boots", "heavy boots", "armored boots"],
    "desc": "Heavy tactical boots with ceramic-composite toe caps and ankle armor. Steel shanks provide arch support and stomp protection.",
    "attrs": [
        ("coverage", ["left_foot", "right_foot"]),
        ("worn_desc", "Heavy {color}gunmetal|n reinforced boots with ceramic-composite armor, their substantial construction offering maximum foot and ankle protection"),
        ("layer", 3),
        ("color", "gunmetal"),
        ("material", "ceramic"),
        ("weight", 2.6),
        ("armor_rating", 8),
        ("armor_type", "ceramic"),
        ("armor_durability", 160),
        ("max_armor_durability", 160),
        ("base_armor_rating", 8),
        ("armor_tier", "reinforced"),
        ("metal_level", 5),
        ("magnetic_level", 3),
    ],
}

# =============================================================================
# TIER 5: MILITARY ARMOR (Rating 10) - Top-tier combat protection
# =============================================================================

MILITARY_HELMET = {
    "prototype_parent": "TIERED_ARMOR_BASE",
    "key": "military helmet",
    "aliases": ["combat helmet", "spec ops helmet", "tactical helmet"],
    "desc": "A state-of-the-art military combat helmet with advanced composite construction, integrated comms, and ballistic face shield. The pinnacle of head protection.",
    "attrs": [
        ("coverage", ["head", "face", "left_ear", "right_ear"]),
        ("worn_desc", "A menacing {color}midnight black|n military helmet with advanced composite construction, its integrated systems and ballistic face shield marking it as top-tier combat gear"),
        ("layer", 3),
        ("color", "midnight"),
        ("material", "advanced_composite"),
        ("weight", 2.8),
        ("armor_rating", 10),
        ("armor_type", "ceramic"),
        ("armor_durability", 200),
        ("max_armor_durability", 200),
        ("base_armor_rating", 10),
        ("armor_tier", "military"),
        ("metal_level", 3),
        ("magnetic_level", 1),
    ],
}

MILITARY_VEST = {
    "prototype_parent": "TIERED_ARMOR_BASE",
    "key": "military vest",
    "aliases": ["combat vest", "spec ops vest", "assault armor"],
    "desc": "Top-of-the-line military body armor with advanced ceramic-composite plates, liquid armor shock absorption, and modular attachment systems. Rated for heavy combat.",
    "attrs": [
        ("coverage", ["chest", "back", "abdomen", "groin"]),
        ("worn_desc", "Imposing {color}midnight black|n military body armor with advanced ceramic-composite plates, its liquid armor technology and modular systems representing the cutting edge of protection"),
        ("layer", 4),
        ("color", "midnight"),
        ("material", "advanced_composite"),
        ("weight", 8.0),
        ("armor_rating", 10),
        ("armor_type", "ceramic"),
        ("armor_durability", 200),
        ("max_armor_durability", 200),
        ("base_armor_rating", 10),
        ("armor_tier", "military"),
        ("deflection_bonus", -0.08),
        ("metal_level", 4),
        ("magnetic_level", 2),
    ],
}

MILITARY_BRACERS = {
    "prototype_parent": "TIERED_ARMOR_BASE",
    "key": "military bracers",
    "aliases": ["combat bracers", "spec ops bracers", "assault bracers"],
    "desc": "Military-grade arm armor with advanced composite shells, integrated forearm shields, and servo-assisted articulation. Maximum protection with minimal mobility loss.",
    "attrs": [
        ("coverage", ["left_arm", "right_arm", "left_hand", "right_hand"]),
        ("worn_desc", "Sleek {color}midnight black|n military bracers with advanced composite shells, servo-assisted articulation allowing full arm mobility despite maximum protection"),
        ("layer", 3),
        ("color", "midnight"),
        ("material", "advanced_composite"),
        ("weight", 2.8),
        ("armor_rating", 10),
        ("armor_type", "ceramic"),
        ("armor_durability", 200),
        ("max_armor_durability", 200),
        ("base_armor_rating", 10),
        ("armor_tier", "military"),
        ("deflection_bonus", 0.08),
        ("metal_level", 3),
        ("magnetic_level", 1),
    ],
}

MILITARY_GREAVES = {
    "prototype_parent": "TIERED_ARMOR_BASE",
    "key": "military greaves",
    "aliases": ["combat greaves", "spec ops greaves", "assault greaves"],
    "desc": "Military-grade leg armor with advanced composite plating, servo-assisted knee joints, and integrated shock absorption. Designed for high-mobility combat operations.",
    "attrs": [
        ("coverage", ["left_thigh", "right_thigh", "left_shin", "right_shin"]),
        ("worn_desc", "Sleek {color}midnight black|n military greaves with advanced composite plating, servo-assisted joints enabling high mobility despite {their} substantial armor rating"),
        ("layer", 3),
        ("color", "midnight"),
        ("material", "advanced_composite"),
        ("weight", 4.8),
        ("armor_rating", 10),
        ("armor_type", "ceramic"),
        ("armor_durability", 200),
        ("max_armor_durability", 200),
        ("base_armor_rating", 10),
        ("armor_tier", "military"),
        ("metal_level", 3),
        ("magnetic_level", 1),
    ],
}

MILITARY_BOOTS = {
    "prototype_parent": "TIERED_ARMOR_BASE",
    "key": "military boots",
    "aliases": ["combat boots", "spec ops boots", "assault boots"],
    "desc": "Military-grade tactical boots with advanced composite armor, shock-absorbing soles, and ankle stabilization systems. Built for combat in any environment.",
    "attrs": [
        ("coverage", ["left_foot", "right_foot"]),
        ("worn_desc", "Sleek {color}midnight black|n military boots with advanced composite armor, their shock-absorbing construction and ankle stabilization marking them as top-tier combat footwear"),
        ("layer", 3),
        ("color", "midnight"),
        ("material", "advanced_composite"),
        ("weight", 3.0),
        ("armor_rating", 10),
        ("armor_type", "ceramic"),
        ("armor_durability", 200),
        ("max_armor_durability", 200),
        ("base_armor_rating", 10),
        ("armor_tier", "military"),
        ("metal_level", 3),
        ("magnetic_level", 1),
    ],
}

# =============================================================================
# ARMOR SET PROTOTYPES - Spawn full sets of matching armor
# Use: @spawn SCRAP_ARMOR_SET (spawns all 5 pieces)
# =============================================================================

# These are batch spawn helpers - when spawned, they create all pieces of a set
# Note: Armor sets stored as actual spawn-able objects with spawn_batch attribute
# These create a dummy object with metadata about what to spawn

SCRAP_ARMOR_SET = {
    "prototype_key": "SCRAP_ARMOR_SET",
    "prototype_desc": "Full set of Tier 1 scrap armor (helmet, vest, bracers, greaves, boots)",
    "prototype_locks": "spawn:perm(Builder);edit:perm(Admin)",
    "key": "scrap armor set (template)",
    "typeclass": "typeclasses.items.Item",
    "desc": "This is a template for spawning a full set of scrap armor. This shouldn't appear in-game.",
    "attrs": [
        ("spawn_batch", ["SCRAP_HELMET", "SCRAP_VEST", "SCRAP_BRACERS", "SCRAP_GREAVES", "SCRAP_BOOTS"]),
        ("is_armor_set", True),
        ("armor_tier", "scrap"),
    ],
}

MAKESHIFT_ARMOR_SET = {
    "prototype_key": "MAKESHIFT_ARMOR_SET",
    "prototype_desc": "Full set of Tier 2 makeshift armor (helmet, vest, bracers, greaves, boots)",
    "prototype_locks": "spawn:perm(Builder);edit:perm(Admin)",
    "key": "makeshift armor set (template)",
    "typeclass": "typeclasses.items.Item",
    "desc": "This is a template for spawning a full set of makeshift armor. This shouldn't appear in-game.",
    "attrs": [
        ("spawn_batch", ["MAKESHIFT_HELMET", "MAKESHIFT_VEST", "MAKESHIFT_BRACERS", "MAKESHIFT_GREAVES", "MAKESHIFT_BOOTS"]),
        ("is_armor_set", True),
        ("armor_tier", "makeshift"),
    ],
}

STANDARD_ARMOR_SET = {
    "prototype_key": "STANDARD_ARMOR_SET",
    "prototype_desc": "Full set of Tier 3 standard armor (helmet, vest, bracers, greaves, boots)",
    "prototype_locks": "spawn:perm(Builder);edit:perm(Admin)",
    "key": "standard armor set (template)",
    "typeclass": "typeclasses.items.Item",
    "desc": "This is a template for spawning a full set of standard armor. This shouldn't appear in-game.",
    "attrs": [
        ("spawn_batch", ["STANDARD_HELMET", "STANDARD_VEST", "STANDARD_BRACERS", "STANDARD_GREAVES", "STANDARD_BOOTS"]),
        ("is_armor_set", True),
        ("armor_tier", "standard"),
    ],
}

REINFORCED_ARMOR_SET = {
    "prototype_key": "REINFORCED_ARMOR_SET",
    "prototype_desc": "Full set of Tier 4 reinforced armor (helmet, vest, bracers, greaves, boots)",
    "prototype_locks": "spawn:perm(Builder);edit:perm(Admin)",
    "key": "reinforced armor set (template)",
    "typeclass": "typeclasses.items.Item",
    "desc": "This is a template for spawning a full set of reinforced armor. This shouldn't appear in-game.",
    "attrs": [
        ("spawn_batch", ["REINFORCED_HELMET", "REINFORCED_VEST", "REINFORCED_BRACERS", "REINFORCED_GREAVES", "REINFORCED_BOOTS"]),
        ("is_armor_set", True),
        ("armor_tier", "reinforced"),
    ],
}

MILITARY_ARMOR_SET = {
    "prototype_key": "MILITARY_ARMOR_SET",
    "prototype_desc": "Full set of Tier 5 military armor (helmet, vest, bracers, greaves, boots)",
    "prototype_locks": "spawn:perm(Builder);edit:perm(Admin)",
    "key": "military armor set (template)",
    "typeclass": "typeclasses.items.Item",
    "desc": "This is a template for spawning a full set of military armor. This shouldn't appear in-game.",
    "attrs": [
        ("spawn_batch", ["MILITARY_HELMET", "MILITARY_VEST", "MILITARY_BRACERS", "MILITARY_GREAVES", "MILITARY_BOOTS"]),
        ("is_armor_set", True),
        ("armor_tier", "military"),
    ],
}

# =============================================================================  
# REPAIR TOOL PROTOTYPES (FOR ARMOR MAINTENANCE)
# =============================================================================

# Sewing Kit - Best for leather armor
SEWING_KIT = {
    "key": "sewing kit",
    "aliases": ["kit", "needles", "thread"],
    "typeclass": "typeclasses.items.Item",
    "desc": "A comprehensive sewing kit with heavy-duty needles, reinforced thread, and leather patches. Perfect for repairing fabric and leather armor.",
    "attrs": [
        ("repair_tool_type", "sewing_kit"),
        ("tool_durability", 25),
        ("max_tool_durability", 25),
    ],
}

# Metalworking Tools - Best for steel armor  
METALWORK_TOOLS = {
    "key": "metalworking tools",
    "aliases": ["tools", "hammer", "anvil", "metalwork"],
    "typeclass": "typeclasses.items.Item", 
    "desc": "A set of metalworking tools including a small anvil, hammer, tongs, and files. Essential for repairing steel and metal armor components.",
    "attrs": [
        ("repair_tool_type", "metalwork_tools"),
        ("tool_durability", 30),
        ("max_tool_durability", 30),
    ],
}

# Ballistic Repair Kit - Best for kevlar
BALLISTIC_REPAIR_KIT = {
    "key": "ballistic repair kit",
    "aliases": ["ballistic kit", "kevlar kit", "fiber kit"],
    "typeclass": "typeclasses.items.Item",
    "desc": "A specialized kit for repairing ballistic armor, containing aramid fibers, ballistic gel, and precision tools for working with advanced protective materials.",
    "attrs": [
        ("repair_tool_type", "ballistic_repair_kit"),
        ("tool_durability", 15),  # Specialized but fragile
        ("max_tool_durability", 15),
    ],
}

# Ceramic Repair Compound - Best for ceramic plates
CERAMIC_REPAIR_COMPOUND = {
    "key": "ceramic repair compound",
    "aliases": ["compound", "ceramic paste", "armor compound"],
    "typeclass": "typeclasses.items.Item",
    "desc": "An advanced ceramic repair compound that can restore cracked trauma plates. Requires precise application and technical expertise to use effectively.",
    "attrs": [
        ("repair_tool_type", "ceramic_repair_compound"),
        ("tool_durability", 8),   # Very specialized, limited uses
        ("max_tool_durability", 8),
    ],
}

# Generic Tool Kit - Moderate for all armor types
GENERIC_TOOL_KIT = {
    "key": "tool kit",
    "aliases": ["tools", "repair kit", "general tools"],
    "typeclass": "typeclasses.items.Item",
    "desc": "A general-purpose tool kit with basic implements for field repairs. Not specialized for any particular material, but versatile enough for emergency fixes.",
    "attrs": [
        ("repair_tool_type", "generic_tools"),
        ("tool_durability", 20),
        ("max_tool_durability", 20),
    ],
}

# Workshop Bench - For full repairs (location-based)
ARMOR_WORKBENCH = {
    "key": "armor workbench", 
    "aliases": ["workbench", "bench", "workshop"],
    "typeclass": "typeclasses.items.Item",
    "desc": "A professional armor repair workbench equipped with specialized tools, proper lighting, and workspace for comprehensive armor restoration. Enables full repair capabilities.",
    "attrs": [
        ("repair_tool_type", "workshop_bench"),
        ("tool_durability", 1000),  # Extremely durable, permanent installation
        ("max_tool_durability", 1000),
        ("workshop_tool", True),    # Special flag for full repairs
    ],
}

# =============================================================================
# MEDICAL ITEM PROTOTYPES
# =============================================================================

# IV Blood Bag - Emergency blood transfusion
BLOOD_BAG = {
    "key": "blood bag",
    "typeclass": "typeclasses.items.Item",
    "aliases": ["iv", "blood", "transfusion"],
    "desc": "A sterile IV blood bag with attached tubing for emergency transfusion. Contains 500ml of universal donor blood.",
    "tags": [("medical_item", "item_type")],
    "attrs": [
        ("medical_type", "blood_restoration"),
        ("uses_left", 1),
        ("max_uses", 1),
        ("stat_requirement", 1),
        ("application_time", 1),
        ("effectiveness", {
            "bleeding": 9,        # Excellent for severe bleeding
            "blood_loss": 10,     # Perfect for blood restoration
            "shock": 7,          # Good for shock treatment
            "organ_damage": 3,   # Limited help for organs
        })
    ],
}

# Injectable Painkiller - Multi-dose pain management
PAINKILLER = {
    "key": "painkiller",
    "typeclass": "typeclasses.items.Item",
    "aliases": ["syringe", "morphine", "pain meds"],
    "desc": "A medical syringe containing powerful analgesic medication. Multiple doses available.",
    "tags": [("medical_item", "item_type")],
    "attrs": [
        ("medical_type", "pain_relief"),
        ("uses_left", 3),
        ("max_uses", 3),
        ("stat_requirement", 0),
        ("application_time", 1),
        ("effectiveness", {
            "pain": 9,           # Excellent pain relief
            "shock": 6,          # Moderate shock treatment
            "bleeding": 2,       # Minimal bleeding help
            "fracture": 4,       # Some fracture pain relief
        })
    ],
}

# Gauze Bandages - Multi-use wound dressing
GAUZE_BANDAGES = {
    "key": "gauze bandages",
    "typeclass": "typeclasses.items.Item",
    "aliases": ["gauze", "bandages", "dressing"],
    "desc": "Sterile gauze bandages for wound dressing and bleeding control. Multiple applications available.",
    "tags": [("medical_item", "item_type")],
    "attrs": [
        ("medical_type", "wound_care"),
        ("uses_left", 5),
        ("max_uses", 5),
        ("stat_requirement", 0),
        ("application_time", 1),
        ("effectiveness", {
            "bleeding": 7,       # Very good bleeding control
            "infection": 8,      # Excellent infection prevention  
            "wound_healing": 6,  # Good wound protection
            "pain": 3,           # Minimal pain relief
        })
    ],
}

# Medical Splint - Single-use bone stabilization
SPLINT = {
    "key": "medical splint",
    "typeclass": "typeclasses.items.Item",
    "aliases": ["splint", "brace"],
    "desc": "A universal medical splint that adapts to immobilize fractured appendages. Works on arms, legs, tentacles, wings, and other limbs.",
    "tags": [("medical_item", "item_type")],
    "attrs": [
        ("medical_type", "fracture_treatment"),
        ("uses_left", 1),
        ("max_uses", 1),
        ("stat_requirement", 2),
        ("application_time", 2),
        ("effectiveness", {
            "fracture": 8,       # Excellent fracture stabilization
            "pain": 4,           # Some pain relief
            "mobility": 6,       # Restores some movement
            "bleeding": 2,       # Minimal bleeding help
        })
    ],
}

# Surgical Kit - Advanced multi-use medical tools
SURGICAL_KIT = {
    "key": "surgical kit",
    "typeclass": "typeclasses.items.Item",
    "aliases": ["surgery", "medical kit", "scalpel"],
    "desc": "A comprehensive surgical kit containing scalpels, sutures, clamps, and other advanced medical tools. Requires significant medical training.",
    "tags": [("medical_item", "item_type")],
    "attrs": [
        ("medical_type", "surgical_treatment"),
        ("uses_left", 10),
        ("max_uses", 10),
        ("stat_requirement", 3),
        ("application_time", 3),
        ("effectiveness", {
            "organ_damage": 10,  # Perfect for internal injuries
            "internal_bleeding": 9, # Excellent for internal bleeding
            "complex_wounds": 8, # Very good for complex injuries
            "infection": 7,      # Good sterile procedures
            "pain": 5,           # Moderate pain management
        })
    ],
}

# Emergency Stimpak - Rapid healing injection
STIMPAK = {
    "key": "stimpak",
    "typeclass": "typeclasses.items.Item",
    "aliases": ["stim", "healing injection"],
    "desc": "An emergency medical stimulant that accelerates natural healing processes. Single-use auto-injector.",
    "tags": [("medical_item", "item_type")],
    "attrs": [
        ("medical_type", "healing_acceleration"),
        ("uses_left", 1),
        ("max_uses", 1),
        ("stat_requirement", 1),
        ("application_time", 1),
        ("effectiveness", {
            "wound_healing": 8,  # Excellent healing boost
            "bleeding": 6,       # Good bleeding control
            "pain": 7,           # Very good pain relief
            "organ_damage": 4,   # Limited organ help
            "fatigue": 9,        # Excellent energy restoration
        })
    ],
}

# Antiseptic Spray - Infection prevention
ANTISEPTIC = {
    "key": "antiseptic spray",
    "typeclass": "typeclasses.items.Item",
    "aliases": ["antiseptic", "disinfectant", "spray"],
    "desc": "Medical-grade antiseptic spray for wound cleaning and infection prevention. Multiple applications per bottle.",
    "tags": [("medical_item", "item_type")],
    "attrs": [
        ("medical_type", "antiseptic"),
        ("uses_left", 8),
        ("max_uses", 8),
        ("stat_requirement", 0),
        ("application_time", 1),
        ("effectiveness", {
            "infection": 9,      # Excellent infection prevention
            "wound_healing": 5,  # Moderate healing assistance
            "bleeding": 3,       # Minimal bleeding help
            "pain": 2,           # Slight pain relief
        })
    ],
}

# ===================================================================
# PHASE 2.5: INHALATION & SMOKING MEDICAL ITEMS
# ===================================================================

OXYGEN_TANK = {
    "key": "oxygen tank",
    "typeclass": "typeclasses.items.Item",
    "aliases": ["oxygen", "o2", "tank"],
    "desc": "Portable oxygen tank with breathing mask. Essential for respiratory emergencies and consciousness recovery.",
    "tags": [("medical_item", "item_type")],
    "attrs": [
        ("medical_type", "oxygen"),
        ("uses_left", 10),
        ("max_uses", 10),
        ("stat_requirement", 0),
        ("application_time", 1),
        ("effectiveness", {
            "consciousness": 9,      # Excellent consciousness boost
            "breathing_difficulty": 8, # Great respiratory help
            "suffocation": 10,       # Perfect suffocation treatment
        })
    ],
}

STIMPAK_INHALER = {
    "key": "stimpak inhaler",
    "typeclass": "typeclasses.items.Item", 
    "aliases": ["inhaler", "stimpak vapor", "medical inhaler"],
    "desc": "Pressurized inhaler containing vaporized stimpak for rapid respiratory absorption. Single use only.",
    "tags": [("medical_item", "item_type")],
    "attrs": [
        ("medical_type", "vapor"),
        ("uses_left", 1),
        ("max_uses", 1),
        ("stat_requirement", 1),
        ("application_time", 2),
        ("effectiveness", {
            "pain": 7,           # Good pain relief
            "blood_loss": 6,     # Moderate blood restoration
            "breathing_difficulty": 5, # Some respiratory help
        })
    ],
}

ANESTHETIC_GAS = {
    "key": "anesthetic gas",
    "typeclass": "typeclasses.items.Item",
    "aliases": ["anesthetic", "knockout gas", "medical gas"],
    "desc": "Medical anesthetic gas canister. Reduces pain but may cause drowsiness. Use with caution.",
    "tags": [("medical_item", "item_type")],
    "attrs": [
        ("medical_type", "anesthetic"),
        ("uses_left", 5),
        ("max_uses", 5),
        ("stat_requirement", 2),
        ("application_time", 2),
        ("effectiveness", {
            "pain": 9,           # Excellent pain relief
            "consciousness": -2,  # Reduces consciousness (side effect)
        })
    ],
}

MEDICINAL_HERB = {
    "key": "medicinal herb",
    "typeclass": "typeclasses.items.Item",
    "aliases": ["herb", "healing herb", "dried herb"],
    "desc": "Dried medicinal herb that can be smoked for natural pain relief and calming effects. Organic treatment option.",
    "tags": [("medical_item", "item_type")],
    "attrs": [
        ("medical_type", "herb"),
        ("uses_left", 3),
        ("max_uses", 3),
        ("stat_requirement", 0),
        ("application_time", 3),
        ("effectiveness", {
            "pain": 6,           # Good natural pain relief
            "stress": 7,         # Excellent stress relief
            "anxiety": 6,        # Good anxiety reduction
        })
    ],
}

PAIN_RELIEF_CIGARETTE = {
    "key": "pain relief cigarette",
    "typeclass": "typeclasses.items.Item",
    "aliases": ["med cigarette", "medical cigarette", "pain cigarette"],
    "desc": "Specially formulated cigarette infused with mild pain-relieving compounds. For medicinal use only.",
    "tags": [("medical_item", "item_type")],
    "attrs": [
        ("medical_type", "cigarette"),
        ("uses_left", 1),
        ("max_uses", 1),
        ("stat_requirement", 0),
        ("application_time", 4),
        ("effectiveness", {
            "pain": 4,           # Mild pain relief
            "stress": 3,         # Minor stress relief
        })
    ],
}

# =============================================================================
# SHOP MERCHANT PROTOTYPES
# =============================================================================

# Base merchant template - holographic shopkeeper
HOLOGRAPHIC_MERCHANT = {
    "key": "holographic merchant",
    "typeclass": "typeclasses.characters.Character",
    "desc": "A shimmering holographic projection of a merchant. The figure flickers slightly, clearly not real.",
    "attrs": [
        ("is_merchant", True),
        ("is_holographic", True),
        ("merchant_greeting", "Welcome to the shop. Browse my wares."),
    ],
    "locks": "get:false();puppet:false()",
}

# Example armory merchant
ARMORY_MERCHANT = {
    "prototype_parent": "HOLOGRAPHIC_MERCHANT",
    "key": "Gunther the Armorer",
    "desc": "A burly holographic figure in tactical gear, arms crossed. The projection glitches occasionally, revealing the emitter underneath.",
    "attrs": [
        ("merchant_greeting", "Need weapons? You've come to the right place."),
        ("merchant_specialty", "weapons and armor"),
    ],
}

# Example general goods merchant
GENERAL_MERCHANT = {
    "prototype_parent": "HOLOGRAPHIC_MERCHANT",
    "key": "Sal the Supplier",
    "desc": "A friendly-looking holographic merchant with a wide smile. The projection flickers blue-green.",
    "attrs": [
        ("merchant_greeting", "Everything you need, right here!"),
        ("merchant_specialty", "general supplies"),
    ],
}

# Example medical supplies merchant
MEDIC_MERCHANT = {
    "prototype_parent": "HOLOGRAPHIC_MERCHANT",
    "key": "Dr. Voss",
    "desc": "A stern holographic figure in a white coat, clipboard in hand. The projection is sharp and professional.",
    "attrs": [
        ("merchant_greeting", "Medical supplies. No prescriptions required."),
        ("merchant_specialty", "medical supplies"),
    ],
}

# Example corner store merchant
CORNERSTORE_MERCHANT = {
    "prototype_parent": "HOLOGRAPHIC_MERCHANT",
    "key": "Juan Sanchez",
    "desc": "A flamboyant holographic merchant with wild hair and an elaborate mustache. His garish outfit shifts between purple and gold as the projection flickers. He gestures dramatically even in stillness.",
    "attrs": [
        ("merchant_greeting", "Welcome, my friend! I have everything you need - and some things you don't!"),
        ("merchant_specialty", "general goods"),
    ],
}

# =============================================================================
# SHOP CONTAINER PROTOTYPES
# =============================================================================

# Base shop container template
SHOP_CONTAINER_BASE = {
    "prototype_key": "shop_container_base",
    "typeclass": "typeclasses.shopkeeper.ShopContainer",
    "locks": "get:false();puppet:false()",
    "attrs": [
        ("is_infinite", True),
        ("markup_percent", 0),
        ("shop_name", "Shop"),
        ("container_type", "shelf"),
        ("prototype_inventory", {}),
        ("item_inventory", {}),
    ],
}

# Weapons shop shelf
WEAPONS_SHELF = {
    "prototype_parent": "shop_container_base",
    "key": "weapons rack",
    "desc": "A sturdy metal weapons rack displaying various implements of violence. Everything from blades to firearms.",
    "attrs": [
        ("shop_name", "Armory"),
        ("container_type", "rack"),
        ("markup_percent", 15),  # 15% markup on weapons
        ("prototype_inventory", {
            "KATANA": 500,
            "SWORD": 250,
            "DAGGER": 80,
            "CHAINSAW": 800,
            "STAFF": 150,
            "BASEBALL_BAT": 60,
            "TENNIS_RACKET": 120,
        }),
    ],
}

# Explosives shop crate
EXPLOSIVES_CRATE = {
    "prototype_parent": "shop_container_base",
    "key": "reinforced crate",
    "desc": "A heavily reinforced military crate with warning labels. Contains various explosive devices - handle with extreme care.",
    "attrs": [
        ("shop_name", "Demolitions Supply"),
        ("container_type", "crate"),
        ("markup_percent", 25),  # 25% markup on dangerous goods
        ("prototype_inventory", {
            "FRAG_GRENADE": 150,
            "TACTICAL_GRENADE": 200,
            "DEMO_CHARGE": 500,
            "FLASHBANG": 100,
            "SMOKE_GRENADE": 75,
            "STICKY_GRENADE": 300,
            "REMOTE_DETONATOR": 250,
        }),
    ],
}

# Armor shop display
ARMOR_DISPLAY = {
    "prototype_parent": "shop_container_base",
    "key": "armor display",
    "desc": "A professional display stand showcasing various protective gear and tactical equipment.",
    "attrs": [
        ("shop_name", "Tactical Outfitters"),
        ("container_type", "display"),
        ("markup_percent", 20),  # 20% markup on armor
        ("prototype_inventory", {
            "KEVLAR_VEST": 800,
            "PLATE_CARRIER": 600,
            "PLATE_MAIL": 1500,
            "ARMORED_LEATHER_JACKET": 400,
            "COMBAT_HELMET": 350,
            "LIGHTWEIGHT_PLATE": 200,
            "STANDARD_PLATE": 350,
            "REINFORCED_PLATE": 600,
            "CERAMIC_PLATES": 500,
            "BEE_HIVE_COVERALL": 1200,  # Premium exotic armor
        }),
    ],
}

# Clothing shop rack
CLOTHING_RACK = {
    "prototype_parent": "shop_container_base",
    "key": "clothing rack",
    "desc": "A sleek chrome clothing rack displaying various garments from tactical to casual wear.",
    "attrs": [
        ("shop_name", "Street Fashion"),
        ("container_type", "rack"),
        ("markup_percent", 10),  # 10% markup on clothing
        ("prototype_inventory", {
            "CODER_SOCKS": 50,
            "DEV_HOODIE": 80,
            "BLUE_JEANS": 60,
            "COTTON_TSHIRT": 25,
            "COMBAT_BOOTS": 120,
            "TACTICAL_JUMPSUIT": 150,
            "TACTICAL_PANTS": 70,
            "TACTICAL_SHIRT": 50,
        }),
        # Integration settings - embeds shop in room description
        ("integrate", True),
        ("integration_desc", "A sleek chrome clothing rack displays various street fashion items, from coding socks to tactical gear."),
        ("integration_priority", 2),
    ],
}

# Medical supplies cabinet
MEDICAL_CABINET = {
    "prototype_parent": "shop_container_base",
    "key": "medical supply cabinet",
    "desc": "A sterile white medical cabinet with glass doors. Stocked with various emergency medical supplies.",
    "attrs": [
        ("shop_name", "Medical Supplies"),
        ("container_type", "cabinet"),
        ("markup_percent", 30),  # 30% markup on medical (premium)
        ("prototype_inventory", {
            "BLOOD_BAG": 200,
            "PAINKILLER": 80,
            "GAUZE_BANDAGES": 30,
            "SPLINT": 100,
            "SURGICAL_KIT": 500,
            "STIMPAK": 150,
            "ANTISEPTIC": 40,
            "OXYGEN_TANK": 250,
            "STIMPAK_INHALER": 120,
            "ANESTHETIC_GAS": 180,
            "MEDICINAL_HERB": 60,
            "PAIN_RELIEF_CIGARETTE": 20,
        }),
    ],
}

# General goods shelf
GENERAL_SHELF = {
    "prototype_parent": "shop_container_base",
    "key": "general goods shelf",
    "desc": "A well-stocked shelf with a variety of useful items and miscellaneous supplies.",
    "attrs": [
        ("shop_name", "General Store"),
        ("container_type", "shelf"),
        ("markup_percent", 5),  # 5% markup on general goods
        ("prototype_inventory", {
            "SPRAYPAINT_CAN": 25,
            "SOLVENT_CAN": 30,
            "KEYRING": 10,
            "ROCK": 1,
            "BOTTLE": 5,
            "SEWING_KIT": 50,
            "METALWORK_TOOLS": 150,
            "BALLISTIC_REPAIR_KIT": 100,
            "CERAMIC_REPAIR_COMPOUND": 200,
            "GENERIC_TOOL_KIT": 75,
        }),
    ],
}

# Ranged weapons locker
FIREARMS_LOCKER = {
    "prototype_parent": "shop_container_base",
    "key": "firearms locker",
    "desc": "A secure firearms locker with reinforced steel construction. Contains various ranged weapons under lock and key.",
    "attrs": [
        ("shop_name", "Gun Shop"),
        ("container_type", "locker"),
        ("markup_percent", 20),  # 20% markup on firearms
        ("prototype_inventory", {
            "PISTOL": 300,
            "SHOTGUN": 500,
            "SNIPER_RIFLE": 1200,
            "BOLT_RIFLE": 800,
            "ANTI_MATERIAL_RIFLE": 2500,
            "ASSAULT_RIFLE": 900,
            "SMG": 600,
            "THROWING_KNIFE": 40,
            "THROWING_AXE": 60,
            "SHURIKEN": 25,
        }),
    ],
}

# Limited stock example - corner store cooler
CORNER_STORE_COOLER = {
    "prototype_parent": "shop_container_base",
    "key": "refrigerated cooler",
    "desc": "A humming refrigerated cooler with glass doors. The stock looks somewhat limited.",
    "attrs": [
        ("shop_name", "Juan's Corner Store"),
        ("container_type", "cooler"),
        ("markup_percent", 50),  # 50% markup - corner store convenience tax!
        ("is_infinite", False),  # Limited stock!
        ("prototype_inventory", {
            "BLOOD_BAG": 500,      # Expensive emergency supply
            "STIMPAK": 350,        # Premium healing
            "PAINKILLER": 150,     # Pain relief
        }),
        ("item_inventory", {
            "BLOOD_BAG": 2,        # Only 2 in stock
            "STIMPAK": 5,          # Only 5 in stock
            "PAINKILLER": 3,       # Only 3 in stock
        }),
    ],
}


# =============================================================================
# SAFETYNET ACCESS DEVICE PROTOTYPES
# =============================================================================

# Standard municipal wristpad - allows map and combat prompt display
# Does NOT provide SafetyNet access - that requires a hacked wristpad
# Cannot be removed while worn (locked to prevent dropping)
MUNICIPAL_WRISTPAD = {
    "prototype_key": "municipal_wristpad",
    "key": "Pulse watch",
    "typeclass": "typeclasses.items.Wristpad",
    "aliases": ["pulse watch", "wristpad", "pulse", "watch"],
    "desc": "A government issue watch with a chunky display screen. The device wraps around the wrist, and has a small little needle that pricks into the underside of your wrist. When activated, a 2.5D display projects readouts about your surroundings and body vitals, complete with a little avatar that smiles when you're healthy and frowns when you're sick or hurt. You've either had it your whole life, or got it when you arrived in China. It's illegal to remove. A logo of a triangle beset with a Y is emblazoned on the casing.",
    "attrs": [
        ("is_municipal_wristpad", True),
        ("is_removable", False),
        ("coverage", ["left_arm", "right_arm"]),
        ("worn_desc", "%N is wearing a Pulse watch on their wrist"),
        ("weight", 0.3),
        ("layer", 10),
    ],
}

# Hacked wristpad - provides SafetyNet access only, no map/combat prompt
HACKED_WRISTPAD = {
    "prototype_key": "hacked_wristpad",
    "key": "hacked wristpad",
    "typeclass": "typeclasses.items.Wristpad",
    "aliases": ["hacked wristpad", "wristpad", "pad", "pda"],
    "desc": "A compact wristpad with a flexible display screen. The device wraps around the forearm, its matte surface dotted with status LEDs and a small speaker grille. The firmware has clearly been modified - the SafetyNet access protocols have been unlocked. The standard mapping and system monitoring functions have been stripped out to avoid detection.",
    "attrs": [
        ("is_wristpad", True),
        ("is_hacked_wristpad", True),
        ("coverage", ["left_arm", "right_arm"]),
        ("worn_desc", "%N is wearing a compact wristpad with a flickering display"),
        ("weight", 0.3),
        ("layer", 10),
    ],
}

# Legacy: keep WRISTPAD as alias for HACKED_WRISTPAD for backward compatibility
WRISTPAD = HACKED_WRISTPAD

# High-end hacked wristpad variant - premium but still just SafetyNet
WRISTPAD_DELUXE = {
    "prototype_key": "wristpad_deluxe",
    "key": "Kiroshi TechBand Pro",
    "typeclass": "typeclasses.items.Wristpad",
    "aliases": ["techband", "kiroshi pad", "pro wristpad"],
    "desc": "A sleek Kiroshi TechBand Pro - the premium wristpad favored by corporate executives and high-end fixers. The flexible OLED display wraps seamlessly around the forearm, with haptic feedback so refined you can feel every notification. The brushed titanium frame houses top-of-the-line processing power and an encrypted quantum chip for secure communications. Despite its corporate origins, this unit has been jailbroken to access the open SafetyNet protocols. The premium features have been stripped out to avoid corporate tracking.",
    "attrs": [
        ("is_wristpad", True),
        ("is_hacked_wristpad", True),
        ("coverage", ["left_arm", "right_arm"]),
        ("worn_desc", "%N is wearing a sleek Kiroshi TechBand with a holographic display"),
        ("weight", 0.2),
        ("layer", 10),
    ],
}

# Fixed computer terminal
COMPUTER_TERMINAL = {
    "prototype_key": "computer_terminal",
    "key": "public access terminal",
    "typeclass": "typeclasses.items.ComputerTerminal",
    "aliases": ["terminal", "computer", "public terminal", "access terminal"],
    "desc": "A battered public access terminal bolted to the wall. The CRT monitor flickers occasionally, displaying the familiar SafetyNet interface. A mechanical keyboard sits below, its keys worn smooth from countless users. Despite its age, the machine provides a fast, reliable connection to the network. A faded municipal seal is barely visible on the casing.",
    "attrs": [
        ("is_computer", True),
        ("weight", 25.0),
    ],
    "locks": "get:false()",
}

# Personal computer terminal  
COMPUTER_PERSONAL = {
    "prototype_key": "computer_personal",
    "key": "personal computer",
    "typeclass": "typeclasses.items.ComputerTerminal",
    "aliases": ["pc", "desktop", "personal terminal"],
    "desc": "A cobbled-together personal computer station. Multiple monitors of different sizes and ages are connected to a tower case held together with zip ties and optimism. Cooling fans hum loudly, and LED strips cast the setup in shifting colors. Despite its chaotic appearance, the rig runs fast - clearly built by someone who knows their hardware.",
    "attrs": [
        ("is_computer", True),
        ("weight", 20.0),
    ],
    "locks": "get:false()",
}

# Portable laptop-style computer
PORTABLE_COMPUTER = {
    "prototype_key": "portable_computer",
    "key": "ruggedized laptop",
    "typeclass": "typeclasses.items.PortableComputer",
    "aliases": ["laptop", "portable", "rugged laptop"],
    "desc": "A ruggedized portable computer with a reinforced case designed to survive the streets of Kowloon. The screen is protected by scratch-resistant polymer, and the sealed keyboard can handle spilled synthohol or worse. A high-gain antenna extends from the back for improved SafetyNet reception even in signal-dead zones. Heavy, but reliable.",
    "attrs": [
        ("is_computer", True),
        ("weight", 3.5),
    ],
}

# Okama Gamebud - retro handheld communication device
# Note: Each device gets a random alias on creation. If you steal someone's Gamebud, you can post as them!
OKAMA_GAMEBUD = {
    "prototype_key": "okama_gamebud",
    "key": "Okama Gamebud",
    "typeclass": "typeclasses.items.OkamaGamebud",
    "aliases": ["gamebud", "okama", "game", "bud"],
    "desc": "Created in 1969 as a companion to the Okama Gamesphere, the Gamebud took on a life of its own in the Walled City due to its revolutionary ability to communicate with other Gamebuds within 0.002 square miles - roughly twice the size of Kowloon. Easy to jailbreak and hack, they have become the best way for the right kinds of people to communicate with others within the city, without ATT or Tri-Net breathing down their neck. It is a bubbly, hard plastic little thing with a transparent shell that fits in the palm of the hand.",
    "attrs": [
        ("is_gamebud", True),
        ("muted", False),
        ("current_page", 0),
        ("weight", 0.2),
    ],
}


# =============================================================================
# DISGUISE SYSTEM TEST PROTOTYPES
# =============================================================================
# These items provide various levels of anonymity for testing the disguise system.
# Item anonymity is simple - when worn and active, provides a descriptor instead of name.
# Items with hoods/masks slip easily during combat, running, shoving, etc.
# =============================================================================

# ----- HOODIES (Simple Anonymity - Slips Easily) -----

# Basic street hoodie - low-tier anonymity
ANONYMITY_HOODIE_BASIC = {
    "prototype_key": "anonymity_hoodie_basic",
    "key": "plain gray hoodie",
    "aliases": ["hoodie", "gray hoodie", "grey hoodie"],
    "typeclass": "typeclasses.items.Item",
    "desc": "A plain gray hoodie with a deep hood. The fabric is thin and worn, the kind of garment that disappears into any crowd. When the hood is pulled up, it casts the wearer's face in shadow, making identification difficult. Nothing special - just another face in the urban sprawl.",
    "attrs": [
        ("coverage", ["face", "head", "chest", "back", "abdomen", "left_arm", "right_arm"]),
        ("worn_desc", "A plain |xgray|n hoodie hanging loose, its worn fabric blending into the urban landscape"),
        ("layer", 2),
        ("color", "gray"),
        ("material", "cotton"),
        ("weight", 0.8),
        # Anonymity attributes - active when hood is up
        ("provides_anonymity", True),
        ("anonymity_active", False),  # Hood starts down
        ("anonymity_descriptor", "a hooded figure"),
    ],
}

# Black tactical hoodie - mid-tier anonymity
ANONYMITY_HOODIE_TACTICAL = {
    "prototype_key": "anonymity_hoodie_tactical",
    "key": "black tactical hoodie",
    "aliases": ["tac hoodie", "tactical hoodie", "black hoodie"],
    "typeclass": "typeclasses.items.Item",
    "desc": "A black tactical hoodie with reinforced seams and a deep, structured hood. The fabric is slightly thicker than standard, with hidden pockets and a drawstring to tighten the hood around the face. Popular with runners and anyone who needs to move fast while staying anonymous.",
    "attrs": [
        ("coverage", ["face", "head", "chest", "back", "abdomen", "left_arm", "right_arm"]),
        ("worn_desc", "A |xblack|n tactical hoodie with clean lines and utilitarian purpose"),
        ("layer", 2),
        ("color", "black"),
        ("material", "synthetic"),
        ("weight", 1.0),
        # Anonymity attributes
        ("provides_anonymity", True),
        ("anonymity_active", False),
        ("anonymity_descriptor", "a hooded stranger in black"),
    ],
}

# ----- MASKS (Simple Anonymity - More Secure) -----

# Surgical mask - minimal anonymity
ANONYMITY_MASK_SURGICAL = {
    "prototype_key": "anonymity_mask_surgical",
    "key": "surgical mask",
    "aliases": ["mask", "medical mask", "face mask"],
    "typeclass": "typeclasses.items.Item",
    "desc": "A disposable surgical mask in pale blue. It covers the nose and mouth, obscuring the lower half of the face. Common enough in Kowloon that no one looks twice - air quality here makes them practical as well as concealing.",
    "attrs": [
        ("coverage", ["face"]),
        ("worn_desc", "A pale blue surgical mask covering the lower face"),
        ("layer", 1),
        ("color", "blue"),
        ("material", "cloth"),
        ("weight", 0.05),
        # Anonymity attributes - always active when worn
        ("provides_anonymity", True),
        ("anonymity_active", True),
        ("anonymity_descriptor", "a masked individual"),
    ],
}

# Ballistic mask - high anonymity, intimidating
ANONYMITY_MASK_BALLISTIC = {
    "prototype_key": "anonymity_mask_ballistic",
    "key": "ballistic face mask",
    "aliases": ["ballistic mask", "tactical mask", "combat mask"],
    "typeclass": "typeclasses.items.Item",
    "desc": "A matte black ballistic face mask that covers everything from forehead to chin. The polymer shell is rated to stop small caliber rounds, but more importantly, it transforms the wearer into something inhuman - a blank, expressionless void where a face should be. Two dark eye slits stare out from the darkness.",
    "attrs": [
        ("coverage", ["face", "head"]),
        ("worn_desc", "A matte |xblack|n ballistic mask that reduces features to a featureless void"),
        ("layer", 2),
        ("color", "black"),
        ("material", "polymer"),
        ("weight", 0.5),
        ("armor_value", 2),
        # Anonymity attributes
        ("provides_anonymity", True),
        ("anonymity_active", True),
        ("anonymity_descriptor", "a masked figure in black"),
    ],
}

# Decorative Oni mask - distinctive but concealing
ANONYMITY_MASK_ONI = {
    "prototype_key": "anonymity_mask_oni",
    "key": "red oni mask",
    "aliases": ["oni mask", "demon mask", "red mask"],
    "typeclass": "typeclasses.items.Item",
    "desc": "A traditional oni mask rendered in lacquered red and gold. The demon face snarls with carved fangs and wild eyes, its expression frozen in supernatural rage. Horns curl back from the forehead. Beautiful craftsmanship - and completely concealing.",
    "attrs": [
        ("coverage", ["face"]),
        ("worn_desc", "A snarling |rred|n oni mask with golden accents and curved horns"),
        ("layer", 2),
        ("color", "red"),
        ("material", "lacquered wood"),
        ("weight", 0.3),
        # Anonymity attributes
        ("provides_anonymity", True),
        ("anonymity_active", True),
        ("anonymity_descriptor", "someone in an oni mask"),
    ],
}

# ----- HELMETS (High Anonymity - Hard to Remove) -----

# Motorcycle helmet - common, full coverage
ANONYMITY_HELMET_MOTORCYCLE = {
    "prototype_key": "anonymity_helmet_motorcycle",
    "key": "motorcycle helmet",
    "aliases": ["helmet", "moto helmet", "bike helmet"],
    "typeclass": "typeclasses.items.Item",
    "desc": "A full-face motorcycle helmet with a tinted visor. The shell is scuffed and worn from use, but structurally sound. With the visor down, the wearer becomes just another rider - anonymous behind dark polymer.",
    "attrs": [
        ("coverage", ["head", "face"]),
        ("worn_desc", "A scuffed motorcycle helmet with tinted visor"),
        ("layer", 3),
        ("color", "black"),
        ("material", "polymer"),
        ("weight", 1.5),
        ("armor_value", 3),
        # Anonymity attributes
        ("provides_anonymity", True),
        ("anonymity_active", True),
        ("anonymity_descriptor", "a helmeted rider"),
    ],
}

# Military helmet with visor
ANONYMITY_HELMET_MILITARY = {
    "prototype_key": "anonymity_helmet_military",
    "key": "military helmet",
    "aliases": ["combat helmet", "mil helmet", "tactical helmet"],
    "typeclass": "typeclasses.items.Item",
    "desc": "A military-grade combat helmet with integrated ballistic visor. The olive drab shell is scarred from use, and the visor can drop down to completely seal the face. Rails along the sides could mount additional equipment. This is the kind of gear that sees real combat.",
    "attrs": [
        ("coverage", ["head", "face"]),
        ("worn_desc", "An olive drab military helmet with ballistic visor"),
        ("layer", 3),
        ("color", "olive"),
        ("material", "composite"),
        ("weight", 2.0),
        ("armor_value", 5),
        # Anonymity attributes
        ("provides_anonymity", True),
        ("anonymity_active", True),
        ("anonymity_descriptor", "a helmeted soldier"),
    ],
}

# ----- DISGUISE KIT ITEMS (For Skill-Based Disguises) -----

# Basic makeup kit - entry level disguise tools
DISGUISE_KIT_BASIC = {
    "prototype_key": "disguise_kit_basic",
    "key": "basic makeup kit",
    "aliases": ["makeup kit", "cosmetics kit", "makeup"],
    "typeclass": "typeclasses.items.Item",
    "desc": "A compact makeup kit containing foundation in various skin tones, concealer, contour powder, and basic applicators. Nothing fancy, but enough to subtly alter facial features - soften jawlines, change apparent bone structure, hide distinguishing marks. The tools of minor transformation.",
    "attrs": [
        ("weight", 0.3),
        ("uses", 10),  # Limited uses before replacement needed
        ("disguise_bonus", 5),  # Small bonus to disguise skill checks
    ],
}

# Professional disguise kit - serious tools
DISGUISE_KIT_PROFESSIONAL = {
    "prototype_key": "disguise_kit_professional",
    "key": "professional disguise kit",
    "aliases": ["pro kit", "theatrical kit", "stage makeup"],
    "typeclass": "typeclasses.items.Item",
    "desc": "A professional-grade disguise kit in a leather case. Contains theatrical-quality makeup, prosthetic adhesive, spirit gum, skin-safe latex, color-matched foundation palettes, and precision brushes. With these tools and enough skill, a face becomes a canvas - age lines can be added or erased, features reshaped, entire identities constructed or destroyed.",
    "attrs": [
        ("weight", 1.0),
        ("uses", 25),
        ("disguise_bonus", 15),  # Significant bonus to disguise skill checks
    ],
}

# ----- WIGS (For Disguise Profiles) -----

# Basic synthetic wig
DISGUISE_WIG_BASIC = {
    "prototype_key": "disguise_wig_basic",
    "key": "synthetic wig",
    "aliases": ["wig", "fake hair", "hairpiece"],
    "typeclass": "typeclasses.items.Item",
    "desc": "A basic synthetic wig in a nondescript brown. The fibers are obviously artificial up close, but from a distance it passes. Comes with a mesh cap to hold natural hair in place. Good enough to change apparent hair color and style - bad enough to slip if handled roughly.",
    "attrs": [
        ("weight", 0.2),
        ("color", "brown"),
        ("provides_anonymity", False),  # Wigs add to disguise, not simple anonymity
        ("disguise_component", True),  # Used in building disguise profiles
        ("disguise_bonus", 5),
    ],
}

# High-quality human hair wig
DISGUISE_WIG_QUALITY = {
    "prototype_key": "disguise_wig_quality",
    "key": "human hair wig",
    "aliases": ["real wig", "quality wig", "natural wig"],
    "typeclass": "typeclasses.items.Item",
    "desc": "A high-quality wig made from real human hair. The lace front is virtually undetectable, and the hair moves naturally. Custom-fitted with an adjustable cap and secure clips. This is the kind of hairpiece worn by actors, cancer patients, and professionals who make people disappear.",
    "attrs": [
        ("weight", 0.15),
        ("color", "black"),
        ("provides_anonymity", False),
        ("disguise_component", True),
        ("disguise_bonus", 15),
    ],
}

# ----- SPECIALTY ITEMS -----

# Voice modulator - changes voice patterns
DISGUISE_VOICE_MODULATOR = {
    "prototype_key": "disguise_voice_modulator",
    "key": "voice modulator",
    "aliases": ["voice changer", "modulator", "voice mod"],
    "typeclass": "typeclasses.items.Item",
    "desc": "A small throat-mounted device that alters voice patterns in real-time. Can shift pitch, add or remove accents, and fundamentally change how a speaker sounds. Battery-powered with approximately eight hours of use. Illegal in most jurisdictions - possession implies intent to deceive.",
    "attrs": [
        ("weight", 0.1),
        ("battery_life", 8),  # Hours
        ("provides_anonymity", False),
        ("disguise_component", True),
        ("disguise_bonus", 10),
    ],
}

# Colored contact lenses
DISGUISE_CONTACTS = {
    "prototype_key": "disguise_contacts",
    "key": "colored contact lenses",
    "aliases": ["contacts", "colored contacts", "eye contacts"],
    "typeclass": "typeclasses.items.Item",
    "desc": "A sterile case containing a pair of colored contact lenses. These particular ones are a striking green, but the same manufacturer produces every natural eye color and some unnatural ones. Comfortable for extended wear, but still foreign objects sitting on your eyeballs.",
    "attrs": [
        ("weight", 0.01),
        ("color", "green"),
        ("provides_anonymity", False),
        ("disguise_component", True),
        ("disguise_bonus", 5),
    ],
}

# Prosthetic face appliances
DISGUISE_PROSTHETICS = {
    "prototype_key": "disguise_prosthetics",
    "key": "facial prosthetics",
    "aliases": ["prosthetics", "face prosthetics", "appliances"],
    "typeclass": "typeclasses.items.Item",
    "desc": "A set of medical-grade silicone facial prosthetics. Includes pieces to alter nose shape, add or hide scars, change apparent age, and modify facial structure. Each piece is custom-blend matched to common skin tones. Application requires skill and patience, but the results are transformative.",
    "attrs": [
        ("weight", 0.2),
        ("uses", 5),  # Limited applications before replacement
        ("provides_anonymity", False),
        ("disguise_component", True),
        ("disguise_bonus", 20),  # Significant bonus when used properly
    ],
}
