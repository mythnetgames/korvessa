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
    # Start the stamina ticker if not already running
    from evennia.scripts.models import ScriptDB
    from world.stamina_ticker import StaminaTicker
    
    ticker = ScriptDB.objects.filter(db_key="stamina_ticker").first()
    if not ticker:
        ticker, _ = StaminaTicker.create(key="stamina_ticker")
        if ticker and not ticker.is_active:
            ticker.start()
        print(f"[STARTUP] Created new stamina ticker: {ticker}")
    elif not ticker.is_active:
        ticker.start()
        print(f"[STARTUP] Started existing stamina ticker: {ticker}")
    else:
        print(f"[STARTUP] Stamina ticker already running: {ticker}, active={ticker.is_active}")
    
    # Start the survival ticker (hunger/thirst/intoxication)
    from world.survival.script import start_survival_ticker
    start_survival_ticker()
    
    # Start the IP grant script if not already running
    from scripts.ip_grant_script import IPGrantScript
    ip_grant = ScriptDB.objects.filter(db_key="ip_grant_script").first()
    if not ip_grant:
        ip_grant, _ = IPGrantScript.create(key="ip_grant_script")
        if ip_grant and not ip_grant.is_active:
            ip_grant.start()
        print(f"[STARTUP] Created new IP grant script: {ip_grant}")
    elif not ip_grant.is_active:
        ip_grant.start()
        print(f"[STARTUP] Started existing IP grant script: {ip_grant}")
    else:
        print(f"[STARTUP] IP grant script already running: {ip_grant}, active={ip_grant.is_active}")


def at_server_stop():
    """
    This is called just before the server is shut down, regardless
    of it is for a reload, reset or shutdown.
    """
    pass


def at_server_reload_start():
    """
    This is called only when server starts back up after a reload.
    """
    pass


def at_server_reload_stop():
    """
    This is called only time the server stops before a reload.
    """
    pass


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
