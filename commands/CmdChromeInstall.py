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
        # Find chrome in installer's inventory by shortname (from chrometable)
        from world.chrometable import CHROME_TABLE
        chrome_entry = next((c for c in CHROME_TABLE if c["shortname"].lower() == shortname.lower()), None)
        if not chrome_entry:
            self.caller.msg(f"No chrome definition found for '{shortname}'.")
            return
        # Match inventory item by prototype shortname
        chrome = None
        for obj in self.caller.contents:
            obj_shortname = getattr(obj.db, "shortname", None)
            if obj_shortname and obj_shortname.lower() == shortname.lower():
                chrome = obj
                break
        if not chrome:
            self.caller.msg(f"You do not have '{chrome_entry['name']}' in your inventory.")
            return
        # Remove chrome from installer's inventory
        chrome.location = None
        # Install chrome: add to target's installed chrome list (ndb)
        if not hasattr(target.ndb, "installed_chrome") or target.ndb.installed_chrome is None:
            target.ndb.installed_chrome = []
        target.ndb.installed_chrome.append(chrome)
        # Apply chrome stat bonus (example: +2 BODY)
        # You should define chrome stat effects elsewhere; here is a placeholder
        if (
            hasattr(chrome, "db") and hasattr(chrome.db, "stat") and chrome.db.stat and isinstance(chrome.db.stat, str)
            and hasattr(chrome.db, "bonus")
        ):
            stat = chrome.db.stat
            bonus = chrome.db.bonus
            current = getattr(target, stat, 0)
            setattr(target, stat, current + bonus)
        self.caller.msg(f"You install '{shortname}' into {target.key}. Surgery auto-succeeds for builders.")
        target.msg(f"{self.caller.key} installs '{shortname}' into you. You feel different.")

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
        # Remove chrome from target's installed chrome list
        chrome_list.remove(chrome)
        # Remove chrome stat bonus
        if hasattr(chrome, "db") and hasattr(chrome.db, "stat") and hasattr(chrome.db, "bonus"):
            stat = chrome.db.stat
            bonus = chrome.db.bonus
            current = getattr(target, stat, 0)
            setattr(target, stat, current - bonus)
        # Place chrome in uninstalling character's inventory
        chrome.location = self.caller
        self.caller.msg(f"You uninstall '{shortname}' from {target.key}. Surgery auto-succeeds for builders.")
        target.msg(f"{self.caller.key} uninstalls '{shortname}' from you. You feel different.")
