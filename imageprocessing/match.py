import cv2
import numpy as np
from utils import cvimage_to_pygame, clamp, group_points, get_distance, checkmousebox, hsv_to_rgb
import pygame
from regression import line, isNaN, intersection
from interfacetools.label import label 

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
		
		self.labels=[]
		self.tempautolabels=[]
		self.labelselect=None
		
		self.lines=[]#line(self.world, x, y, [1,2,3], [1,2,3])
		self.intersections=[]
		
		self.selectmultibox=True
		self.selectsinglebox=False
		self.labelhandled=False
		
	def updatelabelselect(self, label):
		for l in self.labels:
			l.selected=False
		self.labelselect=label
		
	def deletelabel(self,label):
		i=self.labels.index(label)
		del self.labels[i]
		#del label
		
	def reset(self):
		self.labels=[]
		self.tempautolabels=[]
		self.selecting=False
		self.selectbox=[0,0,0,0]
		self.selected=False
		self.template=None
		self.lines=[]
		self.intersections=[]
		#self.selectmultibox=True
		
	def update(self):
		try:
			self.height, self.width, channels = self.img.shape 
		except:
			return
		
		#update the labels selection
		tempselect=False
		for l in self.labels:
			l.update()
			#deselecting
			if self.world.mouse_left_down:
				if (self.x<self.world.mouse_x<self.x+self.width
				   and self.y<self.world.mouse_y<self.y+self.height):
					t = l.checkselect()
					if t:
						tempselect=True
		if self.world.mouse_left_down:
			if (self.x<self.world.mouse_x<self.x+self.width
				   and self.y<self.world.mouse_y<self.y+self.height):
				if not tempselect:
					self.updatelabelselect(None)
			
			
		#start single select
		if self.world.mouse_left_down:
			if self.selectsinglebox:
				if (self.x<self.world.mouse_x<self.x+self.width
				   and self.y<self.world.mouse_y<self.y+self.height):
					self.selectbox[0]=self.world.mouse_x
					self.selectbox[1]=self.world.mouse_y
					self.selecting=True
					self.selected=False

		#start multi select
		if self.world.mouse_left_down:
			if self.selectmultibox:
				if (self.x<self.world.mouse_x<self.x+self.width
				   and self.y<self.world.mouse_y<self.y+self.height):
					self.selectbox[0]=self.world.mouse_x
					self.selectbox[1]=self.world.mouse_y
					self.selecting=True
					self.selected=False
					self.lines=[]
					self.intersections=[]
					#self.labels=[]
					self.tempautolabels=[]
				
		if self.selecting:
			self.selectbox[2]=clamp(self.world.mouse_x-self.selectbox[0],self.x-self.selectbox[0],self.x+self.width-self.selectbox[0])
			self.selectbox[3]=clamp(self.world.mouse_y-self.selectbox[1],self.y-self.selectbox[1],self.y+self.height-self.selectbox[1])
			
			#single
			if self.selectsinglebox:
				if self.world.mouse_left_up:
					self.selecting=False
					self.selectmultibox=False
					if abs(self.selectbox[2])>0 and abs(self.selectbox[3])>0:
						self.selected=True
						#create the label
						#if not self.controller.actionbar.classes==None:
						if not self.controller.actionbar.selected==None:
							labeltext=self.controller.actionbar.classes[self.controller.actionbar.selected]
							labelcolor=hsv_to_rgb(self.controller.actionbar.colors[self.controller.actionbar.selected].slideValue/360,1,1)
						else:
							labeltext="None"
							labelcolor=(0,0,0)
							
						l=label(self.world,self,self.selectbox[0]-self.x,self.selectbox[1]-self.y,self.selectbox[2],self.selectbox[3],labeltext,labelcolor)
						self.labels.append(l)
						self.selectsinglebox=False
						#select the label that was just created
						self.updatelabelselect(l)
						l.selected=True
					else:
						self.selected=False
						return
			#multi
			if self.selectmultibox:
				if self.world.mouse_left_up:
					self.selecting=False
					self.selectmultibox=False
					if abs(self.selectbox[2])>0 and abs(self.selectbox[3])>0:
						self.selected=True
					else:
						self.selected=False
						return
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
					
					#run template matching, get minimum val
					gray = cv2.cvtColor(self.img,cv2.COLOR_BGR2GRAY)
					template = cv2.cvtColor(self.template,cv2.COLOR_BGR2GRAY)
					res = cv2.matchTemplate(gray, template, cv2.TM_CCOEFF_NORMED)#TM_SQDIFF_NORMED
					min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
					
					# create threshold from min val, find where sqdiff is less than thresh
					min_thresh = .9# (min_val + 1e-6) * 1.5
					match_locations = np.where(res >= min_thresh)
					
					match_locations = (np.array(match_locations).T).tolist()
					match_locations = group_points(match_locations,10)
					
					#get the defaults from the actionbar
					try:
						labeltext = self.controller.actionbar.classes[self.controller.actionbar.defaultmatch]
						labelcolor=hsv_to_rgb(self.controller.actionbar.colors[self.controller.actionbar.defaultmatch].slideValue/360,1,1)
					except:
						labeltext = "NONE"
						labelcolor=(0,0,0)
						
					for m in match_locations:
						l=label(self.world,self,m[1],m[0],self.selectbox[2],self.selectbox[3],labeltext,(0,255,0))
						#self.labels.append(l)
						self.tempautolabels.append(l)
						
					#print(self.match_locations)
					
					
					self.predict_missing_boxes(labeltext)
			
				
			
		
	def predict_missing_boxes(self,goodlabeltext):
		#get the defaults from the actionbar
		try:
			labeltext = self.controller.actionbar.classes[self.controller.actionbar.defaultmiss]
			labelcolor=hsv_to_rgb(self.controller.actionbar.colors[self.controller.actionbar.defaultmiss].slideValue/360,1,1)
		except:
			labeltext = "NONE"
			labelcolor = (0,0,0)
			
		for p in self.tempautolabels:
			x=p.x
			y=p.y
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
		
		#find the missing points (intersections with no prediction box) with tolerance
		tolerance=5
		for p in self.intersections:
			#point = [p[1],p[0]]
			inMatch=False
			#for a in self.match_locations:
			for a in self.tempautolabels:
				if a.label==goodlabeltext:#"match":
					x=a.x
					y=a.y
					if (p[0]-tolerance < x < p[0]+tolerance
					and p[1]-tolerance < y < p[1]+tolerance):
						#if not point in self.match_locations:
						inMatch=True
			if not inMatch:
				l=label(self.world,self,p[0],p[1],self.selectbox[2],self.selectbox[3],labeltext,labelcolor)
				self.tempautolabels.append(l)
				#self.miss_locations.append(point)
		print("total labels: "+str(len(self.tempautolabels)))
		#add the temp labels and the labels, delete the temp labels
		self.labels=self.labels+self.tempautolabels
		self.tempautolabels=[]
		
	def draw(self, img):
		self.img = img
		try:
			_,_,_ = self.img.shape 
		except:
			return
			
		self.world.screen.blit(cvimage_to_pygame(img), (self.x, self.y))
		for l in self.lines:
			l.draw(self.width,self.height)
		#select box
		if self.selecting:
			pygame.draw.rect(self.world.screen, (0,255,0), self.selectbox, 3)
		
		'''
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
				pygame.draw.rect(self.world.screen, (255,0,0), box, 3)

			#intersections
			for p in self.intersections:
				x = int(p[0] + self.x)
				y = int(p[1] + self.y)
				pygame.draw.circle(self.world.screen,(255,255,0),(x,y),5)
			'''

		#template image
		try:
			self.world.screen.blit(cvimage_to_pygame(self.template),(self.x, self.y+self.height+10))
		except:
			pass
		
		#draw the selectMutlibox toggle
		box=[self.x,self.y-45,50,32]
		if checkmousebox(box,[self.world.mouse_x,self.world.mouse_y]):
			if self.world.mouse_left_down:
				self.selectmultibox = not self.selectmultibox
				self.selectsinglebox = False
				
			if self.selectmultibox:
				c = (10,200,10)
			else:
				c = (200,200,200)
		else:
			if self.selectmultibox:
				c=(10,180,10)
			else:
				c=(180,180,180)
				
		pygame.draw.rect(self.world.screen, c,(box[0],box[1],box[2],box[3]), 0)
		pygame.draw.rect(self.world.screen, (0,0,0),(box[0]-1,box[1]-1,box[2]+1,box[3]+1), 1)
		self.world.screen.blit(self.world.fontobject.render("AUTO", 1, (0,0,0)),(box[0]+5, box[1]+5))
		
		#draw the add single box
		box=[self.x+75,self.y-45,64,32]
		if checkmousebox(box,[self.world.mouse_x,self.world.mouse_y]):
			if self.world.mouse_left_down:
				self.selectsinglebox = not self.selectsinglebox
				self.selectmultibox = False
				
			if self.selectsinglebox:
				c = (10,200,10)
			else:
				c = (200,200,200)
		else:
			if self.selectsinglebox:
				c=(10,180,10)
			else:
				c=(180,180,180)
				
		pygame.draw.rect(self.world.screen, c,(box[0],box[1],box[2],box[3]), 0)
		pygame.draw.rect(self.world.screen, (0,0,0),(box[0]-1,box[1]-1,box[2]+1,box[3]+1), 1)
		self.world.screen.blit(self.world.fontobject.render("ADD 1", 1, (0,0,0)),(box[0]+5, box[1]+5))
		
		for l in self.labels:
			l.draw()
		
		