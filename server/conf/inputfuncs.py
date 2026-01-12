"""
Input functions

Input functions are always called from the client (they handle server
input, hence the name).

This module is loaded by being included in the
`settings.INPUT_FUNC_MODULES` tuple.

All *global functions* included in this module are considered
input-handler functions and can be called by the client to handle
input.

An input function must have the following call signature:

    cmdname(session, *args, **kwargs)

Where session will be the active session and *args, **kwargs are extra
incoming arguments and keyword properties.

A special command is the "default" command, which is will be called
when no other cmdname matches. It also receives the non-found cmdname
as argument.

    default(session, cmdname, *args, **kwargs)

"""

# def oob_echo(session, *args, **kwargs):
#     """
#     Example echo function. Echoes args, kwargs sent to it.
#
#     Args:
#         session (Session): The Session to receive the echo.
#         args (list of str): Echo text.
#         kwargs (dict of str, optional): Keyed echo text
#
#     """
#     session.msg(oob=("echo", args, kwargs))
#

def default(session, cmdname, *args, **kwargs):
    """
    Handles commands without a matching inputhandler func.
    Checks for ndb.get_input on the player/character and calls it if present.
    Adds debug logging to confirm handler is called.
    """
    player = session.get_puppet_or_player()
    # Debug: log inputfuncs default call
    try:
        from evennia.comms.models import ChannelDB
        debugchan = ChannelDB.objects.get_channel("Splattercast")
        debugchan.msg(f"[inputfuncs.py] default() called: cmdname={cmdname}, player={player}")
    except Exception:
        pass
    if hasattr(player, 'ndb') and hasattr(player.ndb, 'get_input') and player.ndb.get_input:
        handler = player.ndb.get_input
        try:
            del player.ndb.get_input
        except Exception:
            pass
        # Debug: log handler call
        try:
            from evennia.comms.models import ChannelDB
            debugchan = ChannelDB.objects.get_channel("Splattercast")
            debugchan.msg(f"[inputfuncs.py] get_input handler found, calling handler for {player} with input: {cmdname}")
        except Exception:
            pass
        handler(player, cmdname)
        return
    # Fallback: normal command parsing
    session.execute_cmd(cmdname, *args, **kwargs)
