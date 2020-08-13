import cv2
import numpy as np
from utils import cvimage_to_pygame, clamp, group_points, get_distance, checkmousebox, hsv_to_rgb, folderLoad
import pygame
from regression import line, isNaN, intersection
from interfacetools.label import label 
from interfacetools.slider import slider

import os

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
		
		self.template=None
		self.templatewidth=None
		self.templateheight=None
		
		self.tempautolabels=[]
		
		self.lines=[]#line(self.world, x, y, [1,2,3], [1,2,3])
		self.intersections=[]
		
		self.accuracyslider=slider(self.world,400,23,"accuracy",sliderange=(.01,1),start=.9,incriment=.01)
		
		
		
	def reset(self):
		self.tempautolabels=[]
		self.template=None
		self.lines=[]
		self.intersections=[]
	
	def match(self,img,template=None):
		if not template is None:
			self.template=template
		else:
			if self.template is None:
				return
			
		#cv2.imwrite("test.png",template)
		self.tempautolabels=[]
		
		self.templateheight,self.templatewidth,_=self.template.shape
		
		#run template matching, get minimum val
		gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
		gray_template = cv2.cvtColor(self.template,cv2.COLOR_BGR2GRAY)
		
		res = cv2.matchTemplate(gray, gray_template, cv2.TM_CCOEFF_NORMED)#TM_SQDIFF_NORMED
		min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
		
		# create threshold from min val, find where sqdiff is less than thresh
		min_thresh = self.accuracyslider.slideValue#.9# (min_val + 1e-6) * 1.5
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
			l=label(self.world,self.controller,m[1],m[0],self.templatewidth,self.templateheight,labeltext,(0,255,0),accuracy=res[m[0]][m[1]]*100)
			#self.labels.append(l)
			self.tempautolabels.append(l)
			
		#print(self.match_locations)
		return self.predict_missing_boxes(labeltext)
			
				
			
		
	def predict_missing_boxes(self,goodlabeltext):
		self.lines=[]
		self.intersections=[]
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
				l=label(self.world,self.controller,p[0],p[1],self.templatewidth,self.templateheight,labeltext,labelcolor)
				self.tempautolabels.append(l)
				#self.miss_locations.append(point)
		print("total labels: "+str(len(self.tempautolabels)))
		#return self.tempautolabels
	
	def confirm(self):
		temp=self.tempautolabels
		self.tempautolabels=[]
		return temp
	def cancel(self):
		self.tempautolabels=[]
		
	def draw(self, img):
		if img is None:
			return
		height,width,_ = img.shape 
		for l in self.lines:
			l.draw(width,height)
			
		for l in self.tempautolabels:
			l.draw()
		
		
		
		#self.accuracyslider.draw()
		#template image
		try:
			self.world.screen.blit(cvimage_to_pygame(self.template),(self.x, self.y+height+10))
		except:
			pass
		
		
		
		