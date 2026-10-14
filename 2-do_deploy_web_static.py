#!/usr/bin/python3
"""Fabric script that distributes an archive to the web servers."""
import os
try:
    from fabric.api import env, put, run
    FABRIC_1 = True
except ImportError:
    from fabric import Connection
    FABRIC_1 = False

    class _Env:
        """Minimal stand-in for fabric.api.env on Fabric 2+."""
        hosts = []
        user = None
        key_filename = None

    env = _Env()

env.hosts = ['192.0.2.1', '192.0.2.2']


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
