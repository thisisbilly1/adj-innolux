import pygame
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
		self.img = img
		try:
			_,_,_ = self.img.shape 
		except:
			return
			
		self.world.screen.blit(cvimage_to_pygame(img), (self.x, self.y))