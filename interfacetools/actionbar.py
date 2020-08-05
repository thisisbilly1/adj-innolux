import pygame
from utils import drawbox, hsv_to_rgb
from interfacetools.slider import slider
 
class actionbar:
	def __init__(self,world,controller,x,y):
		self.world=world
		self.controller=controller
		self.x=x
		self.y=y
		self.keybinds=[ord("1"),ord("2"),ord("3")]
		self.classes=["good","ng","test"]
		self.colors=[slider(self.world,self.x,self.y,"hue",sliderange=(0,360),start=110),
			   slider(self.world,self.x,self.y,"hue",sliderange=(0,360),start=0),
			   slider(self.world,self.x,self.y,"hue",sliderange=(0,360),start=180)]
		
		self.selected=None
		#for multi select tool
		self.defaultmatch=0
		self.defaultmiss=1
		
		self.editmode=False
		
		self.selectededititem=[None,None]
	
	def reset(self):
		self.editmode=False
		self.selectededititem=[None,None]
		
	def updateedit(self, args=()):
		self.editmode=not self.editmode
		
	def updateselect(self,args=()):
		i=args#[0]
		#print(self.classes[i])
		self.selected=i
		#try to update the selected label box to the current selected
		if self.controller.match.labelselect!=None:
			self.controller.match.labelselect.label=self.classes[i]
			self.controller.match.labelselect.color=hsv_to_rgb(self.colors[i].slideValue/360,1,1)
	
	def updatelabel(self,args=()):
		i=args[0]
		part=args[1]
		self.selectededititem=[i,part]
		pass
	
	def deletelabel(self,args=()):
		self.selectededititem=[None,None]
		del self.classes[args]
		del self.keybinds[args]
		del self.colors[args]
	
	def createlabel(self,args=()):
		self.selectededititem=[None,None]
		self.classes.append("")
		self.keybinds.append(None)
		self.colors.append(slider(self.world,self.x,self.y,"hue",sliderange=(0,360),start=0))
		
	def updateautomiss(self,args=()):
		self.defaultmiss=args
	def updateautomatch(self,args=()):
		self.defaultmatch=args
	
	def update(self):
		#keybind the labels
		if not self.editmode:
			for key in self.world.keyspressed:
					for i in range(len(self.keybinds)):
						if key == self.keybinds[i]:
							self.selected=i
							#try to update the selected label box to the current selected
							if self.controller.match.labelselect!=None:
								self.controller.match.labelselect.label=self.classes[i]
								self.controller.match.labelselect.color=hsv_to_rgb(self.colors[i].slideValue/360,1,1)
		#edit the labels
		else:
			for i in range(len(self.classes)):
				#edit key binds
				if self.selectededititem==[i,0]:
					if self.world.keyspressed:
						key=self.world.keyspressed[0]
						if key <= 127:
							if not key in self.keybinds:
								self.keybinds[i]=key
							
				if self.selectededititem==[i,1]:
					for key in self.world.keyspress:
						if key == pygame.K_RETURN:
							self.selectededititem=[None,None]
						elif key == pygame.K_BACKSPACE:
							self.classes[i] = self.classes[i][0:-1]
						elif key <= 127:
								self.classes[i]+=chr(key)
						
					
	def draw(self):
		#editmode button
		box = [self.x,self.y,64,32]
		c=(200,200,200)
		hc=(175,175,175)
		if self.editmode:
			c=(0,200,0)
			hc=(0,175,0)
		drawbox(box, self.world, c, hc, self.updateedit, text="Edit")
		
		
		
		#label boxes
		if self.editmode:
			for i in range(len(self.classes)):
				y=i*60+40
				#keybind
				c=(200,200,200)
				hc=(175,175,175)
				if self.selectededititem==[i,0]:
					c = (0,200,200)
					hc = (0,175,175)
				box = [self.x,self.y+y,32,32]
				
				if self.keybinds[i]==None:
					txt="NA"
				else:
					txt=str(chr(self.keybinds[i]))
				drawbox(box, self.world, c, hc, self.updatelabel, clickargs=(i,0), text=txt)
				
				#label
				w,h = self.world.fontobject.size(str(self.classes[i]))
				w = max(64,w+20)
				c=(200,200,200)
				hc=(175,175,175)
				if self.selectededititem==[i,1]:
					c=(0,200,200)
					hc=(0,175,175)
				box = [self.x+32,self.y+y,w,32]
				drawbox(box, self.world, c, hc, self.updatelabel, clickargs=(i,1), text=self.classes[i])
				
				#Hue slider
				self.colors[i].draw(x=self.x+46+w,y=self.y+y+15,displayHue=True)
				
				#delete button
				box = [self.x+170+w,self.y+y,32,32]
				drawbox(box, self.world, (200,0,0), (175,0,0), self.deletelabel, clickargs=(i), text="-")
				
			#add button
			box = [self.x,self.y+len(self.classes)*60+80,64,32]
			drawbox(box, self.world, (0,200,0), (0,175,0), self.createlabel, text="+")
			
		else:
			self.world.screen.blit(self.world.fontobject.render("match", 1, (0,0,0)),(self.x+75,self.y))
			self.world.screen.blit(self.world.fontobject.render("miss", 1, (0,0,0)),(self.x+120,self.y))
			for i in range(len(self.classes)):
				w,h = self.world.fontobject.size(str(self.classes[i]))
				w = max(64,w+30)
				box = [self.x,self.y+i*40+40,w,32]
				c=(200,200,200)
				hc=(175,175,175)
				if self.selected==i:
					c=(0,200,0)
					hc=(0,175,0)
					
				if self.keybinds[i]==None:
					txt="NA : "+str(self.classes[i])
				else:
					txt=str(chr(self.keybinds[i]))+" : "+str(self.classes[i])
				drawbox(box, self.world, c, hc, self.updateselect, clickargs=(i),text=txt)
				
				#auto select functions
				#match
				box = [self.x + 11 + w,self.y+i*40+40,32,32]
				c=(200,200,200)
				hc=(175,175,175)
				if self.defaultmatch==i:
					c=(0,200,0)
					hc=(0,175,0)
				drawbox(box, self.world, c, hc, self.updateautomatch, clickargs=(i),text="G")
				
				#miss
				box = [self.x + 46 +w,self.y+i*40+40,32,32]
				c=(200,200,200)
				hc=(175,175,175)
				if self.defaultmiss==i:
					c=(0,200,0)
					hc=(0,175,0)
				drawbox(box, self.world, c, hc, self.updateautomiss, clickargs=(i),text="x")
			