"""
Server startstop hooks

This module contains functions called by Evennia at various
points during its startup, reload and shutdown sequence. It
allows for customizing the server operation as desired.

This module must contain at least these global functions:

at_server_init()
at_server_start()
at_server_stop()
at_server_reload_start()
at_server_reload_stop()
at_server_cold_start()
at_server_cold_stop()

"""


def at_server_init():
    """
    This is called first as the server is starting up, regardless of how.
    """
    pass


def at_server_start():
    """
    This is called every time the server starts up, regardless of
    how it was shut down.
    """
    from evennia import GLOBAL_SCRIPTS
    
    # Broadcast Watcher message on server start
    msg = "|y[WORLD]|n The world shakes as the Watcher turns His attention to mortal affairs."
    GLOBAL_SCRIPTS.broadcast_message(msg)


def at_server_stop():
    """
    This is called just before the server is shut down, regardless
    of it is for a reload, reset or shutdown.
    """
    from evennia import GLOBAL_SCRIPTS
    
    # Broadcast Watcher message on server stop
    msg = "|y[WORLD]|n The shaking stops as the Watcher closes His eye from the mortal plane."
    GLOBAL_SCRIPTS.broadcast_message(msg)


def at_server_reload_start():
    """
    This is called only when server starts back up after a reload.
    """
    from evennia import GLOBAL_SCRIPTS
    
    # Broadcast Watcher message on reload start
    msg = "|y[WORLD]|n The world shakes as the Watcher turns His attention to mortal affairs."
    GLOBAL_SCRIPTS.broadcast_message(msg)


def at_server_reload_stop():
    """
    This is called only time the server stops before a reload.
    """
    from evennia import GLOBAL_SCRIPTS
    
    # Broadcast Watcher message on reload stop
    msg = "|y[WORLD]|n The shaking stops as the Watcher closes His eye from the mortal plane."
    GLOBAL_SCRIPTS.broadcast_message(msg)


def at_server_cold_start():
    """
    This is called only when the server starts "cold", i.e. after a
    shutdown or a reset.
    """
    pass


def at_server_cold_stop():
    """
    This is called only when the server goes down due to a shutdown or
    reset.
    """
    pass
