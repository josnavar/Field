import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation
import math

class createMap(object):
    fig = plt.figure()
    #Symmetry is an integer and represents the following protocols:
    #0:Rotational (by pi)
    #1:Horizontal (Based on y-axis)
    #2:Vertical (based on x-axis)

    #Underlying data structure is a numpy array with dimensions (sizeX,sizeY)
    def __init__(self,sizeX,sizeY,symmetry):
        self.sizeX=sizeX
        self.sizeY=sizeY
        self.symmetry=symmetry

        self.received_click=False
        self.clicked_x=-1
        self.clicked_y=-1
        self.board=np.zeros((sizeX,sizeY))

    #animation function that will handle updating canvas called by funcAnimator
    def iterate(self,i):
        print (self.received_click)
        if self.received_click:
            self.updateCanvas()
            self.received_click=False
        return plt.imshow(self.board,interpolation="nearest",animated=True,cmap="Paired"),
    #Make 3 different cases depending on symmetry, Going to be based on matplotlib and clicks
    #depending on the symmetry it will update the canvas based on it.

    def updateCanvas(self):
        #Vertical reflection
        symmetricX,symmetricY=(-1,-1)
        if self.symmetry==2:
            symmetricX=self.clicked_x
            symmetricY=(2*(self.sizeY-1)/2.0-self.clicked_y)
        elif self.symmetry==1:
            symmetricX=(2*(self.sizeX-1)/2.0-self.clicked_x)
            symmetricY=self.clicked_y
        elif self.symmetry==0:
            #Rotational by pi
            symmetricX=(2*(self.sizeX-1)/2.0-self.clicked_x)
            symmetricY=(2*(self.sizeY-1)/2.0-self.clicked_y)
        #Update the canvas now
        symmetricX=int(round(symmetricX))
        symmetricY=int(round(symmetricY))
        self.board[self.clicked_x,self.clicked_y]=1
        self.board[symmetricX,symmetricY]=1

instance=createMap(100,100,0)
def clickEvent(event):

    #right click
    if event.button==3:
        instance.clicked_x=int(round(event.ydata))
        instance.clicked_y=int(round(event.xdata))
        instance.received_click=True
instance.fig.canvas.mpl_connect("button_press_event",clickEvent)
anim=matplotlib.animation.FuncAnimation(instance.fig,instance.iterate,blit=True,interval=50,frames=1000,repeat=False)
plt.show(anim)


