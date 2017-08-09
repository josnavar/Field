import cleanField
import numpy as np
import random
import math
import Queue
import matplotlib.pyplot as plt
import matplotlib.animation
from random import shuffle
Field=cleanField.Field
clickDelay=0
paused=False
class Pheromone(Field):
    idToTile = {0: (0, 1), 1: (-1, 1), 2: (-1, 0), 3: (-1, -1), 4: (0, -1),
                   -1: (1, 1), -2: (1, 0), -3: (1, -1), -4: (0, -1)}
    adjacentSet={0:0,1:0,-1:0}
    # generates all possible adjacent combinations
    adjacent=Field.generateCombinations([adjacentSet,adjacentSet],{0,0})
    def __init__(self,x,y,numAgents,spawn_radius,decayRate,incrementRate,spread_radius):
        Field.__init__(self,x,y,numAgents)
        self.populateObstacles(16,2)
        self.spawnAgents(spawn_radius,numAgents)
        self.mapShow=np.asarray(self.map)
        self.spread_radius=spread_radius
        self.incrementRate=incrementRate
        self.decayRate=decayRate

        # Represents the matrix of pheromone intensity of agents
        self.pheromoneIntensity=np.zeros((x,y))
        #pheromone maps from location to 4-tuple of (direction,leader boolean,indexOfGoal,distanceToGoal)
        self.pheromoneDirection={}
        # Matrix of directions
        self.heatMap = np.zeros((self.x, self.y))

        self.start=(0,0)
        self.leaderId=[0]
        self.leaderLoc = (0, 0)
        #index of the path
        self.path=[]
        self.path_dictionary={}
        self.index=0

        #For leader lag, maps from id to lag
        self.previous_index=-1
        self.lag=0

    #Check if nextTile has a location and if such location >= index
    #returns a boolean
    def checkIfObstructs(self,newTile):
        if newTile in self.path_dictionary:
            index=self.path_dictionary.get(newTile)
            if index>self.index:
                return True
            else:
                return False
        else:
            return False

    #Returns shuffled list of valid adjacent neighbors based on their pheromone value
    #shouldn't be in banned
    def checkPheromone(self,current):
        eltx=current[0]
        elty=current[1]
        #List of tuples of the form (tile,pheromoneValue)
        validMoves=[]
        for elt in Pheromone.adjacent:
            newLoc= (eltx+elt[0],elty+elt[1])
            if (newLoc[0]>=0 and newLoc[0]<self.x) and (newLoc[1]>=0 and newLoc[1]<self.y):
                tileValue=self.mapShow[newLoc[0],newLoc[1]]
                pheromoneValue=self.pheromoneIntensity[newLoc[0],newLoc[1]]
                if tileValue<4 and tileValue!=1 and pheromoneValue>0 and not self.checkIfObstructs(newLoc):
                    validMoves.append((newLoc,pheromoneValue))
        shuffle(validMoves)
        return validMoves
    #Used by spreadPheromones to generate tiles that are compatible w/ pheromones (none-obstacles)
    def validPheromoneLocations(self,current):
        validMoves=[]
        eltx=current[0]
        elty=current[1]

        for elt in Pheromone.adjacent:
            newLoc=(eltx+elt[0],elty+elt[1])
            if (newLoc[0]>=0 and newLoc[0]<self.x) and (newLoc[1]>=0 and newLoc[1]<self.y) and self.mapShow[newLoc[0],newLoc[1]]!=1:
                validMoves.append(newLoc)
        return validMoves
    #Angle in radians -pi<x<pi
    #Returns the adjacent tile that was point to
    @staticmethod
    def angleToTile(angle,currentTile):
        if angle>=0:
            index = math.floor(8 * angle / math.pi)
            index = int(round(index / 2.0))
        else:
            index=math.ceil(8*angle/math.pi)
            index=int(round(index/2.0))
        tileDifference=Pheromone.idToTile.get(index)
        return (currentTile[0]+tileDifference[0],currentTile[1]+tileDifference[1])
    #start and end are 2tuples, outputs the direction in radians from start to end.
    @staticmethod
    def dirFromTo(start,end):
        xdiff=end[0]-start[0]
        ydiff=end[1]-start[1]
        return -math.atan2(xdiff,ydiff)
    #Mutates the pheromones directions and intensities
    def updatePheromone(self,old,new,leader):
        direction = Pheromone.dirFromTo(old, new)
        if leader:
            self.pheromoneDirection[old]=(direction,leader,self.index,1)
            self.pheromoneIntensity[old[0],old[1]]=self.incrementRate
            self.heatMap[old[0],old[1]]=int(math.degrees(direction)+360)%360
        else:
            currentDistance=self.pheromoneDirection.get(new)[-1]+1
            self.pheromoneDirection[old]=(direction,leader,self.index,currentDistance)
            self.pheromoneIntensity[old[0],old[1]]=self.incrementRate
            self.heatMap[old[0],old[1]]=int(math.degrees(direction)+360)%360

    #Used by spreadPheromones, should only spread to empty locations
    #leader is boolean if agent spreading is a leader
    def reversePheromones(self,current,source,leader):
        if leader:
            #can overwrite anything
            if current in self.pheromoneDirection:
                #initialDistance is the distance to current w/ initial route
                initialDir,initialLeader,initialIndex,initialDistance=self.pheromoneDirection.get(current)
            else:
                initialLeader=False
            if initialLeader:
                initialDistance+=self.index-initialIndex
                currentDirection=self.dirFromTo(current,source)
                currentDistance=self.pheromoneDirection.get(source)[-1]+1
                #Is the older closer?
                if currentDistance < initialDistance:
                    self.pheromoneDirection[current]=(currentDirection,leader,self.index,currentDistance)
                    self.heatMap[current[0], current[1]] = int(math.degrees(currentDirection) + 360) % 360
                    r=self.pheromoneIntensity[source[0],source[1]] #/2
                    self.pheromoneIntensity[current[0],current[1]]=r
            else:
                currentDistance=self.pheromoneDirection.get(source)[-1]+1
                #Overwrite regardless of size
                direction=self.dirFromTo(current,source)
                self.pheromoneDirection[current]=(direction,leader,self.index,currentDistance)
                self.heatMap[current[0], current[1]] = int(math.degrees(direction) + 360) % 360
                r = self.pheromoneIntensity[source[0], source[1]] #/ 2
                self.pheromoneIntensity[current[0],current[1]]=r
        elif self.pheromoneIntensity[current[0],current[1]]==0:
            currentDistance=self.pheromoneDirection.get(source)[-1]+1
            direction = self.dirFromTo(current, source)
            self.pheromoneDirection[current] = (direction, leader,self.index,currentDistance)
            self.heatMap[current[0], current[1]] = int(math.degrees(direction) + 360) % 360
            r = self.pheromoneIntensity[source[0], source[1]] #/ 2
            self.pheromoneIntensity[current[0], current[1]] = r
    #Spread pheromones from currentTile by some distance: d
    #leader is a boolean, true if the agent is a leader or false o.w
    def spreadPheromones(self,currentTile,d,leader):
        processed={}
        processed[currentTile]=0
        q=Queue.Queue()
        q.put(currentTile)
        while q.qsize()!=0:
            u=q.get()
            distance=processed[u]+1
            #Valid pheromone locations ensures that the pheromone levels are none zero.
            neighbors=self.validPheromoneLocations(u)
            if distance>d:
                break
            for elt in neighbors:
                if elt in processed:
                    continue
                processed[elt]=distance
                q.put(elt)
                self.reversePheromones(elt,u,leader)
    #Main iterative function determines the animation for each i'th step
    def iterate(self,i):
        global clickDelay
        global paused
        if paused:
            clickDelay+=1
        else:
            i=i+clickDelay
        #Choose random leader if not already chosen
        if self.leaderId[0]==0:
            self.leaderId[0]=random.randint(4,3+self.numAgents)
            id=self.leaderId[0]
            #Find optimal path for the current leader
            self.path=self.bfsSP(self.agents.get(id),(self.targetx,self.targety))
            #Dictionary is used so followers make sure they don't step on optimal path tiles.

            for elt in range(len(self.path)):
                self.path_dictionary[self.path[elt]]=elt

            self.start=self.agents.get(id)
        self.pheromoneIntensity=np.clip(self.pheromoneIntensity,0,1)

        for agent in self.agents:
            locX,locY=self.agents.get(agent)
            ##################Agent=Leader###################################
            #Action for the leader, essentially BFS heuristic but only for leader, refer to BFS.py
            # Leader continues along its single optimal route
            if agent==self.leaderId[0]:
                print self.path
                if i==self.previous_index:
                    continue
                else:
                    self.previous_index=i
                #reached target
                if (locX,locY)==self.path[-1]:
                    continue
                newX,newY=self.path[i-self.lag]
                self.index=i-self.lag

                #Update tiles (check if the next location is unoccupied) and pheromone levels
                if self.mapShow[newX,newY]>=4 and (newX,newY)!=self.path[-1]:
                    print "stuck"
                    self.lag+=1
                    # # This is a hack so it doesn't get stuck in the beginning
                    # if self.mapShow[newX,newY]!=agent:
                    #     #Don't move since we need a lag (can't currently move there)
                    #     if agent in self.currentStep:
                    #         self.currentStep[agent]+=1
                    #     else:
                    #         self.currentStep[agent]=1
                else:#Update aka move

                    self.leaderLoc=(newX,newY)
                    self.mapShow[locX,locY]=0
                    self.mapShow[newX,newY]=agent
                    self.agents[agent]=(newX,newY)

                    #Update the pheromone:
                    self.updatePheromone((locX,locY),(newX,newY),True)
                    self.spreadPheromones((locX,locY),self.spread_radius+2,True)

            ##################Agent!=Leader##################################
            else: #Other agents that are not leaders but followers

                #Assumptions: The herd has a common point of creation hence distance from herd to pheromone locations are minimal
                locations = self.checkPheromone((locX,locY))
                validMovements=self.checkEmpty(locX,locY,True,self.mapShow)
                sameTile=False
                #first check if the current tile you're in has a pheromone o.w check neibhbors o.w random walk
                if self.pheromoneIntensity[locX,locY]>0:
                    direction=self.pheromoneDirection.get((locX,locY))[0]
                    newX,newY=Pheromone.angleToTile(direction,(locX,locY))
                    #Make sure that the pheromone points to a valid location that ofc is empty and not on optimal path
                    if (self.mapShow[newX,newY]<4 and self.mapShow[newX,newY]!=1 and not self.checkIfObstructs((newX,newY))):
                        sameTile=True
                if len(locations)>0 and not sameTile:
                    #GO to pheromone
                    biggestPheromone=locations[0][0]
                    newX,newY=biggestPheromone
                    #self.updatePheromone((locX,locY),(newX,newY),False)
                    self.spreadPheromones((newX,newY),self.spread_radius,False)
                elif not sameTile:
                    if len(validMovements)>0:
                        newX,newY=validMovements[random.randint(0,len(validMovements)-1)]
                    else:
                        #don't move
                        newX=locX
                        newY=locX

                self.mapShow[locX,locY]=0
                self.mapShow[newX,newY]=agent
                self.agents[agent]=(newX,newY)



        consider=np.concatenate((self.mapShow,self.heatMap),axis=1)
        return plt.imshow(consider,interpolation="nearest",animated=True,cmap="Paired"),
instance=Pheromone(100,100,15,3,0.08,0.95,4)
count=0
def clickEvent(event):
    global count
    global paused
    if count==0:
        if event.button==3:
            anim.event_source.stop()
            paused=True
            count=1
    else:
        if event.button==3:
            anim.event_source.start()
            paused=False
            count=0
instance.fig.canvas.mpl_connect("button_press_event",clickEvent)
anim=matplotlib.animation.FuncAnimation(instance.fig,instance.iterate,blit=True,interval=100,frames=100,repeat=False)
plt.show(anim)
#anim.save("nuts.mp4")