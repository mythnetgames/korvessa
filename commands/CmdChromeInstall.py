from evennia import Command

class CmdChromeInstall(Command):
    """
    Install a chrome item into a target character.
    Usage:
        chromeinstall <shortname> in <person>
    Builder+ automatically pass the surgery/science check.
    The chrome is removed from your inventory and installed in the target, updating their stats.
    """
    key = "chromeinstall"
    locks = "cmd:perm(Builder)"
    help_category = "Admin"

    def func(self):
        if not self.args or " in " not in self.args:
            self.caller.msg("Usage: chromeinstall <shortname> in <person>")
            return
        shortname, person = self.args.split(" in ", 1)
        shortname = shortname.strip()
        person = person.strip()
        target = self.caller.search(person)
        if not target:
            self.caller.msg(f"Target '{person}' not found.")
            return
        
        # Find chrome in installer's inventory by shortname
        chrome = None
        for obj in self.caller.contents:
            obj_shortname = getattr(obj.db, "shortname", None)
            if obj_shortname and obj_shortname.lower() == shortname.lower():
                chrome = obj
                break
        
        if not chrome:
            self.caller.msg(f"You do not have '{shortname}' in your inventory.")
            return
        
        # Get chrome prototype definition for stat bonuses
        chrome_proto = self._get_chrome_prototype(shortname)
        if not chrome_proto:
            self.caller.msg(f"Chrome definition not found for '{shortname}'.")
            return
        
        # Get chrome long name
        chrome_name = chrome_proto.get("key", shortname)
        
        # Remove chrome from installer's inventory
        chrome.location = None
        
        # Install chrome: add to target's installed chrome list (ndb)
        if not hasattr(target.ndb, "installed_chrome") or target.ndb.installed_chrome is None:
            target.ndb.installed_chrome = []
        target.ndb.installed_chrome.append(chrome)
        
        # Store chrome info in character's db for stats display
        chrome_list = target.db.installed_chrome_list
        if chrome_list is None:
            chrome_list = []
        chrome_entry = {
            "name": chrome_name,
            "shortname": shortname,
            "slot": chrome_proto.get("chrome_slot"),
            "type": chrome_proto.get("chrome_type"),
            "empathy_cost": chrome_proto.get("empathy_cost", 0)
        }
        chrome_list.append(chrome_entry)
        target.db.installed_chrome_list = chrome_list
        
        # Stat name mapping (long name -> short name used by character)
        stat_map = {
            "smarts": "smrt",
            "willpower": "will",
            "edge": "edge",
            "reflexes": "ref",
            "body": "body",
            "dexterity": "dex",
            "empathy": "emp",
            "technique": "tech",
        }
        
        # Apply chrome stat bonuses from prototype
        if chrome_proto.get("buffs") and isinstance(chrome_proto["buffs"], dict):
            for stat, bonus in chrome_proto["buffs"].items():
                # Map to short stat name
                short_stat = stat_map.get(stat.lower(), stat)
                max_stat = f"max_{short_stat}"
                # Get current max value from character
                current_max = getattr(target, max_stat, None)
                if current_max is None:
                    current_max = 5
                # Increase max stat
                setattr(target.db, max_stat, current_max + bonus)
                # Also increase current stat
                current_val = getattr(target, short_stat, None)
                if current_val is None:
                    current_val = current_max
                setattr(target.db, short_stat, current_val + bonus)
                self.caller.msg(f"|yDEBUG: Applied +{bonus} to {short_stat} (now {current_val + bonus}/{current_max + bonus})|n")
        
        # Apply empathy cost (reduce max empathy)
        empathy_cost = chrome_proto.get("empathy_cost", 0)
        self.caller.msg(f"|yDEBUG: Empathy cost from proto: {empathy_cost}|n")
        if empathy_cost:
            current_max_emp = getattr(target, "max_emp", None)
            self.caller.msg(f"|yDEBUG: Current max_emp before: {current_max_emp}|n")
            if current_max_emp is None:
                current_max_emp = 10
            target.db.max_emp = current_max_emp - empathy_cost
            self.caller.msg(f"|yDEBUG: New max_emp after: {target.db.max_emp}|n")
            # Also reduce current empathy if it exceeds new max
            current_emp = getattr(target, "emp", None)
            if current_emp is None:
                current_emp = target.db.max_emp
            if current_emp > target.db.max_emp:
                target.db.emp = target.db.max_emp
        
        self.caller.msg(f"You install '{chrome_name}' into {target.key}. Surgery auto-succeeds for builders.")
        target.msg(f"{self.caller.key} installs '{chrome_name}' into you. You feel different.")
    
    def _get_chrome_prototype(self, shortname):
        """Get chrome prototype definition by shortname."""
        from world import chrome_prototypes
        
        # Get all prototype dictionaries from the module
        for name in dir(chrome_prototypes):
            obj = getattr(chrome_prototypes, name)
            if isinstance(obj, dict) and obj.get("shortname", "").lower() == shortname.lower():
                return obj
        return None


