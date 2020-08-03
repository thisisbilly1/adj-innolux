from scipy import stats
import numpy as np
import cv2
import random
import pygame
import math

def point_distance(x1,y1,x2,y2):
	return ((x2-x1)**2+(y2-y1)**2)**.5

def isNaN(num):
    return num != num

def intersection(l1,l2):
	'''
	solves l1=l2
	y=m1x+b1
	y=m2x+b2
	
	m1x+b1=m2x+b2
	
	we find x
	m1x=m2x+b2-b1
	m1x-m2x=b2-b1
	(m1-m2)*x=b2-b1
	x=(b2-b1)/(m1-m2)
	'''
	m1=l1.slope
	b1=l1.intercept
	m2=l2.slope
	b2=l2.intercept
	
	if (isNaN(m1) and not isNaN(m2)):
		x = l1.xlist[0]
	elif (isNaN(m2)) and not isNaN(m1):
		x = l2.xlist[0]
	elif (isNaN(m2) and isNaN(m1)):
		x=None
	elif m1==m2:
		x=None
	else:
		try:
			x = (b2-b1)/(m1-m2)
		except:
			x = None
	
	return x

class line:
	def __init__(self,world,x,y,xlist,ylist):
		self.x = x
		self.y = y
		
		self.xlist = xlist
		self.ylist = ylist
		self.world=world
		
		self.slope, self.intercept, self.r_value, self.p_value, self.std_err = stats.linregress(self.xlist,self.ylist)
		#print(self.slope)
		
	def returny(self,x):
		return self.slope*x+self.intercept
		 
	def draw(self,w,h):
		
		try:
			#pygame.draw.line(self.world.screen, (0,0,255), (100,200), (300,450),5)
			if not isNaN(self.slope):
				if not isNaN(self.intercept):
					#print("asdfasdf")
					startpoint=[self.x, self.y+self.intercept]
					endpoint=[self.x+w,self.y+self.slope*w+self.intercept]
					pygame.draw.line(self.world.screen, (0,0,255), startpoint, endpoint, 1)
					
					#pygame.draw.line(self.world.screen,(0,0,0),p,3)
					#cv2.line(img,startpoint,endpoint,self.color,3)
			else:
				#print(str(self.intercept) + ", "+str(self.slope))
				startpoint=[self.x+self.xlist[0], self.y]
				endpoint=[self.x+self.xlist[0], self.y+h]
				pygame.draw.line(self.world.screen, (0,0,255), startpoint, endpoint, 1)
		except Exception as e:
			#print(str(e)+", "+str(self.slope))
			#print(e)
			pass
			#pass
			
if __name__=="__main__":
	l1=line(None,0,0,[1,2,3],[1,1,1])
	l2=line(None,0,0,[1,1,1],[1,2,3])
	print(intersection(l1,l2))