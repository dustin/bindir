#!/usr/bin/env python
"""

Copyright (c) 2004  Dustin Sallings <dustin@spy.net>
arch-tag: B06B5B4A-1007-11D9-9AEF-000A957659CC
"""

import sys
import os
import time
import stat

# Globals
# Nothing older than a week
max_age = 86400*7
# Debug off by default
_debug = False

def getLines(cmd):
    """Get a list of lines produced by the given command"""
    a=[]
    f=os.popen(cmd)
    l=f.readline()
    while l != '':
        a.append(l.strip())
        l=f.readline()
    f.close()
    return a

def debug(s):
    """Debug function for verbose output"""
    global _debug
    if _debug:
        print s

def getAge(path):
    """Get the age of the file or dir at the given path."""
    st=os.stat(path)
    now=time.time()
    age=now - st[stat.ST_CTIME]
    return age

def cleanup(revlib, arch, cat, branch, ver):
    """Look through the revisions at the given cat/branch/ver for deletables"""
    global max_age
    revs=getLines("tla library-revisions " + arch + "/" + ver)
    debug("\t\t\t\tFound: " + `revs`)
    # Never consider the most recent revision
    candidates=revs[:-1]
    if len(candidates) > 0:
        debug("\t\t\t\tCandidates: " + `candidates`)
        for r in candidates:
            debug("\t\t\t\tChecking " + r)
            age=getAge(os.path.join(revlib, arch, cat, branch, ver,
                ver + "--" + r))
            if age > max_age:
                torm=arch + "/" + ver + "--" + r
                print "***DELETING*** ", torm
                estat=os.system("tla library-remove " + torm)
                if estat != 0:
                    print "Non-zero exit status:  " + `estat`
    else:
        debug("\t\t\t\tNo candidates")

#
# The buck starts here.
#

if __name__ == '__main__':
    revlib=getLines("tla my-revision-library")[0]

    # Check for -v flag
    if len(sys.argv) > 1 and sys.argv[1] == '-v':
        _debug = True

    debug("Revlib: " + `revlib`)

    # Start digging...
    for arch in getLines("tla library-archives"):
        debug("Checking archive " + arch)
        for cat in getLines("tla library-categories " + arch):
            debug("\tcat: " + cat)
            for b in getLines("tla library-branches " + arch + "/" + cat):
                debug("\t\tbranch:  " + b)
                for v in getLines("tla library-versions " + arch + "/" + b):
                    debug("\t\t\tversion:  " + v)
                    cleanup(revlib, arch, cat, b, v)
