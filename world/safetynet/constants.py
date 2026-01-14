"""
SafetyNet Constants

Centralized constants for the SafetyNet system.
"""

# =============================================================================
# SYSTEM SETTINGS
# =============================================================================

# Post decay time in seconds (72 hours)
POST_DECAY_SECONDS = 72 * 60 * 60

# Maximum posts per feed page
POSTS_PER_PAGE = 10

# Maximum DMs to show per page
DMS_PER_PAGE = 10

# Maximum handles per character
MAX_HANDLES_PER_CHARACTER = None  # Unlimited

# Maximum passwords per handle
MAX_PASSWORDS_PER_HANDLE = 1  # One password only

# =============================================================================
# CONNECTION DELAYS (in seconds)
# =============================================================================

# Wristpad delays (slow, dial-up like)
WRISTPAD_DELAY_READ = 2.5
WRISTPAD_DELAY_POST = 3.0
WRISTPAD_DELAY_DM = 2.0
WRISTPAD_DELAY_SEARCH = 4.0
WRISTPAD_DELAY_HACK = 5.0
WRISTPAD_DELAY_LOGIN = 2.0

# Computer delays (fast)
COMPUTER_DELAY_READ = 0.3
COMPUTER_DELAY_POST = 0.5
COMPUTER_DELAY_DM = 0.3
COMPUTER_DELAY_SEARCH = 0.5
COMPUTER_DELAY_HACK = 1.0
COMPUTER_DELAY_LOGIN = 0.3

# =============================================================================
# ICE SETTINGS
# =============================================================================

# Base ICE rating for new accounts
DEFAULT_ICE_RATING = 1

# Maximum ICE rating
MAX_ICE_RATING = 100

# ICE difficulty modifiers
ICE_ONLINE_MODIFIER = -2  # Easier to hack when online
ICE_OFFLINE_MODIFIER = 3  # Harder to hack when offline

# =============================================================================
# HACKING SETTINGS
# =============================================================================

# Base difficulty for hacking (target number on skill check)
HACK_BASE_DIFFICULTY = 10

# Skill used for hacking
HACK_SKILL = "decking"

# Fallback stat if skill not found
HACK_STAT = "smrt"

# DM history access on successful hack (number of recent DMs)
HACK_DM_ACCESS_BASE = 5
HACK_DM_ACCESS_PER_MARGIN = 2  # Extra DMs per margin of success

# =============================================================================
# SYSTEM ACCOUNT
# =============================================================================

SYSTEM_HANDLE = "System"
SYSTEM_DISPLAY = "|w[SYSTEM]|n"

# =============================================================================
# FEED NAMES
# =============================================================================

# Default public feed
DEFAULT_FEED = "public"

# Available feeds
AVAILABLE_FEEDS = [
    "public",      # Main SafetyNet feed
]

# =============================================================================
# PASSWORD GENERATION
# =============================================================================

