#!/usr/bin/python3
"""Fabric script that creates and distributes an archive to the web servers."""
import os
from datetime import datetime
try:
    from fabric.api import env, local, put, run
    FABRIC_1 = True
except ImportError:
    from fabric import Connection
    from invoke import run as local
    FABRIC_1 = False

    class _Env:
        """Minimal stand-in for fabric.api.env on Fabric 2+."""
        hosts = []
        user = None
        key_filename = None

    env = _Env()

env.hosts = ['192.0.2.1', '192.0.2.2']

_archive = []


def do_pack():
    """Packs web_static into versions/web_static_<timestamp>.tgz.

    Returns the archive path on success, otherwise None.
    """
    if not os.path.isdir("web_static"):
        return None
    date = datetime.now().strftime("%Y%m%d%H%M%S")
    archive_path = "versions/web_static_{}.tgz".format(date)
    try:
        local("mkdir -p versions")
        print("Packing web_static to {}".format(archive_path))
        result = local("tar -cvzf {} web_static".format(archive_path))
        if getattr(result, "failed", False):
            return None
        return archive_path
    except (Exception, SystemExit):
        return None


def _deploy(put, run, archive_path):
    """Runs the deployment steps with the given put and run functions."""
    file_name = os.path.basename(archive_path)
    name = file_name.split(".")[0]
    release = "/data/web_static/releases/{}/".format(name)
    put(archive_path, "/tmp/{}".format(file_name))
    run("mkdir -p {}".format(release))
    run("tar -xzf /tmp/{} -C {}".format(file_name, release))
    run("rm /tmp/{}".format(file_name))
    run("mv {0}web_static/* {0}".format(release))
    run("rm -rf {}web_static".format(release))
    run("rm -rf /data/web_static/current")
    run("ln -s {} /data/web_static/current".format(release))
    print("New version deployed!")


def do_deploy(archive_path):
    """Distributes an archive to the web servers.

    Returns True if all operations succeed, otherwise False.
    """
    if not os.path.exists(archive_path):
        return False
    try:
        if FABRIC_1:
            _deploy(put, run, archive_path)
        else:
            for host in env.hosts:
                kwargs = {}
                if env.key_filename:
                    kwargs["key_filename"] = env.key_filename
                conn = Connection(host, user=env.user, connect_kwargs=kwargs)
                _deploy(conn.put, conn.run, archive_path)
        return True
    except (Exception, SystemExit):
        return False


def deploy():
    """Creates an archive and distributes it to the web servers.

    The archive is created once and reused for every host.
    Returns the result of do_deploy, or False if packing failed.
    """
    if not _archive:
        _archive.append(do_pack())
    archive_path = _archive[0]
    if archive_path is None:
        return False
    return do_deploy(archive_path)
