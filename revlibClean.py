#!/usr/bin/env python
"""

Copyright (c) 2004  Dustin Sallings <dustin@spy.net>
arch-tag: B06B5B4A-1007-11D9-9AEF-000A957659CC
"""

import getopt
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
    f=os.popen(cmd)
    a=[l.strip() for l in f]
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

def libRemove(torm):
    print "***DELETING*** ", torm
    estat=os.system("tla library-remove " + torm)
    if estat != 0:
        print "Non-zero exit status:  " + `estat`

# Remove all candidates
def checkCandidateAll(revlib, arch, cat, branch, ver, rev):
    torm=arch + "/" + ver + "--" + rev
    libRemove(torm)

# Remove candidates interactively
def checkCandidateInteractive(revlib, arch, cat, branch, ver, rev):
    torm=arch + "/" + ver + "--" + rev
    sys.stdout.write("Should we remove " + torm + " [y/n] ")
    sys.stdout.flush()
    shouldGo=sys.stdin.readline()
    if shouldGo[0] == 'y':
        libRemove(torm)

# Remove candidates automatically
def checkCandidateAuto(revlib, arch, cat, branch, ver, rev):
    age=getAge(os.path.join(revlib, arch, cat, branch, ver,
        ver + "--" + rev))
    if age > max_age:
        torm=arch + "/" + ver + "--" + rev
        libRemove(torm)

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
            checkCandidate(revlib, arch, cat, branch, ver, r)
    else:
        debug("\t\t\t\tNo candidates")

# This will contain the function that does the candidate checking
checkCandidate = checkCandidateAuto

#
# The buck starts here.
#

if __name__ == '__main__':
    revlib=getLines("tla my-revision-library")[0]

    opts, args=getopt.getopt(sys.argv[1:], 'via')

    for opt in opts:
        if opt[0] == '-v':
            _debug = True
        elif opt[0] == '-i':
            checkCandidate = checkCandidateInteractive
        elif opt[0] == '-a':
            checkCandidate = checkCandidateAll

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
