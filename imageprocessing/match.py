import cv2
import numpy as np
from utils import cvimage_to_pygame, clamp, group_points, get_distance
import pygame
from regression import line, isNaN, intersection

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
		self.miss_locations=[]
		self.lines=[]#line(self.world, x, y, [1,2,3], [1,2,3])
		self.intersections=[]
		
	def reset(self):
		self.match_locations=[]
		self.selecting=False
		self.selectbox=[0,0,0,0]
		self.selected=False
		self.template=None
		self.lines=[]
		self.intersections=[]
		
	def update(self):
		try:
			self.height, self.width, channels = self.img.shape 
		except:
			return
		
		if (self.x<self.world.mouse_x<self.x+self.width
		   and self.y<self.world.mouse_y<self.y+self.height):
			if self.world.mouse_left_down:
				self.selectbox[0]=self.world.mouse_x
				self.selectbox[1]=self.world.mouse_y
				self.selecting=True
				self.selected=False
				self.lines=[]
				
		if self.selecting:
			self.selectbox[2]=clamp(self.world.mouse_x-self.selectbox[0],self.x-self.selectbox[0],self.x+self.width-self.selectbox[0])
			self.selectbox[3]=clamp(self.world.mouse_y-self.selectbox[1],self.y-self.selectbox[1],self.y+self.height-self.selectbox[1])
			
			
			if self.world.mouse_left_up:
				self.selecting=False
				if abs(self.selectbox[2])>0 and abs(self.selectbox[3])>0:
					self.selected=True
				else:
					self.selected=False
					return
				
				#run template matching, get minimum val
				gray = cv2.cvtColor(self.img,cv2.COLOR_BGR2GRAY)
				template = cv2.cvtColor(self.template,cv2.COLOR_BGR2GRAY)
				res = cv2.matchTemplate(gray, template, cv2.TM_CCOEFF_NORMED)#TM_SQDIFF_NORMED
				min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
				
				# create threshold from min val, find where sqdiff is less than thresh
				min_thresh = .9# (min_val + 1e-6) * 1.5
				self.match_locations = np.where(res >= min_thresh)
				
				self.match_locations = (np.array(self.match_locations).T).tolist()
				self.match_locations = group_points(self.match_locations,10)
				#print(self.match_locations)
				
				
				self.predict_missing_boxes()
			
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
			
		
	def predict_missing_boxes(self):
		#self.miss_locations=[]
		distance=15
		#print("predicting missing")

		#xx = np.array(self.match_locations).T[0]
		#yy = np.array(self.match_locations).T[1]
		
		
		for p in self.match_locations:
			x=p[1]
			y=p[0]
			#print(str(x)+","+str(y))
			hline = line(self.world, self.x, self.y, [x,x+10], [y,y])
			vline = line(self.world, self.x, self.y, [x,x], [y,y+10])
			self.lines.append(hline)
			self.lines.append(vline)
		
		#combine the overlapping lines
		slopethresh=.005
		interceptthresh=15
		for i in range(len(self.lines)):
			for j in range(len(self.lines)):
				if not i==j:
					try:
						#for vertical lines
						if (isNaN(self.lines[i].slope) and isNaN(self.lines[j].slope)):
							if np.mean(self.lines[i].xlist)-interceptthresh<np.mean(self.lines[j].xlist)<np.mean(self.lines[i].xlist)+interceptthresh:
								self.lines[i].xlist[0]=(self.lines[i].xlist[0]+self.lines[i].xlist[1])/2
								del self.lines[j]
					except Exception as e:
						#print(e)
						pass
					try:
						if not (isNaN(self.lines[i].slope) and isNaN(self.lines[j].slope)):
							if self.lines[i].slope-slopethresh<self.lines[j].slope<self.lines[i].slope+slopethresh:
								if self.lines[i].intercept-interceptthresh<self.lines[j].intercept<self.lines[i].intercept+interceptthresh:
									self.lines[i].slope=(self.lines[i].slope+self.lines[j].slope)/2
									self.lines[i].intercept=(self.lines[i].intercept+self.lines[j].intercept)/2
									del self.lines[j]
					except Exception as e:
						#print(e)
						pass
		print("total lines: "+str(len(self.lines)))
		
		#find the intersect of all the lines
		'''
		1. go through the lines
		2. check if all the other lines dont intersect, that is if they have a different slope
			-check vertical lines
				-check if both are NAN, if they are then just continue
			-check the non vertical lines
		'''
		colnum=0
		for l1 in self.lines:
			for l2 in self.lines:
				if l1!=l2:
					#get the intersection
					x = intersection(l1, l2)
					p=[]
					if not x == None:
						if not isNaN(l1.slope):
							p=[x,l1.returny(x)]
						else:
							p=[x,l2.returny(x)]
					if p:
						if not p in self.intersections:
							self.intersections.append(p)
		print("total intersections: "+str(len(self.intersections)))
		print(self.intersections)
		
	def draw(self, img):
		self.img = img
		self.world.screen.blit(cvimage_to_pygame(img), (self.x, self.y))
		for l in self.lines:
			l.draw(self.width,self.height)
		#select box
		pygame.draw.rect(self.world.screen, (0,255,0), self.selectbox, 3)
		
		#match boxes
		if self.selecting==False:
			#template matched boxes
			for point in self.match_locations:#zip(self.match_locations[1], self.match_locations[0]):
				x = point[1] + self.x
				y = point[0] + self.y
				#box = [self.x+x,self.y+y, self.selectbox[2], self.selectbox[3]]
				box = [x,y, self.selectbox[2], self.selectbox[3]]
				pygame.draw.rect(self.world.screen, (0,255,0), box, 3)
			
			
			#predicted missing boxes
			for point in self.miss_locations:#(x, y) in zip(self.miss_locations[0], self.miss_locations[1]):
				x = point[1] + self.x
				y = point[0] + self.y
				#box = [self.x+x,self.y+y, self.selectbox[2], self.selectbox[3]]
				box = [x, y, self.selectbox[2], self.selectbox[3]]
				pygame.draw.rect(self.world.screen, (0,0,255), box, 3)
				
			#intersections
			for p in self.intersections:
				x = p[0] + self.x
				y = p[1] + self.y
				pygame.draw.circle(self.world.screen,(255,255,0),(x,y),5)
			

		#selected image
		if self.selected==True:
			self.world.screen.blit(cvimage_to_pygame(self.template),(self.x, self.y+self.height+10))
			
		
			
		