import pygame
import numpy as np
from utils import checkmousebox

class label:
	def __init__(self, world, controller, x, y, w, h, label, color):
		self.world=world
		self.controller=controller
		self.x=x
		self.y=y
		self.w=w
		self.h=h
		
		self.color=color
		self.label=label
		
		self.selected=True
		
	def update(self):
		#updates if this is selected
		pass
		
	def draw(self):
		x = self.x + self.controller.x
		y = self.y + self.controller.y
		box = [x, y, self.w, self.h]
		pygame.draw.rect(self.world.screen, self.color, box, 3)	
		
		'''
		#draw the handles
		if self.selected:
			#top right
			box=[self.x,self.y,5,5]
			if checkmousebox(box,[self.world.mouse_x,self.world.mouse_y]):
				c = (175,175,175)
			else:
				c = (200,200,200)
			pygame.draw.rect(world.screen, c ,(box[0],box[1],box[2],box[3]), 0)
			pygame.draw.rect(world.screen, (0,0,0),(box[0]-1,box[1]-1,box[2]+1,box[3]+1), 1)
		'''
		
