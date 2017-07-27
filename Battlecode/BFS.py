import cleanField as field
import math
import random
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation
import Queue

Field=field.Field
class BFSHeuristic(Field):
    def __init__(self,x,y,numAgents,radius):

        Field.__init__(self,x,y,numAgents)
        self.maxLength=0
        self.paths={}
        self.currentStep={}
        self.populateObstacles(4,2)
        self.spawnAgents(radius,numAgents)
        self.mapShow=np.asarray(self.map)

        for agent in self.agents:
            locX,locY=self.agents.get(agent)
            self.paths[agent]=self.bfsSP((locX,locY),(self.targetx,self.targety))
            if len(self.paths[agent])>self.maxLength:
                self.maxLength=len(self.paths[agent])
    def BFSFunction(self,i):

        for agent in self.agents:

            locX,locY= self.agents.get(agent)

            path=self.paths.get(agent)


            if (locX,locY)== path[-1]:
                continue

            #Due to collision with other agents, the next "pseudo-optimal" move may not be possible
            # to take this into account increase the lag (since the animation increases i monotonically)
            #i is the index accessed into the BFS path solution
            if agent in self.currentStep:

                lag=self.currentStep.get(agent)
                newX,newY=path[i-lag]
            else:
                newX,newY=path[i]

            #Check if next tile is empty, if it is move to it. O.W wait in current Location.
            if self.mapShow[newX,newY]>=4 and (newX,newY)!=path[-1]:
                #This is a hack so it doesn't get stuck in the beginning
                if self.mapShow[newX,newY]!=agent:
                    #Do nothing increase the lag
                    if agent in self.currentStep:
                        self.currentStep[agent]+=1
                    else:
                        self.currentStep[agent]=1
            else: #Update aka move
                self.mapShow[locX,locY]=0
                self.mapShow[newX,newY]=agent
                self.agents[agent]=(newX,newY)

        return plt.imshow(self.mapShow,interpolation="nearest", animated=True),


bfsInstance=BFSHeuristic(200,200,25,10)
anim=matplotlib.animation.FuncAnimation(bfsInstance.fig,bfsInstance.BFSFunction,blit=True,interval=50,frames=200,repeat=False)
plt.show(anim)
