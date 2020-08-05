import numpy as np
import pygame
import cv2
import math

from tkinter import filedialog
from tkinter import *
import os

from utils import clamp, cvimage_to_pygame,drawbox

#from imageprocessing.edge import edge
from imageprocessing.match import match
from interfacetools.actionbar import actionbar

class controller:
	def __init__(self,world):
		self.world=world
        
		#for dragging the image
		self.xx=0
		self.yy=0
		self.mouse_clicked=(0,0)
		
		self.imagelist=[]
		self.imagelistFiles=[]
		self.currentfolder=""
		
		self.img=None
		#self.edge=edge(self.world,self,94,10)
		self.match = match(self.world,self,94,50)
		self.actionbar=actionbar(self.world,self,1125,50)
		
		self.loadFolder("./images/")
		
		self.selected=-1
		
	def update(self):
		#dragging around
		if self.world.mouse_right_down or self.world.mouse_right_up:
			self.mouse_clicked=(self.world.mouse_x,self.world.mouse_y)
		if self.world.mouse_right:
			self.xx+=self.world.mouse_x-self.mouse_clicked[0]
			self.yy+=self.world.mouse_y-self.mouse_clicked[1]
			self.mouse_clicked=(self.world.mouse_x,self.world.mouse_y)
		
		self.match.update()
		self.actionbar.update()
		
	def loadlistimages(self,args=()):
		root = Tk()
		root.withdraw()
		folder = filedialog.askdirectory(parent=root)
		self.loadFolder(folder)
		
	def loadFolder(self,folder):
		self.imagelist=[]
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
		
	def draw(self):
		try:
			
			self.match.draw(self.img)
			self.actionbar.draw()
			#self.edge.draw(self.img)
		except Exception as e:
			print(e)
			#pass
		
		self.world.screen.blit(self.world.fontobject.render(str(self.currentfolder), 1, (0,0,0)),(50, 50))
		
		box=[1,1,84,52+len(self.imagelist)*32+10]
		
		#interface
		pygame.draw.rect(self.world.screen, (200,200,200),(box[0],box[1],box[2],box[3]), 0)
		pygame.draw.rect(self.world.screen, (0,0,0),(box[0]-1,box[1]-1,box[2]+1,box[3]+1), 1)
		
		#load button
		drawbox([10,10,64,32], self.world, (200,200,200), (175,175,175), self.loadlistimages, clickargs=(), text="load")
		
		#image buttons
		for i,img in enumerate(self.imagelist):
			if i!=self.selected:
				drawbox([10,52+i*32,64,32], self.world, (200,200,200), (175,175,175), self.loadimg, clickargs=(i), text=str(img))
			else:
				drawbox([10,52+i*32,64,32], self.world, (0,200,0), (0,175,0), None, text=str(img))
		

        