import pygame
import numpy as np
from utils import checkmousebox, clamp

class label:
	def __init__(self, world, controller, x, y, w, h, label, color,accuracy=100, template=""):
		self.world=world
		self.controller=controller
		self.x=x
		self.y=y
		self.w=w
		self.h=h
		

		
		if w<0:
			self.x=x+w
			self.w=abs(w)
		if h<0:
			self.y=y+h
			self.h=abs(h)
		
		self.color=color
		self.label=label
		self.accuracy=round(accuracy*100)/100
		self.template=template
		
		self.selected=False
		
		self.selecttr=False
		self.selectbl=False
		self.selectedcords=[]
		self.selectmove=False
	def __str__(self):
		return "["+str(self.x)+","+str(self.y)+","+str(self.w)+","+str(self.h)+"]"
	def reset(self):
		self.selecttr=False
		self.selectbr=False
		self.selectmove=False
		self.selectedcords=[]
		
	def checkselect(self):
		#selecting this object
		temp=False
		if not self.controller.labelhandled:
			x = self.x + self.controller.x
			y = self.y + self.controller.y
			selectbox = [x-10, y-10, self.w+20, self.h+20]
			
			if checkmousebox(selectbox,[self.world.mouse_x,self.world.mouse_y]):
				self.controller.updatelabelselect(self)
				self.selected=True
				temp=True
				
				#update the action bar with the current one
				try:
					i=self.controller.actionbar.classes.index(self.label)
					self.controller.actionbar.selected=i#self.controller.controller.actionbar.classes[i]
				except Exception as e:
					print(e)
					#self.controller.controller.actionbar.selected=None
		return temp
	def update(self):
		#deletion
		if not self.controller.actionbar.editmode:			
			if self.selected:
				for key in self.world.keyspressed:
					if key == pygame.K_DELETE or key==pygame.K_BACKSPACE:
						self.controller.deletelabel(self)
						del self
				
	def draw(self):
		x = self.x + self.controller.x
		y = self.y + self.controller.y
		box = [x, y, self.w, self.h]
		pygame.draw.rect(self.world.screen, self.color, box, 3)	
		
		if self.controller.labelshowtext:
			if self.accuracy!=100 and self.controller.labelshowpercent:
				label=str(self.label)+":"+str(self.accuracy)+"%"
			else:
				label=self.label
			#else:
				#label=str(self.label)+":"+str(self.template)+":"+str(self.accuracy)+"%"
				
			w,h = self.world.fontobject.size(label)
			w = max(5,w)
			labelbox=[x+5,y-17,w,15]
			pygame.draw.rect(self.world.screen, (255,255,255), labelbox)	
			self.world.screen.blit(self.world.fontobject.render(label, 1, (0,0,0)),(box[0]+5, box[1]-15))
			
		#draw the handles
		if self.selected:
			xx = self.controller.x
			yy = self.controller.y
			
			#top right
			box=[self.x+xx-5,self.y+yy-5,10,10]
			if checkmousebox(box,[self.world.mouse_x,self.world.mouse_y]):
				c = (175,175,175)
				if not self.controller.labelhandled:
					if self.world.mouse_left_down:
						self.reset()
						self.selectedcords=[self.x+xx+self.w,self.y+self.h+yy]
						self.selecttr=True
						self.controller.labelhandled=True
			else:
				c = (200, 200, 200)
				
			pygame.draw.rect(self.world.screen, c ,(box[0],box[1],box[2],box[3]), 0)
			pygame.draw.rect(self.world.screen, (0,0,0),(box[0]-1,box[1]-1,box[2]+1,box[3]+1), 1)
			
			#bottm left
			box=[self.x+xx+self.w-5,self.y+yy+self.h-5,10,10]
			if checkmousebox(box,[self.world.mouse_x,self.world.mouse_y]):
				c = (175,175,175)
				if not self.controller.labelhandled:
					if self.world.mouse_left_down:
						self.reset()
						self.selectedcords=[self.x+xx, self.y+yy]
						self.selectbl=True
						self.controller.labelhandled=True
			else:
				c = (200, 200, 200)
			pygame.draw.rect(self.world.screen, c ,(box[0],box[1],box[2],box[3]), 0)
			pygame.draw.rect(self.world.screen, (0,0,0),(box[0]-1,box[1]-1,box[2]+1,box[3]+1), 1)
			
			#move middle
			box=[self.x+xx+self.w/2-5,self.y+yy+self.h/2-5,10,10]
			if checkmousebox(box,[self.world.mouse_x,self.world.mouse_y]):
				c = (175,175,175)
				if not self.controller.labelhandled:
					if self.world.mouse_left_down:
						self.reset()
						self.selectedcords=[self.x+xx, self.y+yy]
						self.selectmove=True
						self.controller.labelhandled=True
			else:
				c = (200, 200, 200)
			pygame.draw.rect(self.world.screen, c ,(box[0],box[1],box[2],box[3]), 0)
			pygame.draw.rect(self.world.screen, (0,0,0),(box[0]-1,box[1]-1,box[2]+1,box[3]+1), 1)
			
			
			if self.selectmove:
				if self.world.mouse_left:
					self.x = clamp(self.world.mouse_x-self.controller.x-self.w/2, 0, self.controller.width-self.w)
					self.y = clamp(self.world.mouse_y-self.controller.y-self.h/2, 0, self.controller.height-self.h)
					self.accuracy=100
				else:
					self.selectmove=False
					self.controller.labelhandled=False
			
			if self.selecttr:
				if self.world.mouse_left:
					self.x = clamp(self.world.mouse_x-self.controller.x, 0, self.selectedcords[0]-xx-10)
					self.y = clamp(self.world.mouse_y-self.controller.y, 0, self.selectedcords[1]-yy-10)
					self.w = max(self.selectedcords[0] - clamp(self.world.mouse_x,xx,xx+self.controller.width),10)
					self.h = max(self.selectedcords[1] - clamp(self.world.mouse_y,yy,yy+self.controller.height),10)
					self.accuracy=100
				else:
					self.selecttr=False
					self.controller.labelhandled=False
					
			if self.selectbl:
				if self.world.mouse_left:
					self.w = clamp(self.world.mouse_x - self.selectedcords[0],10, self.controller.width-self.x)#min(self.controller.width -self.x, self.world.mouse_x - self.selectedcords[0])
					self.h = clamp(self.world.mouse_y - self.selectedcords[1],10, self.controller.height-self.y)#min(self.controller.height -self.y, self.world.mouse_y - self.selectedcords[1])
					self.accuracy=100
				else:
					self.selectbl=False
					self.controller.labelhandled=False
		
