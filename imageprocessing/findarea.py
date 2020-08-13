import pygame
from utils import cvimage_to_pygame, clamp

'''
finds the two templates, and then finds the areas around those templates
'''

class findareas:
	def __init__(self,world,x,y):
		self.world=world
		self.x=x
		self.y=y
		
		self.img=None
		self.width=0
		self.height=0
		
	def draw(self, img):
		pass
		if img is None:
			return
		_,_,_ = self.img.shape 
		self.world.screen.blit(cvimage_to_pygame(img), (self.x, self.y))