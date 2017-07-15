#! /usr/bin/env python

import math
import numpy as np

# Global Constants
ARCHON_MOVE_LENGTH = 1
SCOUT_MOVE_LENGTH = 1
TANK_MOVE_LENGTH = 1
SOLDIER_MOVE_LENGTH = 1
SPAWNER_MOVE_LENGTH = 1

ARCHON_ATTACK_LENGTH = 1
SCOUT_ATTACK_LENGTH = 1
TANK_ATTACK_LENGTH = 1
SOLDIER_ATTACK_LENGTH = 1
SPAWNER_ATTACK_LENGTH = 1

ARCHON_MAX_HEALTH = 1
SCOUT_MAX_HEALTH = 1
TANK_MAX_HEALTH = 1
SOLDIER_MAX_HEALTH = 1
SPAWNER_MAX_HEALTH = 1

ARCHON_DAMAGE_RADIUS = 1
SCOUT_DAMAGE_RADIUS = 1
TANK_DAMAGE_RADIUS = 1
SOLDIER_DAMAGE_RADIUS = 1
SPAWNER_DAMAGE_RADIUS = 1

ARCHON_DAMAGE = 1
SCOUT_DAMAGE = 1
TANK_DAMAGE = 1
SOLDIER_DAMAGE = 1
SPAWNER_DAMAGE = 1

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

    def getgame_type(self):
        return self.game_type

    def getLocation(self):
        return (self.x, self.y)
    
    def setLocation(self, x, y):
        self.x = x
        self.y = y

    def distToLocation(self, x, y):
        dx = self.x-x
        dy = self.y-y
        return math.sqrt(dx**2+dy**2)

    def inRange(self, x, y, radius):
        return self.distToLocation(x, y) <= radius

    def isArchon(self):
        return self.game_type == "Archon"

    def isObstacle(self):
        return self.game_type == "Obstacle"

    def getUID(self):
        return self.UID

class Archon(GameObject):
    def __init__(self, x, y, field):
        GameObject.__init__(self, x, y, "Archon", field)
        self.health = ARCHON_MAX_HEALTH

    def move(self, x, y):
        if self.canMoveLocation(x, y):
            self.setLocation(x, y)
        self.checkRep()

    def canMoveLocation(self, x, y):
        # If grid-like movements, uncomment this
        # return abs(self.x-x)+abs(self.y-y) <= ARCHON_MOVE_LENGTH

        return self.distToLocation(x, y) <= ARCHON_MOVE_LENGTH

    def attack(self, x, y):
        field = self.field
        if self.canAttackLocation(x, y):
            field.attack(x, y, ARCHON_DAMAGE, ARCHON_DAMAGE_RADIUS)

    def damage(self, damage):
        self.health -= damage

    def getHealth(self):
        return self.health

    def isAlive(self):
        return self.health > 0

    def canAttackLocation(self, x, y):
        # If grid-like movements, uncomment this
        # return abs(self.x-x)+abs(self.y-y) <= ARCHON_ATTACK_LENGTH

        return self.distToLocation(x, y) <= ARCHON_ATTACK_LENGTH

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

    def attack(self, x, y, damage, damage_radius):
        dead_objects = []
        for teamObject in self.team_objects:
            if teamObject.inRange(x, y, damage_radius):
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
    
        self.game_objects.add(gameObject)
        if gameObject.isObstacle():
            self.obstacle_objects.add(gameObject)
        else:
            self.team_objects.add(gameObject)

    def getUID(self):
        self.latest_assigned_UID += 1
        return self.latest_assigned_UID








