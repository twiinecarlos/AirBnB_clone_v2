#!/usr/bin/python3
"""Fabric script that generates a .tgz archive of the web_static folder."""
from datetime import datetime
from fabric.api import local


def do_pack():
    """Packs web_static into versions/web_static_<timestamp>.tgz.

    Returns the archive path on success, otherwise None.
    """
    date = datetime.now().strftime("%Y%m%d%H%M%S")
    archive_path = "versions/web_static_{}.tgz".format(date)
    try:
        local("mkdir -p versions")
        print("Packing web_static to {}".format(archive_path))
        result = local("tar -cvzf {} web_static".format(archive_path))
        if result.failed:
            return None
        return archive_path
    except Exception:
        return None
