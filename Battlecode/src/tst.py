#! /usr/bin/env python

from game_object import *

field = Field(width=10,height=10,x0=0,y0=0)
archon_1 = Archon(0,0,field)
archon_2 = Archon(4,4,field)
archon_3 = Archon(6,3,field)
scout_1 = Scout(4,7,field)
print field.toString()
print "--------------------"

scout_1.move(3,6)
print field.toString()
print "--------------------"

scout_1.move(3,4)
print field.toString()
print "--------------------"

scout_1.move(5,6)
print field.toString()
print "--------------------"

