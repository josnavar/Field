import math
import random
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation
import Queue


class Field:
    fig=plt.figure()
    #x and y are dimensions of the field
    # map: maps from coordinate to the following protocols: 0=empty, 1 obstacle, 2 start, 3 target unique id for agents where 4<=id<=(m+4)-1,
    #where m=numAgents
    #startx,starty are random coordinates
    #targetx,targety is the target for the agents, it is a mirror of the startx,starty. This was done arbitrarily

    #agents is a dictionary for the id's currently present maps to coordinates
    # agentLocations dictionary which maps: coords->agent IDs (essentially an inverse mapping of agents)
    def __init__(self,x,y,numAgents):
        self.x=x
        self.y=y
        self.numAgents=numAgents
        self.map=[[0 for a in range(x)] for b in range(y)]

        self.startx=random.randint(0,x-1)
        self.starty=random.randint(0,y-1)
        self.targetx=x-int(self.startx*random.random())-1
        self.targety=y-int(self.starty*random.random())-1

        self.agents={}
        self.agentLocations={}
    @staticmethod
    def generateCombinations(sets,discard):
        """
        For obvious reasons this method blows up with large arguments.
        Generates possible combinations , a cartesian product, it outputs a list of these combinations of two sets.
        :param sets: list of 2 sets, each set should be a dictionary whose elements are the domain, the mappings are irrelavent
        :param discard: a dictionary w/ arbitrary elements to remove from final result.
        :return dictionary w/ domain which make up the cartesian product in form of tuples, the order of the dimensions of the tuple is the order of the sets given.
        {a,b}, {c,d} ->{(a,c),(a,d),(b,c),(b,d)}. The first entry always belongs to the first set etc...
        """
        set1=sets[0]
        set2=sets[1]

        result={}
        for x in set1:
            for y in set2:
                if (x,y) in discard:
                    continue
                else:
                    result[(x,y)]=0
        return result
    def populateObstacles(self,w,w0):
        """
        :param w,w0: a real value s.t w>=1 and w0>0, it is used as a parm for probability of a tile having an obstacle Pr=1/(w+w0*#ofNeighbors)
        Iterates through map and assigns an obstacles based on a weighted probability, the idea is that the more obstacles around the coordinate
        the less likely it should be of assigning an obstacles to the current coordinate
        """
        for eltx in range(self.x):
            for elty in range(self.y):
                numOfNeib=self.checkObstacles(eltx,elty)
                probOfObs=1.0/ (w+w0*numOfNeib)
                if (random.random()<probOfObs):
                    self.map[eltx][elty]=1

    def distanceTo(self,a,b):
        """
        :param a: 2-tuples with coordinates in R^2.
        :param b: 2-tuples with coordinates in R^2.
        :return: squared distance between two points
        """
        aX,aY=a
        bX,bY=b
        return (aX-bX)**2+(aY-bY)**2

    def checkObstacles(self,eltx,elty):
        """ Check the # of adjacents coordinates to that are occupied by: obstacles
        :param eltx: Represents the x-dim of the current coordinate
        :param elty: Represents the y-dim of the current coordinate
        sidenote: remember homies function? yeah this is that
        """
        adjacentSet={0:0,1:0,-1:0}
        combinations=Field.generateCombinations([adjacentSet,adjacentSet],{(0,0)})
        count=0
        for elt in combinations:
            newLoc=(eltx+elt[0],elty+elt[1])
            #If a valid coordinate
            if ( newLoc[0]>=0 and newLoc[0]<self.x ) and ( newLoc[1]>=0 and newLoc[1]<self.y):
                #If had an obstacle
                if self.map[newLoc[0]][newLoc[1]]==1:
                    count=count+1
        return count
    #switch=boolean switch
    def checkEmpty(self,eltx,elty,switch=False,mapper=None):
        """

        :param eltx: Represents the x-dim of the current coordinate
        :param elty: Represents the y-dim of the current coordinate
        :return list of valid moves to adjacent steps, this checks for other collisions such as other agents and obstacles
        """
        validMoves=[]
        adjacentSet = {0: 0, 1: 0, -1: 0}
        combinations = Field.generateCombinations([adjacentSet, adjacentSet], {(0, 0)})
        for elt in combinations:
            newLoc = (eltx + elt[0], elty + elt[1])
            # If a valid coordinate
            if (newLoc[0] >= 0 and newLoc[0] < self.x) and (newLoc[1] >= 0 and newLoc[1] < self.y):
                #If it's empty
                if switch:
                    tileValue=mapper[newLoc[0],newLoc[1]]
                else:
                    tileValue = self.map[newLoc[0]][newLoc[1]]

                if tileValue<4 and tileValue!=1:
                    validMoves.append(newLoc)
        return validMoves

    def spawnAgents(self,radius,players):
        """
        Mutates map; it spawns a set # of agents around a radius relative to start location.
        :param radius: none negative value for radius of circle
        :param players: # of players within this radius
        """
        #Recall the protocol, >=4 labels in the grids are reserved for unique agent id's
        for elt in range(4,players+4):
            collision=True
            while collision:
                r=random.random()*radius
                theta=random.random()*2*math.pi
                xLoc=int(math.floor(r*math.cos(theta))+self.startx)
                yLoc=int(math.floor(r*math.sin(theta))+self.starty)

                #Check if the randomly created location is valid
                if not self.agentLocations.has_key((xLoc,yLoc)) and xLoc>=0 and xLoc<self.x and yLoc>=0 and yLoc<self.y:
                    collision=False
                    self.agentLocations[(xLoc,yLoc)]=elt
                    self.agents[elt]=(xLoc,yLoc)

        for elt in self.agentLocations:
            xLoc,yLoc=elt
            self.map[xLoc][yLoc]=self.agentLocations.get(elt)
    #TODO: NEEDS TO FAIL GRACEFULLY IF NO SOLN
    def bfsSP(self,start,target):
        """
        Iterative implementation of BFS
        :param : start is tuple of coordinate in map.
        :param : target is tuple of coordinate in map
        :rtype: list of optimal path from start to target at the current instant. (Individual agent)
        """
        goOn=True
        path=[]
        path.append(target)
        #Already processed, for BFS invariant
        processed={}
        q=Queue.Queue()
        processed[start]=0
        q.put(start)

        while q.qsize()!=0 and goOn:
            u=q.get()
            neighbors=self.checkEmpty(u[0],u[1])
            for elt in neighbors:
                if elt in processed:
                    continue
                processed[elt]=u #Should point to predecessor in order to recontrusct path
                q.put(elt)
                #Found Target
                if elt == target:
                    goOn=False
                    break
        current=target
        if goOn:
            return [start for a in range(30)]
        else:
            while current != start:
                current = processed.get(current)
                path.append(current)


        path.reverse()
        return path[1:]













