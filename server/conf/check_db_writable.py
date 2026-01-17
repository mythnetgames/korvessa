"""
Utility to inspect the configured Django/Evennia database and suggest
permission-fix commands for SQLite files. Run this on the host where the
game runs to get ownership and permission guidance.

Usage:
    python server/conf/check_db_writable.py

This script only prints suggestions; it does not change permissions.
"""
from pathlib import Path
import os
import sys

def main():
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'server.conf.settings')
    try:
        import django
        django.setup()
    except Exception as e:
        print("Failed to setup Django environment:", e)
        sys.exit(1)

    from django.conf import settings

    db = getattr(settings, 'DATABASES', {}).get('default', {})
    engine = db.get('ENGINE', '')

    print("Database engine:", engine or '<not configured>')

    if not engine or 'sqlite3' not in engine:
        print("This helper currently only handles sqlite3 databases.")
        print("DATABASES['default']:", db)
        return

    name = db.get('NAME')
    if not name or name == ':memory:':
        print("SQLite database path is not set or is in-memory.")
        return

    path = Path(str(name)).expanduser()
    print("Configured SQLite DB path:", path)

    # Parent dir info
    parent = path.parent
    print("Parent directory:", parent)

    exists = path.exists()
    print("Exists:", exists)

    try:
        st = path.stat() if exists else parent.stat()
        mode = oct(st.st_mode & 0o777)
        uid = getattr(st, 'st_uid', None)
        gid = getattr(st, 'st_gid', None)
        owner = None
        group = None
        try:
            import pwd, grp
            owner = pwd.getpwuid(uid).pw_name if uid is not None else None
            group = grp.getgrgid(gid).gr_name if gid is not None else None
        except Exception:
            # On non-POSIX systems, pwd/grp may be unavailable
            owner = uid
            group = gid

        print(f"Current perms: {mode}  owner: {owner}  group: {group}")
    except Exception as e:
        print("Failed to stat file/dir:", e)

    print('\nSuggested fix commands (run as root or with sudo on Linux hosts):')
    print('# If the evennia process runs as user "evennia":')
    print('sudo chown evennia:evennia "{}"'.format(path))
    print('sudo chmod 664 "{}"'.format(path))
    print('sudo chown -R evennia:evennia "{}"'.format(parent))
    print('sudo chmod 775 "{}"'.format(parent))

    print('\n# If you prefer to make the DB owner your current user (safe for single-user setups):')
    print('sudo chown $(id -u -n):$(id -g -n) "{}"'.format(path))
    print('sudo chmod 664 "{}"'.format(path))

    print('\nIf the filesystem is mounted read-only (for example inside some containers),')
    print('you must ensure the mount is writable or move the DB to a writable path and update settings.DATABASES["default"]["NAME"] accordingly.')


if __name__ == '__main__':
    main()
