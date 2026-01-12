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
    """
    player = session.get_puppet_or_player()
    if hasattr(player, 'ndb') and hasattr(player.ndb, 'get_input') and player.ndb.get_input:
        # Call the input handler and consume the input
        handler = player.ndb.get_input
        # Remove handler before calling to avoid recursion if handler fails
        del player.ndb.get_input
        handler(player, cmdname)
        return
    # Fallback: normal command parsing
    session.execute_cmd(cmdname, *args, **kwargs)
