import cleanField
import numpy as np
import random
import math
Field=cleanField.Field
class Pheromone(Field):
    def __init__(self,x,y,numAgents,radius,decayRate,incrementRate):
        Field.__init__(self,x,y,numAgents)
        self.populateObstacles(16,2)
        self.spawnAgents(radius,numAgents)
        self.mapShow=np.asarray(self.map)

        # Represents the matrix of pheromone intensity of agents
        self.pheromoneIntensity=np.zeros((x,y))
        #pheromone maps from location to direction (not necessary integer), none zero to not waste memory.
        self.pheromoneDirection={}
        self.incrementRate=incrementRate
        self.decayRate=decayRate
        self.leaderId=[0]
        self.path=[]

        #For leader lag, maps from id to lag
        self.currentStep={}
    #start and end are 2tuples, outputs the direction in radians from start to end.
    @staticmethod
    def dirFromTo(start,end):
        xdiff=end[0]-start[0]
        ydiff=end[1]-start[1]

        return math.atan2(ydiff,xdiff)
    #Main iterative function determines the animation for each i'th step
    def iterate(self,i):
        #Choose random leader if not already chosen
        if self.leaderId[0]==0:
            self.leaderId[0]=random.randint(4,3+self.numAgents)
            id=self.leaderID[0]
            #Find optimal path for the current leader
            self.path=self.bfsSP(self.agents.get(id),(self.targetx,self.targety))


        #Pheremones are present in each entry of the array and they are composed of a vector with r="intensity" and theta="dir"


        #Update the pheromone levels. Pheromone levels are "reals" from 0 to 1 inclusive that decay per round. Decay acts on r
        #The decay rate can be any none decreasing function (TODO consider more functions)
        #For now we will use linear decay rate.

        #Apply the pheromone decay; How to maintain a minimum and max bounds?->Use clip function
        decay=self.decayRate*np.ones((self.x,self.y))
        self.pheromoneIntensity=np.clip(self.pheromoneIntensity-decay,0,1)


        for agent in self.agents:
            locX,locY=self.agents.get(agent)
            ##################Agent=Leader###################################
            #Action for the leader, essentially BFS heuristic but only for leader, refer to BFS.py
            # Leader continues along its single optimal route
            if agent==self.leaderId[0]:

                #reached target
                if (locX,locY)==self.path[-1]:
                    continue
                #There is some lag involved
                if agent in self.currentStep:
                    lag=self.currentStep.get(agent)
                    newX,newY=self.path[i-lag]
                else:
                    newX,newY=self.path[i]

                #Update tiles (check if the next location is unoccupied) and pheromone levels
                if self.mapShow[newX,newY]>=4 and (newX,newY)!=self.path[-1]:
                    # This is a hack so it doesn't get stuck in the beginning
                    if self.mapShow[newX,newY]!=agent:
                        #Don't move since we need a lag (can't currently move there)
                        if agent in self.currentStep:
                            self.currentStep[agent]+=1
                        else:
                            self.currentStep[agent]=1
                else:#Update aka move
                    self.mapShow[locX,locY]=0
                    self.mapShow[newX,newY]=agent
                    self.agents[agent]=(newX,newY)

                    #Update the pheromone:
                    oldTheta=0
                    newTheta=Pheromone.dirFromTo((locX,locY),(newX,newY))
                    r=self.phermoneIntensity[locX,locY]
                    if self.pheromoneDirection.has_key((locX,locY)):
                        oldTheta=self.pheromoneDirection.get((locX,locY))
                    num=r*math.sin(oldTheta)+self.incrementRate*math.sin(newTheta)
                    den=r*math.cos(oldTheta)+self.incrementRate*math.cos(newTheta)

                    updateTheta=math.atan2(num,den)
                    self.pheromoneDirection[locX,locY]=updateTheta
                    self.pheromoneIntensity[locX,locY]=self.pheromoneIntensity[locX,locY]+self.incrementRate
            ##################Agent!=Leader##################################
            else: #Other agents that are not leaders but followers
                #Chooses direction based on strongest pheromone trail. What if no none-zero adjacent pheromone levels?











