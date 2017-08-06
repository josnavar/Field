#! /usr/bin/env python

import math
import numpy as np

# Global Constants
CHANNEL_WIDTH = 10

ARCHON_MOVE_LENGTH = 2
SCOUT_MOVE_LENGTH = 6
TANK_MOVE_LENGTH = 2
SOLDIER_MOVE_LENGTH = 4
SPAWNER_MOVE_LENGTH = 4

ARCHON_ATTACK_LENGTH = 1
SCOUT_ATTACK_LENGTH = 1
TANK_ATTACK_LENGTH = 6
SOLDIER_ATTACK_LENGTH = 3
SPAWNER_ATTACK_LENGTH = 1

ARCHON_MAX_HEALTH = 100
SCOUT_MAX_HEALTH = 100
TANK_MAX_HEALTH = 100
SOLDIER_MAX_HEALTH = 100
SPAWNER_MAX_HEALTH = 100

ARCHON_DAMAGE_RADIUS = 1
SCOUT_DAMAGE_RADIUS = 1
TANK_DAMAGE_RADIUS = 3
SOLDIER_DAMAGE_RADIUS = 2
SPAWNER_DAMAGE_RADIUS = 1

ARCHON_DAMAGE = 40
SCOUT_DAMAGE = 2
TANK_DAMAGE = 10
SOLDIER_DAMAGE = 6
SPAWNER_DAMAGE = 2

GAME_TYPES = ["Archon",
              "Scout",
              "Tank",
              "Soldier",
              "Spawner",
              "Obstacle"]

class GameObject(object):
    def __init__(self, x, y, game_type, field):
        self.game_type = game_type
        self.x = x
        self.y = y
        self.UID = field.getUID()

        self.field = field
        self.field.addObject(self)

        self.checkRep()

    def writeChannel(self, i, data):
        self.field.writeChannel(i, data)

    def readChannel(self, i):
        return self.field.readChannel(i)

    def checkRep(self):
        if self.game_type not in GAME_TYPES:
            raise Exception("Invalid Game game_type")

        x = self.x
        y = self.x
        x0 = self.field.x0
        y0 = self.field.y0
        width = self.field.width
        height = self.field.height

        xOut = x < x0 or x > x0 + width
        yOut = y < y0 or y > y0 + height
        if xOut or yOut:
            raise Exception("Game object out of bounds")

    def get_gameType(self):
        return self.game_type

    def getLocation(self):
        return (self.x, self.y)
    
    def setLocation(self, x, y):
        self.x = x
        self.y = y
        self.checkRep()

    def distToLocation(self, x, y):
        dx = self.x-x
        dy = self.y-y
        return math.sqrt(dx**2+dy**2)

    def canMoveLocation(self, x, y, mov_length):
        x_curr, y_curr = self.getLocation()

        # Limit to 8 cardinal directions
        if x-x_curr != 0 and y-y_curr!=0 and (abs(x-x_curr)!=abs(y-y_curr)):
            return False

        # Verify destination within movement range
        withinMoveRange = max(abs(x-x_curr),abs(y-y_curr)) <= mov_length
        # Verify straight line path to destination is clear
        pathNotImpeded = not self.field.pathImpeded(x_curr,y_curr,x,y)
        return withinMoveRange and pathNotImpeded

    def canAttackLocation(self, x, y, att_length):
        return abs(self.x-x)+abs(self.y-y) <= att_length
 
    def inRange(self, x, y, radius):
        return self.distToLocation(x, y) <= radius

    def isArchon(self):
        return self.game_type == "Archon"

    def damage(self, damage):
        self.health -= damage

    def getHealth(self):
        return self.health

    def isAlive(self):
        return self.health > 0

    def isObstacle(self):
        return self.game_type == "Obstacle"

    def getUID(self):
        return self.UID