# Word lists for password generation (250+ words each to discourage brute forcing)
PASSWORD_WORDS_1 = [
    # Original cyberpunk
    "chrome", "neon", "cyber", "ghost", "shadow", "razor", "steel", "toxic",
    "viral", "glitch", "static", "pulse", "surge", "drift", "void", "black",
    "red", "blue", "green", "white", "dark", "bright", "cold", "hot", "fast",
    "slow", "deep", "high", "low", "wild", "calm", "sharp", "dull", "sweet",
    "bitter", "sour", "fresh", "stale", "raw", "cooked", "frozen", "melted",
    # Additional cyberpunk slang
    "braindead", "jacked", "iced", "burned", "flatlined", "fried", "rezzed",
    "borked", "scrambled", "nuked", "pwned", "hacked", "cracked", "spoofed",
    "mirrored", "phased", "lagged", "pinged", "buffered", "cached", "encoded",
    "encrypted", "decrypted", "compiled", "crashed", "patched", "modded",
    "tweaked", "tuned", "revved", "turbocharged", "supercharged", "overclocked",
    "underclocked", "throttled", "maxed", "pegged", "capped", "topped",
    # Chinese/East Asian loanwords (romanized)
    "kefu", "duobi", "shuajie", "kuafu", "dashi", "taiyang", "yueliang",
    "xingchen", "laohu", "dianlong", "longjing", "chadian", "huangjin",
    "baiyue", "heiyun", "baofeng", "jianfeng", "lithium", "tiefeng",
    # Technical/hacker terminology
    "packet", "payload", "vector", "exploit", "overflow", "injection",
    "rootkit", "malware", "ransomware", "trojan", "worm", "bot", "botnet",
    "ddos", "flood", "ping", "trace", "route", "gateway", "firewall", "proxy",
    "vpn", "tor", "darknet", "deepweb", "blockchain", "hash", "salt",
    "cipher", "algorithm", "protocol", "handshake", "session", "cookie",
    "cache", "buffer", "stack", "heap", "memory", "register", "cpu", "gpu",
    # Obscure/niche words
    "pellucid", "obfuscate", "lambent", "ephemeral", "tenebrous", "sepulchral",
    "querulous", "perfunctory", "perspicacious", "sagacious", "ossified",
    "incandescent", "luminous", "phosphorescent", "opalescent", "iridescent",
    "exiguous", "fulvous", "vitreous", "mucilaginous", "gelatinous",
    # More cyberpunk variations
    "megabyte", "gigabyte", "terabyte", "kilobit", "megabit", "gigabit",
    "quantum", "photonic", "sonic", "plasma", "antimatter", "biolume",
    "exotech", "implant", "neural", "cortex", "synapse", "dendrite",
    "axon", "soma", "ganglion", "medulla", "cortical", "subcortical",
    # Street/slang terms
    "choom", "fixer", "runner", "decker", "street", "alley", "gutter",
    "dumpster", "scrap", "trash", "waste", "refuse", "debris", "rubble",
    "ruin", "decay", "rust", "corrosion", "oxidation", "decomposition",
    "entropy", "chaos", "anarchy", "pandemonium", "bedlam", "tumult",
    # Additional technical depth
    "metadata", "telemetry", "latency", "bandwidth", "throughput", "bitrate",
    "framerate", "resolution", "scanline", "pixelated", "rasterized",
    "vectorized", "tessellated", "voxelated", "interpolated", "extrapolated",
    "modulated", "demodulated", "attenuated", "amplified", "filtered",
    # More exotic cyberpunk
    "samurai", "geisha", "shogun", "ronin", "yakuza", "bushido", "zaibatsu",
    "corporation", "megacorp", "syndicate", "cartel", "gang", "crew", "clan",
    # Sensory/atmospheric words
    "luminescent", "scintillating", "coruscating", "effulgent", "resplendent",
    "incisive", "penetrating", "piercing", "searing", "scalding", "blistering",
    # Final fill to reach 250+
    "analog", "digital", "binary", "hexadecimal", "octal", "decimal",
    "fractional", "logarithmic", "exponential", "polynomial", "algebraic",
    "geometric", "trigonometric", "harmonic", "melodic", "rhythmic",
    "syncopated", "arrhythmic", "discordant", "cacophonous", "euphonious"
]

