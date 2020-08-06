import numpy as np
import pygame
import cv2
import math

from tkinter import filedialog
from tkinter import *
import os

from utils import clamp, cvimage_to_pygame, drawbox, prettifyXML, hsv_to_rgb

#from imageprocessing.edge import edge
from imageprocessing.match import match
from interfacetools.actionbar import actionbar

from xml.etree.ElementTree import Element, SubElement
import xml.etree.ElementTree as ET
from interfacetools.label import label 

class controller:
	def __init__(self,world):
		self.world=world
        
		#for dragging the image
		self.xx=0
		self.yy=0
		self.mouse_clicked=(0,0)
		
		self.imagelist=[]
		self.imagelistFiles=[]
		self.currentfolder="images"
		
		self.img=None
		#self.edge=edge(self.world,self,94,10)
		self.match = match(self.world,self,94,50)
		self.actionbar=actionbar(self.world,self,1125,50)
		
		self.loadFolder(self.currentfolder)
		self.filesperpage=20
		self.page=1
		self.totalpages=0
		
		self.selected=-1
		
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
				
		self.match.update()
		self.actionbar.update()
		
	def loadlistimages(self,args=()):
		root = Tk()
		root.withdraw()
		folder = filedialog.askdirectory(parent=root)
		self.loadFolder(folder)
		
	def loadFolder(self,folder):
		self.imagelist=[]
		self.imagelistFiles=[]
		for file in os.listdir(folder):
			if file.endswith(".png") or file.endswith(".jpg") or file.endswith(".JPG") or file.endswith(".PNG"):
				self.imagelistFiles.append(str(folder)+"/"+str(file))
				if len(str(file))>9:
					self.imagelist.append(str(file)[0:6]+"...")
				else:
					self.imagelist.append(str(file))
		#print(self.imagelist)
				
	def loadimg(self,args=()):
		i=args
		self.selected=i
		self.img=cv2.imread(self.imagelistFiles[i])
		self.match.reset()
		#load the labels if the xml file exists
		xmlfilename=self.imagelistFiles[self.selected][:-3]+"xml"
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
					
				loadedlabel = label(self.world,self.match,x,y,w,h,name.text,c)
				self.match.labels.append(loadedlabel)
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
		filename.text = self.imagelistFiles[self.selected]
		
		path = SubElement(annotation, 'path')
		path.text = os. getcwd() + "\\" +self.imagelistFiles[self.selected].replace("/","\\")
		
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
		
		for l in self.match.labels:
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
		xmlfilename=self.imagelistFiles[self.selected][:-3]+"xml"
		print(xmlfilename)
		if os.path.exists(xmlfilename):
			os. remove(xmlfilename)
			
		f = open(xmlfilename,"a")
		f.write(xmlstring)
		f.close()
		print("saved xml")
		
	def pagedecrease(self,args=()):
		self.page=max(1,self.page-1)
	def pageincrease(self,args=()):
		totalpages=max(len(self.imagelist)//self.filesperpage,1)
		self.page=min(totalpages,self.page+1)
		
	def draw(self):
		try:
			self.match.draw(self.img)
			self.actionbar.draw()
			#draw the save button
			savebuttonbox=[700, 5, 64, 32]
			drawbox(savebuttonbox,self.world,(200,200,200),(175,175,175),self.save,text="save")
			#self.edge.draw(self.img)
		except Exception as e:
			print(e)
			#pass
		
		self.world.screen.blit(self.world.fontobject.render(str(self.currentfolder), 1, (0,0,0)),(0, 100+self.filesperpage*32))
		
		
		
		box=[1,1,84,52+self.filesperpage*32+10]
		
		#interface
		pygame.draw.rect(self.world.screen, (200,200,200),(box[0],box[1],box[2],box[3]), 0)
		pygame.draw.rect(self.world.screen, (0,0,0),(box[0]-1,box[1]-1,box[2]+1,box[3]+1), 1)
		
		#load button
		drawbox([10,10,64,32], self.world, (200,200,200), (175,175,175), self.loadlistimages, clickargs=(), text="load")
		
		#image buttons
		totalimages=len(self.imagelist)
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
			if a!=self.selected:
				drawbox([10,52+i*32,64,32], self.world, (200,200,200), (175,175,175), self.loadimg, clickargs=(a), text=str(self.imagelist[a]))
			else:
				drawbox([10,52+i*32,64,32], self.world, (0,200,0), (0,175,0), None, text=str(self.imagelist[a]))
		

        