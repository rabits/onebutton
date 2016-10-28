#!/usr/bin/env python
# -*- coding: UTF-8 -*-

'''OneButtonDaemon v0.1

Author:      Rabit <home@rabits.org>
License:     GPL v3
Description: Daemon script to run OneButton
Required:    python2.7, python-cffi
'''

import sys, os

import Log as log
from OneButton import OneButton

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print("Usage: onebutton-daemon.py <user> <config.yaml>")
        log.error("Wrong arguments for OneButton Daemon")
        sys.exit(1)
    try:
        from pwd import getpwnam
        user = getpwnam(sys.argv[1])

        # Set user environment
        os.environ['USER'] = user.pw_name
        os.environ['HOME'] = user.pw_dir

        pid = open('/run/onebutton.pid', 'w+')
        logfile = open('/var/log/onebutton.log', 'a', 0)

        log.info("Daemonize with user %s %d" % (user.pw_name, user.pw_uid))

        import daemon
        with daemon.DaemonContext(uid=user.pw_uid,
                gid=user.pw_gid, initgroups=True,
                stdout=logfile,
                stderr=logfile,
                files_preserve=[pid],
                pidfile=pid,
                umask=0o022):
            onebutton = OneButton(sys.argv[2])
            onebutton.run()
    except:
        raise

    log.info("Exiting...")
    sys.exit(0)