PASSWORD_WORDS_2 = [
    # Original cyberpunk
    "runner", "decker", "fixer", "solo", "nomad", "corpo", "punk", "hacker",
    "ghost", "blade", "wire", "node", "grid", "mesh", "link", "port", "gate",
    "door", "wall", "floor", "roof", "street", "alley", "tower", "cube",
    "sphere", "line", "wave", "storm", "rain", "snow", "fire", "ice", "wind",
    "dust", "smoke", "mist", "fog", "haze", "glow", "spark", "flame", "ash",
    # Additional cyberpunk entities
    "syndicate", "nexus", "collective", "network", "system", "matrix",
    "mainframe", "server", "client", "terminal", "workstation", "console",
    "interface", "protocol", "daemon", "process", "thread", "kernel",
    "bootloader", "bios", "firmware", "uefi", "partition", "sector",
    # Chinese/Asian loanwords (romanized)
    "jianghu", "zhenren", "xuechan", "gushi", "jingying", "tianshen",
    "yumeng", "baishe", "heilong", "baijin", "taibai", "cangzhou",
    # Technical components
    "cpu", "gpu", "ram", "ssd", "hdd", "rom", "nvram", "cache",
    "transistor", "diode", "resistor", "capacitor", "inductor", "relay",
    "amplifier", "oscillator", "rectifier", "inverter", "modulator",
    "demodulator", "multiplexer", "demultiplexer", "encoder", "decoder",
    # Network/security concepts
    "firewall", "proxy", "gateway", "router", "switch", "hub", "modem",
    "adapter", "transceiver", "repeater", "bridge", "tunnel", "vlan",
    "subnet", "subnet", "broadcast", "multicast", "anycast", "unicast",
    "packet", "frame", "datagram", "segment", "cell", "payload",
    # Software/code terminology
    "algorithm", "function", "subroutine", "routine", "macro", "library",
    "framework", "sdk", "api", "endpoint", "callback", "handler",
    "exception", "interrupt", "signal", "trap", "breakpoint", "watchpoint",
    "register", "accumulator", "pointer", "reference", "variable", "constant",
    "array", "vector", "matrix", "tensor", "structure", "union", "class",
    # Infrastructure/locations
    "datacenter", "warehouse", "facility", "bunker", "vault", "fortress",
    "stronghold", "outpost", "checkpoint", "waystation", "junction",
    "intersection", "crossroads", "bridge", "passage", "corridor", "tunnel",
    # Dark/noir atmosphere
    "shadow", "darkness", "midnight", "twilight", "dusk", "dawn", "eclipse",
    "void", "abyss", "chasm", "pit", "hole", "cavity", "crevasse", "ravine",
    # Obscure technical terms
    "latch", "flipflop", "monostable", "astable", "bistable", "state",
    "machine", "automaton", "mechanism", "apparatus", "contraption",
    "device", "instrument", "implement", "tool", "gadget", "gizmo",
    # Cyberpunk/noir entities
    "syndicate", "network", "cartel", "organization", "establishment",
    "institution", "agency", "bureau", "department", "division", "branch",
    "chapter", "cell", "unit", "squad", "team", "crew", "band", "group",
    # Physical/sensory
    "phantom", "specter", "revenant", "apparition", "manifestation",
    "illusion", "mirage", "vision", "hallucination", "delusion",
    "thought", "mind", "consciousness", "awareness", "perception",
    # Extreme/intense concepts
    "inferno", "maelstrom", "typhoon", "earthquake", "eruption", "explosion",
    "implosion", "collapse", "cascade", "avalanche", "landslide", "rockslide",
    # Data/information
    "database", "repository", "archive", "repository", "collection",
    "library", "vault", "storage", "container", "repository", "depot",
    "inventory", "registry", "ledger", "manifest", "catalog", "directory",
    # Final fill for 250+
    "enigma", "cipher", "code", "secret", "mystery", "puzzle", "riddle",
    "paradox", "anomaly", "aberration", "deviance", "divergence",
    "variance", "threshold", "boundary", "frontier", "periphery",
    "perimeter", "circumference", "spectrum", "gradient", "continuum",
    "infinity", "eternity", "cosmos", "universe", "dimension", "realm",
    "domain", "territory", "region", "zone", "sector", "district",
    "quarter", "precinct", "borough", "ward", "parish", "circuit"
]

# =============================================================================
# MESSAGES
# =============================================================================

MSG_NO_DEVICE = "SafetyNet: No access device detected. Wristpad or computer required."
MSG_CONNECTING = "|y[SafetyNet] Connecting...|n"
MSG_CONNECTED = "|g[SafetyNet] Connected.|n"
MSG_NOT_LOGGED_IN = "|rSafetyNet: You must be logged in to do that. Use sn/login <handle> <password>.|n"
MSG_ALREADY_LOGGED_IN = "|ySafetyNet: Already logged in as {handle}. Use sn/logout first.|n"
MSG_LOGIN_SUCCESS = "|gSafetyNet: Logged in as {handle}.|n"
MSG_LOGIN_FAILED = "|rSafetyNet: Login failed. Invalid handle or password.|n"
MSG_LOGOUT_SUCCESS = "|ySafetyNet: Logged out.|n"
MSG_HANDLE_NOT_FOUND = "|rSafetyNet: Handle not found.|n"
MSG_POST_SUCCESS = "|gSafetyNet: Post submitted to {feed}.|n"
MSG_DM_SENT = "|gSafetyNet: Message sent to {handle}.|n"
MSG_DM_RECEIVED = "|c[SafetyNet DM from {handle}]|n {message}"
MSG_HACK_SUCCESS = "|gSafetyNet: Access granted. Trace complete.|n"
MSG_HACK_FAILED = "|rSafetyNet: Access denied. Connection terminated.|n"
MSG_HACK_ALERT = "|r[SafetyNet System Notice]|n Your account has been under attack. It is recommended you change your password."
MSG_PASSWORD_CHANGED = "|gSafetyNet: Password changed successfully.|n"
MSG_PASSWORD_ADDED = "|gSafetyNet: Additional password created.|n"
MSG_PASSWORD_REMINDER = "|rOOC: Save this password now. It will NOT be displayed again.|n"

# =============================================================================
# ONLINE/OFFLINE INDICATORS
# =============================================================================

INDICATOR_ONLINE = "|g[ONLINE]|n"
INDICATOR_OFFLINE = "|r[OFFLINE]|n"