class CmdChromeUninstall(Command):
    """
    Uninstall a chrome item from a target character.
    Usage:
        chromeuninstall <shortname> from <person>
    Builder+ automatically pass the surgery/science check.
    The chrome is removed from the target and placed in your inventory, updating their stats.
    """
    key = "chromeuninstall"
    locks = "cmd:perm(Builder)"
    help_category = "Admin"

    def func(self):
        if not self.args or " from " not in self.args:
            self.caller.msg("Usage: chromeuninstall <shortname> from <person>")
            return
        shortname, person = self.args.split(" from ", 1)
        shortname = shortname.strip()
        person = person.strip()
        target = self.caller.search(person)
        if not target:
            self.caller.msg(f"Target '{person}' not found.")
            return
        
        # Find chrome in target's installed chrome list (handle NoneType and match by shortname)
        chrome_list = getattr(target.ndb, "installed_chrome", None)
        if not chrome_list or not isinstance(chrome_list, list):
            self.caller.msg(f"{target.key} does not have any chrome installed.")
            return
        
        chrome = None
        for obj in chrome_list:
            obj_shortname = getattr(obj.db, "shortname", None)
            if obj_shortname and obj_shortname.lower() == shortname.lower():
                chrome = obj
                break
        
        if not chrome:
            self.caller.msg(f"{target.key} does not have '{shortname}' installed.")
            return
        
        # Get chrome prototype definition for stat reversal
        chrome_proto = self._get_chrome_prototype(shortname)
        if not chrome_proto:
            self.caller.msg(f"Chrome definition not found for '{shortname}'.")
            return
        
        # Get chrome long name
        chrome_name = chrome_proto.get("key", shortname)
        
        # Remove chrome from target's installed chrome list
        chrome_list.remove(chrome)
        
        # Remove chrome from stats display list
        chrome_list_db = target.db.installed_chrome_list
        if chrome_list_db and isinstance(chrome_list_db, list):
            target.db.installed_chrome_list = [c for c in chrome_list_db if c.get("shortname", "").lower() != shortname.lower()]
        
        # Stat name mapping (long name -> short name used by character)
        stat_map = {
            "smarts": "smrt",
            "willpower": "will",
            "edge": "edge",
            "reflexes": "ref",
            "body": "body",
            "dexterity": "dex",
            "empathy": "emp",
            "technique": "tech",
        }
        
        # Remove chrome stat bonuses
        if chrome_proto.get("buffs") and isinstance(chrome_proto["buffs"], dict):
            for stat, bonus in chrome_proto["buffs"].items():
                # Map to short stat name
                short_stat = stat_map.get(stat.lower(), stat)
                max_stat = f"max_{short_stat}"
                # Get current max value from character
                current_max = getattr(target, max_stat, None)
                if current_max is not None:
                    setattr(target.db, max_stat, current_max - bonus)
                # Also decrease current stat
                current_val = getattr(target, short_stat, None)
                if current_val is not None:
                    setattr(target.db, short_stat, current_val - bonus)
        
        # Restore empathy cost (increase max empathy)
        empathy_cost = chrome_proto.get("empathy_cost", 0)
        if empathy_cost:
            current_max_emp = getattr(target, "max_emp", None)
            if current_max_emp is None:
                current_max_emp = 10
            target.db.max_emp = current_max_emp + empathy_cost
        
        # Move chrome to installer's inventory
        chrome.location = self.caller
        
        self.caller.msg(f"You uninstall '{chrome_name}' from {target.key}. Surgery auto-succeeds for builders.")
        target.msg(f"{self.caller.key} uninstalls '{chrome_name}' from you. You feel different.")
    
    def _get_chrome_prototype(self, shortname):
        """Get chrome prototype definition by shortname."""
        from world import chrome_prototypes
        
        # Get all prototype dictionaries from the module
        for name in dir(chrome_prototypes):
            obj = getattr(chrome_prototypes, name)
            if isinstance(obj, dict) and obj.get("shortname", "").lower() == shortname.lower():
                return obj
        return None
