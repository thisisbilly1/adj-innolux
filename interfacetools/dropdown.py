from utils import  drawbox

class dropdown:
    def __init__(self, world,x,y,options,label=""):
        self.world=world
        self.x=x
        self.y=y
        self.options=options
        self.selected=0 #index of options list
        
        self.clicked=False
        self.label=label
        
    def updateclicked(self,args=()):
        self.clicked = not self.clicked
    
    def offClick(self,args=()):
        self.clicked = False

    def updateselected(self,args=()):
        self.selected=args
        self.clicked=False
        
    def draw(self):
        box=[self.x,self.y,100,32]
        self.world.screen.blit(self.world.fontobject.render(str(self.label), 1, (0,0,0)),(box[0]+5, box[1]-12))
        
        if self.clicked:
            for i in range(len(self.options)):
                box=[self.x,self.y+i*32+32,100,32]
                if self.selected==i:#if selected
                    hcolor=(150,150,150)
                    color=(175,175,175)
                else:
                    hcolor=(175,175,175)
                    color=(200,200,200)
                drawbox(box,self.world, color, hcolor, self.updateselected, clickargs=(i) ,text=self.options[i])    
        
        box=[self.x,self.y,100,32]
        drawbox(box,self.world,(200,200,200),(175,175,175),self.updateclicked,text=self.options[self.selected], offclickfunction=self.offClick)
                