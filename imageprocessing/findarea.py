import pygame
from utils import cvimage_to_pygame, clamp
from interfacetools.label import label 
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
		
	def inrow(self,rows,label):
		for r in rows:
			for l in r:
				if (l.x==label.x and l.y==label.y and l.w==label.w and l.h==label.h):
					return True
		return False
	
	def find(self,labels):
		#loop through the labels and figure out what ones are in the rows
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
					
					d=.55
					d1=.3
					
					totaly=min(r[i].y,r[i+1].y)
					totalh=(max(r[i].y+r[i].h,r[i+1].y+r[i+1].h)-totaly)
					
					yy1=totaly
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
					xx=r[i].x+r[i].w
					yy=min(r[i].y,r[i+1].y)
					ww=r[i+1].x-xx 
					hh=(max(r[i].y+r[i].h,r[i+1].y+r[i+1].h)-yy)*1.1
					
					l=label(self.world,self.controller,xx,yy,ww,hh,"5",(0,0,255))
					self.tempautolabels.append(l)
				
				
		'''
		for l1 in self.controller.labels:
			temp=[]
			#check if in row already
			inrow=False
			for r in rows:
				if inrow:
					break
				for l in r:
					if (l.x==l1.x and l.y==l1.y and l.h==l1.h and l.w==l1.w):
						inrow=True
			if inrow:
				continue
			#else than look at all the other labels
			for l2 in self.controller.labels:
				if not(l2.x==l1.x and l2.y==l1.y and l2.h==l1.h and l2.w==l1.w):
					if ((l1.y<l2.y<l1.y+l1.h)
					or (l2.y<l1.y<l2.y+l2.h)):
						temp.append(l2)
			if temp:
				rows.append(temp)
				print(len(temp))
				
		#print(len(rows))
		for r in rows:
			print(["("+str(l.y)+","+str(l.h)+")" for l in r])
		'''
		'''
		while sortedlabels:
			ref = sortedlabels.pop(0)
			key="["+str(ref.y)+","+str(ref.h)+"]"
			groups[key] = [ref]
			#print([ref])
			for i, point in enumerate(sortedlabels):
				#d = get_distance(ref, point)
				if (ref.y<point.y<ref.y+ref.h
				or point.y<ref.y<point.y+point.h):
					#print(point)
					groups[key].append(sortedlabels[i])
					sortedlabels[i] = None
			sortedlabels = list(filter(lambda x: x is not None, sortedlabels))
			'''

		# perform average operation on each group
		#return [[int(np.mean([x[0] for x in groups[arr]])), int(np.mean([x[1] for x in groups[arr]]))] for arr in groups]
		'''
		#check the rows
		for r in rows:
			###!!!TODO: check the y + the height
			if (r-tolerance<p.y<r+tolerance
				or r-tolerance<p.y+p.h<r+tolerance):
				inlist=True
				
				
		if not inlist:
			rows.append(p.y)
		'''
	'''
	sortedlabels=sorted(self.controller.labels,key=lambda x:(x.y,x.x))
	for i,p in enumerate(sortedlabels):
		try:
			xx = p.x+p.w
			yy = p.y
			if (p.y<sortedlabels[i+1].y<p.y+p.h
			or p.y<sortedlabels[i+1].y+sortedlabels[i+1].h<p.y+p.h):
				ww = sortedlabels[i+1].x-xx
				hh = (sortedlabels[i+1].y+sortedlabels[i+1].h)-p.y
				l=label(self.world,self.controller,xx,yy,ww,hh,"region test",(0,0,255))
				self.tempautolabels.append(l)
			else:
				continue
		except:
			continue
			
		'''
		#pass
		
	def confirm(self):
		temp=self.tempautolabels
		self.tempautolabels=[]
		return temp
	def cancel(self):
		self.tempautolabels=[]
		
		
	def draw(self, img):
		if img is None:
			return
		self.height,self.width,_ = img.shape 
		
		for l in self.tempautolabels:
			l.draw()