from evennia import DefaultObject

class Door(DefaultObject):
    """A door object that can be attached to an exit."""
    def at_object_creation(self):
        self.db.is_open = False
        self.db.is_locked = False
        self.db.keypad = None  # Reference to attached keypad lock
        self.db.lock = None    # Reference to attached lock

    def open(self, caller):
        if self.db.is_locked:
            caller.msg("The door is locked.")
            return False
        if self.db.keypad and not self.db.keypad.is_unlocked:
            caller.msg("The keypad is locked.")
            return False
        self.db.is_open = True
        caller.msg("You open the door.")
        return True

    def close(self, caller):
        self.db.is_open = False
        caller.msg("You close the door.")
        return True

    def attach_lock(self, lock):
        self.db.lock = lock

    def attach_keypad(self, keypad):
        self.db.keypad = keypad

class Lock(DefaultObject):
    """A simple lock object for doors."""
    def at_object_creation(self):
        self.db.is_locked = True
        self.db.key_id = None  # Key required to unlock

    def unlock(self, key, caller):
        if key and key.db.key_id == self.db.key_id:
            self.db.is_locked = False
            caller.msg("You unlock the lock.")
            return True
        caller.msg("The key doesn't fit.")
        return False

    def lock(self, caller):
        self.db.is_locked = True
        caller.msg("You lock the lock.")
        return True

class KeypadLock(DefaultObject):
    """A programmable keypad lock for doors."""
    def at_object_creation(self):
        self.db.combination = "00000000"
        self.db.is_unlocked = False

    def program_combo(self, new_combo, caller):
        if caller.check_permstring("Builder"):
            if len(new_combo) == 8 and new_combo.isdigit():
                self.db.combination = new_combo
                caller.msg(f"Keypad combination set to {new_combo}.")
                return True
            caller.msg("Combination must be 8 digits.")
            return False
        caller.msg("You lack permission to program the keypad.")
        return False

    def enter_combo(self, combo, caller):
        if combo == self.db.combination:
            self.db.is_unlocked = True
            caller.msg("Keypad unlocked.")
            return True
        caller.msg("Incorrect combination.")
        return False

    def show_combo(self, caller):
        if caller.check_permstring("Builder"):
            caller.msg(f"Keypad combo: {self.db.combination}")
        else:
            caller.msg("You lack permission to view the combo.")

    def hack(self, caller):
        """Future hook for hacking integration."""
        caller.msg("Hacking attempt placeholder.")
        return False
