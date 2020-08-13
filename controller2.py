import numpy as np
import pygame
import cv2
import math

from tkinter import filedialog
from tkinter import *
import os

from utils import clamp, cvimage_to_pygame, drawbox, prettifyXML, hsv_to_rgb,checkmousebox

#from imageprocessing.edge import edge
from imageprocessing.match2 import match
from interfacetools.actionbar import actionbar
from interfacetools.dropdown import dropdown
from interfacetools.label import label 

from xml.etree.ElementTree import Element, SubElement
import xml.etree.ElementTree as ET


class controller:
	def __init__(self,world):
		self.world=world
		
		self.x=94
		self.y=50
		
		#for dragging the image
		self.xx=0
		self.yy=0
		self.mouse_clicked=(0,0)
		
		self.imagelist=[]
		self.imagehasxml=[]
		self.imagelistFiles=[]
		self.currentfolder="images"
		
		self.img=None
		#self.edge=edge(self.world,self,94,10)
		self.match = match(self.world,self,self.x,self.y)
		#self.match = match(self.world,self,94,50)
		self.actionbar=actionbar(self.world,self,1125,50)
		
		self.loadFolder(self.currentfolder)
		self.filesperpage=20
		self.page=1
		self.totalpages=0
		
		self.Fileselected=-1
		
		#labels
		self.labels=[]
		self.labelhandled=False
		self.labelselect=None
		
		self.selectmultibox=False
		self.selectsinglebox=False
		
		self.selecting=False
		self.selectbox=[0,0,0,0]
		self.width=0
		self.height=0
		
		#template
		imglist=["manual"]
		for file in os.listdir("./templates"):
			if file.endswith(".png") or file.endswith(".jpg") or file.endswith(".JPG") or file.endswith(".PNG"):
				imglist.append(str(file))
		self.templatedropdown=dropdown(self.world,400,10,imglist,label="templates")
		
		
	def updatelabelselect(self, label):
		for l in self.labels:
			l.selected=False
		self.labelselect=label
	
	def deletelabel(self,label):
		i=self.labels.index(label)
		del self.labels[i]
		#del label
		
	def update(self):
		#dragging around
		if self.world.mouse_right_down or self.world.mouse_right_up:
			self.mouse_clicked=(self.world.mouse_x,self.world.mouse_y)
		if self.world.mouse_right:
			self.xx+=self.world.mouse_x-self.mouse_clicked[0]
			self.yy+=self.world.mouse_y-self.mouse_clicked[1]
			self.mouse_clicked=(self.world.mouse_x,self.world.mouse_y)
		
		if (pygame.K_s in self.world.keyspress):
			if ((pygame.K_LCTRL) in self.world.keyspressed):
				self.save()
			if ((pygame.K_RCTRL) in self.world.keyspressed):
				self.save()
				
		#self.match.update()
		self.actionbar.update()
		
		if not self.templatedropdown.clicked:
			self.selectregion()
	
	def selectregion(self):
		#selecting
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
					
					
		#start select
		if self.world.mouse_left_down:
			#single
			if self.selectsinglebox:
				if (self.x<self.world.mouse_x<self.x+self.width
				   and self.y<self.world.mouse_y<self.y+self.height):
					self.selectbox[0]=self.world.mouse_x
					self.selectbox[1]=self.world.mouse_y
					self.selecting=True
					self.selected=False
			#multi
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
		#while selecting
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
						if not self.actionbar.selected==None:
							labeltext=self.actionbar.classes[self.actionbar.selected]
							labelcolor=hsv_to_rgb(self.actionbar.colors[self.actionbar.selected].slideValue/360,1,1)
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
					
			#multi match
			if self.selectmultibox:
				if self.world.mouse_left_up:
					self.selecting=False
					#self.selectmultibox=False
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
						
					template=self.img[y1:y2, x1:x2]
					#self.labels+=
					self.match.match(self.img,template)
					
	def loadlistimages(self,args=()):
		root = Tk()
		root.withdraw()
		folder = filedialog.askdirectory(parent=root)
		self.loadFolder(folder)
		
	def loadFolder(self,folder):
		try:
			os.listdir(folder)
		except:
			return
		self.imagelist=[]
		self.imagelistFiles=[]
		self.imagehasxml=[]

		for file in os.listdir(folder):
			if file.endswith(".png") or file.endswith(".jpg") or file.endswith(".JPG") or file.endswith(".PNG"):
				xmlname=str(file)[:-3]+"xml"
				self.imagehasxml.append(os.path.exists(str(folder)+"/"+xmlname))
				
				self.imagelistFiles.append(str(folder)+"/"+str(file))
				if len(str(file))>9:
					self.imagelist.append(str(file)[0:6]+"...")
				else:
					self.imagelist.append(str(file))
		#print(self.imagelist)
				
	def loadimg(self,args=()):
		i=args
		self.Fileselected=i
		self.img=cv2.imread(self.imagelistFiles[i])
		self.match.reset()
		self.labels=[]
		
		#load the labels if the xml file exists
		xmlfilename=self.imagelistFiles[self.Fileselected][:-3]+"xml"
		if os.path.exists(xmlfilename):
			root = ET.parse(xmlfilename).getroot()
			for l in root.findall('object'):
				name=l.find('name')
				#print(name.text)
				
				bndbox=l.find('bndbox')
				xmin=bndbox.find("xmin")
				ymin=bndbox.find("ymin")
				xmax=bndbox.find("xmax")
				ymax=bndbox.find("ymax")
				
				x=float(xmin.text)
				y=float(ymin.text)
				w=float(xmax.text)-float(xmin.text)
				h=float(ymax.text)-float(ymin.text)
				try:
					i=self.actionbar.classes.index(name.text)
					c=hsv_to_rgb(self.actionbar.colors[i].slideValue/360,1,1)
				except:
					c=(0,0,0)
					
				loadedlabel = label(self.world,self,x,y,w,h,name.text,c)
				self.labels.append(loadedlabel)
			print("loaded xml")
	def save(self,args=()):
		try:
			h,w,d = self.img.shape
		except Exception as e:
			return
		
		annotation = Element('annotation')
		
		folder = SubElement(annotation, 'folder')
		folder.text = self.currentfolder
		
		filename = SubElement(annotation, 'filename')
		filename.text = self.imagelistFiles[self.Fileselected]
		
		path = SubElement(annotation, 'path')
		path.text = os. getcwd() + "\\" +self.imagelistFiles[self.Fileselected].replace("/","\\")
		
		source = SubElement(annotation, 'source')
		database = SubElement(source, 'database')
		database.text = "Unknown"
		
		size = SubElement(annotation, 'size')
		width = SubElement(size, 'width')
		width.text = str(w)		
		height = SubElement(size, 'height')
		height.text = str(h)
		depth = SubElement(size, 'depth')
		depth.text = str(d)
		
		segmented = SubElement(annotation, 'segmented')
		segmented.text="0"
		
		for l in self.labels:
			obj = SubElement(annotation, 'object')
			
			name = SubElement(obj, 'name')
			name.text = l.label
			pose = SubElement(obj, 'pose')
			pose.text = "Unspecified"
			truncated = SubElement(obj, 'truncated')
			truncated.text = "1"
			difficult = SubElement(obj, 'difficult')
			difficult.text = "0"
			
			bndbox = SubElement(obj, 'bndbox')
			xmin = SubElement(bndbox, 'xmin')
			xmin.text=str(l.x)
			ymin = SubElement(bndbox, 'ymin')
			ymin.text=str(l.y)
			xmax = SubElement(bndbox, 'xmax')
			xmax.text=str(l.x+l.w)
			ymax = SubElement(bndbox, 'ymax')
			ymax.text=str(l.y+l.h)
		
		xmlstring=prettifyXML(annotation)
		#print(xmlstring)
		xmlfilename=self.imagelistFiles[self.Fileselected][:-3]+"xml"
		print(xmlfilename)
		if os.path.exists(xmlfilename):
			os. remove(xmlfilename)
			
		f = open(xmlfilename,"a")
		f.write(xmlstring)
		f.close()
		self.imagehasxml[self.Fileselected]=True
		print("saved xml")
		
	def pagedecrease(self,args=()):
		self.page=max(1,self.page-1)
	def pageincrease(self,args=()):
		totalpages=max(len(self.imagelistFiles)//self.filesperpage,1)
		self.page=min(totalpages,self.page+1)
	
	def autoselect(self,args=()):
		self.selectmultibox = True
		self.selectsinglebox = False
		
	def autoconfirm(self,args=()):
		self.selectmultibox = False
		self.labels+=self.match.confirm()
	
	def autocancel(self,args=()):
		self.selectmultibox = False
		self.match.cancel()
		
		
	def draw(self):
		try:
			
			self.actionbar.draw()
			#draw the save button
			savebuttonbox=[700, 5, 64, 32]
			drawbox(savebuttonbox,self.world,(200,200,200),(175,175,175),self.save,text="save")
			#self.edge.draw(self.img)
		except Exception as e:
			print(e)
			#pass
		
		self.world.screen.blit(self.world.fontobject.render(str(self.currentfolder), 1, (0,0,0)),(0, 150+self.filesperpage*32))
		
		
		
		box=[1,1,84,52+self.filesperpage*32+10]
		
		#interface
		pygame.draw.rect(self.world.screen, (200,200,200),(box[0],box[1],box[2],box[3]), 0)
		pygame.draw.rect(self.world.screen, (0,0,0),(box[0]-1,box[1]-1,box[2]+1,box[3]+1), 1)
		
		#load button
		drawbox([10,10,64,32], self.world, (200,200,200), (175,175,175), self.loadlistimages, clickargs=(), text="load")
		
		#image buttons
		totalimages=len(self.imagelistFiles)
		totalpages=max(totalimages//self.filesperpage,1)
		
		#page handling
		y=75+self.filesperpage*32
		self.world.screen.blit(self.world.fontobject.render(str(self.page)+"/"+str(totalpages), 1, (0,0,0)),(30, y))
		drawbox([0,y,20,32], self.world, (200,200,200), (175,175,175), self.pagedecrease, clickargs=(), text="<")
		drawbox([60,y,20,32], self.world, (200,200,200), (175,175,175), self.pageincrease, clickargs=(), text=">")
		
		ll=self.filesperpage*(self.page-1)
		ul=min(self.filesperpage*(self.page),totalimages)
		for a,i in zip(range(ll,ul,1),range(0,self.filesperpage)):
		#for i in range(len(self.imagelist)):
			if a!=self.Fileselected:
				c=(200,200,200)
				hc=(175,175,175)
				if self.imagehasxml[a]:
					c=(0,200,0)
					hc=(0,175,0)
				drawbox([10,52+i*32,64,32], self.world, c, hc, self.loadimg, clickargs=(a), text=str(self.imagelist[a]))
			else:
				drawbox([10,52+i*32,64,32], self.world, (200,200,0), (175,175,0), None, text=str(self.imagelist[a]))
		
		
		
		try:
			_,_,_ = self.img.shape 
		except:
			return
		self.world.screen.blit(cvimage_to_pygame(self.img), (self.x, self.y))
		#select box
		if self.selecting:
			pygame.draw.rect(self.world.screen, (0,255,0), self.selectbox, 3)
			
			
		#draw the autoselect box
		box=[self.x+75,self.y-45,64,32]
		if not self.selectmultibox:
			drawbox(box, self.world, (200,200,200), (175,175,175), self.autoselect, text="Auto")
		else:
			drawbox(box, self.world, (0,200,0), (0,175,0), self.autoconfirm, text="confirm")
			drawbox([x+y for x,y in zip(box,[75,0,0,0])], self.world, (200,0,0), (175,0,0), self.autocancel, text="cancel")
			
			self.templatedropdown.draw()
		
		#draw the add single box
		box=[self.x,self.y-45,64,32]
		if not self.selectmultibox:
			if checkmousebox(box,[self.world.mouse_x,self.world.mouse_y]):
				if self.world.mouse_left_down:
					self.selectsinglebox = not self.selectsinglebox
					self.updatelabelselect(None)
				if self.selectsinglebox:
					c = (10,200,10)
				else:
					c = (200,200,200)
			else:
				if self.selectsinglebox:
					c=(10,180,10)
				else:
					c=(180,180,180)
		else:
			c=(150,150,150)
				
		pygame.draw.rect(self.world.screen, c,(box[0],box[1],box[2],box[3]), 0)
		pygame.draw.rect(self.world.screen, (0,0,0),(box[0]-1,box[1]-1,box[2]+1,box[3]+1), 1)
		self.world.screen.blit(self.world.fontobject.render("ADD 1", 1, (0,0,0)),(box[0]+5, box[1]+5))
		
		
		self.match.draw(self.img)
		for l in self.labels:
			l.draw()
        