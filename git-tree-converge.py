#!/usr/bin/env python
"""
Figure out where trees converge in branches when there may be no similar
ancestry.

Copyright (c) 2008  Dustin Sallings <dustin@spy.net>
"""

from __future__ import with_statement

import sys
import difflib
import subprocess
import collections

trees={}
commit_map={}
commits={}

def load_list(branch):
    t=[]
    trees[branch] = t
    cm = collections.defaultdict(list)
    commit_map[branch] = cm

    args = ['git', 'log', '--pretty=format:%T %h', branch]

    sub=subprocess.Popen(args, stdout=subprocess.PIPE, close_fds=True)

    for l in sub.stdout:
        a=l.strip().split()
        commit = a[-1]
        treeHash = a[0]
        t.append(treeHash)
        cm[treeHash].append(commit)

def load_commits():
    args = ['git', 'log', '--all',
        '--pretty=format:%h%x00%an%x00%ae%x00%cn%x00%ce%x00%s']
    sub=subprocess.Popen(args, stdout=subprocess.PIPE, close_fds=True)

    for l in sub.stdout:
        hash, an, ae, cn, ce, desc=l.strip().split("\0")
        commits[hash] = (an, ae, cn, ce, desc)

def commit_info(h):
    branch_a, ae, cn, ce, desc = commits[h]
    if branch_a == cn:
        ai = branch_a
    else:
        ai = "%s (committed by %s)" % (branch_a, cn)
    cl = ('<a href="http://github.com/dustin/memcached/commit/%s">%s</a>'
        % (h, h))
    return "<div>%s: %s<br/>%s</div>" % (cl, ai, desc)

def htmlify_col_list(col):
    if col:
        return "\n".join((commit_info(c) for c in col))
    else:
        return "&nbsp;"

def mk_row(cls, l, r):
    return ("<tr class='%s'><td class='left'>%s</td><td class='right'>%s</td></tr>" % (cls, l, r))

def emit_differing_lists(op, left_col, right_col):
    print mk_row(op, htmlify_col_list(left_col), htmlify_col_list(right_col))

def emit_identical_lists(op, left_col, right_col):
    for l,r in zip(left_col, right_col):
        print mk_row(op, commit_info(l), commit_info(r))

if __name__ == '__main__':
    branch_a, branch_b = sys.argv[1:]

    load_commits()
    load_list(branch_a)
    load_list(branch_b)

    print """<html>
        <head>
            <title>Tree Comparison from %(branch_a)s to %(branch_b)s</title>
            <style type="text/css">
                html {
                    font-family: verdana;
                }
                table tr, table td {
			border: solid 1px;
			vertical-align: top
                }
                .delete .left, .replace .left {
			background: #faa;
			color black;
                }
                .insert .right, .replace .right {
			background: #afa;
			color black;
                }
                table tr td div {
			border: solid 1px;
			padding: 0;
			margin: 0;
                }
            </style>
        </head>
        <body>
        <table>
        <thead>
            <tr>
                <th>%(branch_a)s</th>
                <th>%(branch_b)s</th>
            </tr>
        </thead>
        <tbody>
""" % {'branch_a': branch_a, 'branch_b': branch_b}
    a=trees[branch_a]
    b=trees[branch_b]
    sm = difflib.SequenceMatcher(a=a, b=b)
    for op, i1, i2, j1, j2 in sm.get_opcodes():
        left=a[i1:i2]
        right=b[j1:j2]

        left_col=[commit_map[branch_a][tree].pop() for tree in left]
        right_col=[commit_map[branch_b][tree].pop() for tree in right]

        if op == 'equal':
            emit_identical_lists(op, left_col, right_col)
        else:
            emit_differing_lists(op, left_col, right_col)

    print "</tbody></table></body></html>"
