#!/usr/bin/env python
import re


str = 'next topic >>'
match = re.search(r'next topic', str)
# If-statement after search() tests if it succeeded
if match:                      
   print 'found', match.group() ## 'found word:cat'
else:
   print 'did not find'