class Archon(GameObject):
    def __init__(self, x, y, field):
        GameObject.__init__(self, x, y, "Archon", field)
        self.health = ARCHON_MAX_HEALTH

    def move(self, x, y):
        if GameObject.canMoveLocation(self, x, y, ARCHON_MOVE_LENGTH):
            self.setLocation(x, y)

    def attack(self, x, y):
        if GameObject.canAttackLocation(self, x, y):
            self.field.attack(x, y, ARCHON_DAMAGE, ARCHON_DAMAGE_RADIUS, self.getUID())
   
    def toString(self):
        return "A"

class Scout(GameObject):
    def __init__(self, x, y, field):
        GameObject.__init__(self, x, y, "Scout", field)
        self.health = SCOUT_MAX_HEALTH

    def move(self, x, y):
        if GameObject.canMoveLocation(self, x, y, SCOUT_MOVE_LENGTH):
            self.setLocation(x, y)

    def attack(self, x, y):
        if GameObject.canAttackLocation(self, x, y):
            self.field.attack(x, y, SCOUT_DAMAGE, SCOUT_DAMAGE_RADIUS, self.getUID())
   
    def toString(self):
        return "S"

class Field(object):
    def __init__(self, width, height, x0, y0):
        self.latest_assigned_UID = -1 
        self.game_objects = set()
        self.team_objects = set()
        self.obstacle_objects = set()
        self.x0 = x0
        self.y0 = y0
        self.width = width
        self.height = height
        self.commChannel = [0]*CHANNEL_WIDTH

    def attack(self, x, y, damage, damage_radius, uid):
        dead_objects = []
        for teamObject in self.team_objects:
            if teamObject.inRange(x, y, damage_radius) and teamObject.getUID() != uid:
                teamObject.damage(damage)
            if not teamObject.isAlive():
                dead_objects.append(teamObject)

        for deadObject in dead_objects:
            self.game_objects.remove(deadObject)
            self.team_objects.remove(deadObject)

    def addObject(self, gameObject):
        x, y = gameObject.getLocation()
        xOut = x < self.x0 or x > self.x0 + self.width
        yOut = y < self.y0 or y > self.y0 + self.width

        if xOut or yOut:
            raise Exception("Can't add object out of bounds")
        if self.isOccupied(x,y):
            raise Exception("Can't add object on location with existing object")
    
        self.game_objects.add(gameObject)
        if gameObject.isObstacle():
            self.obstacle_objects.add(gameObject)
        else:
            self.team_objects.add(gameObject)

    def isOccupied(self, x, y):
        for gameObject in self.game_objects:
            x_obj, y_obj = gameObject.getLocation()
            if x==x_obj and y==y_obj:
                return True
        return False
    
    def pathImpeded(self, x0, y0, x1, y1):
        for gameObject in self.game_objects:
            x, y = gameObject.getLocation()
            # Don't check object itself
            if x0-x==0 or y0-y==0:
                continue
            # Verify that no objects lie at the destination
            if x1-x==0 and y1-y==0:
                return True
            m0 = 1.0*(y0-y)/(x0-x)
            m1 = 1.0*(y1-y)/(x1-x)
            xBetween = (x0<x and x<x1) or (x1<x and x<x0)
            yBetween = (y0<y and y<y1) or (y1<y and y<y0)
            if m0==m1 and xBetween and yBetween:
                return True
        return False

    def getUID(self):
        self.latest_assigned_UID += 1
        return self.latest_assigned_UID

    def toString(self):
        field = [["-" for col in range(self.width)] for row in range(self.height)]

        for gameObject in self.game_objects:
            x, y = gameObject.getLocation()
            field[x][y] = gameObject.toString()

        outputStr = ""
        for row in range(self.height):
            for col in range(self.width):
                outputStr += field[col][self.height-1-row] + "\t"
            outputStr += "\n"
        return outputStr

    def writeChannel(self, i, data):
        if type(data) != int:
            raise Exception("Must write integer to channel")
        self.commChannel[i] = data

    def readChannel(self, i):
        return self.commChannel[i]

    def printCommChannel(self):
        print self.commChannel

