#!/usr/bin/env python
"""

Copyright (c) 2003  Dustin Sallings <dustin@spy.net>
$Id: skeleton.py,v 1.2 2003/01/03 08:43:26 dustin Exp $
"""

import sys

for v in sys.argv[1:]:
	v=float(v)
	print (v-32)*5/9
