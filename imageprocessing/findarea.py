import pygame
from utils import cvimage_to_pygame, clamp
from interfacetools.label import label 
import cv2
import numpy as np

'''
finds the two templates, and then finds the areas around those templates
'''

class findareas:
	def __init__(self,world,controller,x,y):
		self.world=world
		self.controller=controller
		self.x=x
		self.y=y
		
		self.tempautolabels=[]
		self.width=0
		self.height=0
		self.img=None
		
		self.templateimages=[]#((x,y),img)
		
	def inrow(self,rows,label):
		for r in rows:
			for l in r:
				if (l.x==label.x and l.y==label.y and l.w==label.w and l.h==label.h):
					return True
		return False
	
	def defectedAreaCheck(self,l):
		#get the image
		x1=int(l.x)
		y1=int(l.y)
		x2=int(l.x+l.w)
		y2=int(l.y+l.h)
		
		#crop and thresh
		cropped = self.img[y1:y2, x1:x2]
		gray = cv2.cvtColor(cropped,cv2.COLOR_BGR2GRAY)
		#thresh = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 11, 2)
		ret,thresh = cv2.threshold(gray,127,255,cv2.THRESH_BINARY)
		
		#open the image
		kernel = np.ones((5,5),np.uint8)
		#opening = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel)
		
		#contours, hierarchy = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
		#cv2.drawContours(cropped, contours, -1, (0,255,0), 3)
		
		#self.templateimages.append(((x1,y1),thresh))
		
		#check for black spots/blobs
		whiteCount=np.count_nonzero(thresh)
		percent=whiteCount/(l.h*l.w)
		print(str(percent*100)+" %")
		#change the label to bad it's too much
		if percent<.9:
			l.color=(255,0,0)
			l.label="ng"
			
	def find(self,labels,img):
		self.img=img
		#loop through the labels and figure out what labels are in the rows
		rows=[]
		for l1 in self.controller.labels:
			if not self.inrow(rows,l1):
				temp=[l1]
				for l2 in self.controller.labels:
					if not l1==l2:
						if not self.inrow(rows,l2):
							if ((l1.y<=l2.y<=l1.y+l1.h-10)
							or (l2.y<=l1.y<=l2.y+l2.h-10)):
								temp.append(l2)
				rows.append(temp)
		#sort the rows
		rows=[sorted(r, key=lambda l: l.x) for r in rows]
		
		#filter out all the rows with only one template label in them
		temp=[]
		for r in rows:
			template1=False
			template2=False
			for l in r:
				if l.template=="square.png":
					template1=True
				if l.template=="test.png":
					template2=True
			if (template1 and template2):
				temp.append(r)
		rows=temp
		
		#make the labels for the rows
		for r in rows:
			#print(["("+str(l.y)+","+str(l.h)+")" for l in r])
			for i in range(len(r)-1):
				
				#seperate 
				if r[i].template!="square.png":
					#underneath the squiggly part
					xx=r[i].x
					ww=r[i].w
					yy=r[i].y+r[i].h
					hh=r[i].h*.55
					
					l=label(self.world,self.controller,xx,yy,ww,hh,"1",(241,255,0))
					self.tempautolabels.append(l)
					
					#middle section, 3 parts
					xx=r[i].x+r[i].w
					ww=r[i+1].x-xx 
					
					d=.48
					d1=.3
					
					miny=min(r[i].y,r[i+1].y) + (max(r[i].y+r[i].h,r[i+1].y+r[i+1].h)-min(r[i].y,r[i+1].y))*.15
					totalh=(max(r[i].y+r[i].h,r[i+1].y+r[i+1].h)-miny)
					
					yy1=miny
					hh1=totalh*d
					
					yy2=yy1+hh1
					hh2=hh1*d1#hh1*(1-d)
					
					yy3=yy2+hh2
					hh3=(totalh*1.07)-hh2-hh1
					
					l=label(self.world,self.controller,xx,yy1,ww,hh1,"2",(241,51,255))
					self.tempautolabels.append(l)
				
					l=label(self.world,self.controller,xx,yy2,ww,hh2,"3",(64,255,249))
					self.tempautolabels.append(l)
					
					l=label(self.world,self.controller,xx,yy3,ww,hh3,"4",(163,32,171))
					self.tempautolabels.append(l)
					
				else:
					xx=r[i].x+r[i].w + (r[i+1].x-r[i].x+r[i].w)*.025
					yy=min(r[i].y,r[i+1].y)+(max(r[i].y+r[i].h,r[i+1].y+r[i+1].h)-min(r[i].y,r[i+1].y))*.15
					
					ww=r[i+1].x-xx 
					hh=(max(r[i].y+r[i].h,r[i+1].y+r[i+1].h)-yy)
					
					#yy1=yy-hh*.05
					#hh1=hh*95
					
					l=label(self.world,self.controller,xx,yy,ww,hh,"5",(0,0,255))
					self.tempautolabels.append(l)
		
		#check the labels for defects
		for l in self.tempautolabels:
			self.defectedAreaCheck(l)
			
			
	def confirm(self):
		temp=self.tempautolabels
		self.tempautolabels=[]
		self.templateimages=[]
		return temp
	
	def cancel(self):
		self.tempautolabels=[]
		self.templateimages=[]
		
	def draw(self, img):
		if img is None:
			return
		self.height,self.width,_ = img.shape 
		
		
		
		
		for l in self.templateimages:
			self.world.screen.blit(cvimage_to_pygame(l[1]), (l[0][0]+self.x,l[0][1]+self.y))
		
		for l in self.tempautolabels:
			l.draw(thickness=1)
		
			