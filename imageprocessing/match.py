import cv2
import numpy as np
from utils import cvimage_to_pygame, clamp
import pygame

'''
1. select region
2. patern match on that region
3. auto detect other spots in that picture
'''

class match:
	def __init__(self,world,controller,x,y):
		self.world=world
		self.controller=controller
		self.x=x
		self.y=y
		
		self.selecting=False
		self.selectbox=[0,0,0,0]
		self.img=None
		self.width=0
		self.height=0
		self.selected=False
		self.template=None
		
		self.match_locations=[]
		
	def reset(self):
		self.match_locations=[]
		self.selecting=False
		self.selectbox=[0,0,0,0]
		self.selected=False
		self.template=None
		
	def update(self):
		try:
			self.height, self.width, channels = self.img.shape 
			if (self.x<self.world.mouse_x<self.x+self.width
			   and self.y<self.world.mouse_y<self.y+self.height):
				if self.world.mouse_left_down:
					self.selectbox[0]=self.world.mouse_x
					self.selectbox[1]=self.world.mouse_y
					self.selecting=True
					self.selected=False
			if self.selecting:
				self.selectbox[2]=clamp(self.world.mouse_x-self.selectbox[0],self.x-self.selectbox[0],self.x+self.width-self.selectbox[0])
				self.selectbox[3]=clamp(self.world.mouse_y-self.selectbox[1],self.y-self.selectbox[1],self.y+self.height-self.selectbox[1])
				
			if self.world.mouse_left_up:
				self.selecting=False
				self.selected=True
				
				#run template matching, get minimum val
				gray = cv2.cvtColor(self.img,cv2.COLOR_BGR2GRAY)
				template = cv2.cvtColor(self.template,cv2.COLOR_BGR2GRAY)
				res = cv2.matchTemplate(gray, template, cv2.TM_CCOEFF_NORMED)#TM_SQDIFF_NORMED
				min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
				
				# create threshold from min val, find where sqdiff is less than thresh
				min_thresh = .9# (min_val + 1e-6) * 1.5
				self.match_locations = np.where(res >= min_thresh)
				
			#create the template
			if self.selectbox[2]>0:
				x1=self.selectbox[0]-self.x
				x2=self.selectbox[0]+self.selectbox[2]-self.x
			else:
				x1=self.selectbox[0]+self.selectbox[2]-self.x
				x2=self.selectbox[0]-self.x
			if self.selectbox[3]>0:
				y1=self.selectbox[1]-self.y
				y2=self.selectbox[1]+self.selectbox[3]-self.y
			else:
				y1=self.selectbox[1]+self.selectbox[3]-self.y
				y2=self.selectbox[1]-self.y
			self.template=self.img[y1:y2, x1:x2]
			
			
			
			
		except:
			pass
			
	def predictboxes(self):
		pass
	
	def draw(self,img):
		self.img=img
		self.world.screen.blit(cvimage_to_pygame(img),(self.x, self.y))
		#select box
		pygame.draw.rect(self.world.screen, (0,255,0), self.selectbox, 3)
		
		#match boxes
		if self.selecting==False:
			for (x, y) in zip(self.match_locations[1], self.match_locations[0]):
				box=[self.x+x,self.y+y,self.selectbox[2],self.selectbox[3]]
				pygame.draw.rect(self.world.screen, (0,0,255), box, 3)
			   
			   
		#selected image
		if self.selected==True:
			self.world.screen.blit(cvimage_to_pygame(self.template),(self.x, self.y+self.height+10))
			
		