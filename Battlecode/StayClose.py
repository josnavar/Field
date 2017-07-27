import cleanField
import math
import random
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation
import Queue

Field=cleanField.Field
class StayClose(Field):
    def __init__(self,x,y,numAgents,radius):
        Field.__init__(self,x,y,numAgents)
        self.populateObstacles(16,2)
        self.spawnAgents(radius,numAgents)
        self.mapShow=np.asarray(self.map)

        #Unused field maxLength
        self.maxLength = 0
        #Precomputed optimal paths
        self.paths={}
        self.leaderId=[0]

        #For lag
        self.currentStep={}
        self.radius=20

        for agent in self.agents:
            locX,locY=self.agents.get(agent)
            self.paths[agent]=self.bfsSP((locX,locY),(self.targetx,self.targety))
            if len(self.paths[agent])>self.maxLength:
                self.maxLength=len(self.paths[agent])

    def leaderFunction(self,i):
        #Choose random leader if not already chosen
        if self.leaderId[0]==0:
            self.leaderId[0]=random.randint(4,3+self.numAgents)
        path=self.paths.get(self.leaderId[0])

        for agent in self.agents:
            locX, locY = self.agents.get(agent)

            #Action for the leader, essentially BFS heuristic but only for leader, refer to BFS.py
            # Leader continues along its single optimal route
            if agent == self.leaderId[0]:

                #Reached target
                if (locX,locY)==path[-1]:
                    continue

                if agent in self.currentStep:
                    lag=self.currentStep.get(agent)
                    newX,newY=path[i-lag]
                else:
                    newX,newY=path[i]

                #Update tiles

                # No need to check for obstacles since (newX,newY) has the invariant of being a tile along the BFS path.
                #The only thing that changes is other agents that may block the way hence only need to check for other
                #agents hence the >=4 according to the protocol.
                if self.mapShow[newX,newY]>=4 and (newX,newY)!=path[-1]:
                    # This is a hack so it doesn't get stuck in the beginning
                    if self.mapShow[newX,newY]!=agent:
                        if agent in self.currentStep:
                            self.currentStep[agent]+=1
                        else:
                            self.currentStep[agent]=1

                else:
                    self.mapShow[locX,locY]=0
                    self.mapShow[newX,newY]=agent
                    self.agents[agent]=(newX,newY)
            else:
                # Everyother agent should stay close to the leader: Move randomly, if out of range move towards leader
                locations=self.checkEmpty(locX,locY,True,self.mapShow)
                leaderLocation=self.agents.get(self.leaderId[0])

                #If outside of acceptable radius

                if self.distanceTo((locX,locY),leaderLocation)>self.radius:
                    #Select closest tile in locations to leader's location

                    distance=2*(self.x)**2
                    bestGuess=(0,0)
                    for elt in locations:
                        currentDistance=self.distanceTo(elt,leaderLocation)
                        if currentDistance<distance:
                            distance=currentDistance
                            bestGuess=elt
                    #Couldn't find anything skip turn, TODO: Improve this, maybe try an alternative to greedy solution.
                    if bestGuess==(0,0):
                        continue

                    #Move to this new Location
                    self.mapShow[locX,locY]=0
                    self.mapShow[bestGuess[0],bestGuess[1]]=agent
                    self.agents[agent]=bestGuess
                else: #move randomly
                    (randX,randY)=locations[random.randint(0,len(locations)-1)]
                    self.mapShow[locX,locY]=0
                    self.mapShow[randX,randY]=agent
                    self.agents[agent]=(randX,randY)

        return plt.imshow(self.mapShow,interpolation="nearest",animated=True),
followLeader=StayClose(200,200,25,10)
anim=matplotlib.animation.FuncAnimation(followLeader.fig,followLeader.leaderFunction,blit=True,interval=50,frames=200,repeat=False)
plt.show(anim)